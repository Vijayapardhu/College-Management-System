/* Performance Optimization Scripts */

// Lazy Loading Images
document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for lazy loading
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const src = img.getAttribute('data-src');
                
                if (src) {
                    img.src = src;
                    img.removeAttribute('data-src');
                    img.classList.add('fade-in');
                    observer.unobserve(img);
                }
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    // Observe all images with data-src attribute
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
});

// Lazy Loading Charts
function lazyLoadChart(chartId, chartFunction) {
    const chartElement = document.getElementById(chartId);
    if (!chartElement) return;

    const chartObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                chartFunction();
                observer.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: '100px 0px',
        threshold: 0.1
    });

    chartObserver.observe(chartElement);
}

// Debounce Function
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

// Throttle Function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Optimize Scroll Performance
const optimizeScroll = throttle(function() {
    // Add scroll-based behaviors here
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Show/hide scroll-to-top button
    const scrollTopBtn = document.getElementById('scroll-to-top');
    if (scrollTopBtn) {
        if (scrollTop > 300) {
            scrollTopBtn.classList.remove('hidden');
        } else {
            scrollTopBtn.classList.add('hidden');
        }
    }
}, 100);

window.addEventListener('scroll', optimizeScroll, { passive: true });

// Preload Critical Resources
function preloadResource(href, as) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = as;
    link.href = href;
    document.head.appendChild(link);
}

// Defer Non-Critical CSS
function loadDeferredCSS(href) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.media = 'print';
    link.onload = function() {
        this.media = 'all';
    };
    document.head.appendChild(link);
}

// Local Storage Cache for Static Data
const CacheManager = {
    set: function(key, value, ttl = 3600000) {
        const item = {
            value: value,
            expiry: new Date().getTime() + ttl
        };
        localStorage.setItem(key, JSON.stringify(item));
    },
    
    get: function(key) {
        const itemStr = localStorage.getItem(key);
        if (!itemStr) return null;
        
        const item = JSON.parse(itemStr);
        if (new Date().getTime() > item.expiry) {
            localStorage.removeItem(key);
            return null;
        }
        
        return item.value;
    },
    
    remove: function(key) {
        localStorage.removeItem(key);
    },
    
    clear: function() {
        localStorage.clear();
    }
};

// AJAX Request Caching
const AjaxCache = new Map();

function cachedAjaxRequest(url, options = {}) {
    const cacheKey = url + JSON.stringify(options);
    
    if (AjaxCache.has(cacheKey)) {
        return Promise.resolve(AjaxCache.get(cacheKey));
    }
    
    return fetch(url, options)
        .then(response => response.json())
        .then(data => {
            AjaxCache.set(cacheKey, data);
            return data;
        });
}

// Optimize Form Submissions
document.addEventListener('DOMContentLoaded', function() {
    // Prevent double submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('loading');
                }, 5000);
            }
        });
    });
});

// Reduce DOM Manipulations
const batchDOMUpdates = (function() {
    let pending = [];
    let scheduled = false;

    return function(callback) {
        pending.push(callback);
        
        if (!scheduled) {
            scheduled = true;
            requestAnimationFrame(() => {
                const callbacks = pending.slice();
                pending = [];
                scheduled = false;
                callbacks.forEach(cb => cb());
            });
        }
    };
})();

// Service Worker Registration (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration.scope);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

// Prefetch Links on Hover
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="/"]');
    const prefetchedLinks = new Set();

    links.forEach(link => {
        link.addEventListener('mouseenter', function() {
            const href = this.getAttribute('href');
            
            if (href && !prefetchedLinks.has(href)) {
                const linkElement = document.createElement('link');
                linkElement.rel = 'prefetch';
                linkElement.href = href;
                document.head.appendChild(linkElement);
                prefetchedLinks.add(href);
            }
        }, { passive: true });
    });
});

// Memory Management - Clear old cache entries
window.addEventListener('load', function() {
    // Clear cache entries older than 24 hours
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
        try {
            const item = JSON.parse(localStorage.getItem(key));
            if (item && item.expiry && new Date().getTime() > item.expiry) {
                localStorage.removeItem(key);
            }
        } catch (e) {
            // Skip non-JSON items
        }
    });
});

// Optimize Table Rendering
function optimizeTableRendering(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    // Use virtual scrolling for large tables
    const rows = table.querySelectorAll('tbody tr');
    if (rows.length > 50) {
        // Implement virtual scrolling
        let visibleRows = 20;
        let startIndex = 0;

        function renderVisibleRows() {
            rows.forEach((row, index) => {
                if (index >= startIndex && index < startIndex + visibleRows) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        renderVisibleRows();

        // Update on scroll
        table.addEventListener('scroll', throttle(function() {
            const scrollTop = this.scrollTop;
            const rowHeight = rows[0].offsetHeight;
            startIndex = Math.floor(scrollTop / rowHeight);
            renderVisibleRows();
        }, 100), { passive: true });
    }
}

// Export optimization utilities
window.PerformanceOptimization = {
    debounce,
    throttle,
    CacheManager,
    cachedAjaxRequest,
    batchDOMUpdates,
    lazyLoadChart,
    optimizeTableRendering
};


