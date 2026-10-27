# CLAUDE.md

Repositório **público** (`github.com/punkmetrics/skills`) com os Agent Skills do método PunkMetrics. Ele também é o plugin `punkmetrics` e o marketplace `punkmetrics-skills` do Claude Code. Os outros projetos referenciam este repo: pelo plugin, ou por cópia com `npx skills`, que grava a origem no `skills-lock.json`.

## Mudar ou criar um skill

1. **Edite aqui**, em `skills/<nome>/`. Nunca numa cópia instalada em `~/.claude/plugins` ou em `.claude/skills` de outro projeto: a próxima atualização apaga a edição.
2. **Teste antes de publicar**, pelo método do skill `superpowers:writing-skills`:
   - rode o cenário sem o skill e anote o que o agente erra;
   - rode com o skill e confira que ele acerta.
3. **Valide:** `claude plugin validate --strict .` (marketplace), `claude plugin validate --strict .claude-plugin/plugin.json` e `claude plugin validate --strict skills`.
4. **Versão:** suba `version` em `.claude-plugin/plugin.json` (semver; skill novo é minor) e registre no `CHANGELOG.md`.
5. **Revisão do que é público:**
   - nenhum id interno, nome de cliente, link privado (Linear, Notion), caminho da máquina ou chave;
   - rode `gitleaks dir .`.

   Exemplo vem do Atlas ou é genérico, nunca de um cliente.
6. **Publique:** commit e push na `main`, só quando o usuário pedir. Depois, `claude plugin marketplace update punkmetrics-skills` nesta máquina.

## Formato

- `SKILL.md`: frontmatter com `name` (igual ao nome da pasta) e `description` em inglês começando por "Use when…". A descrição diz só quando usar, nunca resume o processo. O corpo é em português (pt-BR).
- `reference/`: detalhe pesado, modelos e scripts. Scripts são chamados pelo interpretador (`python3 -I <dir do skill>/reference/x.py`).
- Nome de skill com o prefixo da área: `punkmetrics-<área>-<assunto>`.
