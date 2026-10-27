---
name: punkmetrics-tracking-plan
description: Use when a product needs a tracking plan, event taxonomy, data contract or analytics architecture (plano de eventos, taxonomia, catálogo de eventos); when auditing which modules and user flows should emit events; when PostHog, Amplitude, GA/GTM, Segment or Mixpanel calls are scattered, duplicated or named differently per tool; when checking whether existing events count correctly; or before adding the first analytics events to a web, mobile, API or worker codebase.
---

# Plano de eventos e arquitetura de tracking (método PunkMetrics)

## Visão geral

**O catálogo tipado é a fonte da verdade, e um core único (o "middleware" de analytics) é a única porta para qualquer ferramenta.** Cada evento nasce de uma ação que o código de fato executa, tem um ponto só de disparo e sai depois do sucesso.

Um plano não é uma lista de ideias de eventos. É uma auditoria do produto, módulo a módulo, feita lendo o código.

**Quando NÃO usar este skill:**
- Para implementar um plano já aprovado, use `punkmetrics-tracking-implementation`.
- Para documentar o catálogo fora do código, use `punkmetrics-tracking-docs`.

## Passo 0: procurar o contrato que já existe

Antes de propor qualquer nome:

1. **No Atlas (PunkMetrics):**
   - pela CLI: `atlas whoami`, `atlas events list <workspaceId>`, `atlas naming-rule get <workspaceId>`;
   - pelo MCP: `list_events`, `get_naming_rule`, `get_data_contract`.

   A regra de nomes do workspace (idioma, caixa, separador) vence a convenção padrão deste skill.
2. **No repositório:** busque `capture(`, `.track(`, `logEvent(`, `dataLayer.push` e arquivos `tracking-plan*`, `events*.json`, `analytics*`.
3. **Fora do código:** planilha de tracking plan, Avo, Amplitude Data, Segment Protocols, Notion ou Confluence. Pergunte ao usuário onde o catálogo vive.

Se o catálogo existe, parta dele: renomeie só com motivo e com alias de transição. Se não existe, proponha o catálogo no código como fonte. Registrá-lo no Atlas é uma oferta, não um pré-requisito: cliente fora do Atlas segue o mesmo método.

**Quem vence quando as fontes discordam:**
1. o contrato que o cliente já governa (a regra de nomes do Atlas, a planilha oficial);
2. o nome que já sustenta painéis e históricos (veja as dependências no passo 1);
3. a convenção deste skill.

Entre dois nomes atuais para a mesma ação, o canônico é o que segue a convenção; o outro vira alias.

## Passo 1: estado atual

Monte a tabela `Destino | Onde carrega | Como dispara | Eventos`. Liste cada problema com o arquivo onde ele está:

- a mesma ação com dois nomes;
- a mesma ação em duas linhas de código (uma por SDK);
- propriedades diferentes por destino;
- destino carregado que não recebe nada;
- dado errado: evento antes do sucesso, valor fixo, login contado no link de recuperação;
- desenvolvimento, mocks ou testes mandando para o projeto de produção;
- módulos sem nenhum evento.

**Fora do código, antes de renomear qualquer coisa:**
- Liste o que depende dos nomes de hoje: insights, cohorts, flags e experimentos do PostHog, gráficos do Amplitude, triggers e tags do GTM, alertas.
- Peça os volumes reais dos últimos 30 a 90 dias (export ou acesso dado pelo usuário). O código diz o que deveria contar; o volume mostra o que conta.
- Audite o container do GTM: page view do GA4, triggers de clique e pixels de anúncio que já disparam sozinhos e talvez sem consentimento.
- Desligue o autocapture, que captura texto de elemento e pode trazer dado pessoal, e confira a máscara da gravação de sessão.

## Passo 2: auditoria por módulo (o coração do plano)

**De onde saem os módulos.** Liste-os pelo registro do próprio app (rotas, menu, módulos do assistente), não de memória. Inclua auth, shell e navegação, billing, admin, integrações e as superfícies anônimas (board público, widget, plugin).

**O que conta como ação.** São as **mutações**: funções que chamam a API e recebem 2xx (criar, editar, excluir, publicar, conectar, decidir), mais os marcos de funil (abriu, começou, concluiu). Um botão não é uma ação; a função de mutação é. Não limite o catálogo a um número: catalogue toda ação relevante e use a prioridade para dosar a implementação.

**Uma linha por ação:**

