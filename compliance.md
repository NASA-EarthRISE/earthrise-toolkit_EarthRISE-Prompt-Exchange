# Section 508 / WCAG 2.1 Level AA Accessibility Compliance Report

**Application:** EarthRISE Prompt Exchange
**Test Date:** 2026-07-24
**Standard:** WCAG 2.1 Level A and Level AA (Section 508 equivalent)
**Testing Tool:** pa11y 9.1.1 — runners: `htmlcs` (HTML Code Sniffer) + `axe` (axe-core 4.11.4)
**Browser:** Chromium 150.0.7871.24 (via Puppeteer)
**Authenticated as:** Django superuser (`admin`) via session cookie
**Base URL:** http://localhost:8000

---

## Executive Summary

The EarthRISE Prompt Exchange application **does not currently conform** to WCAG 2.1 Level AA. Automated testing identified **11 distinct WCAG failure categories** across the 7 pages tested, plus 6 categories of best-practice warnings.

All failures are isolated to template markup and are fixable without architectural changes. The most pervasive issue — missing accessible names on the navbar toggler button — appears on every single page because it lives in the shared base template.

| Category | Count |
|----------|------:|
| WCAG errors (Level A failures) | 8 issue types |
| WCAG errors (Level AA failures) | 3 issue types |
| Warnings (best practice) | 6 categories |

---

## Test Methodology

### Pages Tested

All pages were tested with an authenticated Django superuser session to ensure the real application templates were evaluated (not redirects).

| Page | URL | Auth |
|------|-----|:----:|
| Login | `/accounts/login/` | No |
| Access Denied | `/access-denied/` | Yes (admin) |
| Home | `/` | Yes (admin) |
| Browse Prompts | `/prompts/` | Yes (admin) |
| Prompt Detail | `/prompts/solution-co-development-toolkit-web-app/` | Yes (admin) |
| Create Prompt | `/prompts/create/` | Yes (admin) |
| My Prompts | `/my-prompts/` | Yes (admin) |

### Runner Configuration

Both runners were executed independently per page. Results were merged and deduplicated by issue type for this report.

```
Standard:   WCAG2AA
Runners:    htmlcs (HTML Code Sniffer), axe (axe-core 4.11.4)
Notices:    included
Warnings:   included
Timeout:    60 000 ms
Wait:       1 000 ms (allows JS rendering)
```

---

## Results by Page

| Page | htmlcs total | htmlcs errors | axe total | axe errors |
|------|:---:|:---:|:---:|:---:|
| Login | 40 | 1 | 1 | 0 |
| Access Denied | 56 | 1 | 1 | 0 |
| Home | 72 | 1 | 3 | 0 |
| Browse Prompts | 78 | 4 | 3 | 2 |
| Prompt Detail | 85 | 6 | 4 | 2 |
| Create Prompt | 76 | 1 | 5 | 3 |
| My Prompts | 54 | 2 | 2 | 1 |

"Errors" are confirmed WCAG failures. "Warnings" and "Notices" require human judgment and are detailed in the warnings section.

---

## Errors — WCAG Failures

### WCAG 1.3.1 — Info and Relationships (Level A)

#### E1 · Comment textarea has no label — Prompt Detail

The comment form renders the textarea widget (`{{ comment_form.text }}`) without any associated `<label>`, `title`, `aria-label`, or `aria-labelledby`. Confirmed by both htmlcs (`H91.Textarea.Name`, `F68`) and axe.

**Affected element (rendered HTML):**
```html
<textarea name="text" class="form-control" rows="3" id="id_text"></textarea>
```

**Template location:** `templates/prompts/prompt_detail.html` — the comment form block (~line 100)

**Fix:** Add a label before the widget:
```html
<form method="post">
    {% csrf_token %}
    <label for="id_text" class="form-label">Your comment</label>
    {{ comment_form.text }}
    <button type="submit" class="btn btn-primary mt-2">
        <i class="bi bi-send" aria-hidden="true"></i> Post Comment
    </button>
</form>
```

---

### WCAG 1.4.3 — Contrast Minimum (Level AA)

#### E2 · Favorite button — contrast ratio 1.63:1 (required ≥ 3:1 for UI components)

`btn-outline-warning` renders amber/yellow (`#ffc107`) text and border on a white background. pa11y recommendation: change text color to `#967100`.

**Affected element:** `templates/prompts/prompt_detail.html` (~line 83)
```html
<button class="btn btn-outline-warning favorite-btn ...">
```

**Fix — option A** (use solid warning button, dark text on amber — meets contrast):
```html
<button class="btn btn-warning favorite-btn ...">
```

