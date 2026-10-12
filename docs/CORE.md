# Spark Notebook: registo do Core

> Registo técnico e funcional da app. Estado a **12 out 2026**.
> App publicada: https://carloscastro99.github.io/thiirfv588wui5773/
> Repositório: `carlosCastro99/thiirfv588wui5773` (branch `main`, GitHub Pages a partir da raiz)

---

## 1. O que é

Uma app de aprendizagem em cartões ilustrados, inspirada no Deepstash. Funciona offline e não tem contas nem servidor próprio.
Lições curtas (10 cartões cada) com diagramas desenhados à mão, quizzes e um feed vertical tipo TikTok. Cada cartão tem um aprofundamento ("Go deeper").

**Princípios fixos**
- **Sem contas.** Todo o estado fica no dispositivo, com backup e restauro manual em JSON.
- **Offline-first.** É uma PWA instalável: o service worker guarda a "casca" da app e os temas descarregados ficam em IndexedDB.
- **Temas descarregáveis.** O utilizador escolhe que temas quer guardar offline.
- **Aprender de forma fácil.** Texto curto e diagrama primeiro. O detalhe fica no "Go deeper".
- **Regra de conteúdo.** Qualquer tema novo nasce com **20 lições × 10 cartões**, e cada cartão tem aprofundamento.

---

## 2. Números atuais

| Métrica | Valor |
|---|---|
| Temas | 18 |
| Lições | 360 (20 por tema) |
| Cartões | 3.600 (10 por lição) |
| Cartões com "Go deeper" | 3.600 (100%) |
| Blocos de aprofundamento | 37.848 |
| Diagramas nos aprofundamentos | 9.151 |
| Perguntas de quiz | 994 |
| Widgets interativos | 9 |
| Esboços SVG feitos à mão | 70 |
| Tamanho dos packs | ~7,1 MB (18 ficheiros JSON) |
| `index.html` (app completa) | ~252 KB |

### Temas

| Tema | `id` do pack | chave `topic` | Lições | Cartões | Quiz | Versão | kB |
|---|---|---|---|---|---|---|---|
| Artificial Intelligence | `ai` | `ai` | 20 | 200 | 62 | 12 | 396 |
| Generative AI | `genai` | `gen` | 20 | 200 | 60 | 8 | 354 |
| Corporate AI | `corpai` | `corp` | 20 | 200 | 60 | 9 | 338 |
| English (explicado em PT) | `english` | `eng` | 20 | 200 | 69 | 10 | 349 |
| Electricity | `electricity` | `elec` | 20 | 200 | 65 | 7 | 323 |
| Electronics | `electronics` | `tron` | 20 | 200 | 64 | 6 | 298 |
| Engineering | `mechanics` | `mech` | 20 | 200 | 64 | 6 | 310 |
| Physics | `physics` | `sci` | 20 | 200 | 64 | 3 | 467 |
| History | `history` | `hist` | 20 | 200 | 64 | 3 | 464 |
| World | `world` | `world` | 20 | 200 | 64 | 3 | 462 |
| Space | `space` | `space` | 20 | 200 | 46 | 15 | 387 |
| Maths & Logic | `maths` | `math` | 20 | 200 | 45 | 4 | 433 |
| Human Body | `body` | `body` | 20 | 200 | 45 | 4 | 422 |
| Nature & Animals | `nature` | `nature` | 20 | 200 | 45 | 4 | 446 |
| Psychology | `psychology` | `psy` | 20 | 200 | 45 | 4 | 446 |
| Philosophy | `philosophy` | `phil` | 20 | 200 | 44 | 4 | 474 |
| Money | `money` | `money` | 20 | 200 | 44 | 11 | 323 |
| Art & Culture | `art` | `art` | 20 | 200 | 44 | 4 | 456 |

Nota: o tema **English** tem explicações e aprofundamentos em **português**. Todos os outros estão em inglês britânico.

---

## 3. Funcionalidades

**Separadores (tab bar):** Today · Feed · Learn · Favourites · You

