<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Icône d'Antigraf : profil gravé d'une figure couronnée de laurier sur une tuile verte">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <b>Français</b> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>Du grec <i>antígrafo</i> (αντίγραφο) : une copie qui répond à l'original.</b><br>
  Une compétence de duplication, clonage ou étude pour les agents de code IA.<br>
  Elle étudie une source, construit votre propre version<br>
  et <b>prouve</b> sa proximité avec des commandes que vous pouvez relancer.
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="46 scripts, no installs" src="https://img.shields.io/badge/scripts-46%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">
  <img alt="Proven on 0 real pairs" src="https://img.shields.io/badge/proven%20on-0%20real%20pairs-d69e2e?style=flat-square">

  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
</p>

<p align="center">
  <a href="#comment-ça-marche">Comment ça marche</a> ·
  <a href="#quatre-travaux">Quatre travaux</a> ·
  <a href="#ce-qui-le-distingue">Ce qui le distingue</a> ·
  <a href="#installation">Comment l'utiliser</a> ·
  <a href="#comment-lutiliser">Questions</a> ·
  <a href="#les-questions-quon-nous-pose">Statut honnête</a> ·
  <a href="#statut-honnête">La ligne que nous ne franchissons pas</a>
</p>

<br>

Antigraf vit dans votre agent sous la forme d'un paquet d'instructions et d'un jeu de petits outils.
Il parcourt un site, une application mobile ou un jeu, note chaque partie sous forme de nombre, construit
votre propre copie, puis fait répondre les deux côtés aux mêmes contrôles jusqu'à ce que rien n'échoue
et que rien ne reste inconnu.

L'idée n'est pas de dire « ça se ressemble ». L'idée est de montrer la ligne qui diffère encore, et la
commande qui le montre.

<br>

<b>En clair :</b> Antigraf est une compétence de réplication 1:1 pour les agents de code IA. Utilisez-la pour cloner un site web, copier une application web ou un jeu, recréer un design comme le vôtre, ou étudier comment un site est bâti, de l'interface au fond. Elle couvre tout l'ensemble des pages, pas seulement la première : chaque route, section, contrôle, état ouvert, animation, mise en page mobile, comportement hors ligne et scène 3D, chacun comparé à l'original et chacun retenant le verrou à 100% jusqu'à ce qu'il corresponde.

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>Étudier n'importe quoi</h3>
      Pages, écrans, menus, contrôles et ce qui se cache derrière un clic. Chaque nombre porte son origine, donc une supposition ne peut pas se faire passer pour une mesure.
    </td>
    <td width="25%" valign="top">
      <h3>Construire le vôtre</h3>
      Votre copie vit dans votre projet, avec la pile que vous choisissez. Rien de la source ne l'accompagne, sauf ce que vous avez le droit d'utiliser.
    </td>
    <td width="25%" valign="top">
      <h3>Vérifié, pas supposé</h3>
      27 contrôles tournent des deux côtés à chaque tour. Un contrôle jamais lancé, ou qui répond inconnu, bloque le verrou et ne compte jamais comme une réussite.
    </td>
    <td width="25%" valign="top">
      <h3>Prêt pour les agents</h3>
      Un fichier de compétence et des scripts simples, pour que tout modèle et tout environnement pilote les mêmes contrôles. Mesurer ne demande pas d'IA.
    </td>
  </tr>
</table>

<br>

## Comment ça marche

Désignez une source, choisissez un travail, et il avance en cinq étapes :

1. **Étudier :** parcourir la source, ouvrir ce qui se cache derrière un clic et l'enregistrer en nombres.
2. **Planifier :** une ligne par page, section, contrôle, état et route, chacune avec le contrôle qui la juge.
3. **Construire :** écrire votre copie, le visible d'abord. Les pièces serveur sont nommées, jamais copiées.
4. **Vérifier :** les mêmes contrôles tournent sur l'original et sur votre copie, tour après tour.
5. **Affiner :** chaque ligne en échec revient comme le prochain message de construction, jusqu'à ce que le verrou se ferme.

## Quatre travaux

`/antigraf` pose une seule question avant que quoi que ce soit n'arrive.