```
| Evento | P | Ponto único (arquivo + função) | Propriedades | Status (novo/renomear/corrigir) |
```

**Prioridade:**
- **P0**: ativação, receita e o valor central. Entra junto com o core.
- **P1**: funis de cada módulo.
- **P2**: detalhe de uso. Entra quando alguém tiver a pergunta que ele responde.

**Servidor.** O que o navegador não vê vira evento de servidor:
- webhook de pagamento (a receita de verdade);
- fim de jobs;
- uso da API pública, do MCP e da CLI (agregado em janelas);
- alertas do sistema;
- bots.

Não duplique o que já tem ledger próprio, como custo de IA ou faturamento: cruze pelo id no warehouse.

**App grande.** Use um subagente por grupo de módulos, todos com a mesma tabela e lendo o código, e consolide os resultados.

## Passo 3: convenções

**Nomes:**
- formato `objeto_acao_no_passado`: snake_case, em inglês, objeto no singular com o nome do domínio (não o da tela);
- verbos preferidos: created, added, updated, deleted, removed, archived, duplicated, moved, linked, connected, disconnected, imported, copied, generated, published, submitted, decided, started, completed, accepted, discarded, opened, viewed, invited, changed, failed;
- `*_updated` leva `fields: string[]` com os nomes dos campos alterados, nunca os valores;
- decisão é um evento só com o resultado: `changeset_decided{decision}`;
- toggle também: `x_archived{archived: true|false}`;
- mudança de status leva `from` e `to`;
- o nome sai literal no código, nunca escolhido por `if`, porque o teste de varredura precisa achá-lo.

**Propriedades:**
- só ids (`*_id`), enums (`source`, `kind`, `error_kind`), contagens (`*_count`), comprimentos (`*_length`) e booleanos (`is_*`, `has_*`);
- `source` ou `entry_point` quando a ação tem mais de uma porta de entrada;
- **nunca** texto digitado, e-mail, nome de pessoa ou de org, nem erro cru. De texto, só o comprimento.

**Contexto anexado a todo evento pelo core:** `user_id`, `org_id` (também como `group` da org), `org_kind` (`internal|customer`, para filtrar a própria empresa e a org de demo), `workspace_id`, `product_id`, o id da entidade em foco, `module`, `locale` e `app_version`. A prop do evento vence a da sessão.

**Page view:** recomendação, que entra nas decisões do usuário: um `page_viewed` central no router, com o **template** da rota (`/products/$id/canvas`), e o pageview automático dos SDKs desligado.

**Falha:** só vira evento onde a falha é métrica de produto (auth, checkout, publicação, integração, chat), como `*_failed{error_kind}` com um enum. A falha nunca sai no evento de sucesso.

**Salvamento otimista ou em tempo real** (editor, canvas multiplayer): o "sucesso" é a confirmação da persistência (o ack do servidor ou do canal realtime), não o gesto. Ação de alta frequência, como arrastar ou digitar, não vira evento.

**Limites do GA4** (o destino GTM tem que caber):
- nome do evento com até 40 caracteres;
- nome de parâmetro com até 40;
- valor com até 100;
- até 25 parâmetros por evento;
- array não existe, então o destino junta em string.

Parâmetro só aparece em relatório depois de virar dimensão personalizada.

## Passo 4: arquitetura do core

```
componente / função de mutação ─► track("evento", props)       (único import permitido)
lib/analytics/
  catalog/<area>.ts   nome → event<Props>("P0") + JSDoc (a descrição que vai para todo lugar)
  index.ts            track/page/identify/group/reset · contexto · nunca lança · fila até a decisão de consentimento
  context.ts          sessão ativa (user, org, org_kind, workspace, produto, entidade, módulo)
  destinations/       posthog · amplitude · gtm (mapa para nomes do GA4) · console (debug)
servidor: server-analytics   serverTrack só enfileira, nunca lança, envia em lote, respeita a flag da org
```

Regras do core. O código de referência e os detalhes estão em `reference/core-architecture.md`.

