# GhostScrib Design System & Handoff Specification

## 1. Design Tokens (`frontend/src/theme.css`)

### Brand & Surface Palette
```css
--color-primary:        #147D64;  /* buttons, logo, links, icon strokes */
--color-primary-hover:  #0E614D;  /* interactive hover state */
--color-text:           #172723;  /* headings, high-contrast dark text */
--color-text-muted:     #64716C;  /* body text, secondary captions */
--color-text-faint:     #A3BBB0;  /* icons and decoration ONLY; fails contrast for text */
--color-mint:           #AEEBCF;  /* highlights, accents on dark bands */
--color-mint-pale:      #E2F3EA;  /* chips, badges, highlighted cards */
--color-border:         #DFE6E2;  /* card and divider lines */
--color-surface:        #F0F4F1;  /* quiet panels, inner cards */
--color-bg:             #FAFBFA;  /* page background */
--color-band-tint:      #ECF4EE;  /* alternating tinted section */
--color-dark:           #102A24;  /* full-width dark band */
--color-dark-card:      #19382F;  /* cards on the dark band */
--color-dark-border:    #355247;  /* borders on the dark band ONLY; no text (1.8:1) */
```

### Status & Confidence Tokens
```css
--color-amber-bg:       #FBF0DB;  /* "review suggested" / uncertain chip */
--color-amber-text:     #986422;  /* text on amber chip; use bold or 14px+ (4.45:1) */
--color-amber-text-body:#96621F;  /* darkened amber for normal regular body text (4.6:1 AA) */
--color-amber-border:   #E8D0A7;  /* solid border for AI-like / review suggested */
```

### Radii & Geometry
```css
--radius-card:    14px;
--radius-control: 8px;
--radius-pill:    13.5px;
--radius-chip:    6px;
--radius-full:    9999px;
```

### Shadows & Container Max Width
```css
--shadow-card:    0 18px 60px rgba(24, 57, 43, 0.07);
--container-max:  1264px;
```

### Typography Stack
- **Family**: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- Scale: `xs` (12px), `sm` (14px), `base` (16px), `lg` (18px), `xl` (20px), `2xl` (24px), `3xl` (30px), `4xl` (36px), `5xl` (48px).

---

## 2. Status Colour Rules & Treatments

Every status indicator couples color with an explicit textual label and distinct border treatment:

| State | Fill / Background | Text / Stroke | Border Treatment | Indicator Text |
| :--- | :--- | :--- | :--- | :--- |
| **AI-like** | `--color-amber-bg` (`#FBF0DB`) | `--color-amber-text` (`#986422`) | Solid amber border (`#E8D0A7`), 4px left stripe | `AI-like` |
| **Uncertain** | `--color-surface` (`#F0F4F1`) | `--color-text` (`#172723`) | Dashed border (`#DFE6E2`), 4px dashed left stripe | `Uncertain` |
| **Human-like** | `--color-mint-pale` (`#E2F3EA`) | `--color-primary` (`#147D64`) | Solid mint border (`#AEEBCF`), 4px left stripe | `Human-like` |
| **Not assessed**| `--color-bg` (`#FAFBFA`) | `--color-text-muted` (`#64716C`)| Solid light border (`#DFE6E2`), 4px faint stripe | `Not Assessed` (with skip reason) |

---

## 3. WCAG AA Contrast Audit

Audited via standard relative luminance formula $L = 0.2126 \cdot R + 0.7152 \cdot G + 0.0722 \cdot B$:

