---
name: punkmetrics-tracking-implementation
description: Use when implementing an approved tracking plan or event catalog in code, adding or fixing analytics events, writing tests for events, or loading, updating or reading events, descriptions and properties in Atlas (PunkMetrics) through its MCP, CLI or API — including attaching events to journey screens and cross-checking that code, plan and Atlas agree.
---

# Implementar o tracking e sincronizar com o Atlas (método PunkMetrics)

## Visão geral

**Uma fonte, três espelhos.** O catálogo no código, com tipo e JSDoc, é a fonte. O export (CSV/JSON), o Atlas e a documentação são espelhos gerados dele, e um cross-check prova que os quatro concordam.

Nada é dado como pronto sem quatro provas:
- um teste com o payload real;
- esse mesmo teste reprovando no código antigo;
- o evento visto no destino console;
- se o catálogo vive no Atlas, o diff com ele vazio.

**REQUIRED BACKGROUND:** as convenções e a arquitetura do core estão no skill `punkmetrics-tracking-plan`. Sem plano aprovado, comece por ele.

## Pré-voo

1. Leia o plano e o catálogo. Localize o core, os testes de varredura e o comando de export.
2. Rode `git status` e confira a branch. Siga as regras do repo para branch, PR e commit. Na dúvida, trabalhe na branch atual e peça antes de criar outra.
3. Rode `atlas whoami` (ou a tool `whoami` no MCP). Veja se a chave pode **escrever** no domínio `taxonomy`. Uma chave nasce só lendo: o domínio é liberado pela PunkMetrics e o escopo é dado pelo admin da org.
4. **O Atlas guarda o catálogo do workspace em produção**, onde o time lê e onde a saúde das jornadas é calculada. Ler é livre. Toda escrita pede o OK do usuário, por etapa: mostre antes o que vai ser criado ou alterado.

## Ordem de implementação

1. **Fase A, fundação.** Core e destinos, migração dos eventos existentes com aliases, `page_viewed` no router, testes de varredura e gating por ambiente. Nenhum evento novo entra antes disso.
2. **Fase B, P0.** Cada P0 vem com o refactor de ponto único que ele pede: a mutação sobe para um lib compartilhado e recebe `source`. Os P0 de servidor entram aqui também, como a receita pelo webhook.
3. **Fase C, P1**, módulo a módulo.
4. **Fase D, P2** sob demanda, e o resto dos eventos do servidor.

## Cada evento, do mesmo jeito

1. **Entrada no catálogo.** `nome: event<Props>("P1")`, com o JSDoc dizendo o que aconteceu, quando dispara (e quando não) e a nuance de leitura.
2. **Um `track` só**, depois do `await` de sucesso, dentro da função de mutação.
3. **Falha**, quando é métrica de produto, em evento próprio `*_failed{error_kind}` com enum.
4. **Contexto certo no disparo.** Página fora do shell declara a org antes de rastrear.
5. **Contagem única.** Pense em reload, voltar, remount, reenvio, reabrir link e sair e entrar. Use um id da transação (`session_id`) ou uma marca "uma vez por navegador" (`claimOnce(key, id)` no `localStorage`, com fallback em memória).
   - A trava do cliente não cobre outro aparelho nem storage limpo. Quando a contagem exata importa (receita), a fonte é o evento do servidor, e o do web é confirmação de tela.
   - Corrigir a contagem não muda o significado, então o nome fica. Registre a data da correção no plano e na documentação: o dado de antes dela tem a armadilha antiga.

## Testes que provam

