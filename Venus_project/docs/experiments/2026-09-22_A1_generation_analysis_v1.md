# Analyse expérimentale A1 — génération RAG et annotation qualitative des cas tronqués

**Date : 22 septembre 2026**
**Expérience : `benchmark_20260921_final_A1`**
**Configuration : Qwen/Qwen3-Embedding-0.6B + Qwen/Qwen2.5-1.5B-Instruct, top-k=5, CPU, float16, `do_sample=false`, `temperature=0`, `max_new_tokens=256`.

> **Statut : version préliminaire / historique.**
> Cette analyse constitue une première annotation exploratoire réalisée avant la stabilisation de la grille A1. Elle est conservée pour la traçabilité méthodologique. Les résultats de référence sont ceux du compte rendu final `2026-09-23_A1_generation_analysis.md`.
## 1. Objet de l'analyse

Cette analyse complète l'évaluation quantitative du benchmark par une inspection qualitative des 21 générations dont `termination_reason=max_new_tokens`. L'objectif est de distinguer :

- l'effet propre de la borne de génération ;
- les problèmes de focalisation ou de surproduction ;
- les erreurs de génération observables malgré un retrieval correct ;
- les cas où le retrieval lui-même doit être considéré comme facteur explicatif.

L'analyse ne transforme pas les observations qualitatives en score artificiel. Elle utilise des catégories explicites et conserve un statut de vérification lorsqu'une comparaison avec le chunk réellement récupéré est encore nécessaire.

## 2. Constats quantitatifs établis avant annotation

Le benchmark contient 132 questions. Dans A1 :

| Indicateur | Résultat |
|---|---:|
| Hit@1 | 101/132 = 76,5 % |
| Hit@5 | 119/132 = 90,2 % |
| Miss@5 | 13/132 = 9,8 % |
| Terminaison EOS | 111/132 = 84,1 % |
| `max_new_tokens` | 21/132 = 15,9 % |
| `max_new_tokens` + Hit@5 | 20/21 = 95,2 % |
| `max_new_tokens` + Miss@5 | 1/21 = 4,8 % |

Le cas `Q122` est le seul cas qui cumule `Miss@5` et `max_new_tokens`. Son premier chunk pertinent est au rang 12.

## 3. Protocole d'annotation

Chaque cas reçoit quatre dimensions principales :

1. **Complétude** : réponse manifestement incomplète ou apparemment complète en surface ;
2. **Focalisation** : ciblée, mixte, ou dérive manifeste ;
3. **Problème dominant observé** : troncature, surproduction/dérive, incohérence interne, erreur de catégorie, ou combinaison ;
4. **Statut de grounding** : laissé à vérifier lorsque le jugement exige la comparaison fine entre la réponse et les cinq chunks récupérés.

Cette prudence est nécessaire : `Hit@5=1` prouve la présence d'au moins un chunk pertinent dans les cinq premiers, pas que toutes les affirmations de la réponse sont supportées par ce contexte.

## 4. Résultat de l'annotation des 21 cas

**17/21 (81,0 %) présentent une interruption textuelle manifestement dommageable.**
**4/21 (19,0 %) paraissent suffisamment complètes en surface malgré `max_new_tokens=256`**, mais deux d'entre elles portent un risque qualitatif qui nécessite vérification (`Q038`, `Q072`). `Q030` et `Q134` constituent les exemples les plus nets de sortie textuellement complète malgré l'absence d'EOS.

### Cas critiques

**Q122** : cas prioritaire. Il combine échec du retrieval à `k=5`, rang pertinent 12 et troncature. Il doit être utilisé comme exemple de chaîne d'échec retrieval + génération, sans attribuer la totalité de l'erreur à un seul composant.

**Q133** : l'erreur la plus nette de nature sémantique. La réponse présente des certifications comme des rôles professionnels, puis est tronquée. La troncature n'explique donc pas à elle seule la mauvaise orientation de la réponse.

**Q083** : exemple particulièrement instructif de retrieval correct mais génération insuffisamment focalisée. Le modèle part de la thématique Marketing-Communication puis introduit des domaines tels que réseaux, cybersécurité et systèmes d'information avant la coupure.

**Q072** : sortie apparemment complète mais incohérente sur les prérequis, avec coexistence de formulations incompatibles sur le niveau de diplôme. Ce cas montre qu'une réponse terminée n'est pas nécessairement une réponse fiable.

### Cas illustrant la surproduction

Q011, Q021, Q038, Q081, Q083, Q112, Q117, Q127 et Q132 montrent, à des degrés différents, une tendance à développer des listes ou des informations au-delà du noyau immédiatement demandé. Cette observation est qualitative ; elle ne doit pas être convertie en taux de hallucination sans vérification des chunks réellement fournis au modèle.

## 5. Tableau d'annotation détaillé

