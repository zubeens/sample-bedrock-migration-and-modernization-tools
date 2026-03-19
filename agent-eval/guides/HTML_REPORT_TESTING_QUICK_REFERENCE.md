# HTML Report Testing Quick Reference

## Quick Start

### Generate Test Report
```bash
cd agent-eval
python -m agent_eval.cli trace-eval \
  --input test-fixtures/baseline/manifest.yaml \
  --rubrics test-fixtures/rubrics.yaml \
  --output ./test-output
```

### Open Report
```bash
# Report location
open ./test-output/report_<run_id>.html
```

---

## Critical Test Points

### 1. Visual Verification (2 minutes)

**Open report in Chrome, Firefox, Safari:**
- [ ] Report loads without errors
- [ ] All 11 sections visible
- [ ] Charts render (5 charts expected)
- [ ] No console errors

---

### 2. Interactivity Check (3 minutes)

**Collapsible sections:**
- [ ] Click "Adapter Diagnostics" → expands
- [ ] Click "Why this score?" → expands per rubric
- [ ] Arrow icons change (▶ to ▼)

**Chart interactions:**
- [ ] Hover over chart → tooltip appears
- [ ] Double-click chart → zooms in
- [ ] Drag chart → pans view

**Text expansion:**
- [ ] Click "Show more" → text expands
- [ ] Click "Show less" → text collapses

---

### 3. Data Accuracy (5 minutes)

**Cross-check against artifacts:**
- [ ] Run ID matches normalized_run.json
- [ ] Turn count matches
- [ ] Rubric scores match trace_eval.json
- [ ] Judge counts match judge_runs.jsonl

---

### 4. Responsive Design (2 minutes)

**Resize browser window:**
- [ ] Desktop (1920px): Full layout, centered
- [ ] Tablet (768px): Adjusted layout, readable
- [ ] Mobile (375px): Stacked layout, scrollable tables

---

### 5. High-Risk Highlighting (1 minute)

**Find rubrics with disagreement >= 0.3 or score < 0.4:**
- [ ] Row has red background (#ffebee)
- [ ] Row has red left border (4px)
- [ ] Stands out visually

---

### 6. Color Coding (1 minute)

**Verify score colors:**
- [ ] Green: score >= 0.7
- [ ] Orange: 0.4 <= score < 0.7
- [ ] Red: score < 0.4

---

### 7. Edge Cases (3 minutes)

**Test with minimal data:**
```bash
# Generate report with no rubrics/judges
python -m agent_eval.cli trace-eval \
  --input test-fixtures/minimal.yaml \
  --output ./test-minimal
```

- [ ] Report generates without errors
- [ ] Sections show "N/A" or "unavailable"
- [ ] No JavaScript errors

---

## Browser Compatibility Matrix

| Feature | Chrome | Firefox | Safari |
|---------|--------|---------|--------|
| Report loads | ☐ | ☐ | ☐ |
| Charts render | ☐ | ☐ | ☐ |
| Collapsible works | ☐ | ☐ | ☐ |
| Responsive design | ☐ | ☐ | ☐ |
| No console errors | ☐ | ☐ | ☐ |

---

## Common Issues

### Charts don't render
- **Cause:** Plotly CDN blocked
- **Fix:** Check internet connection, try different network

### Styling broken
- **Cause:** Browser cache
- **Fix:** Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

### Report doesn't load
- **Cause:** JavaScript disabled
- **Fix:** Enable JavaScript in browser settings

---

## Expected File Locations

```
test-output/
├── normalized_run.<run_id>.json
├── trace_eval.json
├── judge_runs.jsonl
├── results.json
└── report_<run_id>.html  ← Open this file
```

---

## Score Color Reference

| Score Range | Color | CSS Class |
|-------------|-------|-----------|
| >= 0.7 | Green (#4caf50) | score-high |
| 0.4 - 0.7 | Orange (#ff9800) | score-medium |
| < 0.4 | Red (#f44336) | score-low |

---

## Chart Types

1. **Rubric Score Distribution** - Bar chart, numeric rubrics only
2. **Judge Disagreement Analysis** - Scatter plot, threshold line at 0.3
3. **Latency by Turn** - Line chart with markers
4. **Tool Activity by Turn** - Stacked bar chart (green/red)
5. **Confidence Penalty Summary** - Horizontal bar chart (orange)

---

## Report Sections (in order)

1. Report Metadata
2. Run Summary
3. Trace Summary
4. Rubric Score Table
5. Judge Details
6. Latency Analysis
7. Tool Activity
8. Adapter Diagnostics (collapsible)
9. Evidence Display (per rubric, collapsible)
10. Artifacts Section
11. Charts (if enabled)

---

## Performance Targets

| Dataset | Generation Time | Load Time | File Size |
|---------|----------------|-----------|-----------|
| Typical (10 turns, 5 rubrics) | <2s | <2s | <500KB |
| Large (100 turns, 10 rubrics) | <10s | <5s | <5MB |

---

## Security Tests

### XSS Prevention
```bash
# Test with malicious run_id
python -m agent_eval.cli trace-eval \
  --input test.yaml \
  --output ./test-xss \
  --run-id "<script>alert('XSS')</script>"
```
- [ ] Script tag displayed as text (not executed)

### Path Traversal
```bash
# Test with path traversal run_id
python -m agent_eval.cli trace-eval \
  --input test.yaml \
  --output ./test-path \
  --run-id "../../../etc/passwd"
```
- [ ] Filename sanitized (no directory traversal)

---

## Accessibility Quick Check

- [ ] Tab through interactive elements
- [ ] Enter/Space activates collapsible sections
- [ ] Focus indicators visible
- [ ] Headings structured (h1 > h2 > h3)

---

## Sign-off Checklist

- [ ] All critical test points passed
- [ ] Cross-browser compatibility verified
- [ ] Responsive design works
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Edge cases handled gracefully

**Tester:** `_____________`

**Date:** `_____________`

**Status:** ☐ Pass ☐ Fail ☐ Pass with Issues

---

## Full Documentation

- **Testing Guide:** `MANUAL_TESTING_GUIDE.md`
- **Expected Behaviors:** `HTML_REPORT_EXPECTED_BEHAVIORS.md`
- **Spec:** `.kiro/specs/html-report-generation/`

---

## Support

**Issues found?** Document in `MANUAL_TESTING_GUIDE.md` Issues Found section.

**Questions?** Refer to `HTML_REPORT_EXPECTED_BEHAVIORS.md` for detailed behaviors.
