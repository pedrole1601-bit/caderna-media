---
name: caderna-editorial-design
description: "Compor e auditar capas de notícias da CADERNA com hierarquia editorial, identidade de marca e gates de QA para Instagram."
license: Proprietary project instructions (no third-party skill files vendored)
---

# CADERNA — Editorial Graphic Design v0.7

Esta é uma skill interna **obrigatória** antes de entregar uma peça visual CADERNA. Ela aplica princípios das skills avaliadas e aprovadas em `pedrole1601-bit/Caderna/docs/SKILLS-APROVADAS.md`. Não são dependências pagas nem afirmação de que pacotes externos foram instalados.

## Referências técnicas utilizadas
- [social-media-graphic](https://github.com/ArnavPuri/designskills/tree/main/skills/social-media-graphic) — proporção 4:5, margens e miniatura.
- [graphic-design](https://github.com/ArnavPuri/designskills/tree/main/skills/graphic-design) — composição, uma mensagem por peça, tipografia.
- [design-critique](https://github.com/ArnavPuri/designskills/tree/main/skills/design-critique) — olhar a imagem renderizada, priorizar falhas e testar novamente.
- [collateral-design](https://github.com/zstvns/design-skills/tree/main/skills/collateral-design) — usar marca canônica, não redesenhar símbolo.
- [creative-direction](https://github.com/zstvns/design-skills/tree/main/skills/creative-direction) — gramática visual própria e coerente.

## Objetivo e linguagem
Jornal digital, contexto factual, sem clickbait. 1080×1350 para feed. Azul profundo `#101C2E`, papel `#F5F3ED`, coral `#EA674D` são cores de função, não ornamentais. Foco único (manchete). Elemento de data e arte documental/ilustração com legenda fiel ao seu caráter. Logo oficial sempre de `assets/logo-horizontal-inverse-v01.svg` ou outro arquivo canônico autorizado.

## Passagem obrigatória de composição
1. Ler a pauta factual, corte temporal, fonte original e legenda ANTES de ajustar a arte.
2. Escrever a manchete em 1–2 linhas completas. Palavras são conteúdo, nunca preencher espaços vagos.
3. Definir grade única e fixar a margem óptica de todas as linhas. No modelo 001, `headline_anchor_x=94`, largura útil do bloco: `[92,1012]`.
4. Usar uma família e um corpo para **todas as linhas da manchete**. Não reduzir fontes em linhas independentes nem espremer horizontalmente uma linha.
5. Garantir respiro entre linhas **medido por bbox**, no modelo 001 mínimo 36 px.
6. Reduzir elementos ornamentais quando há conflito com legibilidade. Nenhum texto sobre texto, linhas encostadas em decoração ou ilustrações sob a manchete.
7. Usar original editorial claramente identificado; não gerar falso documento oficial, falso protagonista ou foto documental sintética.
8. Renderizar PNG 1080×1350, JPEG compatível com Meta e prévia 320×400. Verificar visualmente os três, especialmente o mobile.
9. Rodar `python scripts/verify_design_qa.py` e `python -m unittest discover -s tests -p test_visual_qa.py -v` antes de liberar render.
10. Preencher **CRITICA-EDITORIAL** com antes/depois, problemas corrigidos, limitações e status real de aprovação. O teste automatizado nunca marca `human_approved=true`.

## Gate de rejeição
- Manchete com margens diferentes, corpo assimétrico sem intenção editorial formalizada, encaixe por compressão automática, texto cortado, hierarquia indecifrável a 320 px, ilustração confundida com foto real ou ausência de fonte: **FALHA**.
- A versão aprovada pelo autor ainda precisa de validação editorial e aprovação humana explícita para virar `publish/approved`. Os testes de imagem não autorizam postagens.

## Evidência de uso nesta edição
Pauta 001: `scripts/render_enem_001.py`, teste `tests/test_visual_qa.py`, relatório `media/caderna-enem-2026-001-v2-qa.json`, crítica `docs/CRITICA-EDITORIAL-001-v07.md`. Todas essas peças devem estar versionadas. 
