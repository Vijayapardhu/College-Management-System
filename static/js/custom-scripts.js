/**
 * Custom JavaScript for EduVision - College Management System
 * Modern, responsive, and accessible functionality
 */

// Global Variables
let isDarkMode = false;
let sidebarCollapsed = false;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    loadUserPreferences();
    initializeDataTables();
    initializeCharts();
    setupFormValidation();
    setupNotifications();
});

/**
 * Initialize all components
 */
function initializeComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize search
    initializeSearch();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize sidebar
    initializeSidebar();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Window resize
    window.addEventListener('resize', handleResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Form submissions
    document.addEventListener('submit', handleFormSubmission);
    
    // Click outside to close dropdowns
    document.addEventListener('click', handleClickOutside);
    
    // Online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        const html = document.documentElement;
        const body = document.body;
        const themeIcon = document.getElementById('theme-icon');
        
        isDarkMode = true;
        html.classList.add('dark');
        body.classList.add('dark-mode', 'dark');
        
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
        
        console.log('🎨 Loaded dark mode from preferences');
    }
    
    // Load sidebar state
    const savedSidebarState = localStorage.getItem('sidebar-collapsed');
    if (savedSidebarState === 'true') {
        toggleSidebar();
    }
}

/**
 * Initialize DataTables
 */
function initializeDataTables() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            lengthChange: false,
            autoWidth: false,
            buttons: [
                {
                    extend: 'copy',
                    className: 'btn btn-sm btn-outline-primary'
                },
                {
                    extend: 'csv',
                    className: 'btn btn-sm btn-outline-success'
                },
                {
                    extend: 'excel',
                    className: 'btn btn-sm btn-outline-info'
                },
                {
                    extend: 'pdf',
                    className: 'btn btn-sm btn-outline-danger'
                },
                {
                    extend: 'print',
                    className: 'btn btn-sm btn-outline-secondary'
                }
            ],
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                },
                emptyTable: "No data available in table",
                zeroRecords: "No matching records found"
            },
            dom: 'Bfrtip',
            initComplete: function() {
                // Add custom styling to buttons
                this.api().buttons().container().addClass('btn-group');
            }
        });
    }
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    // Chart.js configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6b7280';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize modals
 */
function initializeModals() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        // Auto-focus on modal show
        document.addEventListener('shown.bs.modal', function(event) {
            const modal = event.target;
            const focusableElement = modal.querySelector('input, textarea, select, button');
            if (focusableElement) {
                focusableElement.focus();
            }
        });
    }
}

/**
 * Initialize dropdowns
 */
function initializeDropdowns() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
        const dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }
}

/**
 * Initialize navigation
 */
function initializeNavigation() {
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile navigation
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', toggleMobileSidebar);
    }
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm.length > 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(searchTerm);
                }, 300);
            }
        });
    }
}

/**
 * Perform search
 */
function performSearch(searchTerm) {
    // Implement search functionality here
    console.log('Searching for:', searchTerm);
    
    // Example: Filter table rows
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Initialize theme toggle
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

/**
 * Toggle theme (Tailwind CSS dark mode compatible)
 */
function toggleTheme() {
    const html = document.documentElement;
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    isDarkMode = !isDarkMode;
    
    // Add/remove dark class on HTML element (for Tailwind CSS)
    html.classList.toggle('dark', isDarkMode);
    
    // Also add to body for custom CSS compatibility
    body.classList.toggle('dark-mode', isDarkMode);
    body.classList.toggle('dark', isDarkMode);
    
    // Update theme icon
    if (themeIcon) {
        themeIcon.classList.toggle('fa-moon', !isDarkMode);
        themeIcon.classList.toggle('fa-sun', isDarkMode);
    }
    
    // Save preference
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update chart colors if dark mode
    updateChartColors();
    
    // Log for debugging
    console.log('🎨 Theme toggled:', isDarkMode ? 'Dark Mode' : 'Light Mode');
}

/**
 * Update chart colors for dark mode
 */
function updateChartColors() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isDarkMode ? '#e5e7eb' : '#6b7280';
        Chart.defaults.plugins.legend.labels.color = isDarkMode ? '#e5e7eb' : '#6b7280';
    }
}

