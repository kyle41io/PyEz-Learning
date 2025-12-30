# User Profile Popup System - Usage Guide

## Overview

The user profile popup is a reusable component that displays detailed user information when hovering over profile pictures. It works across any page in your application.

## Files Involved

- **Component Template**: `templates/components/user_profile_popup.html`
- **JavaScript Handler**: `static/js/user_profile_popup.js`
- **Example Usage**: `templates/classroom/dashboard.html`

## How to Use

### Step 1: Include the Popup Component

Add the component once per page (preferably before closing body tag):

```html
{% include 'components/user_profile_popup.html' %}
```

### Step 2: Include the JavaScript

Add this in your template (after including the component):

```html
<script src="{% static 'js/user_profile_popup.js' %}"></script>
```

Make sure to add `{% load static %}` at the top of your template.

### Step 3: Mark Trigger Elements

Add the `user-profile-trigger` class and data attributes to any profile picture or element where you want the popup to appear:

```html
<div
  class="user-profile-trigger cursor-pointer"
  data-user-name="{{ user.first_name }} {{ user.last_name }}"
  data-user-username="{{ user.username }}"
  data-user-email="{{ user.email }}"
  data-user-stars="{{ user.star_points }}"
  data-user-role="{{ user.get_role_display }}"
  data-user-profile-pic="{% if user.profile_picture %}{{ user.profile_picture.url }}{% endif %}"
  data-user-bio="{{ user.bio }}"
  data-user-joined="{{ user.created_at|date:'F j, Y' }}"
>
  {% if user.profile_picture %}
  <img
    src="{{ user.profile_picture.url }}"
    alt="{{ user.first_name }}"
    class="w-10 h-10 rounded-full"
  />
  {% else %}
  <div
    class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center"
  >
    {{ user.first_name|first|upper }}
  </div>
  {% endif %}
</div>
```

## Required Data Attributes

- `data-user-name` - Full name of the user (required)
- `data-user-username` - Username (required)
- `data-user-email` - Email address (required)
- `data-user-stars` - Star points (required)
- `data-user-role` - User role (required)

## Optional Data Attributes

- `data-user-profile-pic` - URL to profile picture
- `data-user-bio` - User biography
- `data-user-joined` - Join date

## Features

✅ Shows on profile picture hover only
✅ Popup stays in fixed position (doesn't follow mouse)
✅ Smooth animations
✅ Dark mode support
✅ Responsive design
✅ Auto-hides when mouse leaves
✅ Can be closed with close button
✅ Works with any number of users on the same page
✅ Fully reusable across pages

## Example: Using in Different Pages

### In a User Search Results Page:

```html
{% extends 'base.html' %} {% load static %} {% load i18n %} {% block content %}
<div class="search-results">
  {% for user in search_results %}
  <div class="user-card">
    <div
      class="user-profile-trigger cursor-pointer"
      data-user-name="{{ user.first_name }} {{ user.last_name }}"
      data-user-username="{{ user.username }}"
      data-user-email="{{ user.email }}"
      data-user-stars="{{ user.star_points }}"
      data-user-role="{{ user.get_role_display }}"
      data-user-profile-pic="{% if user.profile_picture %}{{ user.profile_picture.url }}{% endif %}"
      data-user-bio="{{ user.bio }}"
      data-user-joined="{{ user.created_at|date:'F j, Y' }}"
    >
      <img src="{{ user.profile_picture.url }}" alt="{{ user.first_name }}" />
    </div>
    <h3>{{ user.first_name }} {{ user.last_name }}</h3>
    <p>@{{ user.username }}</p>
  </div>
  {% endfor %}
</div>

{% include 'components/user_profile_popup.html' %}

<script src="{% static 'js/user_profile_popup.js' %}"></script>
{% endblock %}
```

### In a Team/Class Members Page:

```html
{% extends 'base.html' %} {% load static %} {% load i18n %} {% block content %}
<div class="members-list">
  {% for member in team_members %}
  <div class="member-card">
    <div
      class="user-profile-trigger"
      data-user-name="{{ member.first_name }} {{ member.last_name }}"
      data-user-username="{{ member.username }}"
      data-user-email="{{ member.email }}"
      data-user-stars="{{ member.star_points }}"
      data-user-role="{{ member.get_role_display }}"
      data-user-profile-pic="{% if member.profile_picture %}{{ member.profile_picture.url }}{% endif %}"
      data-user-bio="{{ member.bio }}"
      data-user-joined="{{ member.created_at|date:'F j, Y' }}"
    >
      <!-- Profile picture here -->
    </div>
  </div>
  {% endfor %}
</div>

{% include 'components/user_profile_popup.html' %}
<script src="{% static 'js/user_profile_popup.js' %}"></script>
{% endblock %}
```

## Popup Content

The popup displays:

- Profile picture (or initials if no picture)
- User name and username with role badge
- Email (clickable mailto link)
- Stars and role stats
- Bio (if available)
- Join date (if available)
- "View Full Profile" button

## Customization

You can customize the popup appearance by editing:

- `templates/components/user_profile_popup.html` - HTML and styles
- `static/js/user_profile_popup.js` - Behavior and positioning logic

## Notes

- The popup only shows on profile picture hover (not the entire user item)
- Popup position is smart - it appears to the right of the trigger element
- Works with any number of users on the same page
- Only one popup is shown at a time
- Popup auto-dismisses when mouse leaves or clicking elsewhere
