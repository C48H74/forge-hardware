# Complex CAD demonstrations

[English](#english) · [Português](#português) · [Español](#español)

![Three actual CAD demonstrations](https://github.com/user-attachments/assets/aaabe66d-857c-42f9-b944-cd683be8635c)

## English

Three complex, editable examples created using the installed **Forge Hardware** skill. These images render the **actual exported CAD geometry** with a depth buffer. Exploded offsets are presentation-only; the STEP assemblies retain their assembled positions. No geometry is invented by an image model.

| Demonstration | Actual model | Parameter edit checked |
|---|---|---|
| Split bearing housing | 4 solids; ribbed shells, 8 lid bolt locations, mounting feet, 52 mm bearing seats and 2 locating pins | Width 80 → 90 mm; bolt references update |
| Parallel robotic gripper | 9 solids; milled palm, guides, slotted carriages, pocketed fingers and serrated pads; 2 prismatic joints | Finger length 50 → 65 mm; other 7 parts unchanged |
| Serpentine cooling plate | 2 solids; 6 connected flow passes, seal recess, 9 fins, 8 cover bolt locations and 2 fluid ports | Channel depth 7 → 9 mm; cover unchanged |

### 01 — Split bearing housing

![Split bearing housing, actual exploded CAD geometry](https://github.com/user-attachments/assets/d71a5c45-8a5d-4383-ad2f-a883a9339e44)

[Editable source](../examples/gearbox_housing.py). Nominal cast/machined concept; no bearing hardware, threads or fasteners are represented. Pins and seats are geometry demonstrations, not certified fits.

### 02 — Parallel robotic gripper

![Parallel robotic gripper, actual assembled CAD geometry](https://github.com/user-attachments/assets/5085b8a0-864c-43a1-b36c-d6a3955921e1)

[Editable source](../examples/parallel_gripper.py). Nine local-frame link meshes, URDF/SRDF/SDF, opposite ±X slide axes and 20 mm travel per carriage. Mass and inertia use uniform solids with assumed material densities. The two slides are independent; no actuator, synchronization or controller is modeled.

### 03 — Serpentine cooling plate

![Serpentine cooling plate, actual exploded CAD geometry](https://github.com/user-attachments/assets/3e94c914-9fe0-48d9-aa8d-8e029470d02e)

[Editable source](../examples/cooling_manifold.py). The raised cover reveals internal paths and the seal recess. The profile DXF describes an explicit cover outline with holes; it is not an unfolded sheet-metal pattern. Ports and pilot bores are plain holes, not modeled threads. The rectangular seal path is demonstrative and would need production seal design.

### Reproduce the files and images

From the repository root, in the installed Python environment:

```bash
python demos/build_showcase.py --render
python -m pytest -q
node tests/viewer.mjs
```

Or build one model:

```bash
forge build examples/gearbox_housing.py -o build/gearbox_housing
forge build examples/parallel_gripper.py -o build/parallel_gripper
forge build examples/cooling_manifold.py -o build/cooling_manifold
forge view build/parallel_gripper
```

`build/<model>/` contains STEP, STL, 3MF, GLB, review images, drawings and named references. The cooling-cover profile also generates DXF/SVG; the gripper also generates URDF/SRDF/SDF and adjacent local link meshes. Edited variants go in `build/showcase_edits/`. Presentation PNGs are regenerated in `demos/images/`.

[Measured geometry and export evidence](verification.json) · [Showcase tests](../tests/test_showcase.py) · [Renderer source](render_gallery.py)

Validation: **22 Python tests passed**, plus viewer kinematics, depth occlusion and language-parity checks. STEP assemblies were reopened as valid solids. Gripper URDF was read by `urdf_parser_py`. These checks do not certify pressure containment, heat transfer, loads, fatigue, fit, manufacturing or Gazebo/MoveIt behavior.

## Português

Três exemplos complexos criados com a skill Forge Hardware instalada: **carcaça bipartida com 4 sólidos**, **garra robótica com 9 sólidos e 2 juntas prismáticas** e **bloco de refrigeração com 2 sólidos, 6 passagens e 9 aletas**. As imagens mostram geometria CAD real. Os deslocamentos das vistas explodidas servem apenas à apresentação; os arquivos STEP mantêm a montagem.

As fontes Python permanecem editáveis. Foram verificadas três alterações: largura da carcaça de 80 para 90 mm; dedos da garra de 50 para 65 mm, preservando as outras sete peças; e profundidade dos canais de 7 para 9 mm, preservando a tampa. Os **22 testes Python passaram**, além das verificações JavaScript. O STEP foi reaberto e o URDF lido por um parser externo.

Use os comandos acima para regenerar arquivos e imagens. As propriedades físicas da garra são estimativas com densidades assumidas. Os conceitos não possuem qualificação de fabricação, ajustes, pressão, desempenho térmico, cargas ou simulação. Não há acionamento nem sincronização da garra representados.

## Español

Tres ejemplos complejos creados con la skill Forge Hardware instalada: **carcasa partida con 4 sólidos**, **pinza robótica con 9 sólidos y 2 articulaciones prismáticas** y **placa de refrigeración con 2 sólidos, 6 pasos y 9 aletas**. Las imágenes muestran geometría CAD real. Los desplazamientos de las vistas explosionadas sólo sirven para la presentación; los archivos STEP conservan el montaje.

Las fuentes Python siguen siendo editables. Se comprobaron tres cambios: anchura de la carcasa de 80 a 90 mm; dedos de la pinza de 50 a 65 mm, conservando las otras siete piezas; y profundidad de los canales de 7 a 9 mm, conservando la tapa. Pasaron los **22 tests Python**, además de las comprobaciones JavaScript. Se reabrió STEP y un parser externo leyó URDF.

Usa los comandos anteriores para regenerar archivos e imágenes. Las propiedades físicas de la pinza son estimaciones con densidades supuestas. Los conceptos no están cualificados para fabricación, ajustes, presión, rendimiento térmico, cargas ni simulación. No se representa accionamiento ni sincronización de la pinza.