/**
 * Initialize sidebar
 */
function initializeSidebar() {
    const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
}

/**
 * Toggle sidebar
 */
function toggleSidebar() {
    const wrapper = document.querySelector('.wrapper');
    sidebarCollapsed = !sidebarCollapsed;
    
    wrapper.classList.toggle('sidebar-collapsed', sidebarCollapsed);
    localStorage.setItem('sidebar-collapsed', sidebarCollapsed);
}

/**
 * Toggle mobile sidebar
 */
function toggleMobileSidebar() {
    const wrapper = document.querySelector('.wrapper');
    wrapper.classList.toggle('sidebar-mobile-open');
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * Handle form submission
 */
function handleFormSubmission(event) {
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Skip if form has custom handler
    if (form.hasAttribute('data-custom-submit') || form.classList.contains('custom-submit-handler')) {
        return;
    }
    
    if (submitBtn && !submitBtn.disabled) {
        // Store original button content
        if (!submitBtn.hasAttribute('data-original-html')) {
            submitBtn.setAttribute('data-original-html', submitBtn.innerHTML);
        }
        
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        
        // Re-enable button after 3 seconds (fallback)
        setTimeout(() => {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
            const originalHTML = submitBtn.getAttribute('data-original-html');
            if (originalHTML) {
                submitBtn.innerHTML = originalHTML;
            }
        }, 3000);
    }
}

/**
 * Setup notifications
 */
function setupNotifications() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

/**
 * Create toast container
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Handle resize events
 */
function handleResize() {
    const wrapper = document.querySelector('.wrapper');
    
    if (window.innerWidth < 768) {
        wrapper.classList.add('sidebar-collapsed');
    } else {
        wrapper.classList.remove('sidebar-collapsed');
    }
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
}

/**
 * Handle click outside
 */
function handleClickOutside(event) {
    // Close dropdowns when clicking outside
    if (!event.target.closest('.dropdown')) {
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
}

/**
 * Handle online status
 */
function handleOnlineStatus() {
    showNotification('You are back online', 'success');
}

/**
 * Handle offline status
 */
function handleOfflineStatus() {
    showNotification('You are offline. Some features may be limited.', 'warning');
}

/**
 * Utility Functions
 */

/**
 * Format date
 */
function formatDate(date, format = 'short') {
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    
    return new Intl.DateTimeFormat('en-US', options[format]).format(new Date(date));
}

/**
 * Format number
 */
function formatNumber(number, decimals = 0) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard', 'success');
    }
}

/**
 * Download file
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Print element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        @media print { .no-print { display: none; } }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

/**
 * Export functions to global scope
 */
window.EduVision = {
    showNotification,
    formatDate,
    formatNumber,
    formatCurrency,
    copyToClipboard,
    downloadFile,
    printElement,
    toggleTheme,
    toggleSidebar,
    toggleMobileSidebar
};















 * Modern, responsive, and accessible functionality
 */

// Global Variables
let isDarkMode = false;
let sidebarCollapsed = false;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    loadUserPreferences();
    initializeDataTables();
    initializeCharts();
    setupFormValidation();
    setupNotifications();
});

/**
 * Initialize all components
 */
function initializeComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize search
    initializeSearch();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize sidebar
    initializeSidebar();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Window resize
    window.addEventListener('resize', handleResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Form submissions
    document.addEventListener('submit', handleFormSubmission);
    
    // Click outside to close dropdowns
    document.addEventListener('click', handleClickOutside);
    
    // Online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        const html = document.documentElement;
        const body = document.body;
        const themeIcon = document.getElementById('theme-icon');
        
        isDarkMode = true;
        html.classList.add('dark');
        body.classList.add('dark-mode', 'dark');
        
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
        
        console.log('🎨 Loaded dark mode from preferences');
    }
    
    // Load sidebar state
    const savedSidebarState = localStorage.getItem('sidebar-collapsed');
    if (savedSidebarState === 'true') {
        toggleSidebar();
    }
}

