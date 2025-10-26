/* DataTables Helper - Prevents Reinitialization Errors */

(function() {
    'use strict';

    // Store initialized tables
    const initializedTables = new Set();

    /**
     * Safely initialize or reinitialize a DataTable
     * @param {string|HTMLElement|jQuery} selector - Table selector
     * @param {Object} options - DataTable options
     * @returns {DataTable|null} DataTable instance or null
     */
    window.safeDataTable = function(selector, options) {
        if (typeof $ === 'undefined' || typeof $.fn.DataTable === 'undefined') {
            console.warn('DataTables library not loaded');
            return null;
        }

        const $table = $(selector);
        
        if ($table.length === 0) {
            console.warn('Table not found:', selector);
            return null;
        }

        const tableId = $table.attr('id') || 'table-' + Math.random().toString(36).substr(2, 9);
        
        // Check if already initialized
        if ($.fn.DataTable.isDataTable($table)) {
            console.log('DataTable already initialized:', tableId);
            return $table.DataTable();
        }

        // Default options with casual college theme
        const defaultOptions = {
            responsive: true,
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search records...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "No entries to show",
                infoFiltered: "(filtered from _MAX_ total entries)",
                zeroRecords: "No matching records found",
                emptyTable: "No data available in table",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            },
            dom: '<"flex flex-col md:flex-row items-center justify-between mb-4 space-y-2 md:space-y-0"<"flex items-center"l><"flex items-center"f>>rt<"flex flex-col md:flex-row items-center justify-between mt-4 space-y-2 md:space-y-0"<"text-sm text-gray-600"i><"flex items-center"p>>',
            drawCallback: function() {
                applyCasualStyling();
            },
            initComplete: function() {
                console.log('DataTable initialized:', tableId);
                initializedTables.add(tableId);
                applyCasualStyling();
            }
        };

        // Merge options
        const finalOptions = $.extend(true, {}, defaultOptions, options);

        try {
            const dataTable = $table.DataTable(finalOptions);
            return dataTable;
        } catch (error) {
            console.error('Error initializing DataTable:', error);
            return null;
        }
    };

    /**
     * Destroy a DataTable safely
     * @param {string|HTMLElement|jQuery} selector - Table selector
     */
    window.destroyDataTable = function(selector) {
        const $table = $(selector);
        
        if ($.fn.DataTable.isDataTable($table)) {
            const tableId = $table.attr('id');
            $table.DataTable().destroy();
            initializedTables.delete(tableId);
            console.log('DataTable destroyed:', tableId);
        }
    };

    /**
     * Reinitialize a DataTable (destroy then create)
     * @param {string|HTMLElement|jQuery} selector - Table selector
     * @param {Object} options - DataTable options
     */
    window.reinitDataTable = function(selector, options) {
        destroyDataTable(selector);
        return safeDataTable(selector, options);
    };

    /**
     * Apply casual college styling to DataTables elements
     */
    function applyCasualStyling() {
        // Style pagination buttons
        $('.dataTables_paginate .paginate_button').each(function() {
            if (!$(this).hasClass('styled')) {
                $(this).addClass('styled px-3 py-2 text-sm font-medium rounded-lg transition-all');
                
                if ($(this).hasClass('current')) {
                    $(this).addClass('bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md');
                } else if ($(this).hasClass('disabled')) {
                    $(this).addClass('text-gray-400 cursor-not-allowed');
                } else {
                    $(this).addClass('text-gray-700 hover:bg-blue-50 hover:text-blue-600');
                }
            }
        });

        // Style search input
        $('.dataTables_filter input').each(function() {
            if (!$(this).hasClass('styled')) {
                $(this).addClass('styled form-input rounded-xl border-2 border-gray-200 focus:border-blue-500 px-4 py-2 text-sm transition-all');
                $(this).attr('placeholder', $(this).attr('placeholder') || 'Search...');
            }
        });

        // Style length select
        $('.dataTables_length select').each(function() {
            if (!$(this).hasClass('styled')) {
                $(this).addClass('styled form-select rounded-lg border-2 border-gray-200 focus:border-blue-500 px-3 py-2 text-sm transition-all');
            }
        });

        // Style info text
        $('.dataTables_info').each(function() {
            if (!$(this).hasClass('styled')) {
                $(this).addClass('styled text-sm font-medium text-gray-600');
            }
        });

        // Add icons to pagination
        $('.paginate_button.previous').each(function() {
            if (!$(this).find('i').length) {
                $(this).prepend('<i class="fas fa-chevron-left mr-1 text-xs"></i>');
            }
        });
        $('.paginate_button.next').each(function() {
            if (!$(this).find('i').length) {
                $(this).append('<i class="fas fa-chevron-right ml-1 text-xs"></i>');
            }
        });
    }

    /**
     * Auto-initialize tables on page load
     */
    function autoInitialize() {
        // Initialize tables with specific IDs
        const autoInitIds = ['example1', 'example2', 'example3', 'dataTable', 'myTable'];
        
        autoInitIds.forEach(id => {
            const table = document.getElementById(id);
            if (table && !$.fn.DataTable.isDataTable('#' + id)) {
                safeDataTable('#' + id);
            }
        });

        // Initialize tables with data-table class
        $('.data-table').each(function() {
            if (!$.fn.DataTable.isDataTable(this)) {
                safeDataTable(this);
            }
        });

        // Initialize tables with table-auto-init class
        $('.table-auto-init').each(function() {
            if (!$.fn.DataTable.isDataTable(this)) {
                safeDataTable(this);
            }
        });
    }

    // Auto-initialize on DOM ready
    if (typeof $ !== 'undefined') {
        $(document).ready(function() {
            // Small delay to ensure all scripts are loaded
            setTimeout(autoInitialize, 100);
        });

        // Handle AJAX page loads (for SPAs)
        $(document).on('ajaxComplete', function() {
            setTimeout(autoInitialize, 200);
        });
    }

    // Export utilities
    window.DataTablesHelper = {
        init: safeDataTable,
        destroy: destroyDataTable,
        reinit: reinitDataTable,
        applyStyling: applyCasualStyling,
        autoInitialize: autoInitialize
    };

    console.log('DataTables Helper loaded ✅');

})();

// Prevent DataTables warning from appearing in console
if (typeof $.fn.dataTable !== 'undefined') {
    $.fn.dataTable.ext.errMode = 'none';
}


