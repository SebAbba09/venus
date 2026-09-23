# Expérience A1 — Annotation qualitative des générations et analyse de la limite `max_new_tokens=256`

**Projet :** Venus M2
**Expérience :** `benchmark_20260921_final_A1`
**Date de l'expérience :** 21 septembre 2026
**Date de finalisation du compte rendu :** 23 septembre 2026
**Population :** 132 questions
**Configuration considérée :** Qwen/Qwen3-Embedding-0.6B + Qwen/Qwen2.5-1.5B-Instruct, `k=5`, CPU, float16, `max_new_tokens=256`

---

## 1. Objet

Cette analyse vise à caractériser qualitativement le comportement du générateur dans l'expérience A1, en particulier lorsque la génération atteint la limite `max_new_tokens=256`.

L'objectif est de distinguer :

1. l'atteinte mécanique de la limite de génération ;
2. son impact fonctionnel observable sur la réponse ;
3. les autres causes d'erreur présentes dans cette même population.

Cette distinction évite de confondre un événement technique de génération avec une dégradation réelle de la qualité de la réponse.

---

## 2. État de l'annotation

L'annotation qualitative A1 est considérée comme **terminée et stabilisée**.

État au moment du gel :

- **132/132** lignes du CSV sont complètes ;
- les **13 Miss@5** ont été examinés individuellement ;
- les **21 générations atteignant `max_new_tokens=256`** ont été examinées individuellement ;
- la grille de lecture a été appliquée de manière homogène ;
- les résultats sont suffisamment stabilisés pour servir de base aux analyses ultérieures et à la rédaction du mémoire.

---

## 3. Population atteignant `max_new_tokens=256`

Sur les 132 questions du benchmark :

- **21/132 = 15,9 %** des générations atteignent exactement la limite de 256 tokens ;
- **111/132 = 84,1 %** ne l'atteignent pas.

Parmi les 21 générations atteignant la limite :

- **16/21 = 76,2 %** sont classées `yes_but_complete` ;
- **5/21 = 23,8 %** présentent un effet négatif identifiable de la limite.

Rapporté à l'ensemble du benchmark, l'impact fonctionnel identifiable concerne donc **5/132 = 3,8 %** des questions.

### Cas avec impact effectif de la troncature

Les cinq cas identifiés sont :

- **Q010**
- **Q069**
- **Q117**
- **Q120**
- **Q122**

Une distinction méthodologique est conservée :

- **Q010, Q069, Q117 et Q120** : la troncature constitue la cause principale de l'erreur ;
- **Q122** : la réponse est également tronquée, mais l'erreur principale retenue reste **`contradiction`**, car une information incorrecte est introduite avant la coupure.

Ainsi, la sous-population contient **5 cas avec effet fonctionnel de la limite**, mais seulement **4 cas dont la cause principale est explicitement classée `truncation`**.

---

## 4. Qualité des 21 réponses atteignant la limite

| Qualité | Nombre | Pourcentage |
|---|---:|---:|
| Correcte | 6 | 28,6 % |
| Partiellement correcte | 14 | 66,7 % |
| Incorrecte | 1 | 4,8 % |
| **Total** | **21** | **100,0 %** |

Au total, **20/21 réponses (95,2 %) sont au moins partiellement correctes**.

Le seul cas classé incorrect est **Q112**. Son problème principal relève de l'interprétation de la demande : la réponse compare principalement le contenu des deux Masters alors que la question portait spécifiquement sur leurs conditions d'admission. La limite de 256 tokens n'explique donc pas à elle seule cet échec.

---

## 5. Complétude

| Complétude | Nombre | Pourcentage |
|---|---:|---:|
| Complète | 11 | 52,4 % |
| Partielle | 9 | 42,9 % |
| Insuffisante | 1 | 4,8 % |
| **Total** | **21** | **100,0 %** |

Plus de la moitié des réponses atteignant la limite restent donc jugées **complètes**.

La valeur `generated_tokens = 256` doit ainsi être interprétée comme un indicateur de saturation de la génération, et non comme un indicateur direct d'échec fonctionnel.

