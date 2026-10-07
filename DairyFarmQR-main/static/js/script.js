// ==========================================================
// SMART DAIRY FARM MANAGEMENT SYSTEM - JAVASCRIPT
// Mobile & Desktop Interactions
// ==========================================================

document.addEventListener('DOMContentLoaded', function () {
  // ==========================================================
  // SIDEBAR & MOBILE NAVIGATION
  // ==========================================================
  const sidebar = document.getElementById('appSidebar') || document.querySelector('.sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');
  const mobileBottomMenuBtn = document.getElementById('mobileBottomMenuBtn');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('show');
    if (sidebarBackdrop) sidebarBackdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('show');
    if (sidebarBackdrop) sidebarBackdrop.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
  if (mobileBottomMenuBtn) mobileBottomMenuBtn.addEventListener('click', openSidebar);
  if (sidebarCloseBtn) sidebarCloseBtn.addEventListener('click', closeSidebar);
  if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', closeSidebar);

  // Close sidebar on link click on mobile
  if (sidebar) {
    const navLinks = sidebar.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', function () {
        if (window.innerWidth < 992) {
          closeSidebar();
        }
      });
    });
  }

  // ==========================================================
  // AUTO CALCULATE MILK TOTAL PRICE
  // ==========================================================
  const milkQtyInput = document.getElementById('milkQuantity');
  const milkRateInput = document.getElementById('milkRate');
  const milkTotalDisplay = document.getElementById('milkTotalAmount');

  function calculateMilkTotal() {
    if (milkQtyInput && milkRateInput && milkTotalDisplay) {
      const qty = parseFloat(milkQtyInput.value) || 0;
      const rate = parseFloat(milkRateInput.value) || 0;
      const total = qty * rate;
      milkTotalDisplay.value = total.toFixed(2);
    }
  }

  if (milkQtyInput && milkRateInput) {
    milkQtyInput.addEventListener('input', calculateMilkTotal);
    milkRateInput.addEventListener('input', calculateMilkTotal);
    calculateMilkTotal();
  }

  // ==========================================================
  // REAL-TIME INSTANT TABLE SEARCH (NUMBERS / TEXT)
  // ==========================================================
  function setupLiveTableFilter(inputElement, tableSelector) {
    if (!inputElement) return;

    inputElement.addEventListener('input', function () {
      const filter = this.value.trim().toLowerCase();
      const tables = document.querySelectorAll(tableSelector || '.searchable-table');

      tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
          if (row.querySelector('td[colspan]')) return;

          const text = row.textContent.toLowerCase();
          const matches = !filter || text.includes(filter);
          row.style.display = matches ? '' : 'none';
        });
      });
    });
  }

  // Cattle Search Bar
  const cattleSearchInput = document.getElementById('cattleSearchInput');
  setupLiveTableFilter(cattleSearchInput, '.searchable-table');

  // Generic search inputs
  const tableSearchInput = document.getElementById('tableSearch');
  setupLiveTableFilter(tableSearchInput, '.searchable-table');

  const genericSearchInputs = document.querySelectorAll('.table-search-input');
  genericSearchInputs.forEach(input => setupLiveTableFilter(input, '.searchable-table'));

  // ==========================================================
  // GLOBAL NAVBAR SEARCH & MOBILE SEARCH AUTOCOMPLETE
  // ==========================================================
  function setupCattleAutocomplete(searchInput, resultsContainer) {
    if (!searchInput || !resultsContainer) return;
    let debounceTimer = null;

    searchInput.addEventListener('input', function () {
      const query = this.value.trim();
      clearTimeout(debounceTimer);

      if (!query) {
        resultsContainer.style.display = 'none';
        resultsContainer.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/api/animals/search?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            resultsContainer.innerHTML = '';
            if (data.length === 0) {
              resultsContainer.innerHTML = `
                <div class="p-3 text-muted text-center small">
                  <i class="fa-solid fa-circle-question me-1"></i> No cattle found matching "<strong>${escapeHtml(query)}</strong>"
                </div>
              `;
            } else {
              const header = document.createElement('div');
              header.className = 'dropdown-header bg-light py-2 fw-bold text-uppercase small border-bottom';
              header.innerHTML = `<i class="fa-solid fa-cow me-1 text-primary"></i> ${data.length} Cattle Found`;
              resultsContainer.appendChild(header);

              data.forEach(item => {
                const link = document.createElement('a');
                link.href = item.url;
                link.className = 'dropdown-item py-2 px-3 border-bottom d-flex align-items-center justify-content-between text-decoration-none';
                link.innerHTML = `
                  <div>
                    <div class="fw-bold text-primary">${escapeHtml(item.tag_number)} <span class="text-dark fw-semibold small">(${escapeHtml(item.name || item.breed)})</span></div>
                    <div class="small text-muted">${escapeHtml(item.species)} &bull; ${escapeHtml(item.breed)}</div>
                  </div>
                  <div>
                    <span class="badge ${item.milking_status === 'Milking' ? 'bg-primary' : 'bg-secondary'} badge-sm">${escapeHtml(item.milking_status)}</span>
                  </div>
                `;
                resultsContainer.appendChild(link);
              });
            }
            resultsContainer.style.display = 'block';
          })
          .catch(err => {
            console.error('Search error:', err);
          });
      }, 180);
    });

    // Enter & Escape handling
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        const firstItem = resultsContainer.querySelector('a.dropdown-item');
        if (firstItem) {
          firstItem.click();
        }
      } else if (e.key === 'Escape') {
        resultsContainer.style.display = 'none';
      }
    });

    document.addEventListener('click', function (e) {
      if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.style.display = 'none';
      }
    });
  }

  // Desktop Global Search
  const globalNavSearch = document.getElementById('globalNavSearch');
  const globalSearchResults = document.getElementById('globalSearchResults');
  setupCattleAutocomplete(globalNavSearch, globalSearchResults);

  // Mobile Search Toggle & Autocomplete
  const mobileSearchToggleBtn = document.getElementById('mobileSearchToggleBtn');
  const mobileSearchContainer = document.getElementById('mobileSearchContainer');
  const mobileSearchCloseBtn = document.getElementById('mobileSearchCloseBtn');
  const mobileNavSearch = document.getElementById('mobileNavSearch');
  const mobileSearchResults = document.getElementById('mobileSearchResults');

  if (mobileSearchToggleBtn && mobileSearchContainer) {
    mobileSearchToggleBtn.addEventListener('click', function () {
      mobileSearchContainer.classList.toggle('d-none');
      if (!mobileSearchContainer.classList.contains('d-none') && mobileNavSearch) {
        mobileNavSearch.focus();
      }
    });
  }

  if (mobileSearchCloseBtn && mobileSearchContainer) {
    mobileSearchCloseBtn.addEventListener('click', function () {
      mobileSearchContainer.classList.add('d-none');
    });
  }

  setupCattleAutocomplete(mobileNavSearch, mobileSearchResults);
});

// Helper for escaping HTML strings
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Helper for print
function printContent(elementId) {
  window.print();
}
