# HTML Report Expected Behaviors

## Overview

This document provides detailed expected behaviors for the HTML report generation feature. Use this as a reference when performing manual testing to validate that the report behaves correctly.

**Related:** See `MANUAL_TESTING_GUIDE.md` for testing procedures.

---

## Report Structure

### Complete Report Sections (in order)

1. **Report Metadata**
   - Generator version
   - Generation timestamp
   - Charts enabled flag
   - Template version
   - Source artifact versions table

2. **Run Summary**
   - Run ID
   - Processed timestamp
   - Source system (if available)
   - Adapter version
   - Segmentation strategy
   - Run confidence (color-coded)
   - Overall mapping coverage

3. **Trace Summary**
   - Turn count
   - Total steps
   - Tool call count
   - Average latency (or "N/A")
   - Total latency (or "N/A")
   - Finish reasons histogram

4. **Rubric Score Table**
   - Columns: Rubric ID, Scope, Turn ID, Score, Disagreement, High Risk Flag, Scoring Type
   - Sortable by rubric ID (default)
   - Color-coded scores
   - High-risk rows highlighted
   - Collapsible "Why this score?" per rubric

5. **Judge Details**
   - Columns: Judge ID, Provider, Model, Total Jobs, Success Rate, Avg Latency
   - Success rate with progress bar
   - "Judge details unavailable" if no judge data

6. **Latency Analysis**
   - Per-turn latency table
   - Columns: Turn ID, Normalized Latency, Runtime Reported Latency, Total Latency, Step Count
   - "N/A" for missing latency values

7. **Tool Activity**
   - Per-turn tool usage table
   - Columns: Turn ID, Tool Calls, Successful, Failed
   - Individual tool call details

8. **Adapter Diagnostics** (collapsible)
   - Processing statistics
   - Confidence penalties table
   - Orphan tool results table
   - Warnings list
   - Missing fields summary
   - "No adapter diagnostics available" if missing

9. **Evidence Display** (per rubric, collapsible)
   - Final aggregated score/label
   - Evidence fields used
   - Evidence previews (resolved content)
   - Judge reasoning snippets
   - Disagreement summary

10. **Artifacts Section**
    - File paths for all canonical artifacts
    - Checksums (SHA256)
    - File sizes (if available)

11. **Charts** (if enabled)
    - Rubric Score Distribution (numeric only)
    - Judge Disagreement Analysis (numeric only)
    - Latency by Turn
    - Tool Activity by Turn
    - Confidence Penalty Summary

---

## Visual Design Specifications

### Color Palette

**Score Colors:**
- High (>= 0.7): `#4caf50` (green)
- Medium (>= 0.4, < 0.7): `#ff9800` (orange)
- Low (< 0.4): `#f44336` (red)

**High-Risk Highlighting:**
- Background: `#ffebee` (light red)
- Left border: `4px solid #f44336` (red)

**Chart Colors:**
- Successful tools: green
- Failed tools: red
- High-risk points: red
- Normal points: blue
- Confidence penalties: orange
- Evidence borders: `#2196f3` (blue)

**Layout Colors:**
- Body background: `#f5f5f5` (light gray)
- Container background: `white`
- Section borders: `#e0e0e0` (gray)
- Collapsible content: `#fafafa` (off-white)
- Table header: `#f5f5f5` (light gray)
- Hover background: `#f9f9f9` (very light gray)

### Typography

**Font Family:**
- Primary: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- System fonts for optimal rendering

**Font Sizes:**
- Body text: 16px
- Table text: 14px (mobile)
- Headings: h1 (largest), h2 (medium), h3 (small)
- Metadata labels: 12px (uppercase)
- Metadata values: 16px

**Font Weights:**
- Normal: 400
- Medium: 500
- Bold: 600 (table headers)
- Score values: bold

### Spacing

**Container:**
- Max width: 1400px
- Padding: 30px (desktop), 15px (mobile)
- Margin: 0 auto (centered)
- Border radius: 8px

**Sections:**
- Margin bottom: 30px
- Padding: 20px
- Border: 1px solid #e0e0e0
- Border radius: 4px

**Tables:**
- Cell padding: 12px (desktop), 8px (mobile)
- Border: 1px solid #e0e0e0 (bottom only)

**Charts:**
- Margin: 20px 0
- Padding: 15px
- Border radius: 4px

### Responsive Breakpoints

**Desktop (> 768px):**
- Full layout with max-width 1400px
- All features enabled
- Standard padding and spacing

**Mobile (<= 768px):**
- Reduced padding (15px)
- Smaller font sizes (14px tables)
- Smaller cell padding (8px)
- Metadata grid stacks vertically
- Tables may scroll horizontally

---

## Interactive Behaviors

### Collapsible Sections