| ID | Hit@5 | Rang | Complétude | Focalisation | Problème observé | Priorité |
|---|---:|---:|---|---|---|---|
| Q010 | 1 | 1 | incomplete | focused | truncation | normal |
| Q011 | 1 | 1 | incomplete | mixed | truncation+overgeneration | normal |
| Q014 | 1 | 1 | incomplete | focused | truncation | normal |
| Q016 | 1 | 1 | incomplete | mixed | truncation+scope_expansion | normal |
| Q021 | 1 | 1 | incomplete | mixed | truncation+scope_mixing | normal |
| Q030 | 1 | 3 | apparently_complete | focused | no_major_observed_generation_error | normal |
| Q038 | 1 | 1 | apparently_complete | mixed | overgeneration_risk | normal |
| Q069 | 1 | 1 | incomplete | mixed | truncation+overgeneration | normal |
| Q072 | 1 | 1 | apparently_complete | mixed | internal_inconsistency | normal |
| Q081 | 1 | 1 | incomplete | mixed | truncation+repetition | normal |
| Q083 | 1 | 1 | incomplete | off_target | truncation+strong_topic_drift | normal |
| Q093 | 1 | 1 | incomplete | focused | truncation | normal |
| Q112 | 1 | 1 | incomplete | off_target | truncation+unsupported_comparison_risk | normal |
| Q117 | 1 | 1 | incomplete | mixed | truncation+unsupported_detail_risk | normal |
| Q120 | 2 | 1 | incomplete | focused | truncation | normal |
| Q122 | 0 | 12 | incomplete | off_target | retrieval_miss+generation_inconsistency+truncation | high |
| Q127 | 1 | 3 | incomplete | mixed | truncation+scope_shift | normal |
| Q131 | 1 | 1 | incomplete | focused | truncation | normal |
| Q132 | 1 | 1 | incomplete | mixed | truncation+scope_expansion | normal |
| Q133 | 1 | 1 | incomplete | off_target | category_error+truncation | high |
| Q134 | 1 | 1 | apparently_complete | focused | no_major_observed_generation_error | normal |

> **Lecture.** `apparently_complete` signifie seulement que la sortie ne présente pas, à l’œil, une coupure syntaxique manifeste. Cela ne vaut pas validation factuelle. `needs_source_check` signifie que la fidélité fine doit être comparée aux cinq chunks récupérés et à la `reference_answer`.

## 6. Interprétation expérimentale

Le résultat le plus robuste est que **la plupart des troncatures ne sont pas causées par un échec de retrieval** : 20 des 21 générations arrivées à `max_new_tokens` ont `Hit@5=1`.

La borne de 256 tokens agit donc comme une contrainte de génération indépendante du fait que le bon contenu ait été retrouvé. Dans plusieurs cas, son impact est visible par un arrêt au milieu d'une phrase ou d'une liste.

Cependant, la borne n'est pas l'unique facteur explicatif. Plusieurs sorties montrent une tendance à la surproduction, à la dérive de sujet ou à l'agrégation d'informations hétérogènes. Ainsi, une augmentation de `max_new_tokens` pourrait réduire les coupures textuelles sans nécessairement résoudre les problèmes de focalisation ou de fidélité.

Le benchmark met donc en évidence une distinction essentielle entre :

- **qualité du retrieval** : le bon chunk est-il présent dans le top-k ?
- **qualité de sélection/exploitation du contexte** : le modèle utilise-t-il le bon contenu ?
- **qualité de génération** : la réponse est-elle complète, exacte et centrée ?
- **terminaison** : la sortie atteint-elle artificiellement la borne ?

## 7. Limites de cette annotation

Cette première annotation est volontairement conservatrice. Elle est fondée sur les sorties A1, les rangs de retrieval et les questions, mais les jugements de **grounding** doivent être finalisés par comparaison systématique avec les cinq chunks récupérés et la `reference_answer` de chaque cas.

En conséquence, les catégories « dérive », « incohérence » et « erreur de catégorie » sont des observations sur la sortie et non des estimations de taux d'hallucination.

Le benchmark lui-même reste un benchmark synthétique de 132 questions, avec `validated=false`. Les résultats doivent donc être interprétés comme une évaluation contrôlée du pipeline sur le snapshot public ESTM, et non comme une mesure exhaustive d'un assistant institutionnel réel.

## 8. Conclusion utilisable dans le mémoire

L'expérience A1 montre que la qualité du retrieval ne suffit pas à garantir une réponse générée de qualité. Avec un **Hit@5 global de 90,2 %**, le retriever fournit fréquemment un élément pertinent au générateur. Néanmoins, **15,9 % des générations atteignent la borne de 256 tokens**, et 17 des 21 sorties concernées présentent une interruption textuelle manifeste dans l'inspection qualitative réalisée ici. Les cas observés montrent également des phénomènes de surproduction, de dérive thématique et d'incohérence sémantique qui peuvent apparaître alors même que le retrieval est correct.

Ces résultats justifient une évaluation en trois étages — retrieval, génération et qualité de bout en bout — plutôt qu'une interprétation fondée uniquement sur Hit@K. Ils justifient également de conserver A1 comme expérience de référence telle qu'exécutée, puis d'évaluer séparément l'effet de paramètres de génération dans une expérience distincte au lieu de modifier rétroactivement A1.

## 9. Artefact associé

- `a1_truncated_cases_annotation_v1.jsonl` — annotation structurée des 21 cas.