- **Today:** saudação, anel do objetivo diário (5, 10 ou 20 cartões; por omissão 10), streak e semana, "Up next" (próxima lição por terminar), "Sketch of the day" e revisões pendentes.
- **Learn:** biblioteca de temas (descarregar um tema ou todos, atualizar, remover e importar um ficheiro de tema), lista de lições com progresso, leitor de lição (cartões + quiz no fim).
- **Feed:** scroll vertical infinito com scroll-snap, um cartão por ecrã.
  - Chips de categoria: *For you*, *★ Favourites* e um por tema.
  - Um quiz a cada 6 cartões (só perguntas ainda não acertadas).
  - Duplo toque guarda o cartão. O rail lateral tem guardar, ouvir, partilhar e **Deeper**.
  - Personalização *For you*: o tempo de permanência ajusta o peso de cada tema (ver §6).
- **Go deeper:** folha a ecrã inteiro com "In short" (o texto do cartão) e "In depth" (parágrafos, subtítulos, bullets, diagramas, *Key idea*, *Myth/Reality*, *Did you know?*, exemplo resolvido e fórmula). Tem ações Guardar, Ouvir e Voltar. Fecha com `Esc`.
- **Favourites:** cartões e lições guardados, com filtro por tema.
- **You:** objetivo diário, histórico de leitura (mais recente primeiro), backup e restauro, e instalação da PWA.
- **Ouvir:** Web Speech API (`speechSynthesis`) com voz `en-GB`.
- **Partilhar:** `navigator.share`; se não existir, copia para a área de transferência.
- **Revisão:** uma resposta errada no quiz agenda a pergunta para revisão a partir da meia-noite seguinte. Uma resposta certa remove-a da fila.
- **Widgets interativos (9):** `neuron`, `nextword` (AI); `divider` (Electronics); `ohm` (Electricity); `wave` (Physics); `lever` (Engineering); `flip` ×2 (English: falsos amigos e phrasal verbs); `clock` (World: fusos horários).

---

## 4. Arquitetura

### 4.1 Ficheiros publicados (raiz do repo)

```
index.html              App completa (HTML+CSS+JS inline, fontes em base64, motor VZ, FEED, CATALOG)
sw.js                   Service worker (cache da casca + cache-then-network)
manifest.webmanifest    PWA (standalone, theme #1F5FD1, bg #EDF1F6)
icon-192.png, icon-512.png, apple-touch-icon.png
packs/catalog.json      Catálogo (id, topic, title, blurb, version, lessons, cards, quiz, kb)
packs/<id>.json         Um pack por tema (18)
spark-notebook-offline.pdf   PDF offline (versão antiga, sem aprofundamentos)
.nojekyll, README.md
```

### 4.2 Peças dentro do `index.html`

| Peça | Função |
|---|---|
| `CATALOG` | Cópia embutida de `packs/catalog.json`. Serve para detetar versões novas dos packs. |
| `BUNDLE` | `{}` na versão alojada. Na versão standalone leva os packs embutidos. |
| `TOPICS` | Mapa chave → nome do tema (18 entradas) e cores por tema em CSS. |
| `VZ` | Motor de diagramas: gera SVG 320×180 "desenhado à mão" a partir de JSON (§5.4). |
| `FEED` | Módulo do feed: `show`, `hide`, `refresh`, `next`, fila ponderada, IntersectionObserver. |
| `DB` | Wrapper IndexedDB para os packs. |
| `S` | Estado do utilizador, persistido em `localStorage` (§4.4). |
| `indexPacks()` | Constrói `LESSONS`, `CARDS` e `QUIZ` a partir de `PACKS`. |
| `openDeep()` / `closeDeep()` | Folha "Go deeper". |
| `render()` | Render da tab ativa (string templates → `innerHTML`). |

**IDs em runtime:** cartão = `<lessonId>-c<k>` e pergunta = `<lessonId>-q<k>` (k começa em 0). Exemplo: `hi-1755-c1`.
Os IDs não estão guardados nos packs. São derivados da posição, por isso **reordenar cartões numa lição desalinha o progresso** dos utilizadores.

### 4.3 Armazenamento local

| Chave | Onde | Conteúdo |
|---|---|---|
| `spark` (v1), object store de packs | IndexedDB | Packs descarregados (JSON completo + `downloadedAt`) |
| `spark-packs-fallback` | localStorage | Fallback dos packs se o IndexedDB falhar |
| `spark-state-v1` | localStorage | Estado do utilizador `S` |
| Cache `spark-<hash>` | Cache Storage (SW) | Casca da app + catálogo + packs pedidos |

### 4.4 Estado do utilizador (`S`)