/**
 * Initialize DataTables
 */
function initializeDataTables() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            lengthChange: false,
            autoWidth: false,
            buttons: [
                {
                    extend: 'copy',
                    className: 'btn btn-sm btn-outline-primary'
                },
                {
                    extend: 'csv',
                    className: 'btn btn-sm btn-outline-success'
                },
                {
                    extend: 'excel',
                    className: 'btn btn-sm btn-outline-info'
                },
                {
                    extend: 'pdf',
                    className: 'btn btn-sm btn-outline-danger'
                },
                {
                    extend: 'print',
                    className: 'btn btn-sm btn-outline-secondary'
                }
            ],
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                },
                emptyTable: "No data available in table",
                zeroRecords: "No matching records found"
            },
            dom: 'Bfrtip',
            initComplete: function() {
                // Add custom styling to buttons
                this.api().buttons().container().addClass('btn-group');
            }
        });
    }
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    // Chart.js configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6b7280';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize modals
 */
function initializeModals() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        // Auto-focus on modal show
        document.addEventListener('shown.bs.modal', function(event) {
            const modal = event.target;
            const focusableElement = modal.querySelector('input, textarea, select, button');
            if (focusableElement) {
                focusableElement.focus();
            }
        });
    }
}

/**
 * Initialize dropdowns
 */
function initializeDropdowns() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
        const dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }
}

/**
 * Initialize navigation
 */
function initializeNavigation() {
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile navigation
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', toggleMobileSidebar);
    }
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm.length > 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(searchTerm);
                }, 300);
            }
        });
    }
}

/**
 * Perform search
 */
function performSearch(searchTerm) {
    // Implement search functionality here
    console.log('Searching for:', searchTerm);
    
    // Example: Filter table rows
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Initialize theme toggle
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

/**
 * Toggle theme (Tailwind CSS dark mode compatible)
 */
function toggleTheme() {
    const html = document.documentElement;
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    isDarkMode = !isDarkMode;
    
    // Add/remove dark class on HTML element (for Tailwind CSS)
    html.classList.toggle('dark', isDarkMode);
    
    // Also add to body for custom CSS compatibility
    body.classList.toggle('dark-mode', isDarkMode);
    body.classList.toggle('dark', isDarkMode);
    
    // Update theme icon
    if (themeIcon) {
        themeIcon.classList.toggle('fa-moon', !isDarkMode);
        themeIcon.classList.toggle('fa-sun', isDarkMode);
    }
    
    // Save preference
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update chart colors if dark mode
    updateChartColors();
    
    // Log for debugging
    console.log('🎨 Theme toggled:', isDarkMode ? 'Dark Mode' : 'Light Mode');
}

/**
 * Update chart colors for dark mode
 */
function updateChartColors() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isDarkMode ? '#e5e7eb' : '#6b7280';
        Chart.defaults.plugins.legend.labels.color = isDarkMode ? '#e5e7eb' : '#6b7280';
    }
}

/**
 * Initialize sidebar
 */
function initializeSidebar() {
    const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
}

/**
 * Toggle sidebar
 */
function toggleSidebar() {
    const wrapper = document.querySelector('.wrapper');
    sidebarCollapsed = !sidebarCollapsed;
    
    wrapper.classList.toggle('sidebar-collapsed', sidebarCollapsed);
    localStorage.setItem('sidebar-collapsed', sidebarCollapsed);
}

/**
 * Toggle mobile sidebar
 */
