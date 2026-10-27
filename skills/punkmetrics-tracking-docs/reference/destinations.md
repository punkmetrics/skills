# Destinos: limites e como publicar

Os limites mudam. Confirme na documentação da ferramenta antes de um documento grande; a coluna "Fonte" diz de onde veio cada número.

| Destino | Limite que importa | Fonte | Como publicar |
|---|---|---|---|
| **Linear** (documento) | `content` com até **250.000 caracteres** por documento; a API recusa acima disso | Observado (erro da API) | MCP `save_document`: crie com o primeiro pedaço e anexe o resto com o patch `append` (até 50 operações por chamada). Para atualizar, use `replace` ou `replace_range` com âncoras que aparecem uma vez só |
| **Notion** | Por request: até 100 blocos por append, 2.000 caracteres por texto rico, até 1.000 blocos e 500 KB. Limite de página não documentado: meça em **blocos** (cada linha ou item vira um bloco), não em caracteres | Documentação da API | **Prefira um database**: uma linha por evento, com propriedades (prioridade, área, conversão, GA4) e a ficha no corpo. Atualizar um evento vira editar uma linha, e as contagens saem das views. Numa página única: converta o markdown em blocos (títulos até h3, tabela vira bloco `table`), anexe em lotes de 100 e quebre parágrafos com mais de 2.000 caracteres |
| **Confluence** | Sem limite firme documentado aqui; página muito grande fica lenta para editar | Verificar na instância | Formato storage (XHTML): converta o markdown ou use a macro de markdown. Uma página por área, mais a página índice, na mesma árvore |
| **Google Docs** | Até 1,02 milhão de caracteres por documento | Documentação do Google | Crie pelo Drive com conversão de HTML ou DOCX (preserva as tabelas). Atualize com `batchUpdate` por intervalo; o skill de Google Workspace tem os helpers de posição |
| **Markdown no repo** | Sem limite prático; um arquivo por área lê melhor | — | Gere com o script (`docs/events/<area>.md` mais o `index.md`) e trave com um teste que reprova o arquivo desatualizado |

## Regras que valem para qualquer destino

- **Partes:** divida por área. O título diz o escopo ("parte 1/2 (geral, conta, jornada)"), o cabeçalho de cada parte linka as outras, e a parte geral fica na 1.
- **Atualizar não é recriar.** Busque o conteúdo atual, confira cada âncora por script (`texto.count(ancora) == 1`), faça o patch e busque de novo.
- **Renomear muda o link** em algumas ferramentas (Linear inclui o título na URL): busque a URL nova e corrija as outras partes.
- **Mesmo documento sempre:** guarde id e URL das partes (no tracking, no README ou na memória do agente) e atualize esses documentos, sem criar outros.
- **Publicar fora do repo é ação externa.** Ela segue as regras do projeto: em geral é pedida pelo usuário, ou está coberta por uma instrução permanente como "espelhar os docs no Linear".
