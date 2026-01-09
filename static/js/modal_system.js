/**
 * Global Modal System for PyEz-Learning
 * Replaces browser alert() with custom styled modals
 * Supports: alert, confirm, success, error, warning
 */

// Modal HTML template (injected once on page load)
const MODAL_TEMPLATE = `
<div id="global-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] hidden" onclick="if(event.target.id==='global-modal') window.globalModalSystem.hide()">
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all scale-95 modal-content">
    <!-- Header -->
    <div id="modal-header" class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center rounded-t-xl gap-3">
      <div id="modal-icon" class="text-3xl"></div>
      <h3 id="modal-title" class="text-xl font-bold text-gray-900 dark:text-white flex-1"></h3>
    </div>
    
    <!-- Body -->
    <div class="px-6 py-6">
      <p id="modal-message" class="text-gray-700 dark:text-gray-300"></p>
    </div>
    
    <!-- Footer -->
    <div id="modal-footer" class="px-6 py-4 bg-gray-50 dark:bg-gray-900 rounded-b-xl flex justify-end space-x-3">
      <!-- Buttons injected here -->
    </div>
  </div>
</div>
`;

class ModalSystem {
  constructor() {
    this.currentCallback = null;
    this.isInitialized = false;
  }

  init() {
    if (this.isInitialized) return;
    
    // Inject modal into DOM
    const wrapper = document.createElement('div');
    wrapper.innerHTML = MODAL_TEMPLATE;
    document.body.appendChild(wrapper.firstElementChild);
    
    this.modal = document.getElementById('global-modal');
    this.modalHeader = document.getElementById('modal-header');
    this.modalIcon = document.getElementById('modal-icon');
    this.modalTitle = document.getElementById('modal-title');
    this.modalMessage = document.getElementById('modal-message');
    this.modalFooter = document.getElementById('modal-footer');
    
    // ESC key handler
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
        this.hide();
      }
    });
    
    this.isInitialized = true;
  }

  show(options) {
    if (!this.isInitialized) this.init();
    
    const {
      type = 'alert', // alert, confirm, success, error, warning
      title = 'Notification',
      message = '',
      confirmText = 'OK',
      cancelText = 'Cancel',
      onConfirm = null,
      onCancel = null
    } = options;

    // Set icon and color based on type
    const typeConfig = {
      success: {
        icon: '✅',
        color: 'green',
        bgClass: 'bg-green-50 dark:bg-green-900/20',
        textClass: 'text-green-600 dark:text-green-400'
      },
      error: {
        icon: '❌',
        color: 'red',
        bgClass: 'bg-red-50 dark:bg-red-900/20',
        textClass: 'text-red-600 dark:text-red-400'
      },
      warning: {
        icon: '⚠️',
        color: 'yellow',
        bgClass: 'bg-yellow-50 dark:bg-yellow-900/20',
        textClass: 'text-yellow-600 dark:text-yellow-400'
      },
      confirm: {
        icon: '❓',
        color: 'blue',
        bgClass: 'bg-blue-50 dark:bg-blue-900/20',
        textClass: 'text-blue-600 dark:text-blue-400'
      },
      alert: {
        icon: 'ℹ️',
        color: 'gray',
        bgClass: 'bg-gray-50 dark:bg-gray-700',
        textClass: 'text-gray-600 dark:text-gray-400'
      }
    };

    const config = typeConfig[type] || typeConfig.alert;

    // Update header
    this.modalHeader.className = `px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-3 ${config.bgClass}`;
    this.modalIcon.textContent = config.icon;
    this.modalIcon.className = `text-3xl ${config.textClass}`;
    this.modalTitle.textContent = title;

    // Update message
    this.modalMessage.textContent = message;

    // Update footer buttons
    this.modalFooter.innerHTML = '';
    
    if (type === 'confirm') {
      // Cancel button
      const cancelBtn = document.createElement('button');
      cancelBtn.type = 'button';
      cancelBtn.className = 'px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold transition';
      cancelBtn.textContent = cancelText;
      cancelBtn.onclick = () => {
        if (onCancel) onCancel();
        this.hide();
      };
      this.modalFooter.appendChild(cancelBtn);

      // Confirm button
      const confirmBtn = document.createElement('button');
      confirmBtn.type = 'button';
      confirmBtn.className = `px-4 py-2 bg-${config.color}-500 text-white rounded-lg hover:bg-${config.color}-600 font-semibold transition`;
      confirmBtn.textContent = confirmText;
      confirmBtn.onclick = () => {
        if (onConfirm) onConfirm();
        this.hide();
      };
      this.modalFooter.appendChild(confirmBtn);
    } else {
      // Single OK button
      const okBtn = document.createElement('button');
      okBtn.type = 'button';
      okBtn.className = `px-4 py-2 bg-${config.color}-500 text-white rounded-lg hover:bg-${config.color}-600 font-semibold transition`;
      okBtn.textContent = confirmText;
      okBtn.onclick = () => {
        if (onConfirm) onConfirm();
        this.hide();
      };
      this.modalFooter.appendChild(okBtn);
    }

    // Show modal with animation
    this.modal.classList.remove('hidden');
    setTimeout(() => {
      this.modal.querySelector('.modal-content').classList.remove('scale-95');
      this.modal.querySelector('.modal-content').classList.add('scale-100');
    }, 10);
  }

  hide() {
    this.modal.querySelector('.modal-content').classList.add('scale-95');
    setTimeout(() => {
      this.modal.classList.add('hidden');
      this.currentCallback = null;
    }, 150);
  }

  // Convenience methods
  alert(message, title = 'Notice') {
    return new Promise((resolve) => {
      this.show({
        type: 'alert',
        title,
        message,
        onConfirm: resolve
      });
    });
  }

  success(message, title = 'Success') {
    return new Promise((resolve) => {
      this.show({
        type: 'success',
        title,
        message,
        onConfirm: resolve
      });
    });
  }

  error(message, title = 'Error') {
    return new Promise((resolve) => {
      this.show({
        type: 'error',
        title,
        message,
        onConfirm: resolve
      });
    });
  }

  warning(message, title = 'Warning') {
    return new Promise((resolve) => {
      this.show({
        type: 'warning',
        title,
        message,
        onConfirm: resolve
      });
    });
  }

  confirm(message, title = 'Confirm') {
    return new Promise((resolve) => {
      this.show({
        type: 'confirm',
        title,
        message,
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        onConfirm: () => resolve(true),
        onCancel: () => resolve(false)
      });
    });
  }
}

// Create global instance
window.globalModalSystem = new ModalSystem();

// Convenience functions
window.showModal = (options) => window.globalModalSystem.show(options);
window.modalAlert = (message, title) => window.globalModalSystem.alert(message, title);
window.modalSuccess = (message, title) => window.globalModalSystem.success(message, title);
window.modalError = (message, title) => window.globalModalSystem.error(message, title);
window.modalWarning = (message, title) => window.globalModalSystem.warning(message, title);
window.modalConfirm = (message, title) => window.globalModalSystem.confirm(message, title);

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => window.globalModalSystem.init());
} else {
  window.globalModalSystem.init();
}