function toggleMobileSidebar() {
    const wrapper = document.querySelector('.wrapper');
    wrapper.classList.toggle('sidebar-mobile-open');
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * Handle form submission
 */
function handleFormSubmission(event) {
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Skip if form has custom handler
    if (form.hasAttribute('data-custom-submit') || form.classList.contains('custom-submit-handler')) {
        return;
    }
    
    if (submitBtn && !submitBtn.disabled) {
        // Store original button content
        if (!submitBtn.hasAttribute('data-original-html')) {
            submitBtn.setAttribute('data-original-html', submitBtn.innerHTML);
        }
        
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        
        // Re-enable button after 3 seconds (fallback)
        setTimeout(() => {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
            const originalHTML = submitBtn.getAttribute('data-original-html');
            if (originalHTML) {
                submitBtn.innerHTML = originalHTML;
            }
        }, 3000);
    }
}

/**
 * Setup notifications
 */
function setupNotifications() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

/**
 * Create toast container
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Handle resize events
 */
function handleResize() {
    const wrapper = document.querySelector('.wrapper');
    
    if (window.innerWidth < 768) {
        wrapper.classList.add('sidebar-collapsed');
    } else {
        wrapper.classList.remove('sidebar-collapsed');
    }
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
}

/**
 * Handle click outside
 */
function handleClickOutside(event) {
    // Close dropdowns when clicking outside
    if (!event.target.closest('.dropdown')) {
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
}

/**
 * Handle online status
 */
function handleOnlineStatus() {
    showNotification('You are back online', 'success');
}

/**
 * Handle offline status
 */
function handleOfflineStatus() {
    showNotification('You are offline. Some features may be limited.', 'warning');
}

/**
 * Utility Functions
 */

/**
 * Format date
 */
function formatDate(date, format = 'short') {
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    
    return new Intl.DateTimeFormat('en-US', options[format]).format(new Date(date));
}

/**
 * Format number
 */
function formatNumber(number, decimals = 0) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard', 'success');
    }
}

/**
 * Download file
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Print element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        @media print { .no-print { display: none; } }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

/**
 * Export functions to global scope
 */
window.EduVision = {
    showNotification,
    formatDate,
    formatNumber,
    formatCurrency,
    copyToClipboard,
    downloadFile,
    printElement,
    toggleTheme,
    toggleSidebar,
    toggleMobileSidebar
};




















 * Modern, responsive, and accessible functionality
 */

// Global Variables
let isDarkMode = false;
let sidebarCollapsed = false;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    loadUserPreferences();
    initializeDataTables();
    initializeCharts();
    setupFormValidation();
    setupNotifications();
});

/**
 * Initialize all components
 */
function initializeComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize search
    initializeSearch();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize sidebar
    initializeSidebar();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Window resize
    window.addEventListener('resize', handleResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Form submissions
    document.addEventListener('submit', handleFormSubmission);
    
    // Click outside to close dropdowns
    document.addEventListener('click', handleClickOutside);
    
    // Online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        const html = document.documentElement;
        const body = document.body;
        const themeIcon = document.getElementById('theme-icon');
        
        isDarkMode = true;
        html.classList.add('dark');
        body.classList.add('dark-mode', 'dark');
        
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
        
        console.log('🎨 Loaded dark mode from preferences');
    }
    
    // Load sidebar state
    const savedSidebarState = localStorage.getItem('sidebar-collapsed');
    if (savedSidebarState === 'true') {
        toggleSidebar();
    }
}

/**
 * Initialize DataTables
 */
function initializeDataTables() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            lengthChange: false,
            autoWidth: false,
            buttons: [
                {
                    extend: 'copy',
                    className: 'btn btn-sm btn-outline-primary'
                },
                {
                    extend: 'csv',
                    className: 'btn btn-sm btn-outline-success'
                },
                {
                    extend: 'excel',
                    className: 'btn btn-sm btn-outline-info'
                },
                {
                    extend: 'pdf',
                    className: 'btn btn-sm btn-outline-danger'
                },
                {
                    extend: 'print',
                    className: 'btn btn-sm btn-outline-secondary'
                }
            ],
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                },
                emptyTable: "No data available in table",
                zeroRecords: "No matching records found"
            },
            dom: 'Bfrtip',
            initComplete: function() {
                // Add custom styling to buttons
                this.api().buttons().container().addClass('btn-group');
            }
        });
    }
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    // Chart.js configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6b7280';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize modals
 */