```js
{
  feed:   { topic: {<topic>: peso -0.7..3}, seen: {<cardId>: 1} },
  saved:  [<cardId>],            // cartões favoritos
  favL:   [<lessonId>],          // lições favoritas
  favT:   {},                    // filtro de favoritos
  seen:   {<cardId>: 1},         // cartões vistos
  reads:  {"YYYY-MM-DD": [<id>]},// leituras por dia (streak e objetivo)
  log:    [{id, t}],             // histórico (máx. 3000)
  quiz:   {<qId>: {ok, t}},      // respostas
  review: {<qId>: timestamp},    // revisões agendadas
  done:   {<lessonId>: ...},     // lições concluídas
  deepRead: {<cardId>: t},       // aprofundamentos abertos
  goal: 10, best: 0              // objetivo diário, melhor streak
}
```

**Backup:** ficheiro `spark-backup-YYYY-MM-DD.json` com `{kind: "spark-backup", state: S, packs: [...]}`. O restauro repõe o estado e os packs.

### 4.5 Atualizações automáticas

1. Uma alteração de conteúdo num pack incrementa `version` nesse pack, em `packs/catalog.json` **e** no `CATALOG` embutido no `index.html`.
2. Uma alteração ao `index.html` muda o nome da cache em `sw.js` (`spark-<hash>`), e o browser instala o service worker novo.
3. A navegação é *network-first*: online, a app recebe sempre o `index.html` novo. Offline, usa a cópia em cache.
4. A app compara `CATALOG[i].version` com a versão do pack em IndexedDB. Ao abrir online, os packs desatualizados são descarregados de novo automaticamente e aparece um toast. Na biblioteca, esses packs também aparecem marcados como tendo atualização.

---

## 5. Modelo de conteúdo

### 5.1 Pack (`packs/<id>.json`)

```json
{
  "id": "space", "topic": "space", "title": "Space", "version": 14,
  "blurb": "Planets, stars, galaxies and the search for life.",
  "lessons": [ Lesson, ... ]   // 20
}
```

### 5.2 Lição

```json
{ "id": "sp-solar", "title": "The Solar System",
  "summary": "A tour of our neighbourhood, from the Sun to the edge.",
  "cards": [ Card, ... ],      // 10
  "quiz":  [ {"q": "...", "options": ["a","b","c"], "answer": 1, "explain": "..."} ] }
```

Prefixos dos IDs de lição por tema: `ai-`, `gen-`, `corp-`, `en-`, `el-`, `tr-`, `me-`, `ph-` (Physics e Philosophy partilham o prefixo), `hi-`, `wo-`, `sp-`, `ma-`, `bo-`, `na-`, `ps-`, `mo-`, `ar-`.

### 5.3 Cartão

| Campo | Obrig. | Descrição |
|---|---|---|
| `type` | sim | `concept` (3.346), `fact` (112), `formula` (46), `example`, `widget` |
| `title` | sim | Título. É a chave de ligação dos aprofundamentos (match exato). |
| `text` | sim | 60–90 palavras. Parágrafos separados por linha em branco. Suporta `**negrito**` e `*itálico*`. |
| `viz` | — | Diagrama VZ do cartão (3.523 cartões) |
| `sketch` | — | SVG desenhado à mão (70 cartões) |
| `formula` | — | Fórmula em destaque |
| `example` | — | Linhas de exemplo resolvido |
| `widget` | — | Nome do widget interativo |
| `tag`, `say`, `items` | — | Campos do tema English (rótulo PT, frase para ouvir, tabelas de vocabulário) |
| `deep` | sim* | Lista de blocos de aprofundamento (*obrigatório desde out 2026) |

### 5.4 Blocos `deep`

| `t` | Campos | Render |
|---|---|---|
| `p` | `x` (string) | Parágrafo |
| `h` | `x` | Subtítulo |
| `ul` | `x` (lista) | Bullets |
| `key` | `x` | Caixa *Key idea* |
| `myth` | `w` (mito), `r` (realidade) | Caixa *Myth / Reality* |
| `fact` | `x` | Caixa *Did you know?* |
| `ex` | `x` (lista de linhas) | *Worked example* |
| `f` | `x` | Fórmula |
| `viz` | `v` (spec VZ) | Diagrama |

Média por cartão: ~10,5 blocos, ~2,5 diagramas, 200–350 palavras.

### 5.5 Diagramas VZ (`{"k": ...}`)

O SVG é 320×180, com letra Caveat e filtro `#rough` para o efeito de traço à mão. Os limites de texto são práticos: acima deles, o texto transborda ou sobrepõe-se.

