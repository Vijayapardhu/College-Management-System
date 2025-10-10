/**
 * EduVision - Mobile Enhancements JavaScript
 * Provides mobile-specific functionality and optimizations
 */

(function($) {
    'use strict';

    // ========================================
    // Mobile Detection
    // ========================================
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    
    if (isMobile) {
        $('body').addClass('is-mobile');
    }
    
    if (isTouch) {
        $('body').addClass('is-touch');
    }

    // ========================================
    // Update Unread Message Count
    // ========================================
    function updateUnreadCount() {
        $.ajax({
            url: '/messages/',
            method: 'GET',
            success: function(data) {
                // Extract unread count from response (you may need to create an API endpoint)
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, 'text/html');
                const unreadElement = doc.querySelector('[data-unread-count]');
                
                if (unreadElement) {
                    const count = parseInt(unreadElement.getAttribute('data-unread-count'));
                    if (count > 0) {
                        $('#unread-count').text(count).show();
                    } else {
                        $('#unread-count').hide();
                    }
                }
            },
            error: function() {
                console.log('Could not fetch unread count');
            }
        });
    }

    // Update every 30 seconds
    if (typeof updateUnreadCount === 'function') {
        updateUnreadCount();
        setInterval(updateUnreadCount, 30000);
    }

    // ========================================
    // Auto-hide Alerts
    // ========================================
    setTimeout(function() {
        $('.alert:not(.alert-permanent)').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);

    // ========================================
    // Responsive Tables
    // ========================================
    function makeTablesResponsive() {
        $('table:not(.no-responsive)').each(function() {
            if (!$(this).parent().hasClass('table-responsive')) {
                $(this).wrap('<div class="table-responsive"></div>');
            }
            
            // Add mobile-stack class for very small screens
            if (window.innerWidth < 576) {
                $(this).addClass('table-mobile-stack');
                
                // Add data-label attributes from headers
                const headers = [];
                $(this).find('thead th').each(function(i) {
                    headers[i] = $(this).text();
                });
                
                $(this).find('tbody tr').each(function() {
                    $(this).find('td').each(function(i) {
                        $(this).attr('data-label', headers[i]);
                    });
                });
            }
        });
    }

    $(document).ready(function() {
        makeTablesResponsive();
    });

    $(window).resize(function() {
        makeTablesResponsive();
    });

    // ========================================
    // Touch-Friendly Confirmations
    // ========================================
    $('a[data-confirm], button[data-confirm]').on('click', function(e) {
        const message = $(this).data('confirm') || 'Are you sure?';
        if (!confirm(message)) {
            e.preventDefault();
            return false;
        }
    });

    // ========================================
    // Bookmark Toggle
    // ========================================
    $('.bookmark-btn').on('click', function(e) {
        e.preventDefault();
        const btn = $(this);
        const materialId = btn.data('material-id');
        
        $.ajax({
            url: '/student/resource/bookmark/',
            method: 'POST',
            data: {
                material_id: materialId
            },
            success: function(response) {
                if (response.status === 'success') {
                    if (response.action === 'added') {
                        btn.addClass('bookmarked');
                        btn.find('i').removeClass('far').addClass('fas');
                        showToast('Bookmarked!', 'success');
                    } else {
                        btn.removeClass('bookmarked');
                        btn.find('i').removeClass('fas').addClass('far');
                        showToast('Bookmark removed', 'info');
                    }
                }
            },
            error: function() {
                showToast('Failed to bookmark', 'error');
            }
        });
    });

    // ========================================
    // Rating Stars
    // ========================================
    $('.rating-stars i').on('click', function() {
        const rating = $(this).data('rating');
        const materialId = $(this).closest('.rating-stars').data('material-id');
        
        // Highlight selected stars
        $(this).closest('.rating-stars').find('i').each(function(index) {
            if (index < rating) {
                $(this).addClass('active fas').removeClass('far');
            } else {
                $(this).removeClass('active fas').addClass('far');
            }
        });
        
        // Submit rating
        $.ajax({
            url: '/student/resource/rate/',
            method: 'POST',
            data: {
                material_id: materialId,
                rating: rating,
                comment: ''
            },
            success: function(response) {
                if (response.status === 'success') {
                    showToast(`Rated ${rating}/5`, 'success');
                    if (response.average) {
                        $('.avg-rating[data-material-id="' + materialId + '"]').text(response.average);
                    }
                }
            },
            error: function() {
                showToast('Failed to submit rating', 'error');
            }
        });
    });

    // ========================================
    // Event Registration
    // ========================================
    $('.register-event-btn').on('click', function(e) {
        e.preventDefault();
        const eventId = $(this).data('event-id');
        const btn = $(this);
        
        if (btn.hasClass('btn-danger')) {
            // Unregister
            if (!confirm('Unregister from this event?')) return;
            
            $.ajax({
                url: '/student/event/unregister/',
                method: 'POST',
                data: { event_id: eventId },
                success: function(response) {
                    if (response.status === 'success') {
                        btn.removeClass('btn-danger').addClass('btn-primary');
                        btn.html('<i class="fas fa-calendar-plus"></i> Register');
                        showToast('Unregistered successfully', 'info');
                    } else {
                        showToast(response.message, 'error');
                    }
                },
                error: function() {
                    showToast('Failed to unregister', 'error');
                }
            });
        } else {
            // Register
            $.ajax({
                url: '/student/event/register/',
                method: 'POST',
                data: { event_id: eventId },
                success: function(response) {
                    if (response.status === 'success') {
                        btn.removeClass('btn-primary').addClass('btn-danger');
                        btn.html('<i class="fas fa-times-circle"></i> Unregister');
                        showToast('Registered successfully!', 'success');
                    } else {
                        showToast(response.message, 'error');
                    }
                },
                error: function() {
                    showToast('Failed to register', 'error');
                }
            });
        }
    });

    // ========================================
    // Mark Message as Read
    // ========================================
    $('.message-list-item[data-message-id]').on('click', function() {
        const messageId = $(this).data('message-id');
        const item = $(this);
        
        if (item.hasClass('unread')) {
            $.ajax({
                url: '/message/' + messageId + '/mark_read/',
                method: 'POST',
                success: function(response) {
                    if (response.status === 'success') {
                        item.removeClass('unread');
                        // Update counter
                        const currentCount = parseInt($('#unread-count').text()) || 0;
                        if (currentCount > 0) {
                            const newCount = currentCount - 1;
                            if (newCount > 0) {
                                $('#unread-count').text(newCount);
                            } else {
                                $('#unread-count').hide();
                            }
                        }
                    }
                }
            });
        }
    });

    // ========================================
    // Toast Notifications
    // ========================================
    function showToast(message, type = 'info') {
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info'
        };
        
        const iconClass = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        
        const toast = $('<div class="toast-notification ' + bgClass[type] + '">' +
            '<i class="fas ' + iconClass[type] + '"></i> ' +
            '<span>' + message + '</span>' +
            '</div>');
        
        $('body').append(toast);
        
        setTimeout(function() {
            toast.addClass('show');
        }, 100);
        
        setTimeout(function() {
            toast.removeClass('show');
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // Make showToast globally available
    window.showToast = showToast;

    // ========================================
    // Pull to Refresh (Progressive Enhancement)
    // ========================================
    let startY = 0;
    let pullThreshold = 80;
    let isPulling = false;

    if (isTouch) {
        $(document).on('touchstart', function(e) {
            startY = e.touches[0].pageY;
            if ($(window).scrollTop() === 0) {
                isPulling = true;
            }
        });

        $(document).on('touchmove', function(e) {
            if (!isPulling) return;
            
            const currentY = e.touches[0].pageY;
            const distance = currentY - startY;
            
            if (distance > pullThreshold) {
                // Show refresh indicator
                $('#pull-refresh-indicator').show();
            }
        });

        $(document).on('touchend', function(e) {
            if (!isPulling) return;
            
            const currentY = e.changedTouches[0].pageY;
            const distance = currentY - startY;
            
            if (distance > pullThreshold) {
                // Reload page
                location.reload();
            }
            
            isPulling = false;
            $('#pull-refresh-indicator').hide();
        });
    }

    // ========================================
    // Lazy Loading Images
    // ========================================
    if ('loading' in HTMLImageElement.prototype) {
        // Native lazy loading supported
        $('img').attr('loading', 'lazy');
    } else {
        // Fallback for older browsers
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // ========================================
    // Service Worker Registration (PWA Support)
    // ========================================
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/firebase-messaging-sw.js')
            .then(function(registration) {
                console.log('Service Worker registered');
            })
            .catch(function(error) {
                console.log('Service Worker registration failed:', error);
            });
    }

    // ========================================
    // Offline Detection
    // ========================================
    window.addEventListener('online', function() {
        showToast('Back online!', 'success');
    });

    window.addEventListener('offline', function() {
        showToast('No internet connection', 'warning');
    });

    // ========================================
    // Form Validation Enhancements
    // ========================================
    $('form').on('submit', function() {
        const btn = $(this).find('button[type="submit"]');
        btn.prop('disabled', true);
        btn.html('<i class="fas fa-spinner fa-spin"></i> Processing...');
        
        // Re-enable after 3 seconds (in case of validation errors)
        setTimeout(function() {
            btn.prop('disabled', false);
            btn.html(btn.data('original-text') || 'Submit');
        }, 3000);
    });

    // Store original button text
    $('button[type="submit"]').each(function() {
        $(this).data('original-text', $(this).html());
    });

    // ========================================
    // Back Button Functionality
    // ========================================
    $('.back-btn').on('click', function(e) {
        e.preventDefault();
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = '/';
        }
    });

    // ========================================
    // Sidebar Auto-Close on Mobile
    // ========================================
    if (window.innerWidth < 768) {
        $('.nav-sidebar a:not([data-widget])').on('click', function() {
            // Close sidebar after clicking link on mobile
            setTimeout(function() {
                $('[data-widget="pushmenu"]').click();
            }, 300);
        });
    }

    // ========================================
    // Download Progress Indicator
    // ========================================
    $('.download-btn').on('click', function() {
        const btn = $(this);
        btn.html('<i class="fas fa-spinner fa-spin"></i> Downloading...');
        
        setTimeout(function() {
            btn.html('<i class="fas fa-download"></i> Download');
        }, 2000);
    });

    // ========================================
    // File Upload Preview
    // ========================================
    $('input[type="file"]').on('change', function() {
        const fileName = $(this).val().split('\\').pop();
        const fileSize = this.files[0] ? (this.files[0].size / 1024 / 1024).toFixed(2) + ' MB' : '';
        
        $(this).next('.custom-file-label').html(fileName + (fileSize ? ' (' + fileSize + ')' : ''));
        
        // Show preview for images
        if (this.files && this.files[0] && this.files[0].type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = $('<img class="img-thumbnail mt-2" style="max-width: 200px;">');
                preview.attr('src', e.target.result);
                $(this).closest('.form-group').find('.image-preview').remove();
                $(this).closest('.form-group').append('<div class="image-preview"></div>');
                $(this).closest('.form-group').find('.image-preview').append(preview);
            }.bind(this);
            reader.readAsDataURL(this.files[0]);
        }
    });

    // ========================================
    // Swipe Actions for Lists
    // ========================================
    if (isTouch) {
        let startX, currentX, isDragging = false;
        
        $('.swipeable').on('touchstart', function(e) {
            startX = e.touches[0].pageX;
            isDragging = true;
        });
        
        $('.swipeable').on('touchmove', function(e) {
            if (!isDragging) return;
            
            currentX = e.touches[0].pageX;
            const diff = startX - currentX;
            
            if (diff > 50) {
                $(this).addClass('swiped');
            } else if (diff < -20) {
                $(this).removeClass('swiped');
            }
        });
        
        $('.swipeable').on('touchend', function() {
            isDragging = false;
        });
    }

    // ========================================
    // Smooth Scroll to Top
    // ========================================
    // Create scroll to top button
    $('body').append('<button class="scroll-to-top" style="display: none;"><i class="fas fa-arrow-up"></i></button>');
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });
    
    $('.scroll-to-top').on('click', function() {
        $('html, body').animate({scrollTop: 0}, 'smooth');
    });

    // ========================================
    // Search Debounce
    // ========================================
    let searchTimeout;
    $('input[type="search"], .search-input').on('input', function() {
        clearTimeout(searchTimeout);
        const input = $(this);
        const form = input.closest('form');
        
        searchTimeout = setTimeout(function() {
            if (input.val().length >= 3 || input.val().length === 0) {
                // Auto-submit or filter
                form.trigger('submit');
            }
        }, 500);
    });

    // ========================================
    // Prevent Double Submit
    // ========================================
    $('form').on('submit', function() {
        const form = $(this);
        if (form.data('submitted') === true) {
            return false;
        }
        form.data('submitted', true);
    });

    // ========================================
    // Auto-Expand Textareas
    // ========================================
    $('textarea.auto-expand').each(function() {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // ========================================
    // Material Type Toggle
    // ========================================
    $('select[name="material_type"]').on('change', function() {
        const value = $(this).val();
        
        $('.file-upload-group').hide();
        $('.url-input-group').hide();
        
        if (value === 'document') {
            $('.file-upload-group').show();
        } else if (value === 'link' || value === 'video') {
            $('.url-input-group').show();
        }
    }).trigger('change');

    // ========================================
    // Date Countdown for Assignments
    // ========================================
    $('.assignment-deadline[data-due-date]').each(function() {
        const dueDate = new Date($(this).data('due-date'));
        const now = new Date();
        const diff = dueDate - now;
        
        if (diff < 0) {
            $(this).html('<span class="text-danger"><i class="fas fa-exclamation-triangle"></i> Overdue</span>');
        } else {
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            
            if (days > 0) {
                $(this).html('<i class="far fa-clock"></i> Due in ' + days + ' day(s)');
            } else {
                $(this).html('<i class="far fa-clock"></i> Due in ' + hours + ' hour(s)');
                $(this).addClass('text-warning');
            }
        }
    });

    // ========================================
    // YouTube Video Embed
    // ========================================
    $('.youtube-url').each(function() {
        const url = $(this).text();
        const videoId = extractYouTubeId(url);
        
        if (videoId) {
            const embed = '<div class="video-container">' +
                '<iframe src="https://www.youtube.com/embed/' + videoId + '" ' +
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" ' +
                'allowfullscreen></iframe></div>';
            $(this).replaceWith(embed);
        }
    });

    function extractYouTubeId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }

    // ========================================
    // Character Counter for Textareas
    // ========================================
    $('textarea[maxlength]').each(function() {
        const maxLength = $(this).attr('maxlength');
        const counter = $('<small class="form-text text-muted char-counter">0 / ' + maxLength + ' characters</small>');
        $(this).after(counter);
        
        $(this).on('input', function() {
            const length = $(this).val().length;
            counter.text(length + ' / ' + maxLength + ' characters');
            
            if (length > maxLength * 0.9) {
                counter.addClass('text-warning');
            } else {
                counter.removeClass('text-warning');
            }
        });
    });

    // ========================================
    // Responsive Navigation Improvements
    // ========================================
    // Auto-collapse sidebar on page load for mobile
    if (window.innerWidth < 768) {
        $('body').addClass('sidebar-collapse');
    }

    // ========================================
    // Quick Actions Menu
    // ========================================
    $('.quick-action').on('click', function(e) {
        // Add ripple effect
        const ripple = $('<span class="ripple"></span>');
        $(this).append(ripple);
        
        setTimeout(function() {
            ripple.remove();
        }, 600);
    });

    // ========================================
    // Filter Toggle for Mobile
    // ========================================
    $('.filter-toggle').on('click', function() {
        $('.filter-section').slideToggle();
        $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    });

    // ========================================
    // Initialize Tooltips for Mobile
    // ========================================
    if (!isTouch) {
        $('[data-toggle="tooltip"]').tooltip();
    }

    // ========================================
    // Network Speed Detection
    // ========================================
    if ('connection' in navigator) {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        if (connection && connection.effectiveType) {
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                // Disable auto-play videos and heavy features
                $('body').addClass('slow-connection');
                $('.video-container iframe').attr('src', ''); // Don't auto-load videos
            }
        }
    }

    // ========================================
    // Copy to Clipboard
    // ========================================
    $('.copy-btn').on('click', function() {
        const text = $(this).data('copy-text');
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copied to clipboard', 'success');
            });
        } else {
            // Fallback
            const temp = $('<textarea>');
            $('body').append(temp);
            temp.val(text).select();
            document.execCommand('copy');
            temp.remove();
            showToast('Copied to clipboard', 'success');
        }
    });

    // ========================================
    // Progressive Form Validation
    // ========================================
    $('input[required], select[required], textarea[required]').on('blur', function() {
        if (!$(this).val()) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid').addClass('is-valid');
        }
    });

    // ========================================
    // Loading Overlay Helper
    // ========================================
    window.showLoading = function() {
        if ($('.loading-overlay').length === 0) {
            $('body').append('<div class="loading-overlay">' +
                '<div class="spinner-border text-light" role="status">' +
                '<span class="sr-only">Loading...</span>' +
                '</div></div>');
        }
    };

    window.hideLoading = function() {
        $('.loading-overlay').remove();
    };

    // ========================================
    // Safe Area Insets for Notched Devices
    // ========================================
    if (CSS.supports('padding-top: env(safe-area-inset-top)')) {
        $('body').addClass('has-notch');
    }

    // ========================================
    // Console Log Suppression on Production
    // ========================================
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        console.log = function() {};
        console.warn = function() {};
        console.error = function() {};
    }

    // ========================================
    // Initialize on Document Ready
    // ========================================
    console.log('✅ EduVision Mobile Enhancements Loaded');
    console.log('Device: ' + (isMobile ? 'Mobile' : 'Desktop'));
    console.log('Touch: ' + (isTouch ? 'Enabled' : 'Disabled'));

})(jQuery);

// ========================================
// CSS for Toast Notifications
// ========================================
const style = document.createElement('style');
style.textContent = `
    .toast-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        opacity: 0;
        transform: translateY(100px);
        transition: all 0.3s ease;
    }
    
    .toast-notification.show {
        opacity: 1;
        transform: translateY(0);
    }
    
    .toast-notification i {
        font-size: 1.2rem;
    }
    
    .scroll-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #007bff;
        color: white;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        cursor: pointer;
    }
    
    .scroll-to-top:hover {
        background: #0056b3;
    }
    
    @media (max-width: 768px) {
        .toast-notification {
            left: 10px;
            right: 10px;
            bottom: 10px;
        }
    }
`;
document.head.appendChild(style);


