<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Ícone do Antigraf: perfil gravado de uma figura coroada de louro sobre um ladrilho verde">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <b>Português</b>
</p>

<p align="center">
  <b>Do grego <i>antígrafo</i> (αντίγραφο): uma cópia que responde ao original.</b><br>
  Uma habilidade de duplicação, clonagem ou estudo para agentes de código com IA.<br>
  Ela estuda uma fonte, constrói a sua própria versão<br>
  e <b>prova</b> o quão perto está com comandos que você pode rodar de novo.
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="47 scripts, no installs" src="https://img.shields.io/badge/scripts-47%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">

  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
  <img alt="License: Apache-2.0 or MIT" src="https://img.shields.io/badge/license-Apache--2.0%20or%20MIT-2d81ff?style=flat-square">
</p>

<p align="center">
  <a href="#como-funciona">Como funciona</a> ·
<a href="#quatro-trabalhos">Quatro trabalhos</a> ·
<a href="#o-que-o-distingue">O que o distingue</a> ·
<a href="#onde-fica-cada-coisa">Onde fica cada coisa</a> ·
<a href="#instalação">Instalação</a> ·
<a href="#como-usar">Como usar</a> ·
<a href="#perguntas-que-as-pessoas-fazem">Perguntas que as pessoas fazem</a> ·
<a href="#estado-honesto">Estado honesto</a> ·
<a href="#licença">Licença</a> ·
<a href="#contribuição-e-segurança">Contribuição e segurança</a> ·
<a href="#a-linha-que-não-cruzamos">A linha que não cruzamos</a>
</p>

<br>

O Antigraf vive dentro do seu agente como um pacote de instruções e um conjunto de ferramentas
pequenas. Ele percorre um site, um aplicativo de celular ou um jogo, anota cada parte como número,
constrói a sua cópia e então faz os dois lados responderem às mesmas verificações até que nada falhe e
nada fique desconhecido.

A ideia não é dizer "parece igual". A ideia é mostrar a linha que ainda difere, e o comando que mostra
isso.

<br>

<b>Em palavras simples:</b> Antigraf é uma habilidade de replicação 1:1 para agentes de código com IA. Use para clonar um site, copiar um app web ou um jogo, recriar um design como seu, ou estudar como um site é construído, da tela ao interior. Ela cobre o conjunto inteiro de páginas, não só a primeira: cada rota, seção, controle, estado aberto, animação, layout de celular, comportamento offline e cena 3D, cada um comparado ao original e cada um segurando o selo em 100% até bater.

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>Estude qualquer coisa</h3>
      Páginas, telas, menus, controles e o que está atrás de um clique. Cada número carrega a sua origem, então um palpite não pode se passar por uma medição.
    </td>
    <td width="25%" valign="top">
      <h3>Construa a sua</h3>
      A sua cópia vive no seu projeto, com a pilha que você escolher. Nada da fonte viaja com ela, exceto o que você tem o direito de usar.
    </td>
    <td width="25%" valign="top">
      <h3>Verificado, não adivinhado</h3>
      27 verificações rodam dos dois lados em cada rodada. Uma que nunca rodou, ou que respondeu desconhecido, trava o selo e nunca conta como aprovação.
    </td>
    <td width="25%" valign="top">
      <h3>Pronto para agentes</h3>
      Um arquivo de habilidade e scripts simples, para que qualquer modelo e ambiente mova as mesmas verificações. Medir não precisa de IA.
    </td>
  </tr>
</table>

<br>

## Como funciona

Aponte para uma fonte, escolha um trabalho, e ele segue em cinco etapas:

1. **Estudar:** percorrer a fonte, abrir o que se esconde atrás de um clique e registrar como números.
2. **Planejar:** uma linha por página, seção, controle, estado e rota, cada uma com a verificação que a julga.
3. **Construir:** escrever a sua cópia, o visível primeiro. As peças de servidor são nomeadas, nunca copiadas.
4. **Verificar:** as mesmas verificações rodam no original e na sua cópia, rodada após rodada.
5. **Refinar:** cada linha que falha volta como a próxima mensagem de construção, até o selo fechar.

