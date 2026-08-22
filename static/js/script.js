// ==========================================================
// SMART DAIRY FARM MANAGEMENT SYSTEM - JAVASCRIPT
// ==========================================================

document.addEventListener('DOMContentLoaded', function () {
  // Mobile sidebar toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  // Auto calculate milk total price on input
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

  // Client-side quick table search
  const tableSearchInput = document.getElementById('tableSearch');
  if (tableSearchInput) {
    tableSearchInput.addEventListener('keyup', function () {
      const filter = this.value.toLowerCase();
      const rows = document.querySelectorAll('.searchable-table tbody tr');

      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  }
});

// Helper for print
function printContent(elementId) {
  window.print();
}