function initializeModals() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        // Auto-focus on modal show
        document.addEventListener('shown.bs.modal', function(event) {
            const modal = event.target;
            const focusableElement = modal.querySelector('input, textarea, select, button');
            if (focusableElement) {
                focusableElement.focus();
            }
        });
    }
}

/**
 * Initialize dropdowns
 */
function initializeDropdowns() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
        const dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }
}

/**
 * Initialize navigation
 */
function initializeNavigation() {
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile navigation
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', toggleMobileSidebar);
    }
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm.length > 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(searchTerm);
                }, 300);
            }
        });
    }
}

/**
 * Perform search
 */
function performSearch(searchTerm) {
    // Implement search functionality here
    console.log('Searching for:', searchTerm);
    
    // Example: Filter table rows
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Initialize theme toggle
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

/**
 * Toggle theme (Tailwind CSS dark mode compatible)
 */
function toggleTheme() {
    const html = document.documentElement;
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    isDarkMode = !isDarkMode;
    
    // Add/remove dark class on HTML element (for Tailwind CSS)
    html.classList.toggle('dark', isDarkMode);
    
    // Also add to body for custom CSS compatibility
    body.classList.toggle('dark-mode', isDarkMode);
    body.classList.toggle('dark', isDarkMode);
    
    // Update theme icon
    if (themeIcon) {
        themeIcon.classList.toggle('fa-moon', !isDarkMode);
        themeIcon.classList.toggle('fa-sun', isDarkMode);
    }
    
    // Save preference
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update chart colors if dark mode
    updateChartColors();
    
    // Log for debugging
    console.log('🎨 Theme toggled:', isDarkMode ? 'Dark Mode' : 'Light Mode');
}

/**
 * Update chart colors for dark mode
 */
function updateChartColors() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isDarkMode ? '#e5e7eb' : '#6b7280';
        Chart.defaults.plugins.legend.labels.color = isDarkMode ? '#e5e7eb' : '#6b7280';
    }
}

/**
 * Initialize sidebar
 */
function initializeSidebar() {
    const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
}

/**
 * Toggle sidebar
 */
function toggleSidebar() {
    const wrapper = document.querySelector('.wrapper');
    sidebarCollapsed = !sidebarCollapsed;
    
    wrapper.classList.toggle('sidebar-collapsed', sidebarCollapsed);
    localStorage.setItem('sidebar-collapsed', sidebarCollapsed);
}

/**
 * Toggle mobile sidebar
 */
function toggleMobileSidebar() {
    const wrapper = document.querySelector('.wrapper');
    wrapper.classList.toggle('sidebar-mobile-open');
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * Handle form submission
 */
function handleFormSubmission(event) {
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Skip if form has custom handler
    if (form.hasAttribute('data-custom-submit') || form.classList.contains('custom-submit-handler')) {
        return;
    }
    
    if (submitBtn && !submitBtn.disabled) {
        // Store original button content
        if (!submitBtn.hasAttribute('data-original-html')) {
            submitBtn.setAttribute('data-original-html', submitBtn.innerHTML);
        }
        
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        
        // Re-enable button after 3 seconds (fallback)
        setTimeout(() => {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
            const originalHTML = submitBtn.getAttribute('data-original-html');
            if (originalHTML) {
                submitBtn.innerHTML = originalHTML;
            }
        }, 3000);
    }
}

/**
 * Setup notifications
 */
function setupNotifications() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

/**
 * Create toast container
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Handle resize events
 */
function handleResize() {
    const wrapper = document.querySelector('.wrapper');
    
    if (window.innerWidth < 768) {
        wrapper.classList.add('sidebar-collapsed');
    } else {
        wrapper.classList.remove('sidebar-collapsed');
    }
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
}

/**
 * Handle click outside
 */
function handleClickOutside(event) {
    // Close dropdowns when clicking outside
    if (!event.target.closest('.dropdown')) {
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
}

/**
 * Handle online status
 */
function handleOnlineStatus() {
    showNotification('You are back online', 'success');
}

/**
 * Handle offline status
 */
function handleOfflineStatus() {
    showNotification('You are offline. Some features may be limited.', 'warning');
}

/**
 * Utility Functions
 */

/**
 * Format date
 */
function formatDate(date, format = 'short') {
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    
    return new Intl.DateTimeFormat('en-US', options[format]).format(new Date(date));
}

/**
 * Format number
 */
function formatNumber(number, decimals = 0) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard', 'success');
    }
}

