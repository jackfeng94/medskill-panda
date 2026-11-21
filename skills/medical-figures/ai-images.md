# AI-generated illustrations (ChatGPT Images, Gemini)

Image models draw attractive anatomy, organs, cells and devices in seconds. They also
invent structures, connect vessels to the wrong chamber and misspell every label. The
workflow below keeps what they are good at (rendering) and removes what they are bad at
(text and correctness).

**Use for:** schematic anatomy, organs, cells, devices, settings, concept art for a title
slide. **Never use for:** histology, radiology, ECGs, clinical photographs, anything an
audience could read as a real finding, or a patient's likeness.

Generate only after the libraries have been searched (`illustrations.md`, order of
preference) and nothing suitable was found. Use the service the user has an account for,
as recorded in the brief: ChatGPT, Gemini, or either if they have both. If the brief doesn't
say, ask in one line before the first generation. If the user has neither, don't generate:
use a library picture or a simpler schematic instead. In all cases their own signed-in
account is used.

## 1. Prompt

Write the prompt in English, as a recipe:

```
Medical textbook illustration: <view and plane, e.g. frontal (coronal) section of the adult
human heart, anterior view>, showing <every structure the slide needs, by name>.
Anatomically accurate proportions: <the one or two proportions that matter, e.g. left
ventricular wall clearly thicker than the right>.
<Colour code, e.g. deoxygenated blood soft blue, oxygenated soft red, myocardium muted red>.
Clean modern flat vector style with subtle shading, crisp outlines.
Pure white background. Landscape 16:9, subject centred, about 60 % of the width, generous
empty margins left and right for labels added later.
Absolutely no text, no labels, no letters, no numbers, no arrows, no watermark.
```

Labels and arrows are added afterwards as editable text (step 4), so the image must carry
none. Name every structure you will label: the model omits what you don't ask for.

## 2. Generate through the browser

Any browser tool the harness has will do: the Playwright MCP, Claude in Chrome, the
Claude desktop browser, or Antigravity's browser. Use the user's own session and never
handle their password: if the page asks for a login, ask the user to sign in.

1. Open `https://chatgpt.com/images` (ChatGPT) or `https://gemini.google.com` (Gemini;
   start the prompt with "Create an image:"). To check which service is signed in, open the
   page and look for a login button before typing.
2. Click the prompt box, type the prompt and press Enter. Generation takes 30–90 s. Wait,
   then check for the finished image (`img` with alt "Generated image…", or the largest
   image on the page).
3. Save it without screenshots, at full resolution. The image is a `blob:` URL on the page,
   so fetch it in the page and trigger a download:

   ```js
   const img = [...document.querySelectorAll('img')].find(i => i.alt.startsWith('Generated image'));
   const b = await (await fetch(img.src)).blob();
   const a = Object.assign(document.createElement('a'), {href: URL.createObjectURL(b), download: 'fig-heart.png'});
   document.body.append(a); a.click(); a.remove();
   ```

   Move the file from the Downloads folder into `<talk>/figures/ai/`. Gemini shows a
   "Download full size image" button on the image: use it when a cross-origin image can't
   be fetched from the page. The ChatGPT route has been tested; the Gemini route has not
   yet.
4. If it's wrong, regenerate or ask for a specific change in the same chat ("make the left
   ventricular wall twice as thick; remove the arrows"). Edits keep the composition.

With API keys (OpenAI Images, Gemini API), the same prompt can be sent from a script
instead. The rest of the workflow is unchanged.

## 3. Check the anatomy (blocking)

Compare the image with a trusted reference: a Servier Medical Art drawing, an anatomy
atlas or a textbook figure. Check the structures you will label, plus any that are
obviously present:

- every vessel connects to the right chamber (AI images often join the pulmonary veins to
  the right atrium);
- relative sizes and wall thicknesses;
- left and right are anatomically consistent (patient's right is the viewer's left);
- no extra or duplicated structures (a third coronary artery, four valve cusps);
- no hidden text or watermark.

Write what you checked, and anything wrong that you did not label, in
`figures/manifest.json` and in the speaker notes. If a structure the slide needs is wrong,
regenerate. Don't hide a wrong structure behind a label.

## 4. Labels as text, never in the pixels

```bash
python scripts/label_figure.py figures/heart.labels.json -o figures/heart.labelled.svg
```

The spec lists each label's text, the point on the structure (fractions of the image) and
the side. The script places the labels in columns, spaces them so they never overlap, and
draws leader lines and dots. `"whiten": 228` turns an off-white AI background pure white.
For PPTX, put the same `labels` list on a `figure` slide (pptx-deck-building spec), and the
labels become editable text boxes.

Find the points by overlaying a 5 % grid on the image and reading coordinates from it.

## 5. Credit and manifest

On the slide (a credit or footer element, not the body):
`Illustration: generated with ChatGPT (OpenAI), anatomy checked against <reference>; labels added.`

In `figures/manifest.json`:

```json
{"file": "ai/heart-chatgpt.jpg", "kind": "ai-generated", "tool": "ChatGPT Images",
 "prompt": "…full prompt…", "date": "2026-11-18", "checked_against": "Servier Medical Art, Heart physiology",
 "issues": "right pulmonary veins drawn into the right atrium; not labelled",
 "licence": "output owned by the user under the service's terms"}
```

Disclosure of AI-generated illustrations is expected by most journals and congresses. It is
not slop.
