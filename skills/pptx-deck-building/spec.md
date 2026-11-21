# Slide spec for `pptx_from_spec.py`

`build/deck.json`. Paths are relative to the JSON file.

```json
{
  "template": "../theme/template.pptx",
  "layouts": {"title": "Title Slide", "content": "Title Only", "closing": "Title Slide"},
  "theme": {
    "fonts": {"heading": "Arial", "body": "Arial"},
    "colors": {"primary": "#09B1BE", "ink": "#1A1A1A", "muted": "#666666", "line": "#D9D9D9",
               "intervention": "#D7262E", "control": "#5B6B82", "title_text": "#FFFFFF"},
    "type_pt": {"title": 32, "body": 20, "small": 14, "footer": 11}
  },
  "styles": {
    "title": {"size": 38, "bold": true, "color": "#FFFFFF", "caps": true, "align": "center"},
    "title_slide": {"size": 32, "bold": true, "color": "#E8141B", "caps": true},
    "subtitle": {"size": 22, "bold": true, "italic": true, "color": "#002060"}
  },
  "cite": "Long GV, et al. N Engl J Med 2026. DOI: 10.1056/NEJMoa2609762",
  "page_numbers": true,
  "slides": [ … ]
}
```

Leave out `template` for a clean deck drawn from `theme`. `layouts` maps slide kinds to the
template's layouts, by name or, when two masters share a name, by part (`"slideLayout13"`).
`scan_template.py` prints the layouts the template's own slides use: prefer those. A slide may set `"layout"` to
override.

`styles` formats the template's placeholders when the template's own slides were formatted
by hand (common in hospital templates: white bold titles on a coloured band). Read the
sizes, colours and case from `theme/scan.json` and the renders. Keys: `title` (content
slides), `title_slide`, `subtitle`. Each takes `size`, `bold`, `italic`, `color`, `caps`,
`align`, `font`, `anchor` (`top`/`middle`/`bottom`) and `box_in` (`[left, top, width, height]`
in inches, to move the placeholder where the template's own slides put it; `scan.json` →
`title_boxes_in` lists those positions).

## Slide types

| type | fields |
|------|--------|
| `title`, `closing` | `title`, `subtitle`, `presenter` |
| `bullets` | `title`, `bullets`: strings or `{"text", "level", "bold", "color"}` |
| `figure` | `title`, `image` (PNG/JPG), `alt`, `credit`; optional `labels` (`[{"text", "at": [x, y], "side"}]`, as in `label_figure.py`), `margin`, `label_pt` |
| `figure-text` | `title`, `image`, `alt`, `credit`, `bullets`, `split` (0–1, image share) |
| `big-number` | `title`, `numbers`: `[{"value", "label", "color"}]` (1–3), optional `bullets` |
| `table` | `title`, `columns`, `rows`, optional `col_widths` |
| `diagram` | `title`, `nodes`: `[{"id", "x", "y", "w", "h", "text", "style", "shape"}]`, `edges`: `[{"from", "to", "elbow", "from_side", "to_side"}]` |
| `chart` | `title`, `chart` (`bar`, `column`, `line`), `categories`, `series`: `[{"name", "values", "color"}]`, `number_format`, `credit` |
| `references` | `title`, `items` (formatted strings) |

Every slide can carry `notes` (speaker notes) and `cite` (overrides the deck footer).

### Diagram coordinates

`x, y, w, h` are fractions (0–1) of the content area below the title. `style` is
`default`, `int` (intervention arm), `ctl` (control arm), `primary` (filled, white text)
or `muted`. `shape` may be `circle` (use it for the randomisation node). Connector sides:
0 top, 1 left, 2 bottom, 3 right. Defaults run from the right side of `from` to the left
side of `to`.

Example trial schema:

```json
{"type": "diagram", "title": "1,137 patients were randomised 2:1 after tumour sequencing",
 "nodes": [
  {"id": "pop", "x": 0, "y": 0.15, "w": 0.22, "h": 0.7, "text": ["Population", "Resected stage IIB–IV melanoma", "ECOG 0–1"]},
  {"id": "r", "x": 0.27, "y": 0.4, "w": 0.07, "h": 0.2, "text": "R 2:1", "style": "primary", "shape": "circle"},
  {"id": "a", "x": 0.4, "y": 0.05, "w": 0.32, "h": 0.38, "text": ["Intismeran + pembrolizumab", "n = 757"], "style": "int"},
  {"id": "b", "x": 0.4, "y": 0.57, "w": 0.32, "h": 0.38, "text": ["Placebo + pembrolizumab", "n = 380"], "style": "ctl"},
  {"id": "ep", "x": 0.78, "y": 0.15, "w": 0.22, "h": 0.7, "text": ["Primary endpoint", "Recurrence-free survival"]}],
 "edges": [{"from": "pop", "to": "r"}, {"from": "r", "to": "a", "elbow": true}, {"from": "r", "to": "b", "elbow": true},
           {"from": "a", "to": "ep", "elbow": true}, {"from": "b", "to": "ep", "elbow": true}]}
```

## Figures for PPTX

python-pptx cannot embed SVG. Export each figure as PNG at 3× the display size:

- figures lifted from a PDF: `pdf_figures.py raster … --dpi 300` (from the medical-figures skill)
- SVG diagrams or charts: rebuild them as `diagram` or `chart` slides (editable), or rasterise
  the SVG with `scripts/svg_to_png.py`.
