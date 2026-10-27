# Modelo do documento do plano

No repo do produto, quando o pedido inclui escrever lá, use por exemplo `docs/plano-eventos-analytics.md`. Senão, entregue como documento pelo skill `punkmetrics-tracking-docs` (modo "publicar um documento pronto").

```markdown
# Plano de eventos de analytics do <produto>

**Resumo.** O que foi revisado (N módulos, agrupados em M seções), o tamanho do catálogo (N eventos: x P0, y P1, z P2), o que existe hoje e a recomendação de ordem.

## 0. Implementação
Preencher quando o plano for implementado: onde o catálogo vive no código (a fonte da verdade depois disso), as contagens, as decisões aplicadas, os passos de deploy e o comando que exporta o catálogo.

## 1. Estado atual
Tabela Destino | Onde carrega | Como dispara | Eventos. Problemas numerados, com o arquivo de cada um.

## 2. Arquitetura proposta: o core
Diagrama, contrato (`track`, `page`, `identify`, `group`, `reset`), regras, as garantias por teste e onde o `track` mora.

## 3. Convenções
3.1 Nomes · 3.2 Propriedades · 3.3 Contexto anexado · 3.4 Page view · 3.5 Migração dos eventos existentes (tabela: canônico | hoje no destino A | hoje no destino B | observação).

## 4. Catálogo por módulo
Legenda de prioridade e de status. Uma subseção por módulo, com a tabela:
| Evento | P | Ponto único | Propriedades | Status |
As referências `arquivo:linha` têm data; o nome da função é o que vale.

## 5. Eventos do servidor
| Evento | Onde | Por quê |
Inclui o que não vira evento porque já tem ledger.

## 6. Roteiro de implementação
Fase A, fundação: o core, a migração com aliases, o page view, os testes de varredura, a correção dos dados errados e a separação de ambientes.
Fase B: os P0, inclusive os de servidor como a receita pelo webhook, e os refactors de ponto único que eles pedem.
Fase C: os P1, módulo a módulo.
Fase D: os P2 sob demanda e o resto do servidor.
Definition of Done de uma feature nova.

## 7. Decisões
Em aberto (com recomendação) → tomadas (com data).
```

## Checklist antes de entregar

- [ ] O passo 0 foi feito: o catálogo existente e a regra de nomes do Atlas foram consultados, ou registrei que não existem.
- [ ] Todo módulo do registro do app aparece, mesmo que como "sem evento, porque…".
- [ ] Toda linha do catálogo tem ponto único e status.
- [ ] Nenhuma prop de texto livre ou de dado pessoal.
- [ ] Os eventos de servidor cobrem a receita e o fim dos jobs.
- [ ] A revisão dos disparos foi feita nos eventos que já existem.
- [ ] As decisões do usuário estão listadas, com a recomendação.
