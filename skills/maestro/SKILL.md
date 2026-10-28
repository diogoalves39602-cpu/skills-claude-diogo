---
name: maestro
description: Roteador de skills. Use quando o usuário invocar /maestro, ou quando pedir "escolha a skill certa", "qual skill usar", "use a melhor skill para isso". Analisa a tarefa, escolhe entre todas as skills instaladas a mais adequada (ou uma sequência curta delas), avisa qual escolheu e por quê, e executa a tarefa com ela.
---

# Maestro: escolher a skill certa

O usuário tem muitas skills instaladas e não quer decidir qual usar. Seu trabalho é decidir por ele e seguir com a tarefa.

## Como proceder

1. **Entenda a tarefa** que veio junto com `/maestro` (ou na mensagem anterior). Se não veio nenhuma tarefa, pergunte em uma frase o que ele quer fazer.
2. **Consulte a lista real de skills disponíveis** nesta sessão (a lista de skills que o harness mostra no contexto). Ela é a fonte da verdade: skills podem ter sido instaladas ou removidas desde que este arquivo foi escrito. Nunca invente nomes.
3. **Escolha** pelo encaixe com a descrição de cada skill:
   - Prefira **uma** skill. Use uma sequência (no máximo 3) só quando a tarefa tem fases claramente distintas, por exemplo planejar → implementar → revisar.
   - Em caso de empate, use a tabela de preferências abaixo.
   - Se nenhuma skill encaixa bem, diga isso e faça a tarefa diretamente. Não force uma skill.
   - Se parece existir uma skill pública melhor que não está instalada, sugira usar `find-skills` para procurá-la, mas só instale se o usuário aprovar.
4. **Avise em uma linha**, em português, antes de começar: `Vou usar <skill> porque <motivo curto>.` Se for uma sequência, liste a ordem.
5. **Invoque a skill** com a ferramenta Skill e siga as instruções dela até terminar a tarefa. Não pare para pedir confirmação da escolha, a menos que a tarefa seja ambígua de verdade.

## Preferências quando várias skills se sobrepõem

| Tipo de tarefa | Preferir | Alternativas |
|---|---|---|
| Navegar em sites, preencher formulários, prints | navegador embutido (`anthropic-skills:built-in-browser`) | `ego-browser` quando precisar das sessões já logadas do usuário; `anthropic-skills:chrome-browser` quando ele pedir o Chrome |
| Testes automatizados de páginas web, Playwright | `playwright-cli` | `agent-skills:browser-testing-with-devtools` |
| Revisar código antes de merge | `code-review` | `agent-skills:review` (cinco eixos), `engineering:code-review` |
| Auditoria de segurança completa | `security-audit` | `security-review` para revisar só o diff atual |
| Corrigir bug ou erro | `engineering:debug` | `agent-skills:debugging-and-error-recovery` |
| Começar um projeto ou funcionalidade nova | `agent-skills:spec` → `agent-skills:plan` → `agent-skills:build` | `product-management:write-spec` quando for um documento de produto, não código |
| Testes (TDD) | `agent-skills:test` | `engineering:testing-strategy` para planejar a estratégia |
| Simplificar ou limpar código | `simplify` | `agent-skills:code-simplify` |
| Engenharia reversa de apps, binários, sites | `reverse-engineer-anything` | `universal-modder:reverse-engineering` quando o alvo for um jogo |
| Modificar jogos de PC | `universal-modder:mod-any-game` | as outras skills `universal-modder:*` para fases específicas |
| Texto que soa como IA, revisar copy | `slopmonster` | `design:ux-copy` para textos de interface |
| A resposta anterior ficou ruim | `arena-skill:arena` (use `--quick` por padrão, é bem mais barato) | |
| Documentos Word, planilhas, PDF, apresentações | `anthropic-skills:docx`, `anthropic-skills:xlsx`, `anthropic-skills:pdf`, `anthropic-skills:pptx` | |
| Gráficos e dashboards | `dataviz` | |
| SEO | `searchfit-seo:seo-audit` | as outras skills `searchfit-seo:*` e `marketing:seo-audit` |
| Pesquisa aprofundada na web | `anthropic-skills:deep-research` | |
| Contas fixas da J&T no TOTVS | `anthropic-skills:lancar-despesa-totvs-jt` | |
| Criar ou melhorar uma skill | `anthropic-skills:skill-creator` | |
| Procurar uma skill nova para instalar | `find-skills` | |

## Regras

- Responda sempre em português.
- A linha de aviso deve ser curta. Não liste as skills que você descartou, a menos que o usuário pergunte.
- Se uma skill escolhida depende de algo que não está configurado (uma chave de API, um app, um login), avise e proponha a melhor alternativa disponível.
