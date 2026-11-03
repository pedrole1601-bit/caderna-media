# Auditoria de design — CADERNA Enem 2026 / edição 001 v0.7

**STATUS: DESIGN_QA_PASS_TECHNICAL_ONLY — aprovação estética do editor ainda pendente.**

## Diagnóstico da v0.6 rejeitada pelo proprietário em 03/11/2026
1. A manchete `PRIMEIRA PROVA / É NESTE / DOMINGO` tinha linhas arbitrariamente dimensionadas, borda esquerda percebida irregular e peso dominante distribuído por 3 blocos. **Severidade ALTA**.
2. A chamada principal, o numeral `08`, a data `NOVEMBRO`, os círculos azuis e a folha de respostas disputavam atenção. **Severidade MÉDIA**.
3. A ilustração antiga tinha artefatos decorativos que competiam com a informação e tocava a transição de cor. **Severidade MÉDIA**.
4. QA só impedia caixas colididas; **não validava hierarquia, ancoragem nem ritmo editorial. Severidade CRÍTICA de processo**.

## Solução v0.7
- Manchete reescrita de modo factual, em duas linhas: `ENEM COMEÇA` / `NESTE DOMINGO`. **Mesma família, mesmo corpo 126 px, mesma margem x=94 e gap real 40 px**. A peça tem um protagonista semântico.
- Numeral `08` informa data e pertence a outra zona, não ao texto principal.
- Ilustração rotulada `ILUSTRAÇÃO EDITORIAL` e reduzida a uma única área; retiradas grades e marcas arbitrárias.
- Preservados azul-profundo, papel, coral e **SVG original da marca**.
- Apoio sob manchete contém informação nova: local de prova já disponível no cartão.
- PNG 1080×1350, JPEG para hospedagem Meta e mobile 320×400.
- Um arquivo de QA registra medidas dos textos e nega `human_approved` ou `published_to_instagram` por padrão.

## Gate de aceite técnico (prova reprodutível)
- [x] Dimensão 1080×1350 e corte mobile 320×400.
- [x] 2 linhas da manchete, sem autoencaixe individual e corpo idêntico.
- [x] Alinhamento horizontal medido de âncoras <=3 px; margem mínima 88 px.
- [x] Gap visual mínimo de 36 px; medido 40 px neste modelo.
- [x] Detecção de texto vs texto em todos os blocos registrados.
- [x] Marca original; cor de base e laranja conferidos por pixels.
- [x] Exportações em formatos corretos para Instagram e leitura.
- [x] Testes regressivos para margem irregular, linha maior/menor e invasão vertical.
- [ ] Inspeção final do editor/proprietário da peça revisada — **pendente**.
- [ ] Teste real da URL HTTPS do Pages após deploy — **pendente até comprovação**.

## Regras semânticas
Material visual: ilustração original e não foto documental. Matéria: ENEM 2026, 08/11 e 15/11 segundo notas do INEP. Não tratar o cartão desenhado como documento oficial.

Fontes:
- https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-participantes-ja-podem-conferir-os-locais-de-prova/
- https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-confira-o-passo-a-passo-para-visualizar-o-local-de-prova/

## Limitações de QA automático
A checagem detecta métrica e limites geométricos, mas não pode provar sozinha que a composição é bonita, que a data será correta no dia da postagem ou que a tipografia agrada ao público. Por isso, **Ainda não publicado no Instagram**, nenhuma autorização foi alterada. DRAFT até o editor aprovar.

## Skills aplicadas como referências de processo
`social-media-graphic` (safe zone); `graphic-design` (foco); `design-critique` (olhar antes/depois); `collateral-design` (uso correto da marca); `creative-direction` (gramática editorial). Fontes e restrições documentadas em `.agents/skills/caderna-editorial-design/SKILL.md`.

## Revisão de contraste em 03/11/2026
- Crédito pequeno do rodapé na versão intermediária usava `#667487` sobre papel `#F5F3ED`: contraste calculado **4,29:1**, inferior a 4,5:1 para texto pequeno.
- Corrigido para `#5C6B7B`, contraste calculado **4,92:1**, acima do mínimo.
- O contrato `verify_design_qa.py` agora calcula luminância relativa conforme WCAG e rejeita valores abaixo de 4,5:1. Os testes provocam uma falha intencional com a cor antiga para impedir regressão.
- Esses cálculos não substituem inspeção perceptual da composição, especialmente em telas reais.
