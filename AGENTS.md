# Repository guidance

This repository contains 3D printable designs intended for a Prusa MK4S.

- Place each design under `models/<model-name>/`, with editable files in `source/` and selected STL or 3MF files in `exports/`.
- Keep source files and exports in sync. When changing geometry, update any affected exports and the model README.
- Use millimetres for dimensions unless a model explicitly says otherwise. Record the units, critical dimensions, mating surfaces, and intended clearances.
- Add print notes for orientation, material, supports, and settings only where they affect the result. Do not claim a print or fit test unless it was performed.
- Avoid committing sliced G-code or BG-code, application backups, caches, and temporary files.
- Prefer small, focused changes. Do not replace an editable source with only a mesh export.
