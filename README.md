# 3D modeling

Models for 3D printing on a **Prusa MK4S**.

## Models

- [Pony-style yarn bobbin](models/pony-bobbin/README.md)

## Repository layout

Put each design in its own directory under `models/`:

```text
models/
  model-name/
    README.md       # purpose, dimensions, fit, and print notes
    source/         # editable CAD or modeling files
    exports/        # selected printable STL or 3MF files
```

Keep the editable source alongside any exported mesh. Commit exports that are useful to print or share; generated G-code and BG-code stay out of Git because they depend on slicer, material, and printer settings.

## Adding a model

1. Create `models/<model-name>/` and save the editable source in `source/`.
2. Record units (prefer millimetres), important dimensions, assembly or fit details, and any known clearances in the model's README.
3. Export a printable STL or 3MF to `exports/` when ready. Use clear names if there are multiple parts or revisions.
4. Document the intended orientation, material, supports, and any slicer settings that matter. Note whether the part has actually been printed and tested.

Check the exported geometry in a slicer before printing. Choose print settings for the specific part and filament rather than treating repository notes as a printer profile.