**Fix — option B** (custom accessible color in `custom.css`):
```css
.btn-outline-warning.favorite-btn {
    color: #7a5c00;        /* ~5.5:1 on white */
    border-color: #7a5c00;
}
.btn-outline-warning.favorite-btn:hover {
    background-color: #7a5c00;
    color: #fff;
}
```

---

#### E3 · "Public" visibility badge — contrast ratio 1.96:1 (required ≥ 4.5:1)

`badge bg-info` applies Bootstrap's info blue (`#0dcaf0`) background with white text. Both colors are light, producing near-zero contrast. pa11y recommendation: change background to `#00819b`.

**Affected element:** `templates/prompts/prompt_detail.html` (~line 133)
```html
<span class="badge bg-info">Public - All EarthRISE users</span>
```

**Fix:**
```html
<span class="badge" style="background-color: #00819b;">{{ prompt.get_visibility_display }}</span>
```
Or override in `custom.css`:
```css
.badge.bg-info {
    background-color: #00819b !important; /* 4.6:1 on white text */
}
```

---

#### E4 · Inactive "Favorites" tab — contrast ratio 4.13:1 (required ≥ 4.5:1)

Bootstrap's default inactive `.nav-link` color falls just below the 4.5:1 threshold against the white page background.

**Affected element:** `templates/prompts/user_prompts.html` (~line 53)
```html
<button class="nav-link" id="favorites-tab" ...>
```

**Fix in `custom.css`:**
```css
.nav-tabs .nav-link:not(.active) {
    color: #0055a8; /* ~5.9:1 on white */
}
```

---

### WCAG 4.1.2 — Name, Role, Value (Level A)

#### E5 · Navbar toggler button has no accessible name — ALL PAGES

The mobile navigation toggle contains only a decorative icon span with no text, `aria-label`, or `title`. This is the highest-priority fix because it appears on every page via the shared base template.

**Affected element:** `templates/prompts/base.html` (line 29)
```html
<button class="navbar-toggler" type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav">
    <span class="navbar-toggler-icon"></span>
</button>
```

**Fix:**
```html
<button class="navbar-toggler" type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation menu">
    <span class="navbar-toggler-icon"></span>
</button>
```

---

#### E6 · Alert dismiss button has no accessible name — All pages (when messages present)

The Bootstrap dismissible alert close button has no label. Screen readers announce it as "button" with no context.

**Affected element:** `templates/prompts/base.html` (~line 60)
```html
<button type="button" class="btn-close" data-bs-dismiss="alert"></button>
```

**Fix:**
```html
<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Dismiss alert"></button>
```

---

#### E7 · Search submit button has no accessible name — Browse Prompts

An icon-only submit button with no text, `aria-label`, or `title`. Confirmed by htmlcs (`H91.Button.Name`) and axe (`button-name`).

**Affected element:** `templates/prompts/prompt_list.html` (~line 39)
```html
<button class="btn btn-outline-secondary" type="submit">
    <i class="bi bi-search"></i>
</button>
```

**Fix:**
```html
<button class="btn btn-outline-secondary" type="submit" aria-label="Search prompts">
    <i class="bi bi-search" aria-hidden="true"></i>
</button>
```

---

#### E8 · Sort `<select>` has no accessible name — Browse Prompts

The "Sort By" `<label>` element is missing a `for` attribute that matches the select's `id="sort-select"`. Confirmed by htmlcs (`H91.Select.Name`, `F68`) and axe (`select-name`).

**Affected element:** `templates/prompts/prompt_list.html` (~lines 67–68)
```html
<label class="form-label"><strong>Sort By</strong></label>
<select class="form-select" id="sort-select" onchange="updateSort(this.value)">
```

**Fix:** Add `for="sort-select"` to the label:
```html
<label class="form-label" for="sort-select"><strong>Sort By</strong></label>
```

---

#### E9 · Modal close button has no accessible name — Prompt Detail

The Bootstrap `.btn-close` button inside the delete confirmation modal has no label.

**Affected element:** `templates/prompts/prompt_detail.html` (~line 160)
```html
<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
```

**Fix:**
```html
<button type="button" class="btn-close btn-close-white"
        data-bs-dismiss="modal"
        aria-label="Close delete confirmation dialog"></button>
```

---

#### E10 · Three-dots dropdown button has no accessible name — My Prompts

An icon-only button that opens a dropdown menu with no label.

**Affected element:** `templates/prompts/user_prompts.html` (~line 66)
```html
<button class="btn btn-sm btn-link text-muted" type="button" data-bs-toggle="dropdown">
    <i class="bi bi-three-dots-vertical"></i>
</button>
```

