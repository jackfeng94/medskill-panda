# Motion graphics for medical decks (HTML)

Motion earns its place when it shows something a still cannot: the order of events in a
mechanism, a curve unfolding over time, a step in a pathway being blocked. Each motion
should answer "what happens next?". If it only says "look at me", delete it.

## Performance rules (these prevent stutter on presenter laptops)

- Animate only `transform` and `opacity`. They run on the compositor. Never animate
  `width`, `height`, `top`, `left`, `filter: blur()` or SVG attributes frame by frame
  with JavaScript (`setAttribute` in `requestAnimationFrame` on a large SVG stutters).
- `stroke-dashoffset` drawing is fine for **small** paths (connectors, arrows) with
  `pathLength="1"`. For large figures use the wipe reveal below.
- Slide transitions: a short opacity cross-fade (300–450 ms). No clip-path irises, no 3-D
  flips, no blur.
- Keep the slide's content visible until its fade-out ends (remove the "playing" class
  after the transition, not before), or the slide flashes empty.
- Respect `prefers-reduced-motion`: show the final state.
- Measure: a 3-second capture of `requestAnimationFrame` intervals during the animation
  should give a median near 16.7 ms and a 95th percentile under 20 ms.

## Wipe reveal (Kaplan–Meier curves, any large SVG layer)

Two nested boxes translate in opposite directions, so the clipping edge sweeps while the
content stays put. Both transforms are composited, so the reveal stays smooth.

```html
<div class="km">                       <!-- position:relative; fixed aspect ratio -->
  <svg class="base">…axes, labels, risk table…</svg>
  <div class="wipe"><div class="wipe-in"><svg class="curves">…arms…</svg></div></div>
  <svg class="overlay">…24-month marker (a fragment)…</svg>
</div>
```

```css
.km svg, .wipe, .wipe-in { position:absolute; inset:0; width:100%; height:100% }
.wipe    { overflow:hidden; transform:translateX(-71%); will-change:transform }
.wipe-in { transform:translateX(71%); will-change:transform }
.slide.play .wipe, .slide.play .wipe-in {
  transform:none; transition:transform 2.4s cubic-bezier(.45,.05,.3,1) .5s }
```

71 % is the share of the figure's width to the left of time zero. Start the wipe there so
there is no empty pause before the curves appear.

## Step-wise mechanisms

Build the mechanism as one SVG scene. Give each step a class, and advance with the deck's
fragment steps (`data-frag="1"`, `"2"`…), so the presenter controls the pace and can talk
over each step.

```css
.scene .ab   { transform:translate(-220px,-140px); opacity:0; transition:transform .9s, opacity .4s }
.scene.s3 .ab{ transform:none; opacity:1 }          /* antibody docks onto PD-1 at step 3 */
```

In an HTML deck, put `data-scene="4"` on the SVG: the engine sets class `s0`…`s4` as the
presenter clicks.

## Parts: Bioicons, not hand-drawn shapes

Build scenes from library parts: cells, antibodies, receptors and organelles from Bioicons
(`scripts/bioicons.py`), placed as nested `<svg>` elements and animated as groups. Draw only
the small glyphs no library has. Credit every icon on the slide.

## Looping motion graphics (instead of a video or GIF)

When the mechanism should simply play, as a video would, build a loop in CSS. It stays
vector and crisp on any projector, weighs kilobytes, can be edited, and never shows a
player bar.

- One shared duration (12–20 s) for every animated part, `animation-iteration-count:
  infinite`, and keyframe percentages for each stage of the story.
- One caption per stage at the bottom, faded in and out on the same timeline, plus a thin
  progress line, so the audience knows where they are in the loop.
- The scene fades out over the last 3–4 % and back in, so the jump to the start is invisible.
- Start the animations only under an ancestor with class `play` (`.play .mech .x {animation:…}`):
  the deck engine adds it to the active slide, so the loop restarts from the beginning each
  time the slide appears.
- Write the **static CSS state as the most informative frame** (the poster), and set
  `data-poster="0.6"` on the SVG to that point in the loop. Reduced-motion users, PDF
  export and `check_render.py` screenshots then show that frame.
- Moving along a curved route (blood flow, transport): `offset-path: path("…")` with
  `offset-distance` from 0 % to 100 %; stagger many dots with negative `animation-delay`.

Worked examples in `examples/`:

| File | Shows |
|------|-------|
| `checkpoint-blockade.html` | PD-1/PD-L1 blockade in four stages, 16 s loop, captions and progress line; T cell, tumour cell and antibody are Bioicons |


A sequence of illustrations (Servier draws the cardiac cycle in four pictures) becomes
motion without redrawing anything: place the pictures side by side and highlight each in
turn with one keyframe loop and staggered negative delays (`animation-delay: -9s, -6s, -3s`
for four steps in a 12 s loop). The audience reads the sequence as it plays.

## Labels on illustrations

Put labels **outside** the structures, in a column or row, with thin leader lines to the
part. Labels written inside or across a membrane, a vessel or another label are the most
common defect of drawn figures; check each one on the rendered slide.

## Scientific accuracy in motion

- Every arrow, binding and movement corresponds to a sentence in a cited source; put that
  sentence in the speaker notes.
- Keep the relative sizes and compartments right: cytoplasm vs membrane vs extracellular.
  Ligands bind receptors on the correct cell.
- Show the drug at its real site of action (anti-PD-1 binds PD-1 on the T cell; anti-PD-L1
  binds PD-L1 on the tumour or myeloid cell).
- Do not imply a time scale. Add "schematic, not to scale" in the notes, not on the slide.

## PPTX

PowerPoint animations are not portable between versions. For PPTX, show a mechanism as
2–4 static panels on one slide, or one step per slide, and let the presenter's clicks
stand in for motion.
