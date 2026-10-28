# Guia rápido

O Forge Hardware permite que um agente de programação transforme uma descrição em código CAD editável, gere os arquivos e faça alterações por referências estáveis.

1. Instale Python 3.11–3.13, clone este repositório e crie um ambiente virtual.
2. Execute `python -m pip install -e '.[dev]'`.
3. Instale a pasta `skills/forge-hardware` no diretório de skills do seu agente.
4. Peça: “Crie uma placa de 90 × 60 × 8 mm com quatro furos de 5,5 mm, a 10 mm das bordas”.
5. Gere: `forge build examples/fixture.py -o build/fixture`.
6. Veja: `forge view build/fixture` e abra `http://127.0.0.1:8740` no mesmo computador.

O agente escreve e edita Python; o runtime produz geometria real. Os nomes como `base/hole_front_left` permitem pedir “aumente somente este furo”. O viewer funciona com arquivos locais e não depende de backend hospedado.

STEP, STL, 3MF e GLB são gerados para sólidos. DXF exige um perfil plano explícito. URDF, SRDF e SDF exigem dados robóticos. Busca de componentes, download STEP com procedência, exemplos, testes e benchmarks estão incluídos.

As verificações DFM são limitadas ao envelope e às espessuras declaradas. Desenhos de revisão não substituem desenhos de produção cotados e toleranciados. A integração com Gazebo/MoveIt não foi executada. Os serviços de fabricação são encaminhamentos manuais, sem envio ou compra automática.

## Idiomas e referências

[English (principal)](../README.md) · [Español](es.md)

O viewer oferece um seletor de idioma. Os comandos, nomes de parâmetros e identificadores geométricos são iguais em todos os idiomas. As instruções da skill estão traduzidas em `references/pt-BR.md` e `references/es.md`.

## Componentes comerciais

```bash
forge catalog refresh
forge catalog search '608 bearing'
forge catalog search 'NEMA motor'
forge catalog search 'M3 screw' --suppliers
forge catalog search 'JST connector' --suppliers
forge catalog download URL_DIRETA_HTTPS assets/part.step
```

O catálogo padrão usa arquivos STEP do FreeCAD-library fixados em uma revisão. Após atualizar, a busca é local. Os links de fornecedores não garantem estoque, medidas ou licença. Preserve o arquivo `.step.json`, confira as dimensões do fabricante e importe com `forge_hardware.cad.step.load_part`.

## Alterações precisas

```bash
forge build examples/fixture.py -o build/fixture --params '{"length":110,"thickness":10}'
forge refs build/fixture
```

Mudar um parâmetro global de diâmetro altera todos os furos que o utilizam. Para alterar somente `base/hole_front_left`, peça ao agente que edite a construção daquela operação. Os pontos semânticos são anotações de referência, não restrições automáticas do CAD. Índices de faces valem somente para a geração atual.

A fonte Python continua editável; o manifesto registra parâmetros, hashes e duração. Se uma geração falhar, a saída anterior é preservada. Diretórios sem manifesto do Forge não são substituídos.

## Robótica

```bash
forge build examples/robot_arm.py -o build/robot_arm
forge view build/robot_arm
```

Geometria local dos links em mm; origens em metros, ângulos em radianos, massa em kg e inércia em kg·m². São aceitas juntas fixas, revolutas, contínuas e prismáticas em uma árvore. Mantenha `meshes/` junto dos arquivos XML. Os controles do viewer aplicam cinemática direta.

As malhas visuais também são usadas como colisão. Laços fechados, controladores e planejamento exigem extensão explícita. Scripts Python rodam com suas permissões; o daemon e o MCP não são sandboxes.

## Testes e documentação

```bash
python -m pytest -q
node tests/viewer.mjs
python benchmarks/run.py --runs 3
```

[Arquitetura e diagrama](architecture.md) · [Contrato CAD e robôs](modeling.md) · [Instalação para agentes](agents.md) · [Componentes](parts.md) · [Benchmarks medidos](../benchmarks/results.json).

O código usa licença MIT; os modelos externos mantêm suas próprias licenças.