- **Payload real.** Renderize a tela de verdade, faça o clique de verdade e mocke a API com a resposta real. Confira que o evento saiu **uma vez** e com as props. Teste que "arruma" o payload não cobre nada.
- **Reprova no código antigo.** Faça uma cópia do arquivo corrigido, volte a versão anterior (`cp <arquivo> /tmp/novo && git show HEAD:<arquivo> > <arquivo>`), rode o teste e devolva a cópia (`cp /tmp/novo <arquivo>`). Teste novo que passa nas duas versões não testa a correção.
- **Contagem única.** Desmonte e monte de novo, recarregue com o mesmo id, saia e entre, e confira que não houve segundo evento.
- **Varredura e privacidade** verdes. Se o export ficou desatualizado, regenere-o com o comando do repo. O export gera o CSV (import e docs) e o JSON (cross-check).
- **Navegador:** suba o app com o destino console (`VITE_ANALYTICS_DEBUG=true`, em mocks) e confira a linha `[analytics] track <evento> {…}`, com `org_id` e as props. Confirme pelo console e pela URL, não pelo print.
- **Banco:** teste que toca um banco de produção não roda local, fica para o CI. Os testes rodam só num tenant de teste, nunca num de cliente.
- **Em escala** (centenas de eventos):
  - todo evento tem um teste de disparo, agrupado por tela, e passa na varredura;
  - "reprova no código antigo" é obrigatório em toda correção e em todo refactor de evento que já existia;
  - no navegador, confira todos os P0 e uma amostra por módulo.

## Atlas: ler, escrever, conferir

A configuração do MCP e da CLI, os comandos, o formato do CSV e o script de cross-check estão em `reference/atlas.md`.

**1. Ler antes de escrever:**
- `list_products` e `list_journeys`, para achar o produto **pelo id ou pelo slug**. Nunca crie um produto que já existe.
- `list_events` (`atlas events list <ws>`) e `get_event`, para os eventos e as propriedades atuais.
- `get_naming_rule`. A regra pode reescrever nomes na criação: confira o nome que voltou.

**Como o Atlas identifica e escopa um evento:**
- **Identidade:** o nome é único **no workspace**. Um nome que já existe em outro produto do mesmo workspace conta como existente: o import o pula e o `create_event` devolve o existente. Um catálogo por workspace.
- **Escopo:**
  - sem produto nem jornada, o evento vale em qualquer jornada da org;
  - com `productId`, vale nas jornadas daquele produto;
  - com `journeyId`, só naquela jornada.

  Um `attach_event` fora do escopo dá `409 event_out_of_scope`. Evento ligado a telas de várias jornadas do produto leva `productId`.
- **Onde fica cada dado:**
  - a prioridade e a área ficam no `context` (`P1 · web · journey`);
  - a conversão fica em `significance`;
  - o `update_event` edita `description`, `context`, `kind`, `significance` e o escopo;
  - o `status` não muda pela API.
- **Regra de nomes:** antes de gravar, passe os nomes do catálogo pela regra (o preview mostra o nome final). Se ela reescreveria algum, **pare** e decida com o usuário entre ajustar a regra (`set_naming_rule`) e ajustar o catálogo. Nome divergente quebra o cross-check e o binding.
- **Registre o que está implementado.** Um evento planejado e ainda sem `track` aparece como quebrado na saúde da jornada. Se o usuário quiser o catálogo inteiro mesmo assim, prefixe a descrição com "Planejado (sem disparo ainda):" e avise. O cross-check vai acusar a diferença até o evento ser implementado, de propósito.

**2. Diff:** monte a lista de eventos novos, iguais e existentes-mas-diferentes. Compare descrição, `context`, `kind`, `significance` e as props (nome, tipo, obrigatória, valores). Mostre o resumo ao usuário e peça o OK.

**3. Escrever pelo caminho certo:**
- **Lote novo:** o import lê uma **Google Sheet** vinculada em Docs & Context, e a org precisa de conexão com o Google Drive (`list_google_drive_connections`).
  1. Peça ao usuário para subir o CSV como planilha, ou use o conector do Drive se a tarefa autorizar.
  2. Vincule com `add_context_doc` (`atlas context-docs add <url>`). O `docId` vem no retorno ou em `list_context_docs`.
  3. Rode `preview_tracking_plan` e depois `import_tracking_plan`, com `names` e `productId` ou `journeyId`.

  O import **pula o evento que já existe** no workspace e grava toda prop como `string`, não obrigatória. O tipo real só chega com `add_event_property --type`.
