# HTML Report Manual Testing Guide

## Overview

This guide provides comprehensive manual testing procedures for the HTML report generation feature. Since automated browser testing is not available, this checklist ensures thorough validation across browsers, viewports, and data scenarios.

**Task Reference:** Task 7.1 from html-report-generation spec

## Prerequisites

Before starting manual testing:

1. **Generate a test report** from a real evaluation run:
   ```bash
   cd agent-eval
   python -m agent_eval.cli trace-eval \
     --input test-fixtures/baseline/manifest.yaml \
     --rubrics test-fixtures/rubrics.yaml \
     --output ./manual-test-output
   ```

2. **Locate the generated report:**
   - Report file: `./manual-test-output/report_<run_id>.html`
   - Open in multiple browsers for cross-browser testing

3. **Prepare test browsers:**
   - Chrome (latest version)
   - Firefox (latest version)
   - Safari (latest version, macOS only)
   - Optional: Edge, mobile browsers

## Test Scenarios

### Scenario 1: Standard Report with Complete Data

**Test Data:** Use baseline evaluation run with:
- 5-10 turns
- 3-5 rubrics (mix of numeric and categorical)
- 2-3 judges
- Complete latency data
- Tool calls present
- Adapter diagnostics available

**Expected Report Sections:**
1. Report Metadata
2. Run Summary
3. Trace Summary
4. Rubric Score Table
5. Judge Details
6. Latency Analysis
7. Tool Activity
8. Adapter Diagnostics (collapsible)
9. Evidence Display (per rubric)
10. Artifacts Section
11. Charts (5 charts if all data present)

---

### Scenario 2: Minimal Data Report

**Test Data:** Create or use evaluation run with:
- No rubrics (empty rubric_results)
- No judges (empty judge_runs.jsonl)
- No latency data (all latency fields null)
- Minimal turns (1-2 turns)

**Expected Behavior:**
- Report generates successfully without errors
- Sections with no data display "N/A" or "unavailable" messages
- No charts generated (or empty chart placeholders)
- No JavaScript errors in browser console

---

### Scenario 3: Large Dataset Report

**Test Data:** Generate evaluation run with:
- 100+ turns
- 10+ rubrics
- 5+ judges
- Complete data for all fields

**Expected Behavior:**
- Report loads within reasonable time (<5 seconds)
- Tables are scrollable and performant
- Charts render without lag
- Browser doesn't freeze or crash
- File size reasonable (<10MB)

---

## Browser Testing Checklist

### Chrome Testing

**Version:** Record Chrome version: `_____________`

| Test Item | Pass | Fail | Notes |
|-----------|------|------|-------|
| Report loads without errors | ☐ | ☐ | |
| All sections visible | ☐ | ☐ | |
| Charts render correctly | ☐ | ☐ | |
| Charts are interactive (hover, zoom) | ☐ | ☐ | |
| Collapsible sections work | ☐ | ☐ | |
| "Show more" text expansion works | ☐ | ☐ | |
| High-risk rows highlighted in red | ☐ | ☐ | |
| Score color coding correct (green/yellow/red) | ☐ | ☐ | |
| Tables sortable (if implemented) | ☐ | ☐ | |
| Responsive design on resize | ☐ | ☐ | |
| No console errors | ☐ | ☐ | |
| Print preview works | ☐ | ☐ | |

**Console Errors:** (List any JavaScript errors)
```
[Record errors here]
```

---

### Firefox Testing

**Version:** Record Firefox version: `_____________`

| Test Item | Pass | Fail | Notes |
|-----------|------|------|-------|
| Report loads without errors | ☐ | ☐ | |
| All sections visible | ☐ | ☐ | |
| Charts render correctly | ☐ | ☐ | |
| Charts are interactive (hover, zoom) | ☐ | ☐ | |
| Collapsible sections work | ☐ | ☐ | |
| "Show more" text expansion works | ☐ | ☐ | |
| High-risk rows highlighted in red | ☐ | ☐ | |
| Score color coding correct (green/yellow/red) | ☐ | ☐ | |
| Tables sortable (if implemented) | ☐ | ☐ | |
| Responsive design on resize | ☐ | ☐ | |
| No console errors | ☐ | ☐ | |
| Print preview works | ☐ | ☐ | |

**Console Errors:** (List any JavaScript errors)
```
[Record errors here]
```

---

### Safari Testing

**Version:** Record Safari version: `_____________`

