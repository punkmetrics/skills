# Core de analytics: código de referência

A implementação de referência é a do Atlas, produto da PunkMetrics. O código dele não é aberto, mas os trechos abaixo bastam para reproduzir o padrão em qualquer projeto. A estrutura é esta:
- web: `lib/analytics/`;
- servidor: um pacote `server-analytics`;
- testes: um teste de cobertura do catálogo.

Os trechos abaixo são o padrão que este skill recomenda. Adapte a stack, mas mantenha as regras.

## 1. Entrada do catálogo

O tipo vive no genérico e a prioridade em runtime, para o teste listar o catálogo sem ler o fonte. O JSDoc é a descrição oficial do evento: ele vai para o CSV de import, para o Atlas e para a documentação.

```ts
// catalog/define.ts
export type PropValue = string | number | boolean | null | readonly string[]; // nunca objeto livre
export type EventProps = { readonly [key: string]: PropValue | undefined };
export type Priority = "P0" | "P1" | "P2";
export type EventSpec<P extends EventProps> = { readonly priority: Priority; readonly __props?: P };
export function event<P extends EventProps = Record<never, never>>(priority: Priority): EventSpec<P> {
  return { priority };
}

// catalog/journey.ts: um arquivo por área, para cada frente editar só o seu
export const JOURNEY_EVENTS = {
  /**
   * Jornada excluída, depois que a API confirma. Recusa e erro não contam aqui: saem em `journey_delete_failed`.
   */
  journey_deleted: event<{ journey_id: string }>("P1"),
  /** Exclusão de jornada falhou. `error_kind` = `has_children` quando a hierarquia trava a exclusão. */
  journey_delete_failed: event<{ journey_id: string; error_kind: "has_children" | "other" }>("P2"),
};
```

O JSDoc responde três perguntas: **o que aconteceu**, **quando dispara** (e quando não) e **a nuance de leitura**.

## 2. `track` e contexto

```ts
export function track<E extends EventName>(event: E, ...[props]: PropsArgs<E>): void {
  const payload = { ...contextProperties(), ...props };   // a prop do evento vence a da sessão
  each((d) => d.track(event, payload));                    // cada destino roda em try/catch
}
```

O contexto é capturado **na hora do `track`**. Página fora do shell do app, como o checkout ou o callback de auth, precisa declarar a org antes de rastrear (um hook `useAnalyticsOrgScope(ctx, me)`). Sem isso o evento sai sem `org_id`.

Quem declara a org é o efeito do pai, e o efeito do filho roda antes dele. Evento que depende da org e sai no mount de um filho deve ser disparado do componente que declara a org, depois dela.

## 3. Interface de destino

```ts
export type AnalyticsDestination = {
  readonly name: string;
  readonly local?: boolean;              // console: continua recebendo com o rastreamento desligado
  track(event: string, props: Record<string, unknown>): void;
  identify?(userId: string): void;
  group?(orgId: string, traits?: { org_kind: "internal" | "customer" }): void;   // traits só enums
  reset?(): void;
  setTrackingAllowed?(allowed: boolean): void;  // opt-in/out e parada da gravação de sessão
};
```

- **GTM:** `dataLayer.push({ event: ga4Name ?? event, ...props })`, com o mapa `user_signed_up → sign_up`, `user_logged_in → login`, `checkout_started → begin_checkout`, `checkout_completed → purchase`, `page_viewed → page_view`.
- **Alias legado:** `legacyName(event)` dentro do destino que tinha o nome antigo, com a data de remoção num comentário e no plano.

## 4. Ambientes e consentimento

```ts
export function realDestinationsEnabled(env = import.meta.env) {
  if (env.VITE_ANALYTICS_IN_DEV === "true") return true;      // religar em dev para conferir um destino
  return env.PROD === true && env.VITE_USE_MOCKS !== "true";  // dev, mocks e testes nunca vão para produção
}
export function debugDestinationEnabled(env = import.meta.env) {
  return env.VITE_ANALYTICS_DEBUG === "true";               // destino console: imprime `[analytics] track <evento> {…}`
}
```

A decisão (flag da org, consentimento) tem três estados: `null`, `true` e `false`.
- Com `null`, os destinos reais esperam numa fila curta (por exemplo, 100 chamadas).
- Com `true`, a fila sai na ordem.
- Com `false`, a fila é descartada.

Os SDKs só são criados depois do `true`.

## 5. Servidor

```ts
serverTrack("subscription_started", { orgId, userId }, { plan_id, plan_kind });
```

- Só enfileira e **nunca lança**: está no caminho do request.
- O flush roda em intervalo, em lote, com fila máxima (descarta o mais antigo).
- Antes de enviar, consulta a flag e o `org_kind` das orgs do lote. Se a consulta falhar, **não envia**: mandar dado de uma org que desligou o rastreamento é pior que perder o lote.
- Só liga em produção (`NODE_ENV=production` ou uma flag explícita). Sem configuração, é no-op.
- Todo evento sai com `org_id`, `org_kind` e `source: "server"`. O `distinct_id` é o usuário ou `org:<id>`.
- Uso de alto volume (API pública) vai agregado: um evento por combinação a cada N minutos, com contagens.
- Webhook (Stripe e afins) só conta quando o banco muda de fato. Use `UPDATE ... WHERE` com a condição da mudança e `RETURNING`; reenvio do provedor não conta.

## 6. Testes de varredura

```ts
const calls = files.flatMap(({ path, text }) =>
  [...text.matchAll(/\b(?:track|serverTrack)\(\s*"([a-z0-9_]+)"/g)].map((m) => ({ event: m[1], file: path })));
// todo nome do catálogo: exatamente 1 call; toda call: nome conhecido; nada de import de SDK fora do core;
// nenhuma prop chamada email|name|message|title|description|query|error no catálogo.
```

Inclua no mesmo arquivo o teste que reprova o export do catálogo (CSV ou JSON) desatualizado.

## 7. Onde fica cada peça

| Peça | Fica em |
|---|---|
| Catálogo tipado + JSDoc | `lib/analytics/catalog/<area>.ts` |
| Core (`track`, contexto, fila) | `lib/analytics/index.ts`, `context.ts` |
| Destinos | `lib/analytics/destinations/*.ts` |
| Page view | assinatura do router (`onResolved`) com o template da rota |
| Identidade | o contexto de auth chama `identify`; o logout chama `reset` |
| Grupo da org | o shell declara a org e o `org_kind` ativos |
| Servidor | pacote próprio com catálogo próprio e o mesmo vocabulário |