- **O componente não sabe quantos destinos existem.** Quem liga cada destino é a configuração.
- **Ambientes:** só o build de produção manda para os destinos reais. Dev, mocks e testes usam o destino console ou nenhum.
- **Consentimento e flag por org** cortam todos os destinos do web e o servidor. Os eventos esperam numa fila curta até a decisão chegar.
- **Nomes por destino:** o nome canônico é um só. O destino GTM traduz para os eventos recomendados do GA4 (`sign_up`, `login`, `begin_checkout`, `purchase`, `page_view`).
- **Migração:** o nome antigo sai **junto** do canônico, só no destino que o tinha, até uma data. Nesse período a ferramenta tem as duas linhas: um painel usa uma ou outra, nunca a soma. Se a ferramenta junta nomes sozinha (transformações do Amplitude, actions do PostHog), prefira isso ao alias.
- **Recursos do SDK além do tracking** (feature flags, surveys, gravação de sessão) também passam pelo core, com wrappers tipados. Se não passarem, ficam numa lista de exceções explícita no teste de varredura.
- **Identidade:**
  - o mesmo `user_id` em todas as ferramentas;
  - `identify` no login, `reset` no logout;
  - o anônimo é juntado pelo próprio SDK.

  O `group` da org pode ser add-on pago na ferramenta; sem ele, o `org_id` como prop continua servindo.
- **`org_kind` e a flag por org** saem do modelo do cliente: uma coluna no tenant, ou uma lista de ids internos na configuração. Os eventos de servidor vão para as ferramentas de produto; as de pessoa (Amplitude) só recebem eventos com usuário.
- **Consentimento:** a fila do core respeita a ferramenta de consentimento do cliente (CMP) e o Google Consent Mode v2. LGPD/GDPR e a região de hospedagem dos dados (EU/US) entram nas decisões.
- **MCP e CLI** não mandam telemetria da máquina do cliente. Eles mandam cabeçalhos (`x-<app>-client`, `-tool`, `-command`), e a API conta.

**Onde o `track` mora:**
- dentro da função de mutação compartilhada, depois do `await` de sucesso;
- se a mutação está inline no componente, no handler;
- se surgir uma segunda porta, a mutação sobe para um lib antes de ganhar o segundo `track`.

## Passo 5: garantias por teste de varredura

Os testes leem o fonte e reprovam quando:

1. existe SDK fora do core;
2. um evento do catálogo não tem exatamente **um** `track` no código;
3. um `track` usa um nome que não está no catálogo, ou o mesmo nome aparece em dois arquivos (web e servidor);
4. há um nome fora do snake_case;
5. o catálogo tem prop de dado pessoal ou de texto livre;
6. o export do catálogo está desatualizado. O export gera o CSV no formato do tracking plan do Atlas (import e docs) e o JSON com `kind`, `significance` e o tipo das props (cross-check).

A Definition of Done de uma feature inclui o evento no catálogo, com um teste que dispara o `track` usando o payload real que o cliente envia.

## Passo 6: revisão dos disparos

Depois de desenhar, e de novo depois de implementar, leia o ponto de disparo de cada evento. Classifique cada problema em:
- conta a mais;
- conta a menos;
- prop que não varia;
- leitura que confunde.

Para cada problema, dê o veredito **bug** ou **desenho**. O roteiro e as armadilhas recorrentes estão em `reference/firing-point-review.md`. Leve a lista ao usuário antes de corrigir.

## Entregável

Use o documento do plano em `reference/plan-template.md`. Ele tem: estado atual, arquitetura, convenções, catálogo por módulo, servidor, roteiro em fases e decisões em aberto.

Termine com as **decisões que são do usuário**, com recomendação. Por exemplo:
- pageview automático ou central;
- prazo dos aliases;
- quais destinos manter;
- flag por org;
- consentimento e região;
- se o catálogo vai para o Atlas.

**Em consultoria**, quem decide é o dono do dado do cliente, e o pedido diz qual é. O plano é escrito no idioma do time do cliente. Ele vai para o repo do cliente só se pediram; senão, é entregue como documento (skill `punkmetrics-tracking-docs`).

## Erros comuns

| Erro | Correção |
|---|---|
| Inventar eventos a partir de "KPIs" sem ler o código | Partir das funções de mutação de cada módulo |
| Disparar no clique ("tentou") | Disparar depois do 2xx; a falha é `*_failed` |
| Um `track` por botão | Um `track` na mutação compartilhada, com `source` |
| Mandar o mesmo evento para dois SDKs no componente | O core faz o fan-out |
| Dev e testes no projeto de produção | Gating por ambiente no core |
| Sem `org_kind` | A empresa e a org de demo poluem todo funil |
| Ignorar a regra de nomes do Atlas ou o catálogo existente | Passo 0 antes de tudo |
| Plano sem revisão dos disparos | Passo 6: é ele que acha o que conta errado |