**Fix:**
```html
<button class="btn btn-sm btn-link text-muted" type="button"
        data-bs-toggle="dropdown"
        aria-label="Prompt actions for {{ prompt.title }}">
    <i class="bi bi-three-dots-vertical" aria-hidden="true"></i>
</button>
```

---

#### E11 · `aria-describedby` references non-existent element IDs — Create Prompt

Django's form widgets render `aria-describedby` attributes pointing to hint text element IDs (e.g., `id_description_helptext`), but the corresponding `<div class="form-text">` elements in the template have no `id` attributes. This creates broken ARIA relationships that axe flags as `aria-valid-attr-value`.

**Affected elements (rendered HTML):**
```html
<textarea aria-describedby="id_description_helptext" id="id_description" ...></textarea>
<textarea aria-describedby="id_prompt_text_helptext" id="id_prompt_text" ...></textarea>
<input aria-describedby="id_tags_helptext" id="id_tags" ...>
```

**Template location:** `templates/prompts/prompt_form.html` — description, prompt_text, and tags field blocks

**Fix:** Add matching `id` attributes to each `.form-text` hint div:
```html
<!-- Description field -->
<div class="form-text" id="id_description_helptext">
    Explain what this prompt does and when to use it
</div>

<!-- Prompt text field -->
<div class="form-text" id="id_prompt_text_helptext">
    Enter the complete prompt. Use placeholders like [TOPIC] or [DATA] where users should customize.
</div>

<!-- Tags field -->
<div class="form-text" id="id_tags_helptext">
    Add comma-separated tags to help others find your prompt
</div>
```

---

## Warnings — Best Practice / Advisory

These items were flagged by pa11y as warnings (not errors). They do not constitute automatic WCAG failures but represent strong accessibility best practices and may fail a manual audit.

### W1 · No skip navigation link — All pages