| # | Travail | Ce qu'il fait |
|---|---|---|
| **1** | **Cloner** | Copier la source à l'identique. Il ne demande rien de plus et verrouille l'objectif à 100%. |
| **2** | **Recréer** | Copier comme votre propre version. Il demande ce qui doit changer : couleurs, marque, icônes, textes. |
| **3** | **Améliorer** | Confronter une source à votre projet, montrer ce qu'elle fait mieux et finir par une courte liste de prochaines étapes. |
| **4** | **Étudier** | Lecture seule, rien n'est exécuté, les secrets sont masqués. Avec quoi c'est construit, de haut en bas. |

Tout travail terminé se termine par un tableau honnête de 1 à 100 par domaine, ce qui retient chaque
domaine, et vos options pour la suite.

## Ce qui le distingue

| | **Antigraf** | Une compétence de clonage classique |
|---|---|---|
| Où il tourne | Tout environnement, tout modèle. Bibliothèques standard de Python 3 et Node | Lié à une boucle d'agent |
| Comment il décide « terminé » | 27 contrôles, chacun avec son code de sortie, tous à chaque tour | Le modèle dit que ça a l'air bon |
| « Non comparé » | Bloque toujours le verrou | Souvent compté comme une réussite |
| Différences que vous acceptez | Les vôtres seulement, écrites par vous, jamais écartées en silence | Non modélisé |
| Gros travaux | Découpés en couloirs, 3 assistants au plus, règle des 60 minutes | Une longue exécution qui dérive peu à peu |
| Ce qu'il affirme de lui-même | Un bloc de progression généré depuis les registres réels | Ce que dit la page |

Aucun score global ne cache quelle ligne a échoué. Les images seules ne valident jamais rien. Un modèle
plus faible, ou qui ne voit pas les images, ne baisse jamais la barre : il dépense moins et le dit.

## Où se trouve quoi

| Chemin | Contenu |
|---|---|
| `skills/antigraf/SKILL.md` | la compétence elle-même : travaux, étapes, niveaux, espace de travail, tours, règles |
| `skills/antigraf/README.md` | le document complet : contrôles, tolérances, progression, disposition |
| `skills/antigraf/references/` | 12 guides : contrôles, planification, fidélité, scène, remise, preuves |
| `skills/antigraf/scripts/` | 46 outils : 39 Python, 7 navigateur, une liste d'appareils |
| `assets/` | l'icône, en 512 et 128 pixels |

Lisez cette page pour ce qu'elle promet. Lisez le document complet pour la tolérance exacte de chaque contrôle.

## Installation

Pas de gestionnaire de paquets, pas de `pip install`, pas de compte. C'est un dossier de texte et de
scripts simples.

**Option 1 : copier le dossier (recommandé)**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

Puis déplacez `Antigraf/skills/antigraf/` là où votre agent charge les compétences. Le dossier garde
son nom, garde `SKILL.md` en haut, et voyage avec ses dossiers `references/` et `scripts/`.

| Environnement | Où va le dossier |
|---|---|
| Le dossier de compétences d'un projet | `<votre projet>/.claude/skills/antigraf/` |
| Tous les projets de la machine | `~/.claude/skills/antigraf/` |
| Tout autre | le dossier de compétences que lit votre environnement |

**Option 2 : pas d'accès aux dossiers**

Collez le texte de `skills/antigraf/SKILL.md` dans le champ d'instructions personnalisées de votre
agent. La compétence tourne alors avec ce texte seul, sans les outils : les contrôles sont faits à la
main par le modèle, et le tableau final dit lesquels ont été faits ainsi.

**Option 3 : sans agent**

Les outils sont des scripts ordinaires.

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

Prérequis : **Python 3.8 ou plus récent** (bibliothèque standard uniquement), **Node 18 ou plus récent**
pour les outils de navigateur, et un navigateur basé sur Chromium (Edge ou Chrome) pour parcourir et
cliquer. Chaque pièce est facultative : s'il en manque une, la compétence descend d'un niveau et le dit
dans le tableau final au lieu de deviner.