---

## 6. Grounding

| Grounding | Nombre | Pourcentage |
|---|---:|---:|
| Grounded | 11 | 52,4 % |
| Partially grounded | 10 | 47,6 % |
| **Total** | **21** | **100,0 %** |

Dans cette population, le problème n'est donc pas une absence générale de rattachement au contexte récupéré. Des défauts de précision, de sélection d'information, d'exhaustivité ou d'ajouts non nécessaires peuvent cependant subsister malgré un grounding globalement satisfaisant.

---

## 7. Pertinence

| Pertinence | Nombre | Pourcentage |
|---|---:|---:|
| Directement pertinente | 19 | 90,5 % |
| Partiellement pertinente | 2 | 9,5 % |
| **Total** | **21** | **100,0 %** |

La pertinence est élevée dans cette population : **19/21 = 90,5 %** des réponses sont directement pertinentes.

Les difficultés observées concernent donc davantage le contenu précis produit, les omissions, les ajouts ou l'interprétation fine de la demande que l'abandon complet du sujet.

---

## 8. Causes principales d'erreur

| Cause principale | Nombre | Pourcentage |
|---|---:|---:|
| `overgeneration` | 6 | 28,6 % |
| `none` | 6 | 28,6 % |
| `truncation` | 4 | 19,0 % |
| `question_interpretation` | 2 | 9,5 % |
| `unsupported_claim` | 2 | 9,5 % |
| `contradiction` | 1 | 4,8 % |
| **Total** | **21** | **100,0 %** |

Le résultat le plus notable est que **`overgeneration` constitue la cause principale d'erreur la plus fréquente**, à égalité numérique avec les cas classés `none`.

Dans plusieurs réponses longues, le modèle produit suffisamment d'information pour répondre mais poursuit la génération avec des éléments supplémentaires, parfois provenant d'autres parties du contexte ou incorrectement associés à la formation concernée.

### Exemples documentés

- **Q021** : ajout de plusieurs formations alors que la référence n'en identifie explicitement qu'une ;
- **Q038** : ajout de nombreuses activités au-delà de celles attribuées à l'Amicale ;
- **Q083** : insertion de domaines liés aux réseaux/cybersécurité dans le Master Marketing-Communication ;
- **Q133** : confusion entre les rôles associés au CAPM et ceux d'autres certifications.

Ces cas illustrent un comportement où le générateur exploite une partie plus large du contexte que nécessaire ou associe des éléments provenant de domaines voisins, même lorsque le retrieval a fourni le contexte pertinent.

---

## 9. Relation entre retrieval et génération

Parmi les 21 cas atteignant `max_new_tokens=256` :

- **20/21 = 95,2 %** ont **Hit@5 = 1** ;
- **1/21 = 4,8 %** est **Miss@5**.

Le cas Miss@5 est **Q122**.

Cette observation caractérise cette sous-population comme principalement composée de cas où le retrieval fournit déjà au générateur le contexte pertinent dans son top-5.

Le diagnostic doit donc distinguer trois niveaux :

### Retrieval

Dans **20/21 cas**, le chunk pertinent est présent dans le top-5. La disponibilité du contexte pertinent n'est donc généralement pas le problème immédiat de ces générations longues.

### Génération

Les difficultés observées portent davantage sur :

- la surproduction (`overgeneration`) ;
- certaines affirmations insuffisamment supportées ;
- l'interprétation de la question ;
- quelques contradictions ;
- et, dans un nombre limité de cas, la troncature effective.

### Longueur maximale

L'atteinte de la limite est observée dans **21/132 cas (15,9 %)**, mais son impact fonctionnel identifiable n'est retenu que dans **5/132 cas (3,8 %)**.

---

## 10. Interprétation méthodologique

Le principal résultat de cette sous-analyse est la nécessité de distinguer :

> **atteinte de `max_new_tokens=256`**
> de
> **dégradation fonctionnelle due à cette limite**.

Sur les 132 questions :

- 21 générations atteignent la limite ;
- 16 d'entre elles ne montrent pas de perte observable de l'information essentielle ;
- 5 présentent un impact négatif identifiable.