| Test Item | Pass | Fail | Notes |
|-----------|------|------|-------|
| Report loads without errors | ☐ | ☐ | |
| All sections visible | ☐ | ☐ | |
| Charts render correctly | ☐ | ☐ | |
| Charts are interactive (hover, zoom) | ☐ | ☐ | |
| Collapsible sections work | ☐ | ☐ | |
| "Show more" text expansion works | ☐ | ☐ | |
| High-risk rows highlighted in red | ☐ | ☐ | |
| Score color coding correct (green/yellow/red) | ☐ | ☐ | |
| Tables sortable (if implemented) | ☐ | ☐ | |
| Responsive design on resize | ☐ | ☐ | |
| No console errors | ☐ | ☐ | |
| Print preview works | ☐ | ☐ | |

**Console Errors:** (List any JavaScript errors)
```
[Record errors here]
```

---

## Detailed Feature Testing

### 1. Chart Rendering and Interactivity

**Test each chart type:**

#### Chart 1: Rubric Score Distribution
- [ ] Bar chart displays with correct rubric IDs on x-axis
- [ ] Scores displayed on y-axis (0-1 range)
- [ ] Bars colored correctly (green >= 0.7, orange >= 0.4, red < 0.4)
- [ ] Hover shows exact score value
- [ ] Chart title: "Rubric Score Distribution (Numeric Only)"
- [ ] Categorical rubrics excluded from this chart
- [ ] Chart responsive to window resize

#### Chart 2: Judge Disagreement Analysis
- [ ] Scatter plot displays with rubric IDs on x-axis
- [ ] Disagreement signals on y-axis
- [ ] High-risk points colored red, others blue
- [ ] Horizontal dashed line at y=0.3 (threshold)
- [ ] Hover shows rubric ID and disagreement value
- [ ] Chart title: "Judge Disagreement Analysis (Numeric Only)"
- [ ] Categorical rubrics excluded from this chart

#### Chart 3: Latency by Turn
- [ ] Line chart with markers displays turn IDs on x-axis
- [ ] Latency (ms) on y-axis
- [ ] Line connects all points
- [ ] Hover shows turn ID and exact latency
- [ ] Chart title: "Latency by Turn"
- [ ] Handles missing latency data (shows 0 or skips)

#### Chart 4: Tool Activity by Turn
- [ ] Stacked bar chart displays turn IDs on x-axis
- [ ] Tool call counts on y-axis
- [ ] Green bars for successful tools
- [ ] Red bars for failed tools
- [ ] Bars stacked correctly
- [ ] Hover shows count breakdown
- [ ] Chart title: "Tool Activity by Turn"
- [ ] Legend shows "Successful" and "Failed"

#### Chart 5: Confidence Penalty Summary
- [ ] Horizontal bar chart displays penalty reasons on y-axis
- [ ] Total penalty values on x-axis
- [ ] Bars colored orange
- [ ] Hover shows exact penalty value
- [ ] Chart title: "Confidence Penalty Summary"
- [ ] Chart height adjusts to number of reasons
- [ ] Only displays if confidence penalties present

**Chart Interactivity:**
- [ ] Zoom in/out works (double-click or zoom controls)
- [ ] Pan works (click and drag)
- [ ] Reset axes button works
- [ ] Download plot as PNG works (Plotly menu)
- [ ] Charts don't overlap or clip

---

### 2. Collapsible Sections

**Test each collapsible section:**

#### Adapter Diagnostics Section
- [ ] Section starts collapsed by default
- [ ] Click header to expand
- [ ] Arrow icon changes (▶ to ▼)
- [ ] Content displays correctly when expanded
- [ ] Click header again to collapse
- [ ] Smooth transition (no flicker)
- [ ] Hover effect on header (background color change)

#### "Why this score?" Evidence Sections (per rubric)
- [ ] Each rubric row has collapsible evidence section
- [ ] Sections start collapsed
- [ ] Click to expand shows:
  - Final aggregated score/label
  - Evidence fields used (list)
  - Evidence previews (resolved content)
  - Judge reasoning snippets
  - Disagreement summary (if applicable)
- [ ] Evidence content is readable and formatted
- [ ] Judge reasoning grouped correctly by rubric and turn
- [ ] Collapsible behavior consistent across all rubrics

#### Long Text Truncation ("Show more" buttons)
- [ ] Long reasoning text truncated to ~200 characters
- [ ] "Show more" link appears for truncated text
- [ ] Click "Show more" expands full text
- [ ] Link changes to "Show less"
- [ ] Click "Show less" collapses text again
- [ ] Multiple "Show more" sections work independently

---

### 3. High-Risk Row Highlighting

**Test high-risk visual indicators:**

