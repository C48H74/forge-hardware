# Forge Hardware — Español

[English (principal)](../README.md) · [Português](pt-BR.md)

Transforma ideas de piezas, utillajes, mecanismos y robots en código CAD paramétrico editable. El agente de programación interpreta la descripción; build123d/OpenCascade genera la geometría. El visor y los archivos funcionan en tu ordenador, sin un backend alojado ni dependencias de CDN.

## Instalación

Usa Python 3.11–3.13 y un entorno virtual limpio. Python 3.12 en Linux está probado.

```bash
git clone https://github.com/C48H74/forge-hardware.git
cd forge-hardware
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# En PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
forge build examples/fixture.py -o build/fixture
forge view build/fixture
```

Abre `http://127.0.0.1:8740` en el mismo ordenador. Arrastra para orbitar, usa la rueda para ampliar y selecciona una pieza o referencia. El selector de idioma ofrece inglés, portugués y español.

## Instalar la skill del agente

Copia `skills/forge-hardware` al directorio de skills de tu agente, o indica al agente que lea su `SKILL.md`. En Codex CLI:

```bash
mkdir -p ~/.codex/skills
cp -R skills/forge-hardware ~/.codex/skills/forge-hardware
```

ChatGPT Work utiliza su propio flujo de instalación; una copia en tu terminal no instala la skill en otra cuenta. La skill principal está en inglés; las instrucciones traducidas están en `references/es.md` y `references/pt-BR.md`. Los comandos y los identificadores no cambian de idioma.

## Crear y modificar

Pide: “Usa $forge-hardware para crear una placa de 90 × 60 × 8 mm con cuatro agujeros de 5,5 mm a 10 mm de cada borde. Genera CAD, perfil de corte y una vista previa”.

Después: “Aumenta solamente `base/hole_front_left` a 6,5 mm y vuelve a generar los archivos”. El agente cambia la construcción de esa operación en el código; un parámetro global de diámetro cambiaría todos los agujeros.

```bash
forge build examples/fixture.py -o build/fixture --params '{"length":110,"thickness":10}'
forge refs build/fixture
```

Conserva el código fuente y los componentes descargados. El manifiesto registra parámetros, hashes de archivos y tiempo. Si falla una compilación, se conserva la salida anterior. Las referencias semánticas son estables; los índices de caras sólo pertenecen a una compilación.

## Formatos

| Función | Resultado |
|---|---|
| CAD y mallas | STEP, STL, 3MF y GLB |
| Geometría plana explícita en XY | DXF y SVG |
| Revisión | Imagen de geometría, proyecciones, dimensiones generales, referencias y DFM JSON |
| Robótica | URDF, SRDF, SDF y mallas STL locales por eslabón |
| Integración | CLI, cinco herramientas MCP stdio heredadas y adaptador React opcional |

DXF requiere un perfil plano declarado. Los archivos de robot requieren metadatos robóticos. No se realiza desplegado automático de chapa.

## Componentes comerciales

```bash
forge catalog refresh
forge catalog search '608 bearing'
forge catalog search 'NEMA motor'
forge catalog search 'M3 screw' --suppliers
forge catalog search 'JST connector' --suppliers
```

El índice predeterminado usa archivos STEP de FreeCAD-library fijados a una revisión. Tras actualizarlo, la búsqueda es local. Los enlaces de proveedores son búsquedas, no garantías de disponibilidad o dimensiones. Descarga una URL HTTPS directa con `forge catalog download URL assets/part.step` y conserva el registro `.step.json`. Comprueba dimensiones y licencia antes de usarla. Importa con `forge_hardware.cad.step.load_part`.

## Robots y límites

```bash
forge build examples/robot_arm.py -o build/robot_arm
forge view build/robot_arm
```

Geometría de eslabón en mm; orígenes en metros, ángulos en radianes, masas en kg e inercia en kg·m². Se admiten articulaciones fijas, revolutas, continuas y prismáticas en un árbol. Las mallas permanecen junto al XML, en `meshes/`. El visor permite mover las articulaciones.

Las colisiones usan las mallas visuales. Gazebo/MoveIt no se han ejecutado. DFM sólo comprueba la envolvente y espesores declarados; los dibujos de revisión no sustituyen planos de producción acotados y toleranciados. Los servicios de fabricación son enlaces para entrega manual, sin envíos ni pedidos automáticos. Los scripts Python se ejecutan con tus permisos; no son un entorno aislado.

## Pruebas y arquitectura

```bash
python -m pytest -q
node tests/viewer.mjs
python benchmarks/run.py --runs 3
```

[Arquitectura y correspondencia con el diagrama](architecture.md) · [Contrato CAD y robots](modeling.md) · [Configuración del agente](agents.md) · [Componentes](parts.md) · [Benchmarks medidos](../benchmarks/results.json).

Código bajo licencia MIT. Los modelos externos conservan sus licencias originales.
