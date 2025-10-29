/**
 * EduVision College Management System - UX Enhancements
 * This file contains all user experience improvements including:
 * - Loading states
 * - Form validation feedback
 * - Toast notifications
 * - Tooltips and popovers
 * - Empty states
 * - Skeleton loaders
 * - Progress indicators
 * - Contextual help
 */

// ==========================================
// 1. LOADING STATES & PROGRESS INDICATORS
// ==========================================

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
    }

    // Show loading overlay
    showPageLoader(message = 'Loading...') {
        const loader = document.getElementById('page-loader') || this.createPageLoader();
        const loaderText = loader.querySelector('.loader-text');
        if (loaderText) {
            loaderText.textContent = message;
        }
        loader.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    // Hide loading overlay
    hidePageLoader() {
        const loader = document.getElementById('page-loader');
        if (loader) {
            loader.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    // Create page loader element
    createPageLoader() {
        const loader = document.createElement('div');
        loader.id = 'page-loader';
        loader.className = 'page-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="loader-text mt-3">Loading...</p>
            </div>
        `;
        document.body.appendChild(loader);
        return loader;
    }

    // Show button loading state
    showButtonLoading(button, text = 'Loading...') {
        if (!(button instanceof HTMLElement)) return;
        
        button.dataset.originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
        this.activeLoaders.add(button);
    }

    // Hide button loading state
    hideButtonLoading(button) {
        if (!(button instanceof HTMLElement)) return;
        
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
        this.activeLoaders.delete(button);
    }

    // Show inline loader
    showInlineLoader(element, size = 'md') {
        const sizeClass = {
            'sm': 'spinner-border-sm',
            'md': '',
            'lg': 'spinner-border-lg'
        }[size] || '';

        element.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary ${sizeClass}" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
}

// ==========================================
// 2. TOAST NOTIFICATIONS
// ==========================================

class ToastManager {
    constructor() {
        this.container = this.createContainer();
        this.toasts = [];
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);
        
        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: duration
        });
        
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
        
        return toast;
    }

    createToast(message, type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        const colors = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'info'
        };

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${colors[type]} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icons[type]} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// ==========================================
// 3. FORM VALIDATION & FEEDBACK
// ==========================================

class FormValidator {
    constructor(form) {
        this.form = form;
        this.init();
    }

    init() {
        // Add Bootstrap validation classes
        this.form.classList.add('needs-validation');
        this.form.noValidate = true;

        // Handle form submission
        this.form.addEventListener('submit', (e) => {
            if (!this.form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                this.showValidationErrors();
            }
            this.form.classList.add('was-validated');
        });

        // Add real-time validation
        this.addRealTimeValidation();
    }

    addRealTimeValidation() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });

            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });
    }

    validateField(field) {
        if (field.checkValidity()) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            this.hideFieldError(field);
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            this.showFieldError(field);
        }
    }

    showFieldError(field) {
        const feedback = field.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'block';
        }
    }

    hideFieldError(field) {
        const feedback = field.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'none';
        }
    }

    showValidationErrors() {
        const invalidFields = this.form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            // Focus on first invalid field
            invalidFields[0].focus();
            
            // Show toast notification
            window.toast.error('Please fill in all required fields correctly');
        }
    }

    reset() {
        this.form.classList.remove('was-validated');
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
        });
    }
}

// ==========================================
// 4. EMPTY STATES
// ==========================================

class EmptyState {
    static create(config = {}) {
        const {
            icon = 'inbox',
            title = 'No data available',
            message = 'There is no data to display at the moment.',
            actionText = null,
            actionLink = null,
            actionCallback = null
        } = config;

        const container = document.createElement('div');
        container.className = 'empty-state text-center py-5';
        
        let actionButton = '';
        if (actionText) {
            const href = actionLink || '#';
            const onClick = actionCallback ? `onclick="(${actionCallback.toString()})(event)"` : '';
            actionButton = `
                <a href="${href}" class="btn btn-primary mt-3" ${onClick}>
                    <i class="fas fa-plus me-2"></i>${actionText}
                </a>
            `;
        }

        container.innerHTML = `
            <div class="empty-state-icon mb-3">
                <i class="fas fa-${icon}" style="font-size: 4rem; color: #cbd5e0;"></i>
            </div>
            <h4 class="empty-state-title">${title}</h4>
            <p class="empty-state-message text-muted">${message}</p>
            ${actionButton}
        `;

        return container;
    }
}

// ==========================================
// 5. SKELETON LOADERS
// ==========================================

class SkeletonLoader {
    static createCard() {
        const skeleton = document.createElement('div');
        skeleton.className = 'card skeleton-loader';
        skeleton.innerHTML = `
            <div class="card-body">
                <div class="skeleton skeleton-text" style="width: 60%;"></div>
                <div class="skeleton skeleton-text" style="width: 40%;"></div>
                <div class="skeleton skeleton-text" style="width: 80%;"></div>
                <div class="skeleton skeleton-button"></div>
            </div>
        `;
        return skeleton;
    }

    static createTable(rows = 5) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-loader';
        
        let tableRows = '';
        for (let i = 0; i < rows; i++) {
            tableRows += `
                <tr>
                    <td><div class="skeleton skeleton-text"></div></td>
                    <td><div class="skeleton skeleton-text"></div></td>
                    <td><div class="skeleton skeleton-text"></div></td>
                    <td><div class="skeleton skeleton-text"></div></td>
                </tr>
            `;
        }

        skeleton.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th><div class="skeleton skeleton-text"></div></th>
                        <th><div class="skeleton skeleton-text"></div></th>
                        <th><div class="skeleton skeleton-text"></div></th>
                        <th><div class="skeleton skeleton-text"></div></th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        `;
        return skeleton;
    }

    static createList(items = 5) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-loader';
        
        let listItems = '';
        for (let i = 0; i < items; i++) {
            listItems += `
                <div class="d-flex align-items-center mb-3">
                    <div class="skeleton skeleton-avatar me-3"></div>
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text" style="width: 70%;"></div>
                        <div class="skeleton skeleton-text" style="width: 50%;"></div>
                    </div>
                </div>
            `;
        }

        skeleton.innerHTML = listItems;
        return skeleton;
    }
}

// ==========================================
// 6. TOOLTIPS & POPOVERS
// ==========================================

class TooltipManager {
    static init() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

        // Initialize Bootstrap popovers
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }

    static add(element, content, placement = 'top') {
        element.setAttribute('data-bs-toggle', 'tooltip');
        element.setAttribute('data-bs-placement', placement);
        element.setAttribute('title', content);
        new bootstrap.Tooltip(element);
    }
}