**Default State:**
- All collapsible sections start collapsed
- Arrow icon: ▶ (right-pointing)
- Content hidden (display: none)

**Expanded State:**
- Click header to expand
- Arrow icon: ▼ (down-pointing)
- Content visible with smooth transition
- Background color: #fafafa

**Hover State:**
- Cursor changes to pointer
- Background color: #e0e0e0
- Smooth transition (0.2s)

**Sections with Collapsible Behavior:**
- Adapter Diagnostics (main section)
- "Why this score?" (per rubric)
- Evidence details (per rubric)

### Text Truncation ("Show more")

**Truncated State:**
- Long text (>200 chars) truncated
- Max height: 100px
- Overflow hidden
- "Show more" link visible (blue, underlined)

**Expanded State:**
- Click "Show more" to expand
- Max height removed
- Full text visible
- Link changes to "Show less"

**Behavior:**
- Multiple truncated sections work independently
- Smooth transition
- No page jump on expansion

### Chart Interactivity

**Hover:**
- Tooltip appears with exact values
- Highlight active data point
- Smooth transition

**Zoom:**
- Double-click to zoom in
- Drag to select zoom area
- Zoom controls in Plotly menu

**Pan:**
- Click and drag to pan
- Works when zoomed in

**Reset:**
- Reset axes button in Plotly menu
- Returns to original view

**Download:**
- Download plot as PNG from Plotly menu
- Saves current view state

---

## Data Display Rules

### Score Display

**Numeric Scores:**
- Display as decimal (0.0 - 1.0)
- 2 decimal places precision
- Color-coded based on thresholds
- Bold font weight

**Categorical Scores:**
- Display label/category name (not numeric)
- No color coding
- Regular font weight
- Vote breakdown shown in evidence section

### Latency Display

**Present:**
- Display in milliseconds (ms)
- Integer or decimal format
- No color coding

**Missing:**
- Display "N/A"
- No color, regular text
- Consistent across all latency fields

### Turn ID Display

**Turn-scoped rubrics:**
- Display actual turn ID (e.g., "turn_001")
- Link to turn details (if implemented)

**Run-scoped rubrics:**
- Display "N/A"
- Indicates rubric applies to entire run

### Disagreement Signal Display

**Numeric:**
- Display as decimal (0.0 - 1.0+)
- 3 decimal places precision
- No color coding in table
- Color-coded in chart (red if >= 0.3)

**Categorical:**
- Display text description (e.g., "unanimous", "2-1 split")
- Derived from vote dispersion
- No numeric value

### High-Risk Flag Display

**True:**
- Entire row highlighted (red background)
- Red left border (4px)
- Flag icon or "Yes" in column
- Stands out visually

**False:**
- Normal row styling
- No special highlighting
- "No" or empty in column

---

## Chart Specifications

### Chart 1: Rubric Score Distribution

**Type:** Bar chart

**Data:**
- X-axis: Rubric IDs (numeric rubrics only)
- Y-axis: Cross-judge scores (0-1 range)
- Colors: Green (>= 0.7), Orange (>= 0.4), Red (< 0.4)

**Layout:**
- Title: "Rubric Score Distribution (Numeric Only)"
- Height: 400px
- Responsive width

**Behavior:**
- Hover shows exact score
- Bars clickable (Plotly default)
- Categorical rubrics excluded

**Empty State:**
- Chart not rendered if no numeric rubrics
- No error message

---

### Chart 2: Judge Disagreement Analysis

**Type:** Scatter plot

**Data:**
- X-axis: Rubric IDs (numeric rubrics only)
- Y-axis: Disagreement signals
- Colors: Red (high-risk), Blue (normal)
- Threshold line: y=0.3 (dashed red)

**Layout:**
- Title: "Judge Disagreement Analysis (Numeric Only)"
- Height: 400px
- Responsive width

**Behavior:**
- Hover shows rubric ID and disagreement value
- Points clickable
- Threshold line annotated

**Empty State:**
- Chart not rendered if no numeric rubrics
- No error message

---

### Chart 3: Latency by Turn

**Type:** Line chart with markers

**Data:**
- X-axis: Turn IDs
- Y-axis: Total latency (ms)
- Line color: Default Plotly blue
- Markers: Circles

**Layout:**
- Title: "Latency by Turn"
- Height: 400px
- Responsive width

**Behavior:**
- Hover shows turn ID and latency
- Line connects all points
- Missing latency shown as 0 or gap

**Empty State:**
- Chart not rendered if no latency data
- No error message

---

### Chart 4: Tool Activity by Turn

**Type:** Stacked bar chart

**Data:**
- X-axis: Turn IDs
- Y-axis: Tool call counts
- Green bars: Successful tools
- Red bars: Failed tools
- Stacked vertically