Ainsi, écrire que **« 15,9 % des réponses sont tronquées »** serait insuffisant pour l'interprétation expérimentale.

### Formulation retenue pour le mémoire

> **Sur les 132 questions du benchmark, 21 générations sur 132 (15,9 %) ont atteint la limite de 256 tokens. Toutefois, l'analyse qualitative montre que cette limite n'a entraîné une dégradation observable de la réponse que dans 5 cas (3,8 % du benchmark). Dans les 16 autres cas (76,2 % des générations ayant atteint la limite), les éléments essentiels attendus étaient déjà présents avant l'interruption. Les principales difficultés observées dans cette population relèvent plutôt de l'overgeneration, de l'interprétation de la question et de certaines affirmations insuffisamment supportées.**

---

## 11. Limites d'interprétation

Cette analyse doit être lue avec plusieurs précautions :

1. **La causalité est qualitative.** Le classement de la troncature comme cause principale repose sur l'annotation des sorties et non sur une ré-exécution avec une valeur de `max_new_tokens` supérieure.
2. **`generated_tokens = 256` ne suffit pas à conclure à une perte d'information.** Certaines réponses ont déjà fourni l'essentiel avant l'arrêt.
3. **Les catégories d'erreur sont mutuellement exclusives au niveau de la cause principale**, même si une réponse peut présenter plusieurs défauts secondaires.
4. **Le grounding et la pertinence ne sont pas synonymes de correction.** Une réponse peut rester pertinente et partiellement ou totalement grounded tout en contenant une omission, une surinterprétation ou une information incorrecte.
5. **La sous-population de 21 cas n'est pas indépendante du reste du benchmark.** Elle constitue une analyse ciblée des sorties ayant atteint la limite maximale.

---

## 12. Décisions expérimentales issues de A1

À l'issue de cette analyse :

- l'annotation qualitative A1 est considérée **terminée** ;
- les 13 Miss@5 et les 21 cas `max_new_tokens=256` sont considérés comme **analysés** ;
- le CSV de synthèse est considéré comme **complet à 132/132 lignes** ;
- la grille d'annotation est considérée comme **stabilisée** ;
- aucune modification du benchmark ou du protocole de retrieval n'est nécessaire sur la seule base de cette sous-analyse ;
- les phénomènes d'`overgeneration` sont conservés comme piste d'analyse de la génération, distincte du diagnostic retrieval ;
- la limite `max_new_tokens=256` est documentée comme **facteur contributif dans une minorité de cas**, et non comme cause générale des défauts observés.

---

## 13. Conclusion A1

L'expérience A1 montre que l'analyse du comportement du générateur apporte une information complémentaire aux métriques de retrieval.

Le retrieval est généralement suffisant dans les cas où la génération atteint la limite : **20/21 cas ont Hit@5 = 1**. L'atteinte de `max_new_tokens=256` concerne **15,9 %** du benchmark, mais la dégradation fonctionnelle attribuable à cette limite est ramenée à **3,8 % du benchmark** après annotation qualitative.

La principale difficulté observée dans cette population n'est donc pas la longueur maximale en elle-même. Les erreurs relèvent plus largement de la **surproduction**, de la **sélection d'informations**, de l'**interprétation de la question** et de quelques **affirmations insuffisamment supportées ou contradictoires**.

Ces résultats permettent ainsi de séparer plus proprement les trois dimensions du pipeline étudiées dans A1 :

**retrieval → disponibilité du contexte pertinent ;
génération → sélection, formulation et fidélité de la réponse ;
contrainte de longueur → saturation technique dont l'impact fonctionnel reste limité dans l'ensemble du benchmark.**

---

## 14. Prochaine étape

A1 étant stabilisée, ce document peut servir de compte rendu expérimental de référence et alimenter :

- le chapitre de méthodologie, pour documenter le protocole d'annotation et ses critères ;
- le chapitre d'évaluation expérimentale, pour présenter les résultats de génération en complément des métriques de retrieval ;
- la discussion, pour distinguer les limites du retrieval des comportements propres au générateur.
