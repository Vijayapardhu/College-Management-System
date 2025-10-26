/* EduVision - Common Application Utilities */

(function() {
    'use strict';

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeTooltips();
        initializePopovers();
        initializeDataTables();
        initializeFormValidation();
        initializeCounterAnimations();
    });

    // Tooltip Initialization
    function initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            element.addEventListener('mouseenter', function() {
                showTooltip(this, this.getAttribute('data-tooltip'));
            });
            element.addEventListener('mouseleave', hideTooltip);
        });
    }

    function showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            z-index: 1000;
            white-space: nowrap;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
        tooltip.style.left = (rect.left + (rect.width - tooltip.offsetWidth) / 2) + 'px';
        
        element._tooltip = tooltip;
    }

    function hideTooltip(event) {
        if (event.target._tooltip) {
            event.target._tooltip.remove();
            delete event.target._tooltip;
        }
    }

    // Popover Initialization
    function initializePopovers() {
        const popovers = document.querySelectorAll('[data-popover]');
        popovers.forEach(element => {
            element.addEventListener('click', function(e) {
                e.stopPropagation();
                togglePopover(this);
            });
        });
        
        document.addEventListener('click', closeAllPopovers);
    }

    function togglePopover(element) {
        const content = element.getAttribute('data-popover');
        if (element._popover) {
            element._popover.remove();
            delete element._popover;
        } else {
            const popover = document.createElement('div');
            popover.className = 'popover';
            popover.innerHTML = content;
            popover.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                padding: 1rem;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                z-index: 1000;
                max-width: 300px;
            `;
            
            document.body.appendChild(popover);
            
            const rect = element.getBoundingClientRect();
            popover.style.top = (rect.bottom + 8) + 'px';
            popover.style.left = rect.left + 'px';
            
            element._popover = popover;
        }
    }

    function closeAllPopovers() {
        document.querySelectorAll('[data-popover]').forEach(element => {
            if (element._popover) {
                element._popover.remove();
                delete element._popover;
            }
        });
    }

    // DataTables Initialization
    function initializeDataTables() {
        if (typeof $.fn.DataTable !== 'undefined') {
            // Initialize all tables with class 'data-table'
            $('.data-table').each(function() {
                if (!$.fn.DataTable.isDataTable(this)) {
                    $(this).DataTable({
                        responsive: true,
                        pageLength: 25,
                        language: {
                            search: "_INPUT_",
                            searchPlaceholder: "Search records..."
                        },
                        dom: '<"flex items-center justify-between mb-4"lf>rt<"flex items-center justify-between mt-4"ip>',
                        drawCallback: function() {
                            // Apply Tailwind classes after redraw
                            $('.dataTables_paginate .paginate_button').addClass('pagination-btn');
                            $('.dataTables_paginate .paginate_button.current').addClass('pagination-btn-active');
                        }
                    });
                }
            });
            
            // Initialize common table IDs (example1, example2, etc.)
            const commonTableIds = ['example1', 'example2', 'example3', 'dataTable'];
            commonTableIds.forEach(tableId => {
                const table = document.getElementById(tableId);
                if (table && !$.fn.DataTable.isDataTable('#' + tableId)) {
                    $('#' + tableId).DataTable({
                        responsive: true,
                        pageLength: 25,
                        language: {
                            search: "_INPUT_",
                            searchPlaceholder: "Search records..."
                        },
                        dom: '<"flex items-center justify-between mb-4"lf>rt<"flex items-center justify-between mt-4"ip>',
                        drawCallback: function() {
                            // Apply Tailwind classes after redraw
                            $('.dataTables_paginate .paginate_button').addClass('pagination-btn');
                            $('.dataTables_paginate .paginate_button.current').addClass('pagination-btn-active');
                        }
                    });
                }
            });
        }
    }

    // Form Validation
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                    return false;
                }
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
            });
        });
    }

    function validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        let isValid = true;
        let message = '';
        
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'This field is required';
        } else if (type === 'email' && value && !isValidEmail(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        } else if (field.hasAttribute('minlength') && value.length < field.getAttribute('minlength')) {
            isValid = false;
            message = `Minimum ${field.getAttribute('minlength')} characters required`;
        }
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            removeFieldError(field);
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            showFieldError(field, message);
        }
        
        return isValid;
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showFieldError(field, message) {
        removeFieldError(field);
        const error = document.createElement('div');
        error.className = 'invalid-feedback';
        error.textContent = message;
        field.parentNode.appendChild(error);
    }

    function removeFieldError(field) {
        const error = field.parentNode.querySelector('.invalid-feedback');
        if (error) {
            error.remove();
        }
    }

    // Counter Animations
    function initializeCounterAnimations() {
        const counters = document.querySelectorAll('[data-count]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => {
            if (!counter.hasAttribute('data-animated')) {
                observer.observe(counter);
            }
        });
    }

    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const duration = 1500;
        const increment = target / (duration / 16);
        let current = 0;
        
        element.setAttribute('data-animated', 'true');
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };
        
        updateCounter();
    }

    // Export utilities to window object
    window.EduVision = {
        showTooltip,
        hideTooltip,
        validateForm,
        validateField,
        animateCounter,
        
        // Toast notifications
        toast: {
            success: (message) => showToast(message, 'success'),
            error: (message) => showToast(message, 'error'),
            warning: (message) => showToast(message, 'warning'),
            info: (message) => showToast(message, 'info')
        }
    };

    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} notification-slide-in fixed top-4 right-4 z-50 max-w-sm`;
        toast.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'} mr-2"></i>
                    <span>${message}</span>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-current opacity-50 hover:opacity-100">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

})();