All pages lack a "Skip to main content" link. Keyboard users must tab through the entire navigation bar before reaching page content on every page load. The `<main>` element is present (satisfying WCAG 2.4.1's landmark requirement for screen readers), but a visible skip link is still strongly recommended.

**Fix — add as first element after `<body>` in `base.html`:**
```html
<body>
    <a href="#main-content" class="visually-hidden-focusable">Skip to main content</a>
    <nav class="navbar ...">
```
Add `id="main-content"` to the `<main>` element, and add to `custom.css`:
```css
.visually-hidden-focusable:focus {
    clip: auto;
    width: auto;
    height: auto;
    overflow: visible;
    white-space: nowrap;
}
```
Bootstrap 5 includes `.visually-hidden-focusable` natively — no custom CSS needed if using Bootstrap's utility.

---

### W2 · Missing `<h1>` — Login, Access Denied, Create Prompt

Three pages use lower-level headings as their primary title, creating a broken document outline for screen reader users. Axe reports `page-has-heading-one`.

| Page | Current heading | File |
|------|----------------|------|
| Login | `<h2>Welcome Back</h2>` | `templates/account/login.html` |
| Access Denied | `<h2>Access Denied</h2>` | `templates/prompts/access_denied.html` |
| Create Prompt | `<h3>{{ action }} Expert Prompt</h3>` (in card header) | `templates/prompts/prompt_form.html` |

**Fix:** Change the tag to `<h1>` while preserving Bootstrap's visual sizing with a helper class:
```html
<!-- login.html and access_denied.html -->
<h1 class="mt-3 h2">Welcome Back</h1>

<!-- prompt_form.html card header -->
<h1 class="mb-0 h3">
    <i class="bi bi-plus-circle" aria-hidden="true"></i>
    {{ action }} Expert Prompt
</h1>
```

---

### W3 · Heading hierarchy skips — All pages

htmlcs and axe (`heading-order`) flag heading level jumps throughout the application. Bootstrap card layouts encourage `<h5>`/`<h6>` for visual sizing, but the document outline should follow a logical nesting without skipping levels.

| Page | Example | Issue |
|------|---------|-------|
| Home | `<h1>` → `<h5>` card titles | Skips h2–h4 |
| Browse Prompts | `<h1>` → `<h5>` sidebar headings | Skips h2–h4 |
| Prompt Detail | `<h1>` prompt title → `<h5>` section headings | Skips h2–h4 |
| My Prompts | `<h1>` → `<h3>` stats section | Skips h2 |

**Fix:** Use Bootstrap's text-sizing utilities to preserve visual appearance while using semantically correct heading levels:
```html
<!-- Instead of <h5> for card sub-sections after <h1>: -->
<h2 class="h5 mb-0">Filters</h2>
<h2 class="h5 mb-0">Sort By</h2>
```

---

### W4 · Decorative icons not hidden from assistive technology — All pages

Bootstrap Icons (`<i class="bi bi-...">`) are icon font glyphs. Without `aria-hidden="true"`, some screen readers announce them as meaningless characters. All purely decorative icons should be hidden.

**Pervasive in all templates.** Example fix pattern:
```html
<!-- Before -->
<i class="bi bi-rocket-takeoff"></i> EarthRISE Prompt Exchange

<!-- After -->
<i class="bi bi-rocket-takeoff" aria-hidden="true"></i> EarthRISE Prompt Exchange
```

Icons that convey state (e.g., filled vs. unfilled upvote/favorite icons) need a visually hidden text alternative:
```html
<i class="bi bi-hand-thumbs-up-fill" aria-hidden="true"></i>
<span class="visually-hidden">Upvoted</span>
```

---

### W5 · Transparency on nav link colors — All pages

htmlcs (`1_4_3.G18.Alpha`) flags Bootstrap's navbar links because they use `rgba()` colors. The checker cannot compute contrast against transparent backgrounds. This is a tool limitation in measuring Bootstrap's dark navbar — no code change is needed unless a manual visual inspection confirms insufficient contrast at your chosen brand colors.

---

### W6 · `position: fixed` element may require two-dimensional scrolling — Prompt Detail

htmlcs (`1_4_10`) flags a `position: fixed` element on the Prompt Detail page. WCAG 1.4.10 (Reflow) requires content to be accessible without horizontal scrolling at 320px width. Verify the fixed element does not obscure content or require horizontal scrolling on mobile viewports.

---

## Remediation Priority

### Priority 1 — Fix in base template (resolves issue on every page at once)

| # | Issue | File | WCAG |
|---|-------|------|------|
| 1 | Navbar toggler missing `aria-label` | `base.html:29` | 4.1.2 (A) |
| 2 | Alert dismiss button missing `aria-label` | `base.html:~60` | 4.1.2 (A) |
| 3 | Add skip navigation link | `base.html` | 2.4.1 (A) |
| 4 | Add `aria-hidden="true"` to all decorative icons | All templates | advisory |

### Priority 2 — Fix in individual templates (Level A failures)

| # | Issue | File | WCAG |
|---|-------|------|------|
| 5 | Search submit button missing `aria-label` | `prompt_list.html:~39` | 4.1.2 (A) |
| 6 | Sort `<select>` label missing `for` attribute | `prompt_list.html:~67` | 4.1.2 (A) |
| 7 | Comment textarea missing `<label>` | `prompt_detail.html:~100` | 1.3.1, 4.1.2 (A) |
| 8 | Modal close button missing `aria-label` | `prompt_detail.html:~160` | 4.1.2 (A) |
| 9 | `aria-describedby` broken references (3 fields) | `prompt_form.html` | 4.1.2 (A) |
| 10 | Three-dots dropdown missing `aria-label` | `user_prompts.html:~66` | 4.1.2 (A) |

### Priority 3 — Fix Level AA color contrast failures

| # | Issue | File | WCAG | Ratio | Required |
|---|-------|------|------|-------|---------|
| 11 | Favorite button (`btn-outline-warning`) | `prompt_detail.html:~83` | 1.4.3 (AA) | 1.63:1 | 3:1 |
| 12 | Visibility badge (`bg-info` white text) | `prompt_detail.html:~133` | 1.4.3 (AA) | 1.96:1 | 4.5:1 |
| 13 | Inactive Favorites tab | `user_prompts.html:~53` | 1.4.3 (AA) | 4.13:1 | 4.5:1 |

### Priority 4 — Address warnings (best practice)

| # | Issue | Files |
|---|-------|-------|
| 14 | Missing `<h1>` on Login, Access Denied, Create Prompt | `login.html`, `access_denied.html`, `prompt_form.html` |
| 15 | Heading hierarchy skips | All templates |

---

## Conformance Declaration

**Current status: Does not conform to WCAG 2.1 Level AA**

| WCAG Level | Failures |
|------------|----------|
| Level A | 8 (E1, E5, E6, E7, E8, E9, E10, E11) |
| Level AA | 3 (E2, E3, E4) |

The application fails multiple Level A criteria (minimum accessibility floor required by Section 508) primarily due to missing accessible names on interactive controls. All failures are confined to HTML template markup. No backend, database, or infrastructure changes are required.

After remediating issues in Priority 1 and Priority 2, a follow-up automated run and manual keyboard/screen-reader test (NVDA + Chrome, VoiceOver + Safari) is recommended to confirm conformance.

---

*Tested 2026-07-24 with pa11y 9.1.1 (htmlcs + axe-core 4.11.4), authenticated as Django superuser.*