/**
 * Download file
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Print element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        @media print { .no-print { display: none; } }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

/**
 * Export functions to global scope
 */
window.EduVision = {
    showNotification,
    formatDate,
    formatNumber,
    formatCurrency,
    copyToClipboard,
    downloadFile,
    printElement,
    toggleTheme,
    toggleSidebar,
    toggleMobileSidebar
};















 * Modern, responsive, and accessible functionality
 */

// Global Variables
let isDarkMode = false;
let sidebarCollapsed = false;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    loadUserPreferences();
    initializeDataTables();
    initializeCharts();
    setupFormValidation();
    setupNotifications();
});

/**
 * Initialize all components
 */
function initializeComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize search
    initializeSearch();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize sidebar
    initializeSidebar();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Window resize
    window.addEventListener('resize', handleResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Form submissions
    document.addEventListener('submit', handleFormSubmission);
    
    // Click outside to close dropdowns
    document.addEventListener('click', handleClickOutside);
    
    // Online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        const html = document.documentElement;
        const body = document.body;
        const themeIcon = document.getElementById('theme-icon');
        
        isDarkMode = true;
        html.classList.add('dark');
        body.classList.add('dark-mode', 'dark');
        
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
        
        console.log('🎨 Loaded dark mode from preferences');
    }
    
    // Load sidebar state
    const savedSidebarState = localStorage.getItem('sidebar-collapsed');
    if (savedSidebarState === 'true') {
        toggleSidebar();
    }
}

/**
 * Initialize DataTables
 */
function initializeDataTables() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            lengthChange: false,
            autoWidth: false,
            buttons: [
                {
                    extend: 'copy',
                    className: 'btn btn-sm btn-outline-primary'
                },
                {
                    extend: 'csv',
                    className: 'btn btn-sm btn-outline-success'
                },
                {
                    extend: 'excel',
                    className: 'btn btn-sm btn-outline-info'
                },
                {
                    extend: 'pdf',
                    className: 'btn btn-sm btn-outline-danger'
                },
                {
                    extend: 'print',
                    className: 'btn btn-sm btn-outline-secondary'
                }
            ],
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                },
                emptyTable: "No data available in table",
                zeroRecords: "No matching records found"
            },
            dom: 'Bfrtip',
            initComplete: function() {
                // Add custom styling to buttons
                this.api().buttons().container().addClass('btn-group');
            }
        });
    }
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    // Chart.js configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6b7280';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize modals
 */
function initializeModals() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        // Auto-focus on modal show
        document.addEventListener('shown.bs.modal', function(event) {
            const modal = event.target;
            const focusableElement = modal.querySelector('input, textarea, select, button');
            if (focusableElement) {
                focusableElement.focus();
            }
        });
    }
}

/**
 * Initialize dropdowns
 */
function initializeDropdowns() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
        const dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }
}

/**
 * Initialize navigation
 */
function initializeNavigation() {
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile navigation
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', toggleMobileSidebar);
    }
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm.length > 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(searchTerm);
                }, 300);
            }
        });
    }
}

/**
 * Perform search
 */
