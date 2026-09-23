# Experiment reports

| Date | Jalon | Statut | Résumé |
|---|---|---|---|
| 2026-09-18 | Retrieval embeddings | Terminé | Évaluation déterministe des rankings Qwen et GTE sur 33 chunks et 132 questions, avec métriques Hit@K, MRR et nDCG. |
| 2026-09-18 | Analyse retrieval | Terminé | Analyse scientifique comparative Qwen vs GTE : sous-groupes, erreurs, multi-chunk, tests statistiques (McNemar, bootstrap). Qwen supérieur globalement (small effect), GTE meilleur sur general_estm et international. |
| 2026-09-19 | Revue méthodologique | REVIEWED | McNemar exact (Hit@1 p=0.0075 sig., Hit@5 p=0.064 non sig.), bootstrap CIs confirmés, Cohen's d confirmé (small). Analyse gelée avec corrections de formulation. |
| 2026-09-19 | Runtime embeddings | Terminé | Benchmark coût/performance CPU : GTE 3-4× plus rapide que Qwen (encodage, chargement), peak RSS plus bas (2.4 vs 3.3 Go), disque 1.9× plus petit. Retrieval produit scalaire négligeable (~4 μs). |
| 2026-09-19 | Décision embeddings | DECIDED | Qwen3-Embedding-0.6B retenu comme modèle de référence RAG ; GTE conservé comme baseline/alternative orientée ressources. |
| 2026-09-19 | Protocole RAG end-to-end | PROTOCOL | Protocole gelé pour comparer Qwen et GTE à génération identique sur 132 questions, K=5, avec évaluation humaine aveugle et baseline sans RAG. |
| 2026-09-23 | A1 — Annotation qualitative de la génération | Terminé / gelé | Annotation qualitative des 132 questions ; analyse des 13 Miss@5 et des 21 générations atteignant `max_new_tokens=256`. 21/132 (15,9 %) atteignent la limite, mais 5/132 (3,8 %) présentent un effet négatif observable associé à cette limite ; dans 4 cas, la troncature constitue la cause principale retenue. Parmi ces 21 cas, 20/21 ont Hit@5 = 1. |

## Comptes rendus

- `2026-09-18_retrieval_evaluation.md`
- `2026-09-18_retrieval_analysis.md`
- `2026-09-19_retrieval_analysis_review.md`
- `2026-09-19_embedding_runtime_benchmark.md`
- `2026-09-19_rag_end_to_end_protocol.md`
- `2026-09-23_A1_generation_analysis.md` — compte rendu final et gelé de A1
- `2026-09-22_A1_generation_analysis_v1.md` — version préliminaire conservée pour traçabilité