- [ ] Identify rubrics with `high_risk_flag = true` in data
- [ ] Corresponding table rows have:
  - Red background color (#ffebee)
  - Red left border (4px solid #f44336)
- [ ] High-risk styling visible and distinct
- [ ] Hover effect still works on high-risk rows
- [ ] High-risk rows stand out visually from normal rows

**Expected high-risk conditions:**
- Disagreement signal >= 0.3
- Cross-judge score < 0.4 (low score)
- Combination of both

---

### 4. Responsive Design Testing

**Desktop viewport (1920x1080):**
- [ ] Report container centered with max-width 1400px
- [ ] All sections visible without horizontal scroll
- [ ] Tables fit within container
- [ ] Charts display at full width
- [ ] Text readable and well-spaced

**Tablet viewport (768x1024):**
- [ ] Report container adjusts to viewport width
- [ ] Tables remain readable (may scroll horizontally)
- [ ] Charts resize appropriately
- [ ] Font sizes remain readable
- [ ] Padding/margins adjust for smaller screen

**Mobile viewport (375x667):**
- [ ] Report container uses full width with reduced padding
- [ ] Tables scroll horizontally if needed
- [ ] Charts resize to fit mobile width
- [ ] Font sizes reduced but still readable (14px minimum)
- [ ] Collapsible sections work on touch
- [ ] No horizontal page scroll (only table scroll)
- [ ] Metadata grid stacks vertically

**Test resize behavior:**
- [ ] Gradually resize browser from desktop to mobile
- [ ] Layout transitions smoothly
- [ ] No broken layouts at any width
- [ ] Charts redraw correctly on resize

---

### 5. Artifact File Paths Display

**Verify Artifacts section:**

- [ ] Section titled "Artifacts" or "Artifact References"
- [ ] Displays file paths for:
  - normalized_run.json
  - trace_eval.json
  - judge_runs.jsonl
  - results.json
  - report_<run_id>.html (self-reference)
- [ ] File paths are complete and correct
- [ ] Checksums displayed (SHA256 hashes)
- [ ] File sizes displayed (if available)
- [ ] Paths are readable and not truncated

---

### 6. Data Accuracy Verification

**Cross-check report data against source artifacts:**

#### Run Summary
- [ ] Run ID matches normalized_run.json
- [ ] Processed timestamp correct
- [ ] Adapter version matches
- [ ] Segmentation strategy correct
- [ ] Run confidence score accurate
- [ ] Overall mapping coverage accurate

#### Trace Summary
- [ ] Turn count matches number of turns in normalized_run
- [ ] Total steps count correct
- [ ] Tool call count accurate
- [ ] Average latency calculated correctly
- [ ] Total latency sum correct
- [ ] Finish reasons histogram accurate

#### Rubric Scores
- [ ] All rubrics from trace_eval.json present
- [ ] Cross-judge scores match trace_eval
- [ ] Disagreement signals correct
- [ ] High-risk flags match
- [ ] Turn IDs correct for turn-scoped rubrics
- [ ] "N/A" displayed for run-scoped rubrics

#### Judge Details
- [ ] All judges from judge_runs.jsonl present
- [ ] Total jobs count correct per judge
- [ ] Success rate calculated correctly
- [ ] Average latency accurate
- [ ] Provider and model names correct

---

### 7. Edge Cases and Error Handling

**Test with problematic data:**

#### Empty/Missing Data
- [ ] Report with no rubrics displays gracefully
- [ ] Report with no judges displays "unavailable" message
- [ ] Report with no latency shows "N/A" consistently
- [ ] Report with no tool calls shows zero counts
- [ ] Report with no adapter diagnostics shows "unavailable"

#### Special Characters in Data
- [ ] Run IDs with special characters display correctly
- [ ] Rubric IDs with underscores/hyphens render properly
- [ ] Long rubric IDs don't break table layout
- [ ] HTML special characters escaped (<, >, &, ", ')
- [ ] No XSS vulnerabilities (script tags rendered as text)

#### Large Values
- [ ] Very large latency values (>10000ms) display correctly
- [ ] Very small scores (0.001) display with precision
- [ ] Large disagreement signals (>1.0) handled
- [ ] Long reasoning text (>1000 chars) truncated properly

#### Categorical Rubrics
- [ ] Categorical rubrics display in table
- [ ] Categorical values shown (not numeric scores)
- [ ] Categorical rubrics excluded from numeric charts
- [ ] Vote breakdown displayed for categorical rubrics
- [ ] Disagreement text appropriate for categorical (e.g., "unanimous", "2-1 split")

---

### 8. CSS Styling Consistency

**Verify styling across browsers:**

- [ ] Font family consistent (system fonts)
- [ ] Colors match design:
  - Green: #4caf50 (high scores)
  - Orange: #ff9800 (medium scores)
  - Red: #f44336 (low scores, high-risk)
  - Blue: #2196f3 (evidence borders)
- [ ] Border radius consistent (4px for sections, 8px for container)
- [ ] Box shadows render correctly
- [ ] Hover effects smooth and visible
- [ ] Table borders consistent (1px solid #e0e0e0)
- [ ] Background colors correct:
  - Body: #f5f5f5
  - Container: white
  - Section: white with border
  - Collapsible content: #fafafa

**Typography:**
- [ ] Headings (h1, h2, h3) sized appropriately
- [ ] Body text readable (16px base)
- [ ] Table text sized correctly (14px)
- [ ] Monospace fonts for IDs/paths (if applicable)

---

## Performance Testing

### Load Time
- [ ] Report opens in browser within 2 seconds (typical dataset)
- [ ] Report opens within 5 seconds (large dataset)
- [ ] No "page unresponsive" warnings

### Interaction Performance
- [ ] Collapsible sections toggle instantly (<100ms)
- [ ] Chart interactions smooth (no lag on hover)
- [ ] Scrolling smooth (no jank)
- [ ] "Show more" expansion instant

### File Size
- [ ] Report file size reasonable:
  - Typical dataset: <500KB
  - Large dataset: <5MB
- [ ] Charts don't bloat file size excessively

---

## Security Testing

### XSS Prevention
- [ ] Test with malicious input in artifacts:
  - `<script>alert('XSS')</script>` in run_id
  - `<img src=x onerror=alert('XSS')>` in rubric_id
  - JavaScript in reasoning text
- [ ] All malicious input rendered as plain text (escaped)
- [ ] No script execution in browser

### Path Traversal
- [ ] Test with run_id containing `../` or `..\`
- [ ] Generated filename sanitized (no directory traversal)
- [ ] Report written to correct output directory only

### Sensitive Data
- [ ] No API keys visible in report
- [ ] No credentials in report
- [ ] No sensitive system paths exposed
- [ ] PII handled appropriately (if present in test data)

---

## Accessibility Testing (Optional)

### Keyboard Navigation
- [ ] Tab through interactive elements (collapsible headers, links)
- [ ] Enter/Space activates collapsible sections
- [ ] Focus indicators visible
- [ ] Logical tab order

### Screen Reader Compatibility
- [ ] Headings structured correctly (h1 > h2 > h3)
- [ ] Tables have proper headers (th elements)
- [ ] Alt text for charts (if applicable)
- [ ] ARIA labels for interactive elements

### Color Contrast
- [ ] Text meets WCAG AA contrast ratio (4.5:1)
- [ ] Color not sole indicator (use icons/text too)
- [ ] High-risk rows distinguishable without color

---

## Test Results Summary

**Date:** `_____________`

**Tester:** `_____________`

**Overall Status:** ☐ Pass ☐ Fail ☐ Pass with Issues

### Issues Found

| Issue # | Severity | Browser | Description | Status |
|---------|----------|---------|-------------|--------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Severity Levels:**
- Critical: Report doesn't load or major functionality broken
- High: Feature doesn't work as expected
- Medium: Visual issue or minor functionality problem
- Low: Cosmetic issue or enhancement

### Recommendations

```
[Document any recommendations for improvements or fixes]
```

---

## Expected Behaviors Reference

### Score Color Coding
- **Green (score-high):** score >= 0.7
- **Orange (score-medium):** 0.4 <= score < 0.7
- **Red (score-low):** score < 0.4

### High-Risk Criteria
- Disagreement signal >= 0.3, OR
- Cross-judge score < 0.4, OR
- Explicit high_risk_flag = true in data

### Collapsible Section States
- **Collapsed (default):** Arrow icon ▶, content hidden
- **Expanded:** Arrow icon ▼, content visible
- **Hover:** Background color changes to #e0e0e0

### Chart Presence
- Charts only generated if `enable_charts=True`
- Individual charts skipped if data unavailable
- Possible chart count: 0-5 depending on data

### Graceful Degradation
- Missing optional fields display "N/A"
- Empty sections display "unavailable" message
- Report generates successfully even with minimal data
- No JavaScript errors for missing data

---

## Troubleshooting

### Report doesn't load
- Check browser console for errors
- Verify Plotly CDN accessible (requires internet)
- Try disabling browser extensions
- Test in incognito/private mode

### Charts don't render
- Verify Plotly CDN loaded (check Network tab)
- Check for JavaScript errors in console
- Verify chart data present in artifacts
- Try regenerating report with `enable_charts=False`

### Styling issues
- Clear browser cache
- Check for CSS conflicts (browser extensions)
- Verify report file not corrupted
- Compare across browsers to isolate issue

### Performance issues
- Check report file size
- Verify dataset size (turn count, rubric count)
- Test on different hardware
- Profile with browser DevTools

---

## Sign-off

**Manual testing completed by:** `_____________`

**Date:** `_____________`

**Signature:** `_____________`

**Approved for release:** ☐ Yes ☐ No ☐ Conditional

**Conditions (if applicable):**
```
[List any conditions for approval]
```
