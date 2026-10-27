# PunkMetrics Skills

[Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) do método PunkMetrics para design, produto, analytics e growth. Cada skill ensina um agente de IA (Claude Code, Cursor, Codex e outros que leem o padrão Agent Skills) a fazer o trabalho do jeito que a PunkMetrics faz nos projetos dela e dos clientes.

> **English:** agent skills from PunkMetrics for product analytics and growth work: designing a tracking plan and a single analytics core, implementing and syncing events with Atlas, and documenting an event catalog in any tool. Written in Portuguese (pt-BR); install with `/plugin marketplace add punkmetrics/skills` or `npx skills add punkmetrics/skills`.

## O que tem aqui

### Tracking e analytics de produto

| Skill | Para quê | Entra em ação quando |
|---|---|---|
| [`punkmetrics-tracking-plan`](skills/punkmetrics-tracking-plan/SKILL.md) | Planejar o tracking: procurar o catálogo que já existe, auditar módulo a módulo quais ações viram eventos, definir nomes e propriedades e desenhar o core único que repassa os eventos para PostHog, Amplitude, GA/GTM e afins. Revisa os disparos e separa o que é bug do que é desenho | O produto precisa de um plano de eventos, os SDKs estão espalhados ou duplicados, ou alguém quer saber se os eventos contam certo |
| [`punkmetrics-tracking-implementation`](skills/punkmetrics-tracking-implementation/SKILL.md) | Implementar o plano no código com testes que provam a contagem, e sincronizar eventos, descrições e propriedades com o [Atlas](https://punkmetrics.com) pelo MCP ou pela CLI, ligando os eventos às telas das jornadas e conferindo tudo | Um plano aprovado vai para o código, ou o catálogo precisa entrar no Atlas e bater com ele |
| [`punkmetrics-tracking-docs`](skills/punkmetrics-tracking-docs/SKILL.md) | Documentar o catálogo de eventos fora do código: Markdown no repo, Notion, Linear, Confluence ou Google Docs. Gera por script, divide pelo limite da ferramenta e atualiza por trechos | O time pede "a documentação completa de todos os eventos" ou a referência precisa acompanhar uma mudança |

Os três formam um ciclo: **planejar → implementar → documentar**. O Atlas é opcional: sem ele, o catálogo no código é a fonte da verdade e os skills seguem o mesmo método.

## Instalar

### Claude Code (recomendado: recebe as atualizações)

```
/plugin marketplace add punkmetrics/skills
/plugin install punkmetrics@punkmetrics-skills
```

Para atualizar depois:

```
/plugin marketplace update punkmetrics-skills
```

Os skills aparecem como `punkmetrics:punkmetrics-tracking-plan` e assim por diante. O agente os usa sozinho quando o pedido combina; também dá para chamar pelo nome.

### Em um projeto, para o time inteiro

Coloque no `.claude/settings.json` do repositório. Quem abrir o projeto no Claude Code recebe a sugestão de instalar, e a referência continua sendo este repositório:

```json
{
  "extraKnownMarketplaces": {
    "punkmetrics-skills": { "source": { "source": "github", "repo": "punkmetrics/skills" } }
  },
  "enabledPlugins": { "punkmetrics@punkmetrics-skills": true }
}
```

### Cópia dentro do projeto (qualquer agente)

Com o CLI [`npx skills`](https://skills.sh), que copia os skills para o projeto e grava a origem no `skills-lock.json`:

```
npx skills add punkmetrics/skills --agent claude-code --skill '*' --copy
```

Troque `claude-code` pelo seu agente (`cursor`, `codex`…) ou use `'*'` para todos. Comite a pasta copiada (`.claude/skills/` no Claude Code) e o `skills-lock.json`: o time trabalha com a cópia, e o lock aponta para este repositório.

Para trazer as atualizações deste repositório e comitar a cópia nova:

```
npx skills update --project
```

### Manual

Clone este repositório e copie as pastas de `skills/` para o diretório de skills do seu agente:
- Claude Code: `~/.claude/skills/` ou `.claude/skills/` no projeto;
- Cursor: `~/.cursor/skills/`;
- Codex: `~/.codex/skills/`.

Cópia manual não se atualiza sozinha.

## Como pedir

- "Monte o plano de eventos do nosso app: quero saber o que medir em cada módulo."
- "Os eventos de checkout estão contando certo? Revise os disparos."
- "Implemente os P0 do plano e registre o catálogo no Atlas."
- "Documente todos os eventos no Notion, com o que cada propriedade significa."

## Estrutura

```
.claude-plugin/        manifestos do plugin e do marketplace do Claude Code
skills/<nome>/
  SKILL.md             o skill: quando usar, passo a passo, erros comuns
  reference/           detalhes, modelos e scripts que o skill chama quando precisa
```

## Contribuir

Abra uma issue ou um pull request. Skill novo ou mudança de método entra com:
- um cenário de teste: o pedido, o que um agente faz sem o skill e o que deve fazer com ele;
- `claude plugin validate --strict .` passando.

Registre a mudança no [`CHANGELOG.md`](CHANGELOG.md) e suba a versão em `.claude-plugin/plugin.json`.

## Licença

Código e texto dos skills sob a licença [MIT](LICENSE). A marca PunkMetrics e o nome Atlas não estão cobertos pela licença; veja o [`NOTICE.md`](NOTICE.md).
