# AGENTS.md — CADERNA MEDIA (regras obrigatórias)

Este repositório hospeda **somente mídias públicas** para a conta jornalística CADERNA. Não há credenciais, nem envio ao Instagram. O código secreto e as fichas editoriais ficam em `pedrole1601-bit/Caderna` (privado).

## Leitura mandatória antes de qualquer arte
1. `.agents/design-context.md` — marca, público, tipografia, cores e tom.
2. `.agents/skills/caderna-editorial-design/SKILL.md` — skill interna **obrigatória** de layout e QA.
3. `docs/CRITICA-EDITORIAL-001-v07.md` — primeiro caso de regressão de hierarquia.
4. `scripts/verify_design_qa.py` — contrato de layout e critérios bloqueantes.
5. Referências externas (orientação, sem dependência paga): ArnavPuri/designskills `social-media-graphic`, `graphic-design`, `design-critique`; zstvns/design-skills `creative-direction`, `collateral-design`.

## Entregas bloqueadas
- Falha de fonte ou cópia da logo → parar render.
- Manchete com corpos independentes, alinhamentos variáveis ou interlinha pequena → parar render.
- Foto/ilustração sem contexto/documentação de direitos → parar render.
- Arte apenas bonita sem fonte factual → não pode virar reportagem.
- CI técnico aprovado mas sem revisão humana → permanece DRAFT.
- Publicar no Instagram a partir deste repositório → **proibido**; somente depósito público de JPEG/PNG no Pages.

## Testes
`python scripts/render_enem_001.py && python scripts/verify_design_qa.py && python -m unittest discover -s tests -p test_visual_qa.py -v`.

GitHub Actions também verifica skill e crítica e publica mídia apenas se todos os gates passarem.


## Produção de notícias futuras (a partir de 03/11/2026)
- Qualquer nova pauta pública usa `incoming/YYYY-MM-DD-slug.json`, renderizada por `scripts/render_editorial.py`. A pauta NÃO é publicável no Instagram somente por existir aqui.
- `.github/workflows/editorial-pages.yml` exige fontes de hosts diferentes, originalidade, `risk=low`, layout editorial e JPEG íntegro. O `qa.json` contém SHA-256 de cada JPEG e é conferido no repo privado antes de permitir um post.
- Para `headline`: 1 imagem. Para `carousel` ou `explainer`: 4 imagens (capa + 3 quadros de contexto). Temas `ink` e `cream` podem alternar, sem afrouxar margens e legibilidade.
- Toda copy deve passar pela skill obrigatória `Caderna/Caderna/.agents/skills/caderna-guia-de-voz/SKILL.md` no repo **privado** (resumo original de guia do proprietário, não distribuir PDF de terceiro), pelo linter e pela dupla revisão.
- **Proibido** criar pautas automáticas de eleições, conflitos, política, tragédias, saúde, crime, alegações, emergências; nesses casos, encaminhar a equipe responsável sem publicação.
- A demonstração `incoming/2026-11-03-enem-carrossel-teste.json` tem `example_only=true` e `publication_authorized=false`. Ela **nunca** deve ser enviada ao Instagram.
- Toda publicação é realizada exclusivamente pelo repo privado após auditoria e autorização válida. Este repo público não contém os tokens Meta.
