# Forge Hardware — Instrucciones en español

Mantén SKILL.md en inglés como fuente principal. Responde en español cuando el usuario lo solicite. Conserva los comandos, parámetros e identificadores originales.

1. Localiza el toolkit y crea un entorno Python 3.11–3.13. Instala con `python -m pip install -e /ruta/forge-hardware`.
2. Traduce la petición en requisitos explícitos: dimensiones, unidades, interfaces, material, holguras y cargas indicadas. Documenta supuestos; pregunta sólo lo que cambie sustancialmente el diseño.
3. Escribe código Python editable con `build(**parameters) -> Design`, usando `Design` y `Part` de `forge_hardware.cad.build123d`. Valida parámetros y usa la API real de build123d.
4. Asigna nombres estables a piezas y operaciones, como `base/hole_front_left`. Los puntos de referencia son locales en mm. Los índices de caras no persisten entre compilaciones.
5. Modela los perfiles planos explícitamente en XY. No presentes una proyección como un desplegado de chapa. Incluye compensación de pliegue cuando corresponda.
6. Ejecuta `python -m forge_hardware build fuente.py -o build/diseno`. Inspecciona STEP, dimensiones, volumen, referencias y `review.png`. Abre el visor con `python -m forge_hardware view build/diseno`.
7. Para modificar una sola operación, resuelve la referencia y cambia su construcción. Los parámetros globales pueden afectar varias operaciones. Regenera y compara resultados.
8. Busca componentes con `catalog search '608 bearing'`; usa `--suppliers` cuando sea necesario. Descarga una URL STEP directa con `catalog download URL assets/pieza.step` y conserva `.step.json`. Comprueba dimensiones y licencia; nunca ejecutes código descargado.
9. Para robots, usa geometría local en mm y metadatos SI: metros, radianes, kg y kg·m². Define masa, centro de masa, inercia, ejes y límites. Lee [workflow.md](workflow.md) para el esquema completo. Valida un árbol conectado, ausencia de ciclos y pose cero.
10. Entrega código, exportaciones, vista previa y comando de reproducción. Explica los límites relevantes: DFM de envolvente/espesores declarados, dibujos sin tolerancias automáticas y ninguna validación Gazebo/MoveIt hasta ejecutar esas herramientas.

El agente interpreta el lenguaje natural. El toolkit ejecuta geometría determinista y Python de confianza, sin aislamiento de código. La CLI es la integración principal; MCP stdio heredado es opcional y requiere la revisión aplicable del host antes de configurarlo. No envíes diseños a fabricantes ni hagas pedidos sin una petición del usuario.
