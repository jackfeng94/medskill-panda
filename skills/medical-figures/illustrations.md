# Medical illustrations and their licences

Use illustrations to explain, not to decorate. Every image goes into `figures/manifest.json`
with its source URL, author, licence and the attribution text you printed on the slide.

## Order of preference

1. **Existing medical image libraries first.** Search them before generating anything:
   - Servier Medical Art for anatomy, organs, physiology and pathology;
   - Bioicons for cells, antibodies, receptors, molecules and lab icons;
   - NIH BioArt, Wikimedia Commons, and open-access figures in PMC.
   They are drawn by people who checked the science, and their licences are clear.
2. **AI-generated, only when no library has a suitable picture.** Use ChatGPT Images or
   Gemini, whichever the user has an account for (asked in the interview), through their own
   signed-in browser. Check the anatomy against a reference before use (`ai-images.md`).
3. **Draw it yourself** only for simple schematic glyphs a library lacks (a receptor, a
   ligand, an arrow). Never draw organs freehand in SVG: hand-coded anatomy looks crude next
   to illustrator artwork. Code is for labels, arrows, highlights and motion.

**Motion graphics use library parts.** Build a mechanism animation from Bioicons cells and
molecules (`scripts/bioicons.py search` / `get`), and animate those, rather than animating
hand-drawn circles. Draw only what Bioicons lacks.

## Bioicons in practice

```bash
python scripts/bioicons.py search t lymphocyte          # licence, category, author, name
python scripts/bioicons.py get t-lymphocyte cancerous-cell-1 immuneglobuline_igG_blue -o <talk>/figures/icons
```

`get` cleans each SVG for inlining, prefixes its ids, and writes `ATTRIBUTION.md` and
`attribution.json` next to the icons. Put the credits on the slide (`data-cite`), for example
"Icons via Bioicons: T lymphocyte by Servier (CC BY 3.0); IgG by Helicase_11 (CC BY 4.0)".
Share-alike icons are hidden unless `--allow-sa`.

Place an icon in a scene as a nested `<svg x y width height viewBox>` (keeps it vector and
editable). Draw receptors and other small parts *before* the cell icon, so their stalks
disappear under the membrane and only the heads show. Then you don't need to know exactly
where the icon's outline runs.

## Libraries

| Library | What it has | Licence | Attribution you must show |
|---------|-------------|---------|---------------------------|
| Servier Medical Art (smart.servier.com) | anatomy, organs, cells, pathology, physiology sequences, lab equipment | CC BY 4.0, including commercial use | "Servier Medical Art (smart.servier.com), CC BY 4.0", plus "labels added" or "modified" |
| Bioicons (bioicons.com) | molecules, cells, lab icons (SVG) | per icon: CC0, CC BY, CC BY-SA, MIT | as stated on each icon's page |
| NIH BioArt (bioart.niaid.nih.gov) | infectious disease, immunology, lab | mostly public domain; check each item | credit NIAID NIH BioArt |
| Wikimedia Commons | anatomy plates, historical images | per file | as stated on the file page |
| PubMed Central open-access articles | figures from CC BY papers | per article (check the licence line) | citation + licence |

## Servier Medical Art at full resolution

The PNGs on each image page are small (about 400–600 px). Each page also links a themed
PowerPoint kit (`SMART-Heart-physiology.pptx`, `SMART-Heart-pathophysiology.pptx`, …) in
which every drawing is a **vector group** of native shapes. Export the group you need at any
size:

1. Search `https://smart.servier.com/?s=<term>`. Open an image page and find the `.pptx`
   link under it, then download the kit.
2. List the groups on the slide with python-pptx (`slide.shapes`: name, position, size).
3. Export one group, keeping its aspect ratio. With PowerPoint (Windows), copy the group
   into a new presentation whose slide size equals the group's size, and export that slide
   at 2400 px wide. With LibreOffice, render the slide to PDF and crop it with
   `pdf_figures.py raster`. Do not use `Shape.Export`: it ignores the aspect ratio.
4. Convert to JPEG (white background) or keep PNG (transparent), at about twice the
   display size.
5. Add labels with `scripts/label_figure.py`, not inside the image.

Servier sequences (the cardiac cycle in four drawings, for example) make good motion
graphics: show them side by side and highlight each step in turn with a CSS loop
(see the heart-anatomy example in the original Grand Rounds project).

## Rules

- **No licence, no use.** "Found on Google Images" is not a licence.
- CC BY-SA images make the slide that uses them share-alike. Avoid them in decks that will
  be sold.
- AI-generated illustrations are drafts until their anatomy has been checked. Never use
  them for histology, imaging or anything a reader could take as a real finding
  (`ai-images.md`).
- Patient images (clinical photos, radiology, histology) belong to the patient and the
  hospital. Use them only with consent recorded in the brief, with identifiers removed from
  the pixels, including DICOM overlays.
- Keep proportions honest in anything you draw yourself: an antibody is not larger than a
  T cell. Label every part the talk mentions, and nothing else.