**Layout:**
- Title: "Tool Activity by Turn"
- Height: 400px
- Responsive width
- Legend: "Successful" and "Failed"

**Behavior:**
- Hover shows count breakdown
- Bars clickable
- Legend toggles traces

**Empty State:**
- Chart not rendered if no tool calls
- No error message

---

### Chart 5: Confidence Penalty Summary

**Type:** Horizontal bar chart

**Data:**
- Y-axis: Penalty reasons (aggregated)
- X-axis: Total penalty values
- Color: Orange

**Layout:**
- Title: "Confidence Penalty Summary"
- Height: Dynamic (max(300, len(reasons) * 40))
- Responsive width

**Behavior:**
- Hover shows exact penalty value
- Bars clickable
- Sorted by penalty value (descending)

**Empty State:**
- Chart not rendered if no confidence penalties
- No error message

---

## Edge Cases and Error Handling

### Missing Required Artifacts

**Behavior:**
- Report generation fails
- Error message: "Missing required artifact: <filename>"
- No partial report generated

**Required Artifacts:**
- normalized_run.<run_id>.json
- trace_eval.json
- judge_runs.jsonl
- results.json (optional, graceful if missing)

---

### Invalid JSON in Artifacts

**Behavior:**
- Report generation fails
- Error message: "Invalid JSON in artifact: <filename>"
- No partial report generated

---

### Missing Optional Fields

**Behavior:**
- Report generates successfully
- Missing fields display "N/A" or default values
- No error messages
- Sections with no data show "unavailable" message

**Optional Fields:**
- metadata (in normalized_run)
- adapter_stats (in normalized_run)
- rubric_results (in trace_eval)
- latency fields (all)
- source field (in metadata)

---

### Empty Collections

**Empty rubric_results:**
- Rubric Score Table shows "No rubrics evaluated"
- No rubric score charts generated
- Evidence sections not displayed

**Empty judge_runs:**
- Judge Details section shows "Judge details unavailable"
- No judge disagreement chart generated

**Empty turns:**
- Latency Analysis shows "No turns available"
- Tool Activity shows "No turns available"
- No latency or tool activity charts

**Empty confidence_penalties:**
- Adapter Diagnostics shows "No confidence penalties"
- No confidence penalty chart generated

---

### Special Characters in Data

**HTML Special Characters:**
- `<`, `>`, `&`, `"`, `'` escaped automatically
- Displayed as plain text, not interpreted as HTML
- Jinja2 autoescape enabled

