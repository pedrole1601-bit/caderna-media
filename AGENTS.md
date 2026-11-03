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
