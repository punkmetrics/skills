# Revisão dos disparos ("armadilhas conhecidas")

Rode esta revisão em dois momentos:
- quando o plano fica pronto;
- quando a implementação termina.

O plano diz o que o evento deveria contar. Só a leitura do disparo diz o que ele conta de verdade.

## Roteiro

Para cada evento, abra o ponto de disparo e responda:

1. **Quem dispara e quando?** Usuário ou sistema, qual tela, qual condição, e o que **não** dispara.
2. **Pode contar a mais?** Reload, botão voltar, remount (StrictMode em dev), retry, reenvio de webhook, sair e entrar de novo, reabrir o mesmo link, recarga de lista, recusa contada como sucesso.
3. **Pode contar a menos?** Outra porta de entrada sem o `track`, URL de retorno sem marca, timeout que desiste, ação que roda no servidor e não passa pelo web, evento que depende de algo que só às vezes acontece.
4. **As props variam?** Uma prop que é sempre `true`, ou um valor do enum que o código nunca manda, não serve para segmentar.
5. **O contexto está certo?** `org_id`, `org_kind` e a entidade em foco no momento do disparo, inclusive nas páginas fora do shell.
6. **A leitura engana?** Nome que promete mais do que mede, ou um mesmo evento saindo de módulos diferentes.

Para app grande, rode um subagente por área. Todos usam o **mesmo schema da ficha de documentação** (`punkmetrics-tracking-docs/reference/event-entry.md`), com o campo `issues` preenchido. A mesma leitura serve à revisão e à doc.

## Veredito por item

| Veredito | Quando | O que fazer |
|---|---|---|
| **Bug** | O evento conta algo diferente do que o nome e o JSDoc prometem, sem querer | Corrigir no código, com teste que reprova no código antigo |
| **Desenho** | A escolha foi deliberada e tem motivo (limite do polling, fonte da receita no servidor) | Documentar a leitura correta; não mexer |
| **Desenho que engana** | Foi deliberado, mas o nome ou o padrão do catálogo contradiz | Propor um evento separado (`*_failed`) em vez de sobrecarregar |

Entregue a lista ao usuário **antes** de corrigir, separada em bug e desenho, com o arquivo de cada item.

## Armadilhas recorrentes e a correção

| Armadilha | Correção |
|---|---|
| Cadastro OAuth decidido por "conta criada há menos de N min": sair e entrar na janela conta de novo | Contar uma vez por conta (marca no navegador, ou o servidor decidir na criação). `last_sign_in_at` do Supabase/GoTrue é regravado a cada login e não serve |
| Página de sucesso que confirma pelo estado ("plano já é X"): reload ou voltar conta de novo, e a URL adivinhada também conta | Uma vez por id da transação (`session_id` do checkout); sem id, não conta |
| Cancelamento medido só numa porta: a outra porta volta para a página de origem sem marca | Marca na URL de volta (`?checkout_canceled=<plano>`), tirada da URL no boot antes do router, e o evento sai com `entry_point` |
| Recusa da API saindo no evento de sucesso com `error_kind` | Evento separado `*_failed{error_kind}`; o de sucesso só com a ação feita |
| Página fora do shell sem org no contexto | Declarar a org (hook de escopo) antes de rastrear |
| Busca com debounce rastreada de novo quando a lista recarrega | Rastrear só quando a consulta muda, não quando os dados mudam |
| Contagem somando duas listas que mostram o mesmo item | Contar ids únicos |
| Evento de "gerado automaticamente" a cada abertura da aba | Desenho, se a prop separa (`trigger=auto_open`); documentar o filtro |
| Rename que dispara sem mudança de nome | Comparar com o valor anterior antes do `track` |
| Webhook que só conta no tipo `deleted`, quando o status já tinha mudado num `updated` | Contar pela transição de estado, não pelo tipo do webhook |
| Autosave por tecla | Um evento por salvamento confirmado |
| Evento no mount de um filho, antes do pai declarar o contexto | Disparar do componente que declara o contexto, depois dele |
