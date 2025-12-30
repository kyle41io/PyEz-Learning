# Django i18n Translation Guide

This project uses Django's internationalization (i18n) system for multi-language support.

## Current Supported Languages

- **English (en)** - Default language
- **Vietnamese (vi)** - Tiếng Việt

## How to Add Translations

### Step 1: Mark Strings for Translation

In **HTML templates**, wrap translatable text:

```html
{% load i18n %}

<!-- Simple string translation -->
<p>{% trans "Dashboard" %}</p>

<!-- String with variables (use blocktrans) -->
{% blocktrans %}You have completed {{ count }} lessons.{% endblocktrans %}
```

In **Python files**, use gettext:

```python
from django.utils.translation import gettext_lazy as _

message = _("Welcome to PyEz Learning")
```

### Step 2: Extract Translatable Strings

Run this command to create/update the `.po` files:

```bash
python manage.py makemessages -l vi  # For Vietnamese
python manage.py makemessages -l en  # For English
```

This scans all templates and Python files for `{% trans %}`, `_()` strings.

### Step 3: Add Translations

Edit the `.po` file for your language:

**File:** `locale/vi/LC_MESSAGES/django.po` (Vietnamese example)

```po
msgid "Dashboard"
msgstr "Bảng Điều Khiển"

msgid "Hello, {{ name }}"
msgstr "Xin chào, {{ name }}"
```

### Step 4: Compile Translations

Convert the `.po` files to `.mo` (binary) files:

```bash
python manage.py compilemessages
```

### Step 5: Test the Translation

Restart the server and visit:

- English: `http://localhost:8000/en/`
- Vietnamese: `http://localhost:8000/vi/`

## File Structure

```
locale/
├── en/
│   └── LC_MESSAGES/
│       ├── django.po      # English translations
│       └── django.mo      # Compiled (auto-generated)
└── vi/
    └── LC_MESSAGES/
        ├── django.po      # Vietnamese translations
        └── django.mo      # Compiled (auto-generated)
```

## Adding a New Language

To add a new language (e.g., French):

1. Run: `python manage.py makemessages -l fr`
2. Add `('fr', 'Français')` to `LANGUAGES` in `settings.py`
3. Translate the strings in `locale/fr/LC_MESSAGES/django.po`
4. Run: `python manage.py compilemessages`

## Common Django i18n Functions

| Function                       | Usage                    | Example                                            |
| ------------------------------ | ------------------------ | -------------------------------------------------- |
| `{% trans %}`                  | Simple string            | `{% trans "Hello" %}`                              |
| `{% blocktrans %}`             | With variables           | `{% blocktrans %}Hi {{ name }}{% endblocktrans %}` |
| `gettext_lazy()` (alias `_()`) | Python files             | `msg = _("Welcome")`                               |
| `gettext()`                    | Python files (immediate) | `msg = gettext("Welcome")`                         |

## Language Switcher

Users can switch languages using the 🇬🇧/🇻🇳 button in the navbar. The selected language is preserved in the URL:

- `/en/` - English version
- `/vi/` - Vietnamese version

---

**Developer Tips:**

- Always wrap UI text with translation tags
- Keep translation strings short and simple
- Use descriptive msgid values
- Test translations before deployment
- Use `blocktrans` when you need variables in translated text
