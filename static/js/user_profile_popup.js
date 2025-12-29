/**
 * User Profile Popup System
 * 
 * This script creates interactive user profile popups that appear when hovering
 * over profile pictures or elements with the "user-profile-trigger" class.
 * 
 * Usage:
 * 1. Add class "user-profile-trigger" to your profile picture/element
 * 2. Add data attributes to store user information:
 *    - data-user-name (required)
 *    - data-user-username (required)
 *    - data-user-email (required)
 *    - data-user-stars (required)
 *    - data-user-role (required)
 *    - data-user-profile-pic (optional)
 *    - data-user-bio (optional)
 *    - data-user-joined (optional)
 * 3. Include the popup component: {% include 'components/user_profile_popup.html' %}
 * 4. Load this script: <script src="{% static 'js/user_profile_popup.js' %}"></script>
 */

document.addEventListener('DOMContentLoaded', function () {
  console.log('✓ DOMContentLoaded event fired');

  const popup = document.getElementById('user-profile-popup');
  const triggers = document.querySelectorAll('.user-profile-trigger');
  let currentTimeout;

  console.log('Popup component found:', !!popup);
  console.log('Number of triggers found:', triggers.length);

  if (popup) {
    console.log('Popup element details:', {
      id: popup.id,
      classes: popup.className,
      display: popup.style.display
    });
  }

  if (!popup) {
    console.warn('User profile popup component not found. Make sure to include it in your template.');
    return;
  }

  // Test: Log trigger details
  triggers.forEach((trigger, index) => {
    console.log(`Trigger ${index}:`, {
      name: trigger.dataset.userName,
      email: trigger.dataset.userEmail,
      classes: trigger.className
    });
  });

  /**
   * Populate popup with user data
   */
  function populatePopup(trigger) {
    const userData = {
      name: trigger.dataset.userName || 'Unknown',
      username: trigger.dataset.userUsername || '',
      email: trigger.dataset.userEmail || '',
      stars: trigger.dataset.userStars || '0',
      role: trigger.dataset.userRole || 'Student',
      profilePic: trigger.dataset.userProfilePic || '',
      bio: trigger.dataset.userBio || '',
      joined: trigger.dataset.userJoined || '',
      progress: trigger.dataset.userProgress || '0%'
    };

    // Update profile picture or avatar
    const profilePicElement = popup.querySelector('#popup-profile-pic');
    if (userData.profilePic) {
      profilePicElement.innerHTML = `<img src="${userData.profilePic}" alt="${userData.name}" class="w-20 h-20 rounded-full object-cover border-4 border-primary shadow-lg">`;
    } else {
      const initial = userData.name.charAt(0).toUpperCase();
      profilePicElement.innerHTML = `<div class="w-20 h-20 rounded-full bg-primary text-white flex items-center justify-center text-3xl font-bold shadow-lg">${initial}</div>`;
    }

    // Update name
    document.getElementById('popup-name').textContent = userData.name;

    // Update username and role
    document.getElementById('popup-username').textContent = `@${userData.username}`;
    document.getElementById('popup-role').textContent = userData.role;

    // Update email
    const emailLink = document.getElementById('popup-email');
    emailLink.href = `mailto:${userData.email}`;
    emailLink.textContent = userData.email;

    // Update stars
    document.getElementById('popup-stars').textContent = userData.stars;

    // Update progress
    document.getElementById('popup-progress').textContent = userData.progress;

    // Show/hide bio
    const bioSection = document.getElementById('popup-bio-section');
    if (userData.bio) {
      document.getElementById('popup-bio').textContent = userData.bio;
      bioSection.style.display = 'block';
    } else {
      bioSection.style.display = 'none';
    }

    // Show/hide joined date
    const joinedSection = document.getElementById('popup-joined-section');
    if (userData.joined) {
      document.getElementById('popup-joined').textContent = userData.joined;
      joinedSection.style.display = 'block';
    } else {
      joinedSection.style.display = 'none';
    }
  }

  /**
   * Show popup near trigger element
   */
  function showPopup(trigger) {
    // Clear any pending hide timeout
    clearTimeout(currentTimeout);

    // Populate popup with data
    populatePopup(trigger);

    // Get trigger position
    const rect = trigger.getBoundingClientRect();
    const scrollY = window.scrollY;
    const scrollX = window.scrollX;

    // Get popup height to position it so bottom aligns with trigger center
    const popupHeight = popup.offsetHeight || 400; // fallback height
    const triggerCenterY = rect.top + (rect.height / 2);

    // Position popup to the right of trigger, with bottom aligned to trigger center
    const popupTop = scrollY + triggerCenterY - popupHeight + 20; // 20px offset
    const popupLeft = rect.right + scrollX + 20; // 20px gap from trigger

    console.log('Showing popup at:', { popupTop, popupLeft });

    popup.style.top = popupTop + 'px';
    popup.style.left = popupLeft + 'px';
    popup.style.display = 'block';

    // Add show class
    popup.classList.add('show');
    console.log('Popup displayed with class show');
  }

  /**
   * Hide popup with delay
   */
  function hidePopup() {
    currentTimeout = setTimeout(() => {
      popup.style.display = 'none';
      popup.classList.remove('show');
    }, 150);
  }

  // Add hover listeners to all triggers
  triggers.forEach((trigger, index) => {
    console.log(`Setting up trigger ${index}:`, trigger);

    // Add a visible indicator when hovering
    trigger.style.borderRadius = '50%';
    trigger.style.transition = 'transform 0.2s ease';

    trigger.addEventListener('mouseenter', function () {
      console.log('✓ Mouse entered trigger:', this);
      this.style.transform = 'scale(1.2)';  // Visual feedback
      showPopup(this);
    });

    trigger.addEventListener('mouseleave', function () {
      console.log('Mouse left trigger');
      this.style.transform = 'scale(1)';  // Reset visual feedback
      hidePopup();
    });
  });

  // Keep popup visible when hovering over it
  popup.addEventListener('mouseenter', function () {
    clearTimeout(currentTimeout);
  });

  popup.addEventListener('mouseleave', function () {
    hidePopup();
  });

  // Close button functionality
  const closeButton = popup.querySelector('.close-popup');
  if (closeButton) {
    closeButton.addEventListener('click', function (e) {
      e.preventDefault();
      popup.style.display = 'none';
      popup.classList.remove('show');
    });
  }

  // Hide popup when clicking outside
  document.addEventListener('click', function (e) {
    if (!popup.contains(e.target) && !e.target.closest('.user-profile-trigger')) {
      popup.style.display = 'none';
      popup.classList.remove('show');
    }
  });
});
