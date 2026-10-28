# Forge Hardware — Instruções em português

Mantenha o SKILL.md principal em inglês. Responda em português quando o usuário pedir. Preserve comandos, parâmetros e identificadores em sua forma original.

1. Localize o toolkit e crie um ambiente Python 3.11–3.13. Instale com `python -m pip install -e /caminho/forge-hardware`.
2. Traduza o pedido em requisitos explícitos: medidas, unidades, interfaces, material, folgas e cargas informadas. Registre suposições; pergunte apenas o que muda materialmente o projeto.
3. Escreva fonte Python editável com `build(**parameters) -> Design`, usando `Design` e `Part` de `forge_hardware.cad.build123d`. Valide parâmetros e use a API real do build123d.
4. Dê nomes estáveis às peças e operações, como `base/hole_front_left`. Pontos de referência são locais, em mm. Índices de faces não são persistentes entre gerações.
5. Modele perfis planos explicitamente no plano XY. Não chame uma projeção de desdobramento de chapa. Aplique compensação de dobra quando exigida.
6. Execute `python -m forge_hardware build fonte.py -o build/projeto`. Inspecione STEP, dimensões, volume, referências e `review.png`. Abra o viewer com `python -m forge_hardware view build/projeto`.
7. Para alterar uma operação específica, localize a referência e edite sua construção. Parâmetros globais podem afetar várias operações. Regenere e compare resultados.
8. Busque componentes com `catalog search '608 bearing'`; use `--suppliers` quando necessário. Baixe uma URL STEP direta com `catalog download URL assets/peca.step` e conserve o `.step.json`. Confira dimensões e licença; nunca execute código baixado.
9. Para robôs, use geometria local em mm e metadados SI: metros, radianos, kg e kg·m². Defina massa, centro de massa, inércia, eixos e limites. Leia [workflow.md](workflow.md) para o esquema completo. Valide árvore conectada, ausência de ciclos e pose zero.
10. Entregue fonte, arquivos exportados, revisão e comando de reprodução. Informe limites relevantes: DFM restrito a envelope/espessuras declaradas, desenhos sem toleranciamento automático, sem validação Gazebo/MoveIt até executar essas ferramentas.

A linguagem natural é interpretada pelo agente. O toolkit executa geometria determinística e Python confiável, sem sandbox. CLI é a integração principal; MCP stdio legado é opcional e requer revisão aplicável do host antes de configurar. Nunca envie projetos a fabricantes nem faça pedidos sem solicitação do usuário.