## Quatro trabalhos

`/antigraf` faz uma única pergunta antes de qualquer coisa acontecer.

| # | Trabalho | O que faz |
|---|---|---|
| **1** | **Clonar** | Copia a fonte 1:1. Não pergunta nada mais e trava o alvo em 100%. |
| **2** | **Recriar** | Copia como a sua própria versão. Pergunta o que deve mudar: cores, marca, ícones, textos. |
| **3** | **Melhorar** | Coloca uma fonte ao lado do seu projeto, mostra o que ela faz melhor e termina com uma lista curta do que fazer em seguida. |
| **4** | **Estudar** | Só leitura, nada é executado, segredos são ocultados. Com o que é construído, de fora para dentro. |

Todo trabalho concluído termina com uma tabela honesta de 1 a 100 por área, o que segura cada área,
e as suas opções para seguir.

## O que o distingue

| | **Antigraf** | Uma habilidade de clonagem comum |
|---|---|---|
| Onde roda | Qualquer ambiente, qualquer modelo. Só bibliotecas padrão de Python 3 e Node | Presa a um laço de agente |
| Como decide "pronto" | 27 verificações, cada uma com seu código de saída, todas em cada rodada | O modelo diz que parece certo |
| "Não comparado" | Sempre trava o selo | Costuma contar como aprovação |
| Diferenças que você aceita | Só suas, escritas por você, nunca descartadas em silêncio | Não modelado |
| Trabalhos grandes | Divididos em faixas, 3 ajudantes no máximo, regra de 60 minutos | Uma execução longa que desvia aos poucos |
| O que afirma sobre si | Um bloco de progresso gerado de registros reais | O que a página disser |

Nenhuma nota global esconde qual linha falhou. Imagens sozinhas nunca aprovam nada. Um modelo mais fraco,
ou que não vê imagens, nunca baixa a régua: gasta menos e diz isso.

## Onde fica cada coisa

| Caminho | O que é |
|---|---|
| `skills/antigraf/SKILL.md` | a habilidade em si: trabalhos, etapas, níveis, espaço de trabalho, rodadas, regras |
| `skills/antigraf/README.md` | o documento completo: checagens, tolerâncias, progresso, disposição |
| `skills/antigraf/references/` | 12 guias: checagens, planejamento, fidelidade, cena, entrega, evidências |
| `skills/antigraf/scripts/` | 47 ferramentas: 40 Python, 7 de navegador, uma lista de aparelhos |
| `assets/` | o ícone, em 512 e 128 pixels |

Leia esta página pelo que ela promete. Leia o documento completo para a tolerância exata de cada checagem.

## Instalação

Sem gerenciador de pacotes, sem `pip install`, sem conta. É uma pasta de texto e scripts simples.

**Opção 1: copiar a pasta (recomendado)**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

Depois mova `Antigraf/skills/antigraf/` para onde o seu agente carrega habilidades. A pasta mantém o
nome, mantém `SKILL.md` no topo e viaja com as pastas `references/` e `scripts/`.

| Ambiente | Onde a pasta vai |
|---|---|
| A pasta de habilidades de um projeto | `<seu projeto>/.claude/skills/antigraf/` |
| Todos os projetos da máquina | `~/.claude/skills/antigraf/` |
| Qualquer outro | a pasta de habilidades que o seu ambiente lê |

**Opção 2: sem acesso a pastas**

Cole o texto de `skills/antigraf/SKILL.md` no campo de instruções personalizadas do seu agente. A
habilidade roda só com esse texto, sem as ferramentas: as verificações passam a ser feitas à mão pelo
modelo, e a tabela final diz quais foram feitas assim.

**Opção 3: sem agente**

As ferramentas são scripts comuns.

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

Requisitos: **Python 3.8 ou mais novo** (só biblioteca padrão), **Node 18 ou mais novo** para as
ferramentas de navegador, e um navegador baseado em Chromium (Edge ou Chrome) para percorrer e clicar.
Cada peça é opcional: se faltar uma, a habilidade desce um nível e diz isso na tabela final em vez de
adivinhar.

## Como usar

Uma linha basta:

```
/antigraf https://example.com
```

