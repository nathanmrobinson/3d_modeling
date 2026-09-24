# Pony-style yarn bobbin

A simplified reconstruction of the flat Pony P60624 bobbin from the supplied photo. The long sides are parallel, the bottom fork has straight edges, and the domed opening connects to the top notch through an open slit.

## Files

- [Printable STL](exports/pony-bobbin-65x25x1mm.stl), with coordinates in millimetres.
- [3MF model](exports/pony-bobbin-65x25x1mm.3mf), with millimetre units embedded. This contains geometry; choose your own printer and filament settings in PrusaSlicer.
- [Screenshot](preview.png), showing top and angled views rendered directly from the exported STL.
- [Editable Python source](source/build.py) and [SVG outline](source/outline.svg).

## Size and reference

| Feature | Dimension |
| --- | --- |
| Overall length along Y | 65 mm / 6.5 cm |
| Overall width along X | 25 mm / 2.5 cm |
| Thickness along Z | 1 mm / 0.1 cm |
| Top slit | 0.6 mm clear width, through the full thickness |
| Domed opening | 14.2 mm wide |
| Bottom fork depth | Approximately 10.5 mm |

The silhouette follows the [supplied Amazon image](https://m.media-amazon.com/images/I/5136FlLMooL._AC_UF350,350_QL80_.jpg), with nearly straight edges regularised and small surface details omitted. The slit is slightly right of centre, as in the photo, and widened for printing.

The [Amazon product](https://www.amazon.ie/Pony-P60624-Yarn-Bobbin-Multi-Colour/dp/B0063G24RM) title supplied by the user gives 9.5 × 6 × 14.2 cm. Its dimension table could not be retrieved. Those dimensions appear to refer to the pack. A [listing for the same P60624](https://allegro.pl/oferta/bobinki-sorter-organizer-szpulki-do-nici-wloczek-muliny-10sz-pony-60624-9662982469) gives one bobbin as 65 × 25 × 1 mm. The user chose the smaller version while retaining the photo's proportions. Internal dimensions are estimated from the photo, with a deliberate 0.6 mm slit.

## Printing on the Prusa MK4S

Import either model into PrusaSlicer and select the MK4S profile for your actual nozzle and filament. Keep the broad face flat on the bed, with thickness along Z. The STL is already oriented this way, with its underside at Z = 0.

A starting setup is 0.2 mm layers, 3 perimeters, solid rectilinear infill, and no supports or brim. The 1 mm thickness gives five layers. PLA or PETG can be trialled; the slit grip and part flexibility still need a physical print test.

The part can be enlarged in PrusaSlicer. Uniform scaling also scales thickness and slit width; use independent axis scaling if you want to change the footprint while retaining thickness. Reducing the size can close the slit in practice, so inspect the layer preview after scaling.

## Verification

The exported STL is watertight, has consistent normals, and contains one solid with 628 triangles. Its measured bounds are 25 × 65 × 1 mm. PrusaSlicer 2.9.2 imported both STL and 3MF as one manifold part.

The STL was sliced using `Original Prusa MK4S HF0.4 nozzle`, `0.20mm STRUCTURAL @MK4S 0.4`, and `Prusament PLA @MK4S HF0.4`, with the settings above. A check of the extrusion paths found an open channel from the eye to the outside on every layer. Nominal clearances at the slit were 1.0 mm on the first layer (elephant-foot compensation) and 0.6 mm on the remaining four layers. See [geometry verification](validation.json) and [slicing verification](slicing-validation.json).

No physical print or yarn retention test has been performed. The verification G-code was temporary; slice the model for your own printer setup.

## Rebuilding

From this directory:

```sh
python3 -m venv .venv
.venv/bin/pip install -r source/requirements.txt
.venv/bin/python source/build.py
.venv/bin/python source/render_preview.py
```

The screenshot script uses an installed Chromium or Google Chrome browser. `build.py` regenerates both model formats, the SVG outline, and the geometry report. The slicing report records the checked STL hash and should be renewed after geometry changes.
