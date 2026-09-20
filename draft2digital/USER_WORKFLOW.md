# Draft2Digital (D2D) Publishing Operational Rules & Learnings

## 1. EPUB Specification & Validation Rules
- **Relative Path Resolution**: `nav.xhtml` located in `OEBPS/Text/nav.xhtml` must use relative links matching its folder level (`href="ch01.xhtml"`, `href="../Styles/main.css"`).
- **NCX Declaration for MOBI Compatibility**: `content.opf` must include `<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>` in `<manifest>` and `toc="ncx"` attribute in `<spine>`. Without these, D2D/KindleGen fails with 'Unable to generate styled mobi'.

## 2. Browser & Execution Workflow Rules
- **Manual Browser Mode**: The user opens their browser manually. The agent must NEVER launch background, headless, or automated browser instances.
- **User-Driven Step Execution**: The user navigates to the step page and explicitly requests field population (e.g., "fill step 1", "continue").
- **CDP Port Connection**: Scripts attach via Playwright CDP (`http://127.0.0.1:9222`) to populate the active user tab.

## 3. Strict "Never-Submit / Draft-Only" Guardrail
- **No Submission Clicks**: Form autofill scripts (`d2d_1_fill_metadata.py`, `d2d_2_fill_details.py`, `d2d_3_fill_pricing.py`) MUST ONLY populate fields and then immediately pause.
- **No Auto-Navigation**: Scripts MUST NOT click 'Save & Continue', 'Preview', or 'Publish My Book'.
- **Manual Review**: The user retains full control to inspect populated fields on-screen and click navigation/publishing buttons manually.