// ==========================================
// 7. CONTEXTUAL HELP
// ==========================================

class HelpSystem {
    constructor() {
        this.helpData = {};
        this.init();
    }

    init() {
        // Add help button to navigation
        this.addGlobalHelpButton();
        
        // Initialize help tooltips
        this.initHelpTooltips();
    }

    addGlobalHelpButton() {
        const helpBtn = document.createElement('button');
        helpBtn.className = 'btn btn-link position-fixed';
        helpBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; width: 60px; height: 60px; border-radius: 50%; background: #007bff; color: white; box-shadow: 0 4px 12px rgba(0,123,255,0.3);';
        helpBtn.innerHTML = '<i class="fas fa-question fa-lg"></i>';
        helpBtn.setAttribute('data-bs-toggle', 'tooltip');
        helpBtn.setAttribute('title', 'Need help? Click for assistance');
        
        helpBtn.addEventListener('click', () => this.showHelpModal());
        
        document.body.appendChild(helpBtn);
        new bootstrap.Tooltip(helpBtn);
    }

    initHelpTooltips() {
        // Add help icons next to complex form fields
        const complexFields = document.querySelectorAll('[data-help]');
        complexFields.forEach(field => {
            const helpText = field.dataset.help;
            const helpIcon = document.createElement('i');
            helpIcon.className = 'fas fa-question-circle text-muted ms-2';
            helpIcon.style.cursor = 'pointer';
            helpIcon.setAttribute('data-bs-toggle', 'tooltip');
            helpIcon.setAttribute('title', helpText);
            
            field.parentNode.appendChild(helpIcon);
            new bootstrap.Tooltip(helpIcon);
        });
    }