A partir daí ele roda em seis passos.

| Passo | O que acontece |
|---|---|
| **1. Perguntar o trabalho** | 1 Clonar, 2 Recriar, 3 Melhorar, 4 Estudar. Nada é copiado antes da sua resposta. |
| **2. Perguntar só o necessário** | Clonar não pergunta mais. Recriar pergunta o que muda. Melhorar pede o seu projeto e o que você realmente quer. Estudar pergunta a profundidade e a parte que importa. |
| **3. Escrever um plano que você vê** | No máximo sete passos nas suas palavras, um marcado *para aqui*, salvo em disco para outro modelo retomar no mesmo passo. |
| **4. Estudar, planejar, construir, medir** | As mesmas verificações rodam no original e na sua cópia, rodada após rodada. |
| **5. Fechar as lacunas** | Cada linha que falha volta como a próxima mensagem, e uma linha que passava e agora falha é marcada como regressão. |
| **6. Mostrar a tabela** | Nove áreas, cada uma sobre 100, nomeando o que a segura. Depois as suas opções. |

A tabela final é assim, e é calculada a partir da prova registrada, nunca digitada pelo modelo:

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  ----------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4
Behaviour, flows          20%     1     3        1  failing: G6, G7, G23
Phone & PWA              100%     2     0        0
Motion & 3D               33%     1     0        2  not measured: G25, G26
Media & speed            100%     2     0        0
Accessibility              0%     0     1        0  failing: G9
Sources, repairs          75%     3     0        1  not measured: G22
Evidence, proof, pages    40%     2     2        1  failing: G11, G12
```

Uma verificação que nunca rodou, ou que respondeu desconhecido, conta como **zero**, então o total nunca
pode elogiar a cópia. Todo trabalho termina com esta tabela e três ofertas: seguir empurrando, aceitar
uma diferença como sua com uma renúncia assinada, ou parar.

O selo fecha em **100%** e só então: cada linha aprovada, nada desconhecido, nenhuma diferença sem
explicação. Até lá a tabela diz o que está aberto, por verificação e por linha, por exemplo
`G5 @1440 hero pad 16 12 -4 +-4`.

## Perguntas que as pessoas fazem

**Dá para copiar o site inteiro, ou só a primeira página?**
Ela segue todos os links do mesmo site e captura cada página em três larguras, celulares e tablets. O que não alcançou, as páginas não percorridas e os controles não pressionados ficam escritos como *não explorado* e seguram o selo. Você sempre vê a conta: páginas achadas contra páginas percorridas.

**Ela me entrega o código-fonte do original?**
Não. Ela mede o original e você constrói a sua cópia com a sua tecnologia. O que sai é o seu código, não uma cópia do deles.

**Funciona com um modelo que não vê imagens?**
Sim. O design viaja como números: tamanhos, cores, espaçamento, tipografia, áreas clicáveis. As imagens servem para comparar, nunca para aprender, então um modelo só de texto também constrói a partir das medidas.

**Do que ela se recusa a copiar?**
Lógica de servidor, credenciais, tokens de sessão, pagamentos e dados contábeis. Um campo com esse formato para a execução e vai para `HANDOVER.md`, para você saber o que ligar sozinho.

**Como sei que realmente funcionou?**
Cada checagem deixa um arquivo com seu próprio código de saída, e a tabela final é calculada desses registros. Uma checagem que não rodou, ou que respondeu desconhecido, vale zero. O modelo não pode escrever a própria nota.

**Que tipos de fonte ela atende?**
Sites e apps web de várias páginas, apps de celular e comportamento PWA, telas de streaming com player, lojas e catálogos, sites de documentação, e cenas 3D com chamadas de desenho, shaders e movimento.

**Do que ela precisa para rodar?**
Python 3.8 ou mais, só com a biblioteca padrão, Node 18 ou mais para as ferramentas de navegador, e um navegador Chromium. Sem instalar pacotes, sem conta, sem chave.

## Estado honesto

Dois numeros diferentes aparecem aqui de proposito: a pontuacao e o que os portoes dizem de um par real original-copia, e os comprovados sao quantos pares passaram todos os portoes. O segundo decide se a ferramenta esta pronta.

**Capacidade medida, nao declarada.** Todos os portoes existem e executam. O que realmente passou e contado a parte do que um unico par pontuou.

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 80.4% out of 100 - the three-page test pair (round 6)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 100% | 2 | 0 | 0 | - |
| Behaviour, flows | 60% | 3 | 0 | 2 | not measured: G7, G19 |
| Phone & PWA | 100% | 2 | 0 | 0 | - |
| Motion & 3D | 33% | 1 | 0 | 2 | not measured: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Accessibility | 100% | 1 | 0 | 0 | - |
| Sources, repairs | 100% | 4 | 0 | 0 | - |
| Evidence, proof, pages | 40% | 2 | 2 | 1 | failing: G11, G12 |
| **Total** | **80.4%** | 20 | 2 | 5 | 7 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### Portao por portao

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates  ·  0 proven on a real original-to-copy pair  ·  1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | measured | the three-page test pair round 6 |
| Icons and pictures, one partner each | G8, G17 | measured | the three-page test pair round 6 |
| Every page walked, planned and shipped | G11 | measured | the three-page test pair round 6 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | the three-page test pair round 6 |
| States: hover, focus, open, empty, error | G6 | measured | the three-page test pair round 6 |
| Motion: durations, easings, scroll | G13 | measured | the three-page test pair round 6 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | the three-page test pair round 6 |
| Speed and weight budgets | G15 | measured | the three-page test pair round 6 |
| Logic: same input, same answer, no secrets | G19 | measured | the three-page test pair round 6 |
| Defects found, and the copy repaired | G20, G21 | measured | the three-page test pair round 6 |
| 3D scene read as numbers | G25 | measured | the three-page test pair round 6 |
| 3D motion compared frame by frame | G26 | measured | the three-page test pair round 6 |
| Server seams listed for you to hook up | G16 | measured | the three-page test pair round 6 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | the three-page test pair round 6 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| the three-page test pair | unknown | round 6 | 20 of 27 | 2 | 5 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**A metade que mede funciona. A metade que constrói ainda não produziu uma cópia que passasse em todas as
verificações.**

O bloco de progresso do documento completo é escrito a partir dos registros em disco, nunca à mão. Hoje
ele diz 27 verificações, 0 provadas em um par real original-cópia. Preferimos mostrar um zero e o motivo
a um cem e uma mentira.

## Licença

Duas licenças, você escolhe: **Apache License 2.0** ([LICENSE-APACHE](LICENSE-APACHE)) ou **MIT** ([LICENSE-MIT](LICENSE-MIT)). A versão curta, e o que as licenças não cobrem, está em [LICENSE.md](LICENSE.md). O ícone e o nome ficam com o projeto; um fork é aceitável desde que diga que é um fork.

## Contribuição e segurança

Como propor uma alteração, e a única regra que importa (uma verificação nova precisa ser mostrada falhando primeiro), está em [CONTRIBUTING.md](CONTRIBUTING.md). Como avisar de uma falha de segurança em privado, e do que o Antigraf protege você ou não, está em [SECURITY.md](SECURITY.md).

## A linha que não cruzamos

O Antigraf copia como uma página parece e como se comporta no seu navegador. Ele **não** copia lógica de
servidor, credenciais, tokens de sessão, dados de pagamento ou contábeis, e para e recusa quando
encontra um campo com esse formato. Essas peças são escritas em `HANDOVER.md`, para você saber exatamente
o que ligar ao seu próprio backend, legalmente e nos seus termos.

**Não toleramos pirataria, compartilhamento de contas, burla de paywall, DRM ou login, extração de dados
privados, nem reprodução do conteúdo, da marca ou dos recursos de outros sem permissão.** Use o Antigraf
com o que é seu, o que tem licença aberta, ou o que você tem permissão de estudar. Imagens, fontes, logos
e textos sem direitos são substituídos pelos seus, e uma licença que ninguém esclareceu mantém o selo
travado até que você a esclareça ou a troque.

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf. Uma habilidade de duplicação, clonagem ou estudo para agentes de código com IA.</sub>
</p>
