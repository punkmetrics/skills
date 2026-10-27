---
name: punkmetrics-tracking-docs
description: Use when documenting an analytics event catalog, tracking plan or data contract outside the code — a Markdown file in the repo, Google Docs, Notion, Linear, Confluence or a similar tool — when a team asks for "the complete documentation of every event", when a reference doc is too large for the destination, or when an existing event reference must be updated after the catalog changes.
---

# Documentar o catálogo de eventos (método PunkMetrics, agnóstico de ferramenta)

## Visão geral

**O documento é um espelho gerado, nunca escrito à mão, evento por evento.** O conteúdo vem de duas fontes:
- **o catálogo**: nome, prioridade, tipo das props e o JSDoc como descrição;
- **a leitura do ponto de disparo de cada evento**: quando dispara, onde fica na tela, o que cada prop significa e as armadilhas.

O JSDoc sozinho dá uma doc rasa. É a leitura do disparo que a torna útil para PM e analista.

O destino muda pouca coisa: a forma de publicar e o limite de tamanho. O conteúdo e o processo são os mesmos.

## Quando usar

- Pedido de "documentação completa dos eventos" (Linear, Notion, Confluence, Google Docs ou `.md`).
- Catálogo mudou e a referência precisa acompanhar.
- Documento grande demais para a ferramenta.
- **Publicar um documento pronto** (o plano de eventos, por exemplo): pule "Produzir" e use só "Publicar" e "Atualizar".

**Quando não usar:**
- Desenhar o plano: `punkmetrics-tracking-plan`.
- Gravar eventos no Atlas: `punkmetrics-tracking-implementation`. O Atlas guarda a descrição no próprio evento e não precisa deste skill.

## Estrutura do documento

**1. Cabeçalho:**
- o escopo (N eventos, por superfície);
- a **fonte da verdade** (o caminho do catálogo e o commit SHA);
- o comando que regenera o export;
- "o que muda no código chega aqui por <processo>";
- os links para as outras partes.

**2. Resumo:** uma tabela `Área | Eventos | P0 | P1 | P2`, com total. Os números saem do script, nunca digitados.

**3. Parte geral:**
- como ler cada evento (a legenda);
- como os eventos saem (destinos, ambientes, flag por org);
- o contexto anexado a todo evento;
- os nomes por destino (GA4);
- os aliases legados, com prazo;
- como os eventos de servidor saem;
- as conversões e a fonte da receita;
- **armadilhas conhecidas**;
- como adicionar ou mudar um evento.

**4. Uma seção por área**, com cada evento no modelo de `reference/event-entry.md`:
- badges: prioridade, superfície, conversão, nome no GA4 e alias;
- descrição (o JSDoc);
- quando dispara;
- onde;
- código (`arquivo` + função, ou permalink no SHA);
- propriedades, com o significado e os valores;
- notas (pares de funil, armadilhas, como filtrar).

## Produzir

1. **Extraia o catálogo** para dados. O gerador lê o CSV no formato do tracking plan do Atlas (Event, Description, Context, Type, Conversion, Parameters). Outro formato é convertido para ele antes. Registre o **commit SHA** da fonte: a branch anda, e o SHA permite diff depois.
2. **Detalhe cada evento lendo o código.** Use um subagente por área (área grande vira duas), com o schema JSON fixo de `reference/event-entry.md`. Cada um devolve só JSON e não inventa: lacuna vira `"notes": "não encontrado"`.
   - **Confira o que voltou por script:** o `call_site` contém `track("<evento>"` e os nomes das props batem com o catálogo.
   - **No campo Código:** use `arquivo` + função, ou um permalink no SHA. Número de linha solto envelhece a cada commit.