## Comment l'utiliser

Une ligne suffit :

```
/antigraf https://example.com
```

Ensuite, six étapes.

| Étape | Ce qui arrive |
|---|---|
| **1. Demander le travail** | 1 Cloner, 2 Recréer, 3 Améliorer, 4 Étudier. Rien n'est copié avant votre réponse. |
| **2. Demander seulement le nécessaire** | Cloner ne demande rien de plus. Recréer demande ce qui change. Améliorer demande votre projet et ce que vous voulez vraiment. Étudier demande la profondeur et la partie qui compte. |
| **3. Écrire un plan que vous voyez** | Sept étapes au plus, dans vos mots, une marquée *s'arrête ici*, enregistrée sur disque pour qu'un autre modèle reprenne à la même étape. |
| **4. Étudier, planifier, construire, mesurer** | Les mêmes contrôles tournent sur l'original et sur votre copie, tour après tour. |
| **5. Fermer les écarts** | Chaque ligne en échec revient comme le prochain message, et une ligne qui passait avant et échoue maintenant est signalée comme régression. |
| **6. Montrer le tableau** | Huit domaines, chacun sur 100, chacun nommant ce qui le retient. Puis vos options. |

Le tableau final ressemble à ceci, et il est calculé depuis la preuve enregistrée, jamais tapé par le
modèle :

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  -----------------------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4 contrast
Behaviour, flows           0%     0     0        5  not measured: G6, G7, G23, G24, G19
Phone & PWA                0%     0     1        1  failing: G14 tap targets
Motion & 3D               33%     1     0        2  not measured: G25, G26
Media & speed            100%     2     0        0
Sources, repairs          50%     2     0        2  not measured: G22, G16
Evidence, proof, pages    60%     3     1        1  failing: G12
```

Un contrôle jamais lancé, ou qui a répondu inconnu, compte comme **zéro**, donc le total ne peut jamais
flatter la copie. Tout travail se termine par ce tableau et trois offres : pousser plus loin, accepter
une différence comme la vôtre avec une renonciation signée, ou arrêter.

Le verrou se ferme à **100%** et seulement alors : chaque ligne passe, rien d'inconnu, aucune différence
inexpliquée. D'ici là le tableau dit ce qui est ouvert, par contrôle et par ligne, par exemple
`G5 @1440 hero pad 16 12 -4 +-4`.

## Les questions qu'on nous pose

**Peut-elle copier tout un site, ou seulement la première page ?**
Elle suit tous les liens du même site et capture chaque page en trois largeurs, sur mobile et tablette. Ce qu'elle n'a pas atteint, les pages non parcourues et les contrôles non pressés, est écrit comme *non exploré* et retient le verrou. Vous voyez toujours le compte : pages trouvées contre pages parcourues.

**Me donne-t-elle le code source de l'original ?**
Non. Elle mesure l'original et vous construisez votre copie avec vos outils. Ce qui est livré est votre code, pas une copie du sien.

**Fonctionne-t-elle avec un modèle qui ne voit pas les images ?**
Oui. Le design passe par des nombres : tailles, couleurs, espacements, typographie, zones cliquables. Les images servent à comparer, jamais à apprendre, donc un modèle texte seul construit aussi à partir des mesures.

**Qu'est-ce qu'elle refuse de copier ?**
La logique serveur, les identifiants, les jetons de session, les paiements et les données comptables. Un champ de cette forme arrête l'exécution et part dans `HANDOVER.md`, pour que vous sachiez quoi brancher.

**Comment savoir si ça a vraiment marché ?**
Chaque contrôle laisse un fichier avec son code de sortie, et le tableau final est calculé à partir de ces registres. Un contrôle qui n'a pas tourné, ou qui a répondu inconnu, vaut zéro. Le modèle ne peut pas écrire sa propre note.

**Quels types de sources gère-t-elle ?**
Sites web et applications multi-pages, applications mobiles et comportement PWA, interfaces de streaming avec lecteur, boutiques et catalogues, sites de documentation, et scènes 3D avec leurs appels de dessin, shaders et mouvement.

**De quoi a-t-elle besoin pour tourner ?**
Python 3.8 ou plus, bibliothèque standard seulement, Node 18 ou plus pour les outils navigateur, et un navigateur Chromium. Aucun paquet à installer, aucun compte, aucune clé.

## Statut honnête

Deux nombres differents sont montres ici a dessein : la note dit ce que les portes pensent d'un vrai couple original-copie, et le nombre de couples prouves dit combien ont passe toutes les portes. C'est le second qui decide si l'outil est termine.

**Une capacite mesuree, pas declaree.** Toutes les portes existent et s'executent. Ce qui a vraiment passe est compte a part de ce qu'un seul couple a obtenu.

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 54.0% out of 100 - test-pair-3page (round 1)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 100% | 2 | 0 | 0 | - |
| Behaviour, flows | 0% | 0 | 5 | 0 | failing: G6, G7, G23, G24, G19 |
| Phone & PWA | 0% | 0 | 2 | 0 | failing: G14, G18 |
| Motion & 3D | 33% | 1 | 2 | 0 | failing: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Sources, repairs | 50% | 2 | 1 | 1 | failing: G16 |
| Evidence, proof, pages | 60% | 3 | 2 | 0 | failing: G1, G12 |
| **Total** | **54.0%** | 13 | 13 | 1 | 14 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### Porte par porte

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates · 0 proven on a real original-to-copy pair · 1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | proven | test-pair-3page checks/round-1 |
| Icons and pictures, one partner each | G8, G17 | proven | test-pair-3page checks/round-1 |
| Every page walked, planned and shipped | G11 | proven | test-pair-3page checks/round-1 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | test-pair-3page checks/round-1 |
| States: hover, focus, open, empty, error | G6 | measured | test-pair-3page checks/round-1 |
| Motion: durations, easings, scroll | G13 | proven | test-pair-3page checks/round-1 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | test-pair-3page checks/round-1 |
| Speed and weight budgets | G15 | proven | test-pair-3page checks/round-1 |
| Logic: same input, same answer, no secrets | G19 | measured | test-pair-3page checks/round-1 |
| Defects found, and the copy repaired | G20, G21 | proven | test-pair-3page checks/round-1 |
| 3D scene read as numbers | G25 | measured | test-pair-3page checks/round-1 |
| 3D motion compared frame by frame | G26 | measured | test-pair-3page checks/round-1 |
| Server seams listed for you to hook up | G16 | measured | test-pair-3page checks/round-1 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | test-pair-3page checks/round-1 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| test-pair-3page | unknown | round 1 | 13 of 27 | 13 | 0 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**La moitié qui mesure fonctionne. La moitié qui construit n'a pas encore produit une copie passant
tous les contrôles.**

Le bloc de progression du document complet est écrit depuis les registres sur disque, jamais à la main.
Il indique aujourd'hui 27 contrôles, 0 prouvé sur un vrai couple original-copie. Nous préférons vous
montrer un zéro et sa raison plutôt qu'un cent et un mensonge.

## La ligne que nous ne franchissons pas

Antigraf copie l'apparence d'une page et son comportement dans votre navigateur. Il ne copie **pas**
la logique serveur, les identifiants, les jetons de session, les données de paiement ou de comptabilité,
et il s'arrête et refuse quand il trouve un champ de cette forme. Ces pièces sont écrites dans
`HANDOVER.md`, pour que vous sachiez exactement quoi brancher à votre propre backend, légalement et
selon vos conditions.

**Nous ne cautionnons pas le piratage, le partage de comptes, le contournement de paywall, de DRM ou de
connexion, l'extraction de données privées, ni la reproduction du contenu, de la marque ou des
ressources d'autrui sans permission.** Utilisez Antigraf sur ce qui vous appartient, ce qui est sous
licence ouverte, ou ce que vous avez le droit d'étudier. Les images, polices, logos et textes sans
droits sont remplacés par les vôtres, et une licence que personne n'a clarifiée garde le verrou fermé
jusqu'à ce que vous la clarifiiez ou la changiez.

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf. Une compétence de duplication, clonage ou étude pour les agents de code IA.</sub>
</p>