    showHelpModal() {
        const modal = this.createHelpModal();
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    createHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle me-2"></i>Help & Support
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6><i class="fas fa-book me-2"></i>Documentation</h6>
                                        <p class="text-muted small">Access comprehensive guides and tutorials</p>
                                        <a href="#" class="btn btn-sm btn-outline-primary">View Docs</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6><i class="fas fa-video me-2"></i>Video Tutorials</h6>
                                        <p class="text-muted small">Watch step-by-step video guides</p>
                                        <a href="#" class="btn btn-sm btn-outline-primary">Watch Videos</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6><i class="fas fa-comments me-2"></i>Live Chat</h6>
                                        <p class="text-muted small">Get instant help from support team</p>
                                        <a href="#" class="btn btn-sm btn-outline-primary">Start Chat</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6><i class="fas fa-envelope me-2"></i>Email Support</h6>
                                        <p class="text-muted small">Send us your questions</p>
                                        <a href="mailto:support@eduvision.com" class="btn btn-sm btn-outline-primary">Send Email</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <h6>Quick Tips:</h6>
                            <ul class="text-muted small">
                                <li>Use keyboard shortcuts for faster navigation (Ctrl+K for search)</li>
                                <li>Hover over buttons to see tooltips with additional information</li>
                                <li>All forms have real-time validation to help prevent errors</li>
                                <li>Your data is automatically saved as you work</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }
}

// ==========================================
// 8. CONFIRMATION DIALOGS
// ==========================================

class ConfirmationDialog {
    static show(config = {}) {
        const {
            title = 'Confirm Action',
            message = 'Are you sure you want to proceed?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            type = 'warning',
            onConfirm = () => {},
            onCancel = () => {}
        } = config;

        const icons = {
            warning: 'exclamation-triangle text-warning',
            danger: 'exclamation-circle text-danger',
            info: 'info-circle text-info',
            success: 'check-circle text-success'
        };

        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center p-4">
                        <i class="fas fa-${icons[type]} fa-3x mb-3"></i>
                        <h5>${title}</h5>
                        <p class="text-muted">${message}</p>
                        <div class="mt-4">
                            <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">${cancelText}</button>
                            <button type="button" class="btn btn-primary confirm-btn">${confirmText}</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        
        modal.querySelector('.confirm-btn').addEventListener('click', () => {
            onConfirm();
            bsModal.hide();
        });

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });

        bsModal.show();
    }
}

// ==========================================
// 9. PROGRESS TRACKER
// ==========================================

class ProgressTracker {
    constructor(element) {
        this.element = element;
        this.progress = 0;
    }

    update(value) {
        this.progress = Math.min(100, Math.max(0, value));
        this.render();
    }

    render() {
        this.element.innerHTML = `
            <div class="progress" style="height: 25px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" 
                     style="width: ${this.progress}%"
                     aria-valuenow="${this.progress}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${this.progress}%
                </div>
            </div>
        `;
    }
}

// ==========================================
// 10. KEYBOARD SHORTCUTS
// ==========================================

class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyCombo(e);
            const handler = this.shortcuts.get(key);
            if (handler) {
                e.preventDefault();
                handler(e);
            }
        });

        // Register default shortcuts
        this.register('ctrl+k', () => {
            const searchInput = document.getElementById('global-search');
            if (searchInput) {
                searchInput.focus();
            }
        });

        this.register('ctrl+/', () => {
            document.querySelector('[data-bs-toggle="tooltip"][title*="help"]')?.click();
        });
    }

    getKeyCombo(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }

    register(combo, handler) {
        this.shortcuts.set(combo, handler);
    }
}

// ==========================================
// INITIALIZATION
// ==========================================

// Create global instances
window.loader = new LoadingManager();
window.toast = new ToastManager();
window.helpSystem = new HelpSystem();
window.shortcuts = new KeyboardShortcuts();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    TooltipManager.init();

    // Initialize all forms
    document.querySelectorAll('form:not(.no-validation)').forEach(form => {
        new FormValidator(form);
    });

    // Add loading states to all form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.checkValidity()) {
                const submitBtn = this.querySelector('[type="submit"]');
                if (submitBtn) {
                    window.loader.showButtonLoading(submitBtn, 'Processing...');
                }
            }
        });
    });

    // Add confirmation to delete buttons
    document.querySelectorAll('[data-confirm-delete]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.dataset.confirmDelete || 'Are you sure you want to delete this item?';
            ConfirmationDialog.show({
                title: 'Confirm Delete',
                message: message,
                type: 'danger',
                confirmText: 'Delete',
                onConfirm: () => {
                    window.location.href = this.href;
                }
            });
        });
    });

    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Export for use in other modules
export {
    LoadingManager,
    ToastManager,
    FormValidator,
    EmptyState,
    SkeletonLoader,
    TooltipManager,
    HelpSystem,
    ConfirmationDialog,
    ProgressTracker,
    KeyboardShortcuts
};


















