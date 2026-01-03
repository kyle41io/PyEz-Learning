/**
 * Custom Dropdown System
 * Provides interactive dropdowns to replace default select elements
 */

document.addEventListener('DOMContentLoaded', function() {
  const dropdowns = document.querySelectorAll('.custom-dropdown');
  
  dropdowns.forEach(dropdown => {
    const dropdownId = dropdown.dataset.dropdownId;
    const btn = dropdown.querySelector('.custom-dropdown-btn');
    const menu = dropdown.querySelector('.custom-dropdown-menu');
    const input = dropdown.querySelector(`#${dropdownId}-input`);
    const text = dropdown.querySelector('.dropdown-text');
    const arrow = dropdown.querySelector('.dropdown-arrow');
    const items = dropdown.querySelectorAll('.dropdown-item');
    
    // Toggle dropdown
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      // Close other dropdowns
      document.querySelectorAll('.custom-dropdown-menu').forEach(m => {
        if (m !== menu) m.classList.add('hidden');
      });
      document.querySelectorAll('.dropdown-arrow').forEach(a => {
        if (a !== arrow) a.style.transform = '';
      });
      
      // Toggle current dropdown
      menu.classList.toggle('hidden');
      arrow.style.transform = menu.classList.contains('hidden') ? '' : 'rotate(180deg)';
    });
    
    // Handle item selection
    items.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const value = item.dataset.value;
        const label = item.textContent.trim();
        
        // Update input value
        input.value = value;
        
        // Update button text
        text.textContent = label;
        text.classList.remove('text-gray-500', 'dark:text-gray-400');
        text.classList.add('text-gray-900', 'dark:text-white');
        
        // Update active state
        items.forEach(i => {
          i.classList.remove('bg-primary/10', 'text-primary', 'font-bold');
        });
        item.classList.add('bg-primary/10', 'text-primary', 'font-bold');
        
        // Close dropdown
        menu.classList.add('hidden');
        arrow.style.transform = '';
      });
    });
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', () => {
    document.querySelectorAll('.custom-dropdown-menu').forEach(menu => {
      menu.classList.add('hidden');
    });
    document.querySelectorAll('.dropdown-arrow').forEach(arrow => {
      arrow.style.transform = '';
    });
  });
  
  // Prevent closing when clicking inside dropdown
  dropdowns.forEach(dropdown => {
    dropdown.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  });
});
