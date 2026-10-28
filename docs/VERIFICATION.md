# Sally kit verification

## Generated deliverables

- Vector PNG/SVG exports regenerated from the Sally geometry for all ten expressions.
- Idle, wave and dance loops regenerated as transparent WebP and sprite sheets, plus square/portrait H.264 MP4.
- Ten procedural Blender/GLB models and transparent rendered previews generated with Blender 4.3.2, 48 Cycles samples.
- Glossy transparent menu illustration and six-expression atlas generated separately from the mesh, as documented in ART_DIRECTION.md.

## Checks

- Python generators and validator compile.
- `git diff --check` passes.
- Atlas frame coordinates verified for all six expressions, including invalid input handling.
- Headless Chromium tested the local gallery: six 512px transparent artwork canvases; ten vector expression cards; PNG download with expected filename; model-expression selector updates preview and GLB link; all displayed images load; mobile viewport has no horizontal overflow; no JavaScript errors.
- Visual review of the glossy hero, glossy atlas, vector contact sheet, actual happy mesh render and full gallery screenshot.
- `tools/validate_assets.py` checks all delivered model/image/video formats and required Sally-specific geometry/layers. CI runs it on push and pull request.

## Practical limits

The glossy artwork is an illustrated raster asset, not a mesh render. The procedural model is a simplified editable interpretation; its lighting, surface detail and facial shapes do not exactly duplicate the original sheet. No facial blend shapes, skin weights or lip sync are included. Raster atlas download preserves the source resolution (512 × 512 per expression) and alpha; the vector pack and mesh renders provide separate 1080px outputs.
