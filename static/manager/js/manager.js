(function () {
    "use strict";

    function getManagerRoot() {
        const body = document.body;
        return body && body.dataset.managerRoot ? body.dataset.managerRoot : "/";
    }

    function debounce(fn, delay) {
        let timer = null;
        return function () {
            const args = arguments;
            const context = this;
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn.apply(context, args);
            }, delay);
        };
    }

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

    function buildAutocompleteUrl(appLabel, modelName) {
        return getManagerRoot() + "autocomplete/" + appLabel + "/" + modelName + "/";
    }

    function renderDropdown(dropdown, results, onSelect) {
        dropdown.innerHTML = "";

        if (!results.length) {
            const empty = document.createElement("div");
            empty.className = "autocomplete-empty";
            empty.textContent = "نتیجه‌ای یافت نشد";
            dropdown.appendChild(empty);
            dropdown.hidden = false;
            return;
        }

        results.forEach(function (item) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "autocomplete-option";
            button.textContent = item.label;
            button.addEventListener("mousedown", function (event) {
                event.preventDefault();
                onSelect(item);
            });
            dropdown.appendChild(button);
        });

        dropdown.hidden = false;
    }

    function initAutocompleteField(wrapper) {
        const appLabel = wrapper.dataset.appLabel;
        const modelName = wrapper.dataset.modelName;
        const searchInput = wrapper.querySelector(".autocomplete-search");
        const dropdown = wrapper.querySelector(".autocomplete-dropdown");
        const isMultiple = wrapper.classList.contains("manager-autocomplete-multiple");

        if (!appLabel || !modelName || !searchInput || !dropdown) {
            return;
        }

        const url = buildAutocompleteUrl(appLabel, modelName);
        const hiddenInputsContainer = wrapper.querySelector(".autocomplete-hidden-inputs");
        const selectedContainer = wrapper.querySelector(".autocomplete-selected");
        const fieldName = wrapper.dataset.fieldName || "field";

        function hideDropdown() {
            dropdown.hidden = true;
        }

        function fetchResults(query, callback) {
            if (query.length < 2) {
                hideDropdown();
                callback([]);
                return;
            }

            dropdown.hidden = false;
            dropdown.innerHTML = '<div class="autocomplete-loading">در حال جستجو...</div>';

            fetch(url + "?q=" + encodeURIComponent(query), {
                credentials: "same-origin",
                headers: { "X-Requested-With": "XMLHttpRequest" },
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("request failed");
                    }
                    return response.json();
                })
                .then(function (data) { callback(data.results || []); })
                .catch(function () {
                    dropdown.innerHTML = '<div class="autocomplete-empty">خطا در جستجو</div>';
                    callback([]);
                });
        }

        let onSelectItem = null;

        if (isMultiple) {
            function addChip(item) {
                if (wrapper.querySelector('.autocomplete-chip[data-id="' + item.id + '"]')) {
                    return;
                }

                const chip = document.createElement("span");
                chip.className = "autocomplete-chip";
                chip.dataset.id = item.id;
                chip.innerHTML = item.label + ' <button type="button" class="autocomplete-chip-remove" aria-label="حذف">×</button>';

                const hidden = document.createElement("input");
                hidden.type = "hidden";
                hidden.name = fieldName;
                hidden.value = item.id;

                chip.querySelector(".autocomplete-chip-remove").addEventListener("click", function () {
                    chip.remove();
                    hidden.remove();
                });

                selectedContainer.appendChild(chip);
                hiddenInputsContainer.appendChild(hidden);
            }

            onSelectItem = function (item) {
                addChip(item);
                searchInput.value = "";
                hideDropdown();
            };

            wrapper.querySelectorAll(".autocomplete-chip-remove").forEach(function (button) {
                button.addEventListener("click", function () {
                    const chip = button.closest(".autocomplete-chip");
                    const id = chip.dataset.id;
                    chip.remove();
                    hiddenInputsContainer.querySelectorAll("input").forEach(function (input) {
                        if (input.value === id) {
                            input.remove();
                        }
                    });
                });
            });

        } else {
            const hiddenInput = wrapper.querySelector(".autocomplete-value");

            onSelectItem = function (item) {
                hiddenInput.value = item.id;
                searchInput.value = item.label;
                hideDropdown();
            };

            searchInput.addEventListener("input", debounce(function () {
                if (!searchInput.value.trim()) {
                    hiddenInput.value = "";
                }
            }, 250));
        }

        function runSearch() {
            fetchResults(searchInput.value.trim(), function (results) {
                renderDropdown(dropdown, results, onSelectItem);
            });
        }

        searchInput.addEventListener("input", debounce(runSearch, 250));

        searchInput.addEventListener("blur", function () {
            setTimeout(hideDropdown, 200);
        });

        searchInput.addEventListener("focus", function () {
            if (searchInput.value.trim().length >= 2) {
                runSearch();
            }
        });

        document.addEventListener("click", function (event) {
            if (!wrapper.contains(event.target)) {
                hideDropdown();
            }
        });
    }

    function initAutocompleteFields() {
        document.querySelectorAll(".manager-autocomplete").forEach(initAutocompleteField);
    }

    document.addEventListener("DOMContentLoaded", function () {
        initSidebarToggle();
        initBulkSelection();
        initFilterPanel();
        initSidebarSections();
        initAutocompleteFields();
    });
})();