**Path Traversal Characters:**
- `../`, `..\` in run_id sanitized
- Replaced with underscores
- No directory traversal possible

**Long Strings:**
- Run IDs truncated to 100 characters (filename)
- Display values not truncated (full length shown)
- Long reasoning text truncated with "Show more"

---

### Large Datasets

**100+ turns:**
- Tables remain scrollable
- Charts may have dense x-axis labels
- Performance should remain acceptable (<5s load)

**10+ rubrics:**
- Rubric table may be long (scrollable)
- Charts may have many bars/points
- All rubrics displayed (no pagination)

**5+ judges:**
- Judge details table shows all judges
- No performance issues expected

---

### Categorical Rubrics

**Table Display:**
- Categorical rubrics shown in Rubric Score Table
- Score column shows label/category (not numeric)
- Scoring Type column shows "categorical"

**Chart Exclusion:**
- Categorical rubrics excluded from:
  - Rubric Score Distribution chart
  - Judge Disagreement Analysis chart
- Info message logged (not visible in report)

**Evidence Display:**
- Vote breakdown shown (counts per label)
- Disagreement text (e.g., "unanimous", "2-1 split")
- Judge reasoning snippets included

---

## Security Behaviors

### XSS Prevention

**Input Sanitization:**
- All user-provided data escaped
- HTML tags rendered as plain text
- JavaScript not executed
- Jinja2 autoescape enabled

**Test Cases:**
- `<script>alert('XSS')</script>` → displayed as text
- `<img src=x onerror=alert('XSS')>` → displayed as text
- `javascript:alert('XSS')` → displayed as text

---

### Path Traversal Prevention

**Filename Sanitization:**
- Non-alphanumeric characters (except `.`, `_`, `-`) replaced with `_`
- Leading/trailing dots and underscores stripped
- Truncated to 100 characters
- No directory traversal possible

**Test Cases:**
- `../../../etc/passwd` → `etc_passwd`
- `..\..\windows\system32` → `windows_system32`
- `run/../../../file` → `run_file`

---

### Sensitive Data Protection

**Not Included in Report:**
- API keys
- Credentials
- Passwords
- AWS access keys
- Private keys

**PII Handling:**
- PII in test data displayed as-is (no special handling)
- Recommendation: Sanitize PII before evaluation

---

## Performance Expectations

### Load Time

**Typical Dataset (10 turns, 5 rubrics, 3 judges):**
- Report generation: <2 seconds
- Browser load: <2 seconds
- Total: <5 seconds

**Large Dataset (100 turns, 10 rubrics, 5 judges):**
- Report generation: <10 seconds
- Browser load: <5 seconds
- Total: <15 seconds

---

### File Size

**Typical Dataset:**
- Report file: 200-500 KB
- With charts: +100-200 KB
- Total: <1 MB

**Large Dataset:**
- Report file: 1-3 MB
- With charts: +500 KB - 1 MB
- Total: <5 MB

---

### Interaction Performance

**Collapsible Sections:**
- Toggle time: <100ms
- Smooth transition
- No lag or flicker

**Chart Interactions:**
- Hover response: <50ms
- Zoom/pan: Smooth (60fps)
- No freezing or lag

**Scrolling:**
- Smooth scrolling (60fps)
- No jank or stutter
- Large tables remain performant

---

## Browser Compatibility

### Supported Browsers

**Desktop:**
- Chrome 90+ (fully supported)
- Firefox 88+ (fully supported)
- Safari 14+ (fully supported)
- Edge 90+ (fully supported)

**Mobile:**
- Chrome Mobile (Android)
- Safari Mobile (iOS)
- Firefox Mobile (Android)

### Known Limitations

**Internet Explorer:**
- Not supported (IE 11 and below)
- Modern JavaScript features used
- Plotly requires modern browser

**Older Browsers:**
- May have CSS rendering issues
- Chart interactivity may be limited
- Recommend updating to latest version

---

## Accessibility

### Keyboard Navigation

**Supported:**
- Tab through interactive elements
- Enter/Space to activate collapsible sections
- Arrow keys in charts (Plotly default)

**Focus Indicators:**
- Visible focus outline on interactive elements
- Consistent across browsers

---

### Screen Reader Compatibility

**Semantic HTML:**
- Proper heading hierarchy (h1 > h2 > h3)
- Table headers (th elements)
- ARIA labels on interactive elements

**Limitations:**
- Charts may not be fully accessible
- Complex tables may be difficult to navigate
- Recommendation: Provide alternative data formats

---

### Color Contrast

**WCAG AA Compliance:**
- Text contrast ratio: 4.5:1 minimum
- Large text: 3:1 minimum
- Interactive elements: 3:1 minimum

**Color Independence:**
- High-risk rows have border + background (not just color)
- Scores have text labels + color
- Charts have hover tooltips

---

## Troubleshooting Guide

### Report Doesn't Load

**Possible Causes:**
- Plotly CDN blocked (firewall, no internet)
- JavaScript disabled in browser
- Corrupted report file
- Browser compatibility issue

**Solutions:**
- Check browser console for errors
- Verify internet connection
- Try different browser
- Regenerate report

---

### Charts Don't Render

**Possible Causes:**
- Plotly CDN not loaded
- JavaScript errors
- No chart data in artifacts
- Charts disabled (enable_charts=False)

**Solutions:**
- Check Network tab for Plotly CDN
- Check console for JavaScript errors
- Verify artifacts contain chart data
- Regenerate with enable_charts=True

---

### Styling Issues

**Possible Causes:**
- Browser cache
- CSS conflicts (extensions)
- Browser compatibility
- Corrupted report file

**Solutions:**
- Clear browser cache
- Disable browser extensions
- Try different browser
- Regenerate report

---

### Performance Issues

**Possible Causes:**
- Very large dataset (1000+ turns)
- Slow hardware
- Browser resource constraints
- Too many charts

**Solutions:**
- Close other browser tabs
- Regenerate with enable_charts=False
- Use more powerful hardware
- Split evaluation into smaller runs

---

## Validation Checklist

Use this checklist to validate expected behaviors:

- [ ] All sections present and visible
- [ ] Data accuracy verified against source artifacts
- [ ] Score color coding correct (green/yellow/red)
- [ ] High-risk rows highlighted properly
- [ ] Charts render and are interactive
- [ ] Collapsible sections work correctly
- [ ] "Show more" text expansion works
- [ ] Responsive design works on mobile
- [ ] No JavaScript errors in console
- [ ] No XSS vulnerabilities
- [ ] Path traversal prevented
- [ ] Performance acceptable (<5s load)
- [ ] File size reasonable (<5MB)
- [ ] Cross-browser compatibility verified
- [ ] Accessibility features work
- [ ] Edge cases handled gracefully

---

## Conclusion

This document provides comprehensive expected behaviors for the HTML report generation feature. Use it as a reference during manual testing to ensure the report meets all requirements and behaves correctly across browsers, viewports, and data scenarios.

For testing procedures, see `MANUAL_TESTING_GUIDE.md`.
