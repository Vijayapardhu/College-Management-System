"""
Playwright Test Script for College Management System
Tests the application and reports errors
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

class CMSTestRunner:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.errors = []
        self.warnings = []
        self.test_results = []
        
    def log_error(self, page_name, error_type, message, details=None):
        """Log an error found during testing"""
        error = {
            "page": page_name,
            "type": error_type,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error)
        print(f"❌ ERROR on {page_name}: {error_type} - {message}")
        
    def log_warning(self, page_name, message):
        """Log a warning found during testing"""
        warning = {
            "page": page_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning)
        print(f"⚠️  WARNING on {page_name}: {message}")
        
    def log_success(self, page_name, message):
        """Log a successful test"""
        result = {
            "page": page_name,
            "status": "success",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"✅ SUCCESS on {page_name}: {message}")

    async def check_console_errors(self, page, page_name):
        """Check for console errors on the page"""
        console_errors = []
        
        def handle_console(msg):
            if msg.type in ['error', 'warning']:
                console_errors.append({
                    "type": msg.type,
                    "text": msg.text
                })
                
        page.on('console', handle_console)
        return console_errors

    async def check_network_errors(self, page, page_name):
        """Check for network/HTTP errors"""
        network_errors = []
        
        def handle_response(response):
            if response.status >= 400:
                network_errors.append({
                    "url": response.url,
                    "status": response.status,
                    "statusText": response.status_text
                })
                
        page.on('response', handle_response)
        return network_errors

    async def test_public_pages(self, page):
        """Test public accessible pages"""
        print("\n" + "="*60)
        print("TESTING PUBLIC PAGES")
        print("="*60)
        
        # Test landing page
        try:
            await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            title = await page.title()
            print(f"\n📄 Landing Page Title: {title}")
            
            # Check for errors in page
            error_element = await page.query_selector('h1:has-text("Error")')
            if error_element:
                error_text = await error_element.inner_text()
                self.log_error("Landing Page", "Page Error", f"Error heading found: {error_text}")
            else:
                self.log_success("Landing Page", "Page loaded without errors")
                
            # Check if login form exists
            login_form = await page.query_selector('form')
            if login_form:
                print("✓ Login form found")
            else:
                self.log_warning("Landing Page", "No login form found")
                
            # Take screenshot
            await page.screenshot(path="screenshots/landing_page.png", full_page=True)
            
        except Exception as e:
            self.log_error("Landing Page", "Load Error", str(e))

        # Test public information page
        try:
            public_url = f"{self.base_url}/public/"
            await page.goto(public_url, wait_until="networkidle", timeout=30000)
            
            title = await page.title()
            print(f"\n📄 Public Info Page Title: {title}")
            
            error_element = await page.query_selector('h1:has-text("Error")')
            if error_element:
                error_text = await error_element.inner_text()
                self.log_error("Public Info", "Page Error", f"Error heading found: {error_text}")
            else:
                self.log_success("Public Info", "Page loaded successfully")
                
            await page.screenshot(path="screenshots/public_info.png", full_page=True)
            
        except Exception as e:
            self.log_error("Public Info", "Load Error", str(e))

    async def test_login_flow(self, page):
        """Test the login flow with OTP"""
        print("\n" + "="*60)
        print("TESTING LOGIN FLOW")
        print("="*60)
        
        try:
            await page.goto(f"{self.base_url}/login/", wait_until="networkidle")
            
            # Check if we're on login page
            current_url = page.url
            print(f"\n🔗 Current URL: {current_url}")
            
            # Look for email input
            email_input = await page.query_selector('input[name="email"], input[type="email"]')
            if email_input:
                print("✓ Email input found")
                self.log_success("Login Page", "Login form rendered correctly")
            else:
                self.log_error("Login Page", "Form Error", "Email input not found")
                
            # Check for password input
            password_input = await page.query_selector('input[name="password"], input[type="password"]')
            if password_input:
                print("✓ Password input found")
            else:
                self.log_error("Login Page", "Form Error", "Password input not found")
                
            # Take screenshot
            await page.screenshot(path="screenshots/login_page.png", full_page=True)
            
        except Exception as e:
            self.log_error("Login Page", "Load Error", str(e))

    async def test_admin_pages_without_auth(self, page):
        """Test admin pages without authentication (should redirect)"""
        print("\n" + "="*60)
        print("TESTING ADMIN PAGES (WITHOUT AUTH)")
        print("="*60)
        
        admin_urls = [
            "/admin/home/",
            "/hod-dashboard/",
            "/department-management/",
            "/department-analytics/",
            "/user-management-hub/",
            "/academic-operations/",
            "/timetable-dashboard/",
        ]
        
        for url_path in admin_urls:
            try:
                full_url = f"{self.base_url}{url_path}"
                print(f"\n🔍 Testing: {url_path}")
                
                response = await page.goto(full_url, wait_until="domcontentloaded", timeout=15000)
                
                # Check if redirected to login
                final_url = page.url
                if "/login" in final_url or "login" in final_url.lower():
                    print(f"✓ Correctly redirected to login")
                    self.log_success(url_path, "Auth protection working - redirected to login")
                elif response.status == 403:
                    print(f"✓ Access denied (403)")
                    self.log_success(url_path, "Auth protection working - 403 forbidden")
                elif response.status >= 500:
                    error_text = await page.content()
                    self.log_error(url_path, f"Server Error ({response.status})", "Page returned server error")
                elif response.status >= 400:
                    self.log_error(url_path, f"Client Error ({response.status})", "Page returned client error")
                else:
                    # Page loaded without redirect - possible security issue
                    self.log_warning(url_path, "Page loaded without authentication - check @login_required decorator")
                    
            except Exception as e:
                self.log_error(url_path, "Request Error", str(e))

    async def check_broken_links(self, page):
        """Check for broken links on main pages"""
        print("\n" + "="*60)
        print("CHECKING FOR BROKEN LINKS")
        print("="*60)
        
        try:
            await page.goto(self.base_url, wait_until="networkidle")
            
            # Get all links
            links = await page.query_selector_all('a[href]')
            print(f"\n📊 Found {len(links)} links on landing page")
            
            checked_urls = set()
            
            for link in links[:10]:  # Check first 10 links to save time
                href = await link.get_attribute('href')
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                    
                if href.startswith('http') and 'localhost' not in href and '127.0.0.1' not in href:
                    continue  # Skip external links
                    
                if href in checked_urls:
                    continue
                    
                checked_urls.add(href)
                
                try:
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = href
                        
                    response = await page.request.head(full_url)
                    
                    if response.status >= 400:
                        self.log_error("Broken Links", f"Dead link ({response.status})", f"URL: {href}")
                        print(f"  ❌ {href} - {response.status}")
                    else:
                        print(f"  ✓ {href} - OK")
                        
                except Exception as e:
                    print(f"  ⚠️  {href} - Error checking: {str(e)}")
                    
        except Exception as e:
            self.log_error("Link Checker", "Error", str(e))

    async def run_tests(self):
        """Run all tests"""
        async with async_playwright() as p:
            print("\n🚀 Starting Playwright Tests for College Management System")
            print("="*60)
            
            # Launch browser
            browser = await p.chromium.launch(headless=False)  # Set to True for headless
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True
            )
            page = await context.new_page()
            
            # Create screenshots directory
            import os
            os.makedirs("screenshots", exist_ok=True)
            
            # Setup console and network error listeners
            page.on('console', lambda msg: 
                print(f"🖥️  Console [{msg.type}]: {msg.text}") if msg.type in ['error', 'warning'] else None)
            
            page.on('pageerror', lambda exc: 
                self.log_error("JavaScript", "Runtime Error", str(exc)))
            
            # Run test suites
            await self.test_public_pages(page)
            await self.test_login_flow(page)
            await self.test_admin_pages_without_auth(page)
            await self.check_broken_links(page)
            
            # Close browser
            await browser.close()
            
            # Print summary
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        print(f"\n✅ Successful Tests: {len([r for r in self.test_results if r['status'] == 'success'])}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n" + "="*60)
            print("DETAILED ERRORS")
            print("="*60)
            for idx, error in enumerate(self.errors, 1):
                print(f"\n{idx}. {error['page']} - {error['type']}")
                print(f"   Message: {error['message']}")
                if error['details']:
                    print(f"   Details: {error['details']}")
                    
        if self.warnings:
            print("\n" + "="*60)
            print("WARNINGS")
            print("="*60)
            for idx, warning in enumerate(self.warnings, 1):
                print(f"\n{idx}. {warning['page']}")
                print(f"   {warning['message']}")
        
        # Save report to JSON
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.test_results),
                "successful": len([r for r in self.test_results if r['status'] == 'success']),
                "warnings": len(self.warnings),
                "errors": len(self.errors)
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "test_results": self.test_results
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Full report saved to: test_report.json")
        print(f"📸 Screenshots saved to: screenshots/ directory")

async def main():
    runner = CMSTestRunner()
    await runner.run_tests()

if __name__ == "__main__":
    asyncio.run(main())