| `k` | Estrutura | Limites práticos |
|---|---|---|
| `flow` | `steps[]` | 3–5 passos, ≤ 28 car. |
| `cycle` | `steps[]` | 3–5, ≤ 26 car. |
| `stack` | `items[]` (topo primeiro) | 3–5, ≤ 32 car. |
| `list` | `items[]` | 3–5, ≤ 34 car. |
| `tree` | `root`, `items[]` | raiz ≤ 24; 3–4 ramos ≤ 28 |
| `cmp` | `l:{t,items}`, `r:{t,items}` | título ≤ 18; 2–3 itens ≤ 24 |
| `pairs` | `items[{a,b}]` | 2–4; a ≤ 22, b ≤ 30 |
| `fix` | `items[{w,r}]` | 1–2 (errado → melhor) |
| `time` | `events[{y,l}]` | 3–5; y ≤ 9, l ≤ 22 |
| `nums` | `items[{v,l}]` | 2–3; v ≤ 10, l ≤ 24 |
| `bars` | `unit`, `items[{l,v,t?,hi?}]` | 2–5; valores numéricos ≥ 0 (negativos desenham-se como barra vazia; usar `pairs`, `nums` ou `scale`); unit ≤ 30 |
| `scale` | `lo`, `hi`, `unit`, `log?`, `items[{l,v,t?,hi?}]` | 3–4; unit ≤ 18, labels ≤ 14 |
| `terms` | `f`, `items[{s,m}]` | fórmula ≤ 24; 2–4 símbolos |

---

## 6. Algoritmo do feed

- **Fila:** `score = (visto ? 0.15 : 1) × peso(tema) × random()`, ordenada por ordem decrescente. Na categoria *For you* usa o peso do tema. Nas outras categorias o peso é 1.
- **Peso do tema:** `clamp(1 + F.topic[t], 0.25, 4)`.
- **Aprendizagem por permanência** (cartão ≥ 60% visível):
  - < 1,2 s → −0,15 · 3–6 s → +0,10 · > 6 s → +0,25 (acumulado limitado a −0,7…3)
  - ≥ 1,4 s visível → conta como lido (`markRead`) e como visto no feed.
- **Quizzes:** um a cada 6 cartões, baralhados, excluindo os já acertados.
- **Paginação:** acrescenta 8 itens quando o fim da lista está a 200% da altura do ecrã.

---

## 7. Pipeline de conteúdo e ferramentas

> **Fonte de verdade = `packs/*.json`.** O pipeline original (`build.py`, `dsl.py`, `lessons/*.txt`, template) perdeu-se quando o ambiente de trabalho foi reciclado a 12 out 2026. O `index.html` publicado já tem o `viz.js` e o `feed.js` embutidos e está completo. Os aprofundamentos estão também em texto, em `content/deep/<pack>.txt`, exportados com verificação de ida e volta.

Estrutura no repositório:

```
tools/      ferramentas Python (precisam de python3; check_viz/e2e precisam de Playwright + Chromium)
content/deep/<pack>.txt   aprofundamentos dos 18 temas em formato de texto (DSL)
docs/CORE.md              este documento
```

| Ferramenta | Uso |
|---|---|
| `tools/dump.py <pack> [lessonIds]` | Lista os títulos exatos e os textos dos cartões |
| `tools/deeptool.py check <pack> <ficheiros>` | Faz parse e valida aprofundamentos (títulos, specs VZ, mínimo de 3 blocos) |
| `tools/deeptool.py attach <pack> <ficheiros>` | Escreve no pack, faz bump de `version`, atualiza `kb`, `catalog.json`, `CATALOG` no `index.html` e a cache do `sw.js` |
| `tools/export_deep.py [packs]` | Exporta os aprofundamentos dos packs para `content/deep/` e verifica a ida e volta |
| `tools/check_viz.py <pack> [ficheiros]` | Renderiza todos os diagramas com o `VZ` real (Chromium) e reporta overflow, sobreposição e texto < 9 px |
| `tools/e2e.py <packs…>` | Descarrega packs na app e abre todos os "Go deeper" à procura de erros |
| `tools/AGENT_GUIDE.md`, `tools/example.txt` | Guia de escrita para agentes paralelos |

Os caminhos são relativos à raiz do repositório. Pode ser sobreposto com a variável `SITE=/caminho/para/o/repo`.

