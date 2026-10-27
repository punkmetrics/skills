# Atlas: conexão, comandos, formato e cross-check

O MCP e a CLI são clientes finos da mesma API `/v1`: o que um faz, o outro faz. Use o MCP quando ele estiver conectado na sessão e a tarefa pedir Atlas. Use a CLI em scripts e diffs.

## Conectar

**MCP (Claude Code):**

```bash
claude mcp add --transport http --scope user --header "Authorization: Bearer atlas_..." atlas https://api.punkmetrics.com/mcp
```

**CLI:**

```bash
npm install -g @punkmetrics/atlas-cli
```

Variáveis de ambiente (ou as flags `--api-url`, `--api-key`, `--org-id`):
- `ATLAS_API_URL=https://api.punkmetrics.com/v1`;
- `ATLAS_API_KEY=atlas_...`;
- `ATLAS_ORG_ID` (o `orgId` que o `atlas whoami` devolve).

Guarde as variáveis em `~/.atlas.env` com `chmod 600`. Nunca cole a chave em chat nem a comite.

Se `atlas --help` mostrar comandos do MongoDB, o executável é o do MongoDB Atlas CLI: rode `npx @punkmetrics/atlas-cli`.

**Escrita:** o `whoami` mostra `write` por domínio (`read`, `write`, `delete` ou `suspended`). Os erros mais comuns:

| Erro | Causa |
|---|---|
| `403 api_key_scope` | O admin não deu o escopo à chave |
| `402 plan_gate` | O domínio não foi liberado para a org |
| `400 invalid_body` + `details` | O campo e o motivo estão no `details` |

## Mapa de operações (MCP tool → CLI)

| O quê | MCP | CLI |
|---|---|---|
| Quem é a chave | `whoami` | `atlas whoami` |
| Produtos e jornadas | `list_products`, `list_journeys`, `get_journey_canvas` | `atlas journeys list <productId>`, `atlas journeys canvas <journeyId>` |
| Eventos | `list_events`, `get_event` | `atlas events list <workspaceId>`, `atlas events get <eventId>` |
| Catálogo de props | `list_properties` | `atlas properties list` |
| Regra de nomes | `get_naming_rule`, `set_naming_rule` | `atlas naming-rule get\|set <workspaceId>` |
| Contrato de dados | `get_data_contract`, `generate_data_contract` | `atlas events generate-data-contract --workspace-id <ws>` |
| Criar evento | `create_event` | `atlas events create-event --workspace-id <ws> --name … --description … --kind general --significance normal --product-id <id>` |
| Editar e apagar evento | `update_event`, `delete_event` | `atlas events update-event --event <id> --description …` |
| Props do evento | `add_event_property`, `remove_event_property` | `atlas events add-event-property --event <id> --name journey_id --type string --required true` |
| Ligar à tela | `attach_event` (`nodeId`, `hotspotId?`), `detach_event` | `atlas events attach-event --event <id> --node-id <nodeId> --hotspot-id <id>` |
| Ligar ao analytics | `create_event_binding`, `delete_event_binding`, `get_journey_bindings` | `atlas events create-event-binding --event <id> --analytics-target-id … --external-name <nome que chega no destino; no GA4, o traduzido, como purchase>`, `atlas journeys bindings <journeyId>` |
| Trazer o que a fonte já recebe | `import_product_events`, `import_journey_events` | `atlas events import-product-events --product <id>` |
| Docs vinculados e Drive | `list_google_drive_connections`, `add_context_doc`, `list_context_docs` | `atlas context-docs connections`, `atlas context-docs add <url>`, `atlas context-docs list` |
| Alvos de analytics | `list_integration_targets` | `atlas integrations targets <integrationId>` |
| Tracking plan por planilha | `preview_tracking_plan`, `import_tracking_plan` (`names`, `productId`\|`journeyId`) | `atlas context-docs tracking-plan <docId> --workspace <ws>` (prévia); `--import --names a,b --product <id>` grava |
| Codegen | `generate_event_code` | `atlas events generate-event-code --event <id> --platform … --vendor …` |
| Saúde | `get_event_health`, `get_journey_health` | `atlas events health <eventId>`, `atlas journeys health <journeyId>` |

Os comandos de escrita da CLI têm o nome da tool em kebab-case e recebem **opções, não argumentos posicionais**. O campo do corpo vira flag (`--product-id`), o id vem em `--event` ou `--workspace-id`, e campo composto vem de `--file <json>` (a flag vence o arquivo). Leitura usa posicionais (`events list <workspaceId>`). A CLI é beta (0.x): confirme com `atlas events <comando> --help`.

## Limites do contrato

**Evento:**
- `name` com até 160 caracteres;
- `description` com até 2000;
- `context` com até 2000;
- `kind`: `screenview` ou `general`;
- `significance`: `conversion` ou `normal`;
- escopo `productId` **ou** `journeyId`, nunca os dois.

