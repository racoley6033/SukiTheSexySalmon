# Sally the Sexy Salmon — character kit

Based on the **Sally the Sexy Salmon Character Sheet** supplied by the user: a round chibi mascot with salmon-slice bob hair, a separate peach face, large green eyes with lashes, a broad perpendicular avocado fringe, seeded jalapeño ring with one sauce dot, rice collar, glossy black gloves and chunky boots.

![Sally illustrated menu cutout](assets/artwork/sally-menu-hero.png)

## Choose the right asset

| Use | Files | What you can edit |
| --- | --- | --- |
| Glossy menu illustration | `assets/artwork/sally-menu-hero.png` | Transparent raster artwork; place in menus, layouts or video editors |
| Glossy expressions | `assets/artwork/sally-expressions-atlas.png` | Six-cell raster artwork atlas; the local gallery exports individual PNG cells |
| Editable 2D expressions | `assets/2d/*.svg`, `*.png` | Named SVG layers, gradients, shapes, colors and facial features |
| Editable 3D mascot | `assets/3d/suki-happy.blend`, `suki-*.glb` | Mesh parts, materials and object animation controls |
| Social animations | `assets/social/` | Idle, wave and dance WebP, RGBA sprite sheets and H.264 MP4 |

**The glossy raster artwork is not a render of the downloadable mesh.** The vector and procedural 3D versions are simpler interpretations of the supplied design. They are suitable starting assets for editing and animation, rather than an exact sculpt or trace of the original illustration. The original character sheet remains the visual source of truth.

The character is called **Sally**. Existing repository, generator and `suki-*` filenames remain for compatibility. `character.json` records her name, expression list and design requirements.

## Expressions and formats

The reference's six expressions are **happy, wink, flirty, excited, sassy and surprised**. Vector and 3D packs add love, sad, angry and sleepy for ten expressions total.

- SVG: layered vector, scalable for menus and print. Groups include `salmon-bob-locks`, `peach-face`, `rice-collar`, `avocado-forehead`, `jalapeno-hat`, `left-arm-glove`, `right-arm-glove` and `boots`.
- PNG: 1080 × 1080, transparent, for each vector expression and actual 3D render.
- GLB: one animated model per expression, with bob and wave clips. Named parts are editable; this is object animation, not a skinned skeleton or facial blend-shape system.
- BLEND: editable happy-expression scene, camera, lights and controls. Use `--expression` to save a scene for another expression.
- WebP: transparent animated loops, 48 frames, approximately two seconds (42ms per frame).
- Sprite sheets: 8 columns × 6 rows, 512px RGBA frames, 24fps; layout in `assets/social/sprites.json`.
- MP4: 48 frames at 24fps; square 1080 × 1080 and vertical 1080 × 1920, cream background. MP4 does not preserve transparency.

## Run in Visual Studio Code

Install **Python 3.11+**, **Blender 4.3+** and **FFmpeg** with H.264 support. Make `python`, `blender` and `ffmpeg` available on PATH. Open this repository folder in VS Code.

```sh
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Select that Python interpreter in VS Code, then run:

```sh
python -m pip install -r requirements.txt
python tools/export_2d.py --video
blender --background --python 3d-blender/export_suki.py -- --render
python -m http.server 8000
```

Open [the local gallery](http://localhost:8000/preview.html). It displays the glossy artwork, editable vectors, actual model renders and animation download links. It can export any of the six glossy atlas cells as a transparent PNG. You can also run the included tasks with **Terminal → Run Task** in VS Code.

CairoSVG needs native Cairo: `brew install cairo` on macOS, `sudo apt install libcairo2` on Debian/Ubuntu, or follow [CairoSVG's Windows installation instructions](https://cairosvg.org/documentation/). If Blender is not on PATH, put its full executable path in `.vscode/tasks.json`. Omit `--video` if FFmpeg is not installed. FFprobe, distributed with FFmpeg, is required for validation.

The Python/Blender generators reproduce the editable vectors, mesh models and social animations. The AI-assisted glossy raster illustrations are included as static art assets; running those generators does not reproduce them. Their art direction is recorded in `docs/ART_DIRECTION.md`.

## Customize

Edit `tools/export_2d.py` for vector geometry and motion, `3d-blender/export_suki.py` for mesh geometry and materials, and `character.json` for expression ordering. Keep the reference's round head, peach face, green eyes, lashes, salmon curls and full costume when making changes.

In Blender, edit `Sally_root` for bobbing and `Wave_pivot` for the right hand. The 48-frame timeline exports bob and wave as separate glTF animation clips; how clips are combined depends on the importing application.

```sh
blender --background --python 3d-blender/export_suki.py -- --expression wink --render
blender --background --python 3d-blender/export_suki.py -- --expression happy --animation
```

`--animation` writes a transparent 48-frame 3D PNG sequence for compositing in a video editor. Rendering all expressions or animation frames can take several minutes. The generator clears the current Blender document: run it in background as shown or in a new empty document. Matching outputs under `assets/` are overwritten, so save custom work elsewhere.

The original `2d-godot/` and `3d-blender/suki_blockout.py` are legacy prototypes and do not represent Sally's reference design. The current kit runs independently of Godot/.NET.

## Validate

```sh
python tools/validate_assets.py
```

Checks all ten expressions, required vector layers and model parts, transparent PNG dimensions, GLB headers and animation channels, WebP frames, glossy artwork alpha and all six MP4 resolutions/frame counts. GitHub Actions runs the same asset checks on pushes and pull requests. These are technical checks; visual fidelity still requires comparison with the supplied sheet.

## Rights

Existing Aquinos branding and reference-art rights remain with their respective owners. This repository does not grant third-party branding rights.