### 7.1 Formato de texto dos aprofundamentos (DSL)

```
== <lesson-id>
# <título exato do cartão>
Parágrafo simples (2–4 frases).
### Subtítulo
• bullet
> Key idea (uma por cartão)
!! Mito => Realidade
!? Did you know?
ex: passo 1 | passo 2 | resultado
= fórmula
@viz {"k":"flow","steps":["A","B","C"]}
// comentário
```

### 7.2 Regras editoriais

- O aprofundamento vai **além** do texto do cartão (mecanismo, números, datas, nomes, consequências) e não o repete.
- Inglês britânico, claro e sem jargão por explicar. English é a exceção e é escrito em português.
- Rigor: factos bem estabelecidos e números arredondados com "about". Nada de citações nem estudos inventados. Conhecimento até 2026.
- Ângulo Portugal/Europa quando for natural. Unidades métricas, €, °C.
- Psicologia: indicar o estado de replicação dos estudos contestados.
- Filosofia e religião: apresentar posições com as objeções mais fortes, sem tomar partido.
- Arte: não reproduzir letras nem poemas publicados depois de 1929; descrevê-los.

### 7.3 Processo para acrescentar ou alterar conteúdo

1. Editar `content/deep/<pack>.txt` (ou escrever um ficheiro novo) e correr `tools/deeptool.py attach <pack> content/deep/<pack>.txt`.
2. `deeptool.py check` → `check_viz.py` até dar **0 problemas**.
3. `deeptool.py attach` (faz bump de versão automaticamente).
4. `e2e.py` para o smoke test.
5. Fazer commit e push para `main`. O GitHub Pages publica em ~1 min e as apps instaladas atualizam ao abrir com rede.

---

## 8. Publicação

- GitHub Pages a partir da raiz do branch `main`, com `.nojekyll`.
- Os commits levam os trailers `Co-Authored-By: Claude …` e `Claude-Session: …`.
- Para usar no avião: instalar a PWA (Adicionar ao ecrã principal), abrir online, descarregar os temas em *Learn* e confirmar o toast "N topics ready offline".

---

## 9. Histórico

| Data | Marco |
|---|---|
| 11 out 2026 | v1 "Kernel" → reescrita como **Spark Notebook**: PWA offline, sem contas, temas descarregáveis |
| 11 out | Diagramas gerados (VZ) + DSL de lições; AI e English com 20 lições |
| 11 out | Electricity, Electronics, Engineering, Physics, History e World com 20 lições |
| 11 out | Generative AI e Corporate AI |
| 11 out | Feed tipo TikTok + 8 categorias novas (Space, Maths, Body, Nature, Psychology, Philosophy, Money, Art) |
| 11 out | Todas as categorias com 20 lições (3.600 cartões) |
| 11 out | "Go deeper" (piloto: Solar System) |
| 12 out | Aprofundamentos em todos os cartões: Space, AI, GenAI, Corporate AI, Money, English, Electricity, Electronics, Engineering |
| 12 out | Últimos 9 temas, escritos por agentes em paralelo → **3.600/3.600** |
| 12 out | Ferramentas, aprofundamentos em texto e este documento guardados no repo; corrigidos 5 gráficos de barras com valores negativos ou nulos (AI, Corporate AI, Space) |

---

## 10. Pendentes e riscos

- **Lições e quizzes só existem em JSON.** Os ficheiros de texto originais das lições perderam-se. Para alterar cartões ou quizzes, edita-se o JSON do pack e faz-se bump manual de `version` (ou corre-se `deeptool.py attach` com um ficheiro de aprofundamento).
- **5 diagramas antigos com texto pequeno** (< 9 px) em AI e Corporate AI (citações longas em `fix`/`bars`). São legíveis, mas convém encurtá-los.
- **O PDF offline está desatualizado:** não tem os aprofundamentos nem os temas novos.
- **IDs derivados da posição:** reordenar cartões ou lições afeta o progresso. Convém acrescentar sempre no fim.
- **Tamanho:** ~7 MB para todos os temas. Está bem para IndexedDB, mas convém vigiar se se adicionarem imagens.
- **Prefixo `ph-` partilhado** por Physics e Philosophy. Funciona porque os IDs completos são únicos, mas um tema novo deve usar um prefixo próprio.
- **Revisão factual humana:** o conteúdo foi gerado e verificado automaticamente (parse, render e e2e). Uma amostragem humana por tema é recomendável.
