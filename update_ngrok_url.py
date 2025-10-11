"""
Script to update ngrok URL in Django settings
Run this script whenever you get a new ngrok URL
"""
import re

def update_ngrok_url():
    print("🔗 Update ngrok URL for Django")
    print("=" * 50)
    
    # Get current ngrok URL from user
    ngrok_url = input("Enter your ngrok URL (e.g., https://abc123.ngrok-free.app): ").strip()
    
    if not ngrok_url:
        print("❌ No URL provided. Exiting.")
        return
    
    # Ensure it starts with https://
    if not ngrok_url.startswith('http'):
        ngrok_url = 'https://' + ngrok_url
    
    # Remove trailing slash
    ngrok_url = ngrok_url.rstrip('/')
    
    try:
        # Read settings.py
        with open('student_management_system/settings.py', 'r') as f:
            content = f.read()
        
        # Pattern to find CSRF_TRUSTED_ORIGINS list
        pattern = r"(CSRF_TRUSTED_ORIGINS = \[)(.*?)(\])"
        
        def replace_ngrok(match):
            start = match.group(1)
            middle = match.group(2)
            end = match.group(3)
            
            # Split existing origins
            lines = middle.split('\n')
            new_lines = []
            ngrok_found = False
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Check if this line contains an ngrok URL
                if 'ngrok-free.app' in line or 'ngrok.io' in line:
                    # Replace with new URL
                    new_lines.append(f"    '{ngrok_url}',")
                    ngrok_found = True
                else:
                    new_lines.append(line)
            
            # If no ngrok URL was found, add it
            if not ngrok_found:
                new_lines.insert(0, f"    '{ngrok_url}',")
            
            new_middle = '\n'.join(new_lines) + '\n'
            return start + new_middle + end
        
        # Replace the CSRF_TRUSTED_ORIGINS list
        new_content = re.sub(pattern, replace_ngrok, content, flags=re.DOTALL)
        
        # Write back to settings.py
        with open('student_management_system/settings.py', 'w') as f:
            f.write(new_content)
        
        print(f"\n✅ Successfully updated ngrok URL to: {ngrok_url}")
        print("\n📝 Updated CSRF_TRUSTED_ORIGINS in settings.py")
        print("\n🚀 You can now access your app through ngrok!")
        print(f"   Visit: {ngrok_url}")
        print("\n⚠️  Remember to restart Django server if it's running:")
        print("   python manage.py runserver")
        
    except FileNotFoundError:
        print("❌ Error: settings.py not found!")
        print("   Make sure you're running this script from the project root directory.")
    except Exception as e:
        print(f"❌ Error updating settings: {e}")

def show_current_urls():
    """Show currently configured ngrok URLs"""
    try:
        with open('student_management_system/settings.py', 'r') as f:
            content = f.read()
        
        # Find CSRF_TRUSTED_ORIGINS
        pattern = r"CSRF_TRUSTED_ORIGINS = \[(.*?)\]"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            origins_str = match.group(1)
            origins = re.findall(r"'([^']+)'", origins_str)
            
            print("\n📋 Currently configured trusted origins:")
            for origin in origins:
                if 'ngrok' in origin:
                    print(f"   🔗 {origin} (ngrok)")
                else:
                    print(f"   🌐 {origin}")
        else:
            print("❌ Could not find CSRF_TRUSTED_ORIGINS in settings.py")
            
    except Exception as e:
        print(f"❌ Error reading settings: {e}")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("   Django ngrok URL Updater")
    print("="*50 + "\n")
    
    print("Options:")
    print("1. Update ngrok URL")
    print("2. Show current URLs")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        update_ngrok_url()
    elif choice == '2':
        show_current_urls()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")