| Foreground Token / Hex | Background Token / Hex | Contrast Ratio | WCAG Compliance | Usage Notes |
| :--- | :--- | :--- | :--- | :--- |
| `--color-text` (`#172723`) | `--color-bg` (`#FAFBFA`) | **14.99:1** | AAA | Headings, titles, high-emphasis text |
| `--color-text` (`#172723`) | `--color-surface` (`#F0F4F1`) | **14.00:1** | AAA | Cards, inner quiet panels |
| `--color-text` (`#172723`) | White Card (`#FFFFFF`) | **15.55:1** | AAA | Primary card headings |
| `--color-text-muted` (`#64716C`) | `--color-bg` (`#FAFBFA`) | **4.91:1** | AA | Normal body text, subtitles |
| `--color-text-muted` (`#64716C`) | `--color-surface` (`#F0F4F1`) | **4.59:1** | AA | Secondary text inside panels |
| `--color-text-muted` (`#64716C`) | White Card (`#FFFFFF`) | **5.10:1** | AA | Card descriptions |
| `--color-primary` (`#147D64`) | White Card (`#FFFFFF`) | **5.06:1** | AA | Links, primary accents, active tabs |
| White (`#FFFFFF`) | `--color-primary` (`#147D64`) | **5.06:1** | AA | Primary action button text |
| White (`#FFFFFF`) | `--color-dark` (`#102A24`) | **15.23:1** | AAA | Dark band headings |
| `--color-mint` (`#AEEBCF`) | `--color-dark` (`#102A24`) | **11.30:1** | AAA | Dark band accents & subheadings |
| `--color-amber-text` (`#986422`)| `--color-amber-bg` (`#FBF0DB`) | **4.45:1** | AA Large / Bold | Review suggested badges (bold / 14px+) |
| `--color-amber-text-body` (`#96621F`)| `--color-amber-bg` (`#FBF0DB`) | **4.60:1** | AA Normal Text | Regular body text on amber alert cards |
| `--color-text-faint` (`#A3BBB0`) | `--color-bg` (`#FAFBFA`) | 1.97:1 | N/A (Decoration only)| Decorative divider borders, never text |

---

## 4. Files Controlling Layout Per Page

| Route | Page / Feature Component | Style File | Layout Notes |
| :--- | :--- | :--- | :--- |
| **All Routes** | `frontend/src/App.tsx` | `theme.css` | Global sticky nav with brand pill and max container (`1264px`). |
| `/` (Landing) | `frontend/src/pages/LandingPage.tsx` | `theme.css` | 9-section editorial narrative with dark section (`#102A24`). |
| `/analyze` (Upload) | `frontend/src/pages/HomePage.tsx` | `theme.css` | Centered upload drop zone, file cards, domain selector. |
| (Component) | `frontend/src/features/upload/UploadZone.tsx` | `theme.css` | Dashed border dropzone with hover & drag-over states. |
| `/analyzing/:jobId` | `frontend/src/pages/AnalyzingPage.tsx` | `theme.css` | 6-stage progressive analysis stepper with status icons. |
| `/report/:jobId` | `frontend/src/pages/ReportPage.tsx` | `theme.css` | Report shell, top export bar, tab navigation bar. |
| ↳ Overview | `frontend/src/features/report/OverviewTab.tsx` | `theme.css` | 6 invariant metric cards with ranges, footnotes, warnings. |
| ↳ Document View | `frontend/src/features/report/tabs/DocumentViewTab.tsx` | `DocumentViewTab.module.css` | Collapsible section accordions, paragraph badges, sentence tooltips. |
| ↳ Attribution | `frontend/src/features/report/tabs/AttributionTab.tsx` | `theme.css` | Model distribution, stylometric burstiness, experimental badge. |
| ↳ Citations | `frontend/src/features/report/tabs/CitationsTab.tsx` | `theme.css` | Crossref validation table, filter pills, DOI external links. |
| ↳ Breakdown | `frontend/src/features/report/tabs/BreakdownTab.tsx` | `theme.css` | Detailed per-section metrics, structure verdicts, skip totals. |
| ↳ Limitations | `frontend/src/features/report/tabs/LimitationsTab.tsx` | `theme.css` | Explicit disclaimer cards, boundary constraints, ESL notes. |
| `/about` | `frontend/src/pages/AboutPage.tsx` | `theme.css` | Architecture overview, 5-layer pipeline explanation, privacy policy. |
| `/dev/sandbox` | `frontend/src/pages/DevSandbox.tsx` | `DevSandbox.module.css` | Adversarial text fixture testing suite with escaped preview. |