- **Existentes-mas-diferentes:** `update_event` para a descrição, o `context`, o kind e a conversão. Para as props, `add_event_property` / `remove_event_property`. O import não atualiza nada.
  - Antes de remover uma prop, veja se um binding, o contrato de dados ou o codegen usa ela (`get_journey_bindings`, `get_data_contract`).
  - **Renomear prop:** adicione a nova antes de tirar a antiga.
  - **Trocar o tipo** da mesma prop: remova e adicione de novo com o tipo certo, porque o nome é o mesmo.
- **Descontinuar:** a API não muda o `status`. Prefixe a descrição com "Descontinuado até <data>: use `novo_nome`". Apague com `delete_event`, com OK, depois do prazo do alias.
- **Mapa vivo:**
  - `get_journey_canvas` lista as telas (nós) e os hotspots. Case cada evento com a tela pelo nome da tela e pela rota, junto com o usuário. Tela que não está no canvas vai para um relatório; não crie nó sem pedir. Evento de servidor não tem tela.
  - `attach_event` liga o evento à tela (`nodeId`) e ao hotspot.
  - `create_event_binding` liga o evento ao alvo de analytics. Os ids dos alvos saem de `atlas integrations targets <integrationId>`. Faça binding só quando o pedido ou o plano incluir: sem binding o modo View não mostra métricas, mas binding errado mostra métrica errada.
  - Attach e binding são do domínio `taxonomy`. A escrita pela API é direta: se o cliente aprova mudanças de jornada por changeset, pergunte antes.
- **Escrita em volume:** as portas públicas não têm lote, dry-run nem rollback.
  1. Faça um piloto com 1 a 3 eventos e releia.
  2. Depois rode um script que chama a CLI em sequência, grava cada id criado num arquivo (a lista para desfazer) e para no primeiro erro.
- **Script direto no banco** (só para quem opera a plataforma Atlas): só se nenhuma porta pública servir, e pelo mesmo caminho da rota (schema → criação com a regra de nomes → auditoria). Rode numa transação, com dry-run que dá rollback.

**4. Conferir:** releia do Atlas e refaça o diff, que tem que vir **vazio**. Depois do deploy, `get_event_health` (24h/7d) mostra o que está definido e não chega.

## Quando o plano estiver errado

- Classifique como **bug** ou **desenho** (a revisão dos disparos está no skill de plano). Leve a lista ao usuário antes de corrigir.
- Não sobrecarregue um evento existente. Prefira um evento novo (`*_failed`, ou um `entry_point` novo) a mudar o que ele significa.
- A correção atualiza, juntos:
  - o código;
  - o JSDoc;
  - o export;
  - o plano ("Decisões");
  - o Atlas;
  - a documentação externa (skill `punkmetrics-tracking-docs`).

  Os passos que gravam fora do repo pedem OK.
- Evento já no Atlas não é renomeado no lugar: crie o novo e deprecie o antigo, com alias no destino.

## Antes de dizer "pronto"

- Rode o suite inteiro do pacote e o typecheck.
- Faça a revisão dos disparos (passo 6 do `punkmetrics-tracking-plan`) nos eventos novos e alterados.
- Confira o estado real do PR antes de falar dele: `gh pr view <n> --json state,headRefOid`. Um PR já mergeado não recebe commits novos, e eles precisam de outro PR.
- Relate o que **não** foi verificado: o fluxo real no provedor (Stripe), o CI e o deploy.

## Erros comuns

| Erro | Correção |
|---|---|
| Teste que só passa (não reprova no código antigo) | Reverter temporariamente e ver falhar |
| Contar no estado ("plano já é X") | Contar por id da transação |
| Recusa no evento de sucesso | `*_failed` separado |
| Criar no Atlas sem ler | Listar, achar pelo slug, diff e OK |
| Achar que o import atualiza a descrição | O import pula o existente; use `update_event` |
| Ignorar a regra de nomes | O nome gravado pode mudar; confira o retorno |
| Esquecer o `attach_event` e o binding | O mapa não mostra métrica sem eles |
| Afirmar o estado do PR de memória | `gh pr view --json state` |