3. **Escreva a parte geral uma vez, como prosa:** o cabeçalho e a parte geral vão num arquivo (`intro_md` do config), com `{{resumo}}` onde entra a tabela de contagens.
4. **Monte com script, não à mão:** `python3 -I <dir do skill>/reference/render-event-doc.py <config.json>`. O script cruza o catálogo com os detalhes e recusa se faltar detalhe de algum evento. Ele também calcula as contagens e corta em pedaços entre eventos, nunca no meio de um.
5. **Revise o texto** para leitores pouco técnicos: dado direto, frase curta, sem jargão sem explicação, e nenhum exemplo com dado pessoal. **Edite o JSON e renderize de novo.** Edição feita no markdown se perde na próxima geração.
6. **Guarde as fontes da doc**: o `config.json`, os JSONs de detalhe e o SHA. Ponha num lugar durável (`docs/events/.source/` no repo, ou anexo no item de trabalho), nunca só num diretório temporário. É com elas que a atualização recalcula as contagens sem detalhar tudo de novo. O gerador está em português: troque os rótulos se o time ler outro idioma.

## Publicar

**Meça antes.** Compare o tamanho total com o limite do destino (`reference/destinations.md`) e deixe ~10% de folga.
- Coube: um documento só.
- Não coube: divida **por fronteira de área** em "parte N/M", com o escopo no título e links cruzados.

**Crie e depois anexe.** Crie o documento com o cabeçalho e o primeiro pedaço, e anexe o resto em ordem (`append`). Se uma chamada recusar por tamanho, feche esta parte e abra a próxima.

**Confira:**
- busque o documento publicado;
- rode o `check-anchors.py` sobre todas as partes juntas, com todos os títulos `### \`evento\``: cada um deve aparecer uma vez, e o total tem que bater com o catálogo;
- abra os links cruzados;
- se renomear o título, a URL pode mudar: busque de novo e corrija os links das outras partes.

**Registre:**
- o id e a URL de cada parte no tracking (issue, README ou memória);
- um comentário no item de trabalho com os links.

## Atualizar depois de mudança no catálogo

**Não recrie o documento.** Faça patches no que existe:

0. **Descubra o que mudou:** `git diff <sha da doc>..HEAD -- <catálogo>`.
   - Detalhe de novo só os eventos novos ou alterados.
   - Junte o resultado nos JSONs guardados e renderize tudo, para as contagens virem do script.
   - Prop renomeada se busca pelo **nome da prop**, não só pelo do evento. A ficha ganha nas notas "até <data> se chamava `x`". No GA4, a dimensão com o nome antigo continua com o histórico.
1. Busque o conteúdo atual. Ele é a base, e não a cópia local. A ferramenta pode devolver o markdown diferente do que você mandou (títulos, código): monte as âncoras sobre o texto que ela devolveu.
2. Para cada mudança, escolha uma âncora (um título `### \`evento\`` até o próximo título, ou uma frase) e **confira por script que ela aparece exatamente uma vez** (`python3 -I <dir do skill>/reference/check-anchors.py atual.md anchors.json`).
3. Troque a ficha inteira do evento (um replace de intervalo, de título a título). Insira o evento novo logo depois do vizinho.
4. Atualize também o que deriva da ficha:
   - as contagens do resumo e do cabeçalho;
   - a contagem da área;
   - as armadilhas;
   - as notas de outros eventos que citam o alterado;
   - os links.
5. Busque o documento de novo e confirme que saiu certo.
6. Procure o evento em **todas** as partes antes de dar por encerrado. As contagens e as citações podem morar em outra parte.

## Erros comuns

| Erro | Correção |
|---|---|
| Doc só com JSDoc e tipos | Ler o disparo de cada evento (quando, onde, significado, armadilhas) |
| Contagens digitadas | Saem do script |
| Um documento gigante que a ferramenta recusa | Medir antes e dividir por área em partes com links |
| Cortar no meio de um evento | Cortar só entre fichas |
| Recriar o documento a cada mudança | Patch com âncora conferida |
| Âncora que aparece duas vezes | Conferir por script antes; ampliar a âncora |
| Esquecer o resumo e as citações em outros eventos | Buscar o nome do evento no documento inteiro, em todas as partes |
| Link quebrado depois de renomear | Buscar a URL nova e corrigir as outras partes |
