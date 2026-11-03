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

## Regra 0 — fotografia obrigatória, antes de qualquer layout

TODAS as capas de notícias e carrosséis devem conter fotografia **real, licenciada, relacionada ao assunto e auditável**, ocupando no mínimo 55% da altura. O elemento principal não pode ser uma inicial, um círculo decorativo, um logo, uma ilustração ou uma imagem de IA. Registrar `photo.image_url`, `source_page`, `author`, `credit`, `license`, `license_url`, `description`, `date_taken`, `context`, `context_note`. Somente considerar foto de arquivo se a própria imagem e a legenda disserem que não registra o evento/instalação. Se não houver foto legal e adequada, reportar BLOCKED_GATE. Verificar JPEG, SHA, QA e mobile antes do manifesto privado.

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
- Este repositório gera mídia, mas não autoriza publicações por si só. Para todas as editorias, o gate privado valida fontes, materiais e autorização permanente v3; temas de alto impacto requerem três provas independentes em vez de uma aprovação humana por pauta.

## Evidência de uso nesta edição
Pauta 001: `scripts/render_enem_001.py`, teste `tests/test_visual_qa.py`, relatório `media/caderna-enem-2026-001-v2-qa.json`, crítica `docs/CRITICA-EDITORIAL-001-v07.md`. Todas essas peças devem estar versionadas. 


## Templates dinâmicos e alternância
O `scripts/render_editorial.py` implementa títulos de corpo único em 2 ou 3 linhas, mesma âncora x, respiro medido (tamanho homogêneo), safe zones fixas, SVG oficial e minibanner de origem. Suporta `headline` de imagem única e `carousel`/`explainer` de quatro páginas; temas `ink` e `cream`. O `media/auto/*-qa.json` inclui hashes SHA-256 e o workflow valida cada JPEG em HTTPS antes da aprovação privada.

Usar obrigatoriamente a **skill de voz privada**: `pedrole1601-bit/Caderna/.agents/skills/caderna-guia-de-voz/SKILL.md`. Notícias continuam escritas com contexto e fontes, sem CTA manipulativo; nunca inventar porcentagem de probabilidade de autoria IA.

**Nota de segurança:** a conta Meta não pode ser alcançada deste repositório. O exemplo `2026-11-03-enem-carrossel-teste` é apenas teste de render e jamais deve ser publicado como nova notícia.

## V3 — Editorias sensíveis renderizáveis com verificação reforçada
O proprietário autorizou notícias automáticas de política, guerras, geopolítica, saúde e segurança, desde que a apuração alcance os critérios reforçados do repositório privado. Não bloquear a composição apenas porque a arte menciona assunto sensível; bloquear **risco subdeclarado** ou `risk=high` sem três URLs, três excertos documentais, `review_checks` completos e `claim_status=verified`. O renderer não é verificador de verdade, apenas recebe dados; a publicação continua vedada aqui e controlada pelo GitHub privado.
