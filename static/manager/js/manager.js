(function () {
    "use strict";

    function initSidebarToggle() {
        const sidebarToggle = document.getElementById("sidebar-toggle");
        const sidebar = document.querySelector(".manager-sidebar");

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener("click", function () {
                sidebar.classList.toggle("open");
            });
        }
    }

    function initBulkSelection() {
        const selectAll = document.getElementById("select-all");
        const rowCheckboxes = document.querySelectorAll(".row-checkbox");
        const bulkToolbar = document.getElementById("bulk-toolbar");
        const selectedCount = document.getElementById("selected-count");
        const bulkButtons = document.querySelectorAll(".bulk-action-btn");

        if (!bulkToolbar || !selectedCount) {
            return;
        }

        function updateBulkState() {
            const checked = document.querySelectorAll(".row-checkbox:checked");
            const count = checked.length;

            selectedCount.textContent = count;
            bulkToolbar.classList.toggle("is-visible", count > 0);

            bulkButtons.forEach(function (button) {
                button.disabled = count === 0;
            });

            if (selectAll) {
                selectAll.checked = rowCheckboxes.length > 0 && count === rowCheckboxes.length;
                selectAll.indeterminate = count > 0 && count < rowCheckboxes.length;
            }
        }

        if (selectAll) {
            selectAll.addEventListener("change", function () {
                rowCheckboxes.forEach(function (checkbox) {
                    checkbox.checked = selectAll.checked;
                });
                updateBulkState();
            });
        }

        rowCheckboxes.forEach(function (checkbox) {
            checkbox.addEventListener("change", updateBulkState);
        });

        updateBulkState();
    }

    function initFilterPanel() {
        const toggle = document.getElementById("filters-toggle");
        const panel = document.getElementById("filters-panel");

        if (!toggle || !panel) {
            return;
        }

        toggle.addEventListener("click", function () {
            panel.classList.toggle("is-open");
            toggle.classList.toggle("is-open");
        });
    }

    function initSidebarSections() {
        document.querySelectorAll(".sidebar-section-toggle").forEach(function (button) {
            button.addEventListener("click", function () {
                const section = button.closest(".sidebar-section");
                if (section) {
                    section.classList.toggle("is-collapsed");
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initSidebarToggle();
        initBulkSelection();
        initFilterPanel();
        initSidebarSections();
    });
})();