function performSearch(searchTerm) {
    // Implement search functionality here
    console.log('Searching for:', searchTerm);
    
    // Example: Filter table rows
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Initialize theme toggle
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

/**
 * Toggle theme (Tailwind CSS dark mode compatible)
 */
function toggleTheme() {
    const html = document.documentElement;
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    isDarkMode = !isDarkMode;
    
    // Add/remove dark class on HTML element (for Tailwind CSS)
    html.classList.toggle('dark', isDarkMode);
    
    // Also add to body for custom CSS compatibility
    body.classList.toggle('dark-mode', isDarkMode);
    body.classList.toggle('dark', isDarkMode);
    
    // Update theme icon
    if (themeIcon) {
        themeIcon.classList.toggle('fa-moon', !isDarkMode);
        themeIcon.classList.toggle('fa-sun', isDarkMode);
    }
    
    // Save preference
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update chart colors if dark mode
    updateChartColors();
    
    // Log for debugging
    console.log('🎨 Theme toggled:', isDarkMode ? 'Dark Mode' : 'Light Mode');
}

/**
 * Update chart colors for dark mode
 */
function updateChartColors() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isDarkMode ? '#e5e7eb' : '#6b7280';
        Chart.defaults.plugins.legend.labels.color = isDarkMode ? '#e5e7eb' : '#6b7280';
    }
}

/**
 * Initialize sidebar
 */
function initializeSidebar() {
    const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
}

/**
 * Toggle sidebar
 */
function toggleSidebar() {
    const wrapper = document.querySelector('.wrapper');
    sidebarCollapsed = !sidebarCollapsed;
    
    wrapper.classList.toggle('sidebar-collapsed', sidebarCollapsed);
    localStorage.setItem('sidebar-collapsed', sidebarCollapsed);
}

/**
 * Toggle mobile sidebar
 */
function toggleMobileSidebar() {
    const wrapper = document.querySelector('.wrapper');
    wrapper.classList.toggle('sidebar-mobile-open');
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * Handle form submission
 */
function handleFormSubmission(event) {
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Skip if form has custom handler
    if (form.hasAttribute('data-custom-submit') || form.classList.contains('custom-submit-handler')) {
        return;
    }
    
    if (submitBtn && !submitBtn.disabled) {
        // Store original button content
        if (!submitBtn.hasAttribute('data-original-html')) {
            submitBtn.setAttribute('data-original-html', submitBtn.innerHTML);
        }
        
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        
        // Re-enable button after 3 seconds (fallback)
        setTimeout(() => {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
            const originalHTML = submitBtn.getAttribute('data-original-html');
            if (originalHTML) {
                submitBtn.innerHTML = originalHTML;
            }
        }, 3000);
    }
}

/**
 * Setup notifications
 */
function setupNotifications() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

/**
 * Create toast container
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Handle resize events
 */
function handleResize() {
    const wrapper = document.querySelector('.wrapper');
    
    if (window.innerWidth < 768) {
        wrapper.classList.add('sidebar-collapsed');
    } else {
        wrapper.classList.remove('sidebar-collapsed');
    }
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
}

/**
 * Handle click outside
 */
function handleClickOutside(event) {
    // Close dropdowns when clicking outside
    if (!event.target.closest('.dropdown')) {
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
}

/**
 * Handle online status
 */
function handleOnlineStatus() {
    showNotification('You are back online', 'success');
}

/**
 * Handle offline status
 */
function handleOfflineStatus() {
    showNotification('You are offline. Some features may be limited.', 'warning');
}

/**
 * Utility Functions
 */

/**
 * Format date
 */
function formatDate(date, format = 'short') {
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    
    return new Intl.DateTimeFormat('en-US', options[format]).format(new Date(date));
}

/**
 * Format number
 */
function formatNumber(number, decimals = 0) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard', 'success');
    }
}

/**
 * Download file
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Print element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        @media print { .no-print { display: none; } }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

/**
 * Export functions to global scope
 */
window.EduVision = {
    showNotification,
    formatDate,
    formatNumber,
    formatCurrency,
    copyToClipboard,
    downloadFile,
    printElement,
    toggleTheme,
    toggleSidebar,
    toggleMobileSidebar
};





















