> **VERSÃO ATIVA: v0.7, 03/11/2026.** A v0.6 do Enem foi rejeitada por hierarquia visual insuficiente. **Nunca** usar `caderna-enem-2026-001.jpg` da v0.6 em publicações. A arte atual é [`caderna-enem-2026-001-v2.jpg`](media/caderna-enem-2026-001-v2.jpg). O Pages está ativo e a mídia JPEG foi verificada por HTTP 200 e igualdade binária no [GitHub Actions](https://github.com/pedrole1601-bit/caderna-media/actions/runs/41697279205). Nada publicado no Instagram.

# CADERNA · Acervo público de mídia

Este repositório **público** hospeda exclusivamente ativos editoriais da [CADERNA](https://github.com/pedrole1601-bit/Caderna) destinados a uso público. O código de autenticação da Meta, fontes internas e tokens continuam no repositório privado.

## Primeira arte — edição 001
- Pauta: **Enem 2026 começa no domingo, 8 de novembro**.
- Data da produção: 03/11/2026.
- Origem dos fatos: Inep, notícias de 27 e 28/10/2026.
- Arte: ilustração editorial original, sem fotografia de terceiros.
- Estado: **PRÉVIA EDITORIAL. NÃO PUBLICADA NO INSTAGRAM.** A aprovação de publicação é uma etapa separada.
- Exportação: `media/caderna-enem-2026-001-v2.jpg` (JPEG), `media/caderna-enem-2026-001-v2.png` (PNG).

## Infraestrutura
GitHub Pages via `.github/workflows/pages.yml`. Ative em **Settings → Pages → Source: GitHub Actions** se a interface exigir. Não use esta pasta para credenciais, documentos não publicados ou material protegido sem licença.

A geração da primeira peça é reproduzível com `scripts/render_enem_001.py`. O fluxo de exportação é gratuito e roda em GitHub Actions. O resultado público do arquivo não é autorização de postagem no Instagram.

## Fonte
- [Inep — locais de prova já disponíveis](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-participantes-ja-podem-conferir-os-locais-de-prova/)
- [Inep — passo a passo do cartão](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-confira-o-passo-a-passo-para-visualizar-o-local-de-prova/)

## Skills e controles de design
A skill interna mandatória está em [.agents/skills/caderna-editorial-design/SKILL.md](.agents/skills/caderna-editorial-design/SKILL.md); a direção visual está em [.agents/design-context.md](.agents/design-context.md); a crítica da versão rejeitada e a solução está em [docs/CRITICA-EDITORIAL-001-v07.md](docs/CRITICA-EDITORIAL-001-v07.md). O pipeline rejeita headline com tamanhos diferentes, âncoras divergentes ou interlinha insuficiente, valida mobile, marca vetorial, cores, JPEG, URLs públicas e não pode conceder aprovação editorial. O [AGENTS.md](AGENTS.md) torna essas regras obrigatórias aos futuros agentes.

O [acervo público no GitHub Pages](https://pedrole1601-bit.github.io/caderna-media/) é apenas hospedagem de arquivos. Publicação no Instagram é um processo separado e ainda não aprovado.


## Famílias editoriais dinâmicas
- **Uma imagem (manchete)** e **carrossel/explicador de 4 quadros**, ambos em temas `ink` e `cream`, são renderizados por [`scripts/render_editorial.py`](scripts/render_editorial.py) sem custo de modelo de imagem.
- Entradas: [`incoming/`](incoming/). O desenho rejeita título fora da área, fontes indisponíveis, colidências de texto, imagens ruins e pautas de risco elevado. Outputs: `media/auto/<slug>-01.jpg` a `-04.jpg`, PNGs, miniaturas e `<slug>-qa.json` com checksums de cada JPEG.
- Workflow: [`.github/workflows/editorial-pages.yml`](.github/workflows/editorial-pages.yml). O pipeline faz deploy e checa HTTP 200 + igualdade binária de cada mídia. **A publicação no Instagram nunca ocorre neste repositório**.
- Primeira amostra: [`incoming/2026-11-03-enem-carrossel-teste.json`](incoming/2026-11-03-enem-carrossel-teste.json), rotulada **exemplo não publicável**. A capa ENEM original já publicada continua em `media/caderna-enem-2026-001-v2.jpg`.
- Guia de Voz é obrigatório no [repo privado Caderna](https://github.com/pedrole1601-bit/Caderna/blob/main/.agents/skills/caderna-guia-de-voz/SKILL.md); o PDF original foi enviado pelo proprietário e não foi disponibilizado neste repositório público.
