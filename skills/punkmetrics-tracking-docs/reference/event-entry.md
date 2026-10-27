# Ficha de evento: modelo e schema dos detalhes

## Modelo renderizado

```markdown
### `checkout_completed`

`P0` · web · **conversão** · GA4: `purchase`

Tela de sucesso do checkout confirmou que a org já está no plano comprado. Uma vez por sessão de checkout da Stripe neste navegador.

* **Quando dispara:** Sistema, na volta da Stripe para /checkout/success. Lê os entitlements a cada 2 s, até 15 vezes; sai quando o plano bate e o `session_id` ainda não contou. Se o webhook demora mais, não sai.
* **Onde:** /checkout/success (volta da Stripe)
* **Código:** `apps/web/src/pages/checkout-success.tsx` · `CheckoutSuccessPage` (poll)
* **Propriedades:**
  * `plan_id` · `string | null` — Id do plano atual da org, lido dos entitlements.
  * `attempts` · `number` — Leituras até o plano aparecer (1 = já estava ativo).
* **Notas:** A receita de verdade é `subscription_started`, no servidor. Em aba privada, a trava vale só enquanto a aba está aberta.
```

**Regras da ficha:**
- A primeira linha depois do título são os badges: prioridade, superfície, conversão, nome em outro destino e alias legado com prazo. No servidor, também o ator (pessoa ou org).
- A descrição é o JSDoc do catálogo, sem reescrever. Se o JSDoc estiver errado, corrija o catálogo e regenere.
- "Quando dispara" diz quem dispara (usuário ou sistema), a condição, o que **não** dispara e os limites.
- Cada propriedade traz o **significado** e os valores possíveis, não só o tipo. Um enum lista os valores com o que cada um quer dizer.
- As notas trazem o par de funil, as armadilhas e como filtrar (por exemplo, "para exclusões reais, filtre sem `error_kind`").

## Schema que cada subagente devolve (um arquivo por área)

```json
{
  "checkout_completed": {
    "description": "o JSDoc, como está no catálogo",
    "actor": "user | system | org (só no servidor)",
    "trigger": "quem, quando, condição, o que não dispara",
    "where": "Caminho na interface (Tela › seção › botão) ou rota",
    "call_site": "caminho/do/arquivo.ts · função (ou permalink no SHA)",
    "props": [{ "name": "plan_id", "meaning": "significado e valores" }],
    "notes": "pares, armadilhas, filtros; 'não encontrado' quando não achou",
    "issues": [{ "kind": "a_mais | a_menos | prop_fixa | leitura", "verdict": "bug | desenho", "detail": "o que e onde" }]
  }
}
```

## Briefing do subagente (por área)

> Leia o catálogo `<arquivo>` e, para cada evento dele, o ponto de disparo no código (procure `track("<evento>"` ou `serverTrack("<evento>"`). Devolva **só** JSON no schema acima, com uma chave por evento, todas presentes.
>
> - Escreva em português claro para PM e analista.
> - Não invente: se não achou algo, escreva "não encontrado".
> - Em `issues`, registre o que pode contar a mais, a menos, prop que não varia e leitura que confunde, com o veredito bug ou desenho. Em `notes`, o resumo disso para o leitor.
>
> Salve em `<scratch>/<area>.json`.