**Propriedade:**
- `name` com até 120 caracteres;
- `type` com até 40 (padrão `string`);
- `required`;
- `allowedValues`.

## Formato do tracking plan (CSV/planilha)

O cabeçalho é detectado em EN, PT ou ES. Uma linha por evento:

```csv
"Event","Description","Context","Type","Conversion","Parameters"
"checkout_cancelled","Pessoa voltou do checkout da Stripe sem pagar…","P1 · web · account","general","no","plan_kind: string
entry_point: ""landing"" | ""upgrade_dialog"""
```

- **Description:** o JSDoc do catálogo, uma linha.
- **Context:** `P · superfície · área`.
- **Type:** `screenview` para o page view e `general` para o resto.
- **Conversion:** `yes` nos eventos marcados como conversão no plano.
- **Parameters:** `nome: tipo` por linha. Enum entre aspas, `(opcional)` para prop opcional.

Gere o arquivo do catálogo com um script (`analytics:export`) e trave-o com um teste que reprova CSV desatualizado.

Antes de importar, confira o arquivo com o parser de verdade do import: N eventos, 6 colunas e **0 descartados**.

## Cross-check (código ↔ export ↔ Atlas)

**1. Baixar o estado do Atlas.** O `events get` traz as `properties` e os `attachments` de cada evento.

```bash
# os eventos com nome no catálogo (de qualquer escopo do workspace) e os do produto que o catálogo não tem
atlas events list "$WS" | jq -r --arg p "$PRODUCT" --slurpfile c catalog.json \
  '($c[0] | map(.name)) as $n | .[] | select((.name as $x | $n | index($x)) or .productId == $p) | .id' \
  | while read -r id; do atlas events get "$id"; done | jq -s . > atlas-events.json
```

**2. Comparar com o catálogo exportado:**

```js
// node cross-check.mjs catalog.json atlas-events.json
// catalog.json: [{ name, description, context, kind, significance, params: [{ name, type, required }] }]
import { readFileSync } from "node:fs";
const [catalog, atlas] = process.argv.slice(2).map((p) => JSON.parse(readFileSync(p, "utf8")));
const byName = new Map(atlas.map((e) => [e.name, e]));
const rows = [];
const diff = (name, field, want, got) => { if ((want ?? null) !== (got ?? null)) rows.push([name, field, String(want), String(got)]); };
for (const ev of catalog) {
  const a = byName.get(ev.name);
  if (!a) { rows.push([ev.name, "evento", "existe", "faltando"]); continue; }
  for (const field of ["description", "context", "kind", "significance"]) diff(ev.name, field, ev[field], a[field]);
  const props = new Map((a.properties ?? []).map((p) => [p.name, p]));
  for (const p of ev.params) {
    const q = props.get(p.name);
    if (!q) { rows.push([ev.name, `prop ${p.name}`, p.type, "faltando"]); continue; }
    diff(ev.name, `prop ${p.name}.type`, p.type, q.type);
    diff(ev.name, `prop ${p.name}.required`, Boolean(p.required), Boolean(q.required));
    props.delete(p.name);
  }
  for (const extra of props.keys()) rows.push([ev.name, `prop ${extra}`, "—", "sobrando"]);
  byName.delete(ev.name);
}
for (const name of byName.keys()) rows.push([name, "evento", "—", "só no Atlas"]);
console.table(rows);
process.exit(rows.length ? 1 : 0);
```

Compare pelo nome. Isso só vale depois de confirmar que a regra de nomes não reescreveu nenhum: se reescreveu, resolva antes. O filtro pega os nomes do catálogo em qualquer escopo (o nome é único no workspace) e os eventos do produto que sobraram fora do catálogo. O formato da saída pode mudar na 0.x: confira uma chamada antes de rodar.

**O import de tracking plan grava toda prop como `type: "string"` e `required: false`**: o tipo da coluna Parameters não chega ao Atlas. Depois de um import, o cross-check acusa tipo e obrigatoriedade em todas as props. Decida com o usuário:
- se o tipo importa, corrija com `add_event_property --type … --required …` (remova a antiga antes, com OK);
- se não importa, compare só os nomes das props (tire as duas linhas `diff` de `.type` e `.required`).

## Escrita fora das portas públicas (último recurso, só para quem opera o Atlas)

Use só se nenhuma tool ou comando cobrir o caso, e com o OK do usuário para gravar em produção:

1. **Mesmo caminho da rota.** Faça o parse com o schema do contrato, crie com a mesma função da API (ela aplica a regra de nomes e a checagem de identidade) e grave a auditoria.
2. **Transação.** Tudo numa transação só; `DRY=1` faz rollback e imprime o que faria.
3. **Escopo.** Só a org e o produto do pedido; nunca uma org de cliente. O ator é um membro real da org.
4. **Releitura.** Releia e refaça o cross-check.
