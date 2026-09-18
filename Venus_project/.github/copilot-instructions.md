# VENUS M2 — COPILOT PROJECT INSTRUCTIONS

## 1. Projet

Venus M2 est un assistant Web Django destiné principalement aux étudiants et au personnel de l'ESTM.

Objectif scientifique principal :

Évaluer l'apport du RAG en comparant un LLM seul avec un LLM + RAG sur un corpus institutionnel.

Architecture cible :

Django monolithique
→ Chat
→ Knowledge
→ Retrieval
→ contexte documentaire
→ LLM
→ réponse + sources

Ne pas transformer le projet en architecture microservices.

---

## 2. Workspace et Git

Workspace de référence :

`D:\Venus_M2\Venus_project`

Branche de développement :

`m2-rag`

Dépôt GitHub :

`SebAbba09/venus`

Règles impératives :

* Ne jamais travailler sur `main`.
* Ne jamais proposer ni exécuter de fusion vers `main` sans demande explicite.
* Ne jamais utiliser `E:` comme environnement de développement.
* Ne jamais introduire de chemin absolu vers `E:`.
* `E:` peut être débranché à tout moment.
* Considérer `D:\Venus_M2\Venus_project` comme la seule source locale de travail.
* Préserver les commits Git existants.
* Ne jamais utiliser de commande Git destructive sans demande explicite.
* Vérifier l'état du dépôt avant toute opération Git importante.
* Ne pas commit ou push automatiquement sauf demande explicite.
* Lorsqu'un push est explicitement demandé, pousser uniquement vers `m2-rag`.

---

## 3. État fonctionnel déjà établi

Le projet possède déjà :

* `users`
* `chat`
* authentification Django
* `Conversation`
* `Message`
* endpoint chat POST JSON
* contexte conversationnel limité
* `TextGenerator`
* `StubGenerator`
* `TransformersGenerator` générique
* gestion de backend configurable
* tests `users` / `chat`
* application `knowledge`
* `Category`
* `Document`
* `DocumentVersion`
* `DocumentChunk`
* administration Knowledge
* migrations Knowledge

Le générateur ne doit pas être verrouillé sur BlenderBot.

BlenderBot est un élément historique du projet L3 et ne constitue pas le choix définitif de Venus M2.

Ne pas reconstruire ou remplacer inutilement ces composants existants lorsqu'ils répondent déjà au besoin.

---

## 4. Environnement technique

Python :

`3.14.4`

Django :

`5.2.17`

Dépendances M2 minimales actuellement :

```text
Django==5.2.17
python-dotenv==1.2.3
torch==2.10.0
transformers==4.57.3
```

Environnement virtuel :

`D:\Venus_M2\Venus_project\.venv`

Les tests doivent fonctionner hors ligne lorsque cela est possible.

Ne télécharger aucun modèle pendant les tests automatisés.

Ne pas installer de gros modèles uniquement pour valider du code.

---

## 5. Architecture LLM

Utiliser une abstraction de génération model-agnostic.

Architecture visée :

```text
TextGenerator
├── StubGenerator
├── TransformersGenerator
├── Ollama backend futur
└── API backend futur
```

Ne choisir aucun modèle LLM définitif sans benchmark.

Candidats futurs possibles :

* Qwen
* Phi
* Gemma
* Ministral

Le benchmark sera réalisé dans une étape dédiée avec un protocole commun et reproductible.

Ne pas commencer le benchmark avant que l'architecture RAG nécessaire à la comparaison soit suffisamment stable.

---

## 6. Architecture RAG

Architecture finale visée :

```text
Knowledge
→ extraction
→ nettoyage
→ chunking
→ embeddings
→ PostgreSQL + pgvector
→ retrieval
→ contexte
→ LLM
→ réponse + sources
```

Règles :

* SQLite est acceptable pour les tests et les premières étapes.
* PostgreSQL + pgvector est la cible finale du système RAG.
* Ne pas introduire FAISS comme architecture finale sans décision explicite.
* Ne pas ajouter plusieurs vector stores uniquement par commodité.
* Ne pas installer embeddings/vector stores avant l'étape prévue.

---

## 7. Knowledge

Modèles principaux :

* `Category`
* `Document`
* `DocumentVersion`
* `DocumentChunk`

Les documents ESTM réels ne sont pas encore disponibles.

Ne jamais bloquer le développement à cause de leur absence.

Pour les tests, utiliser uniquement des données explicitement fictives et clairement identifiées, par exemple :

`DEMO - Calendrier académique`

Ne jamais présenter des données inventées comme des documents officiels de l'ESTM.

Les données de démonstration doivent rester clairement séparées des données institutionnelles réelles.

---

## 8. Séparation stricte des étapes

Toujours respecter exactement le périmètre de la tâche demandée.

Ne pas commencer automatiquement l'étape suivante.

Exemple :

Si la tâche porte sur l'ingestion documentaire, ne pas commencer :

* embeddings
* PostgreSQL
* pgvector
* retrieval
* RAG
* benchmark LLM

Si une dépendance entre étapes est découverte, la signaler dans le rapport sans implémenter l'étape suivante.

Une tâche terminée doit rester terminée jusqu'à ce qu'une nouvelle tâche soit explicitement demandée.

---

## 9. Méthode de travail

Pour une tâche complexe :

1. Inspecter uniquement les fichiers pertinents.
2. Comprendre le comportement actuel concerné.
3. Définir brièvement l'approche nécessaire.
4. Implémenter la modification.
5. Exécuter les tests pertinents.
6. Vérifier le diff.
7. Vérifier l'état Git.
8. S'arrêter lorsque l'objectif demandé est atteint.

Pour une tâche simple, agir directement sans lancer un audit général ni produire un plan inutile.

Ne pas refaire un audit général si l'état du projet est déjà connu.

Ne pas relire inutilement toute la base de code.

Utiliser le plus petit ensemble de fichiers, outils et dépendances nécessaire.

---

## 10. Qualité du code

Priorité :

`correctness > simplicité > optimisation prématurée`

Éviter :

* duplication
* sur-ingénierie
* abstraction inutile
* dépendances inutiles
* code mort ajouté uniquement "pour plus tard"

Ne pas modifier plusieurs composants sans nécessité.

Ne pas résoudre un problème par une réécriture complète lorsqu'une modification ciblée suffit.

Conserver les interfaces existantes lorsqu'elles sont compatibles avec la tâche.

Privilégier un code lisible, testable, maintenable et défendable dans un mémoire de Master 2.

---

## 11. Tests

Toute modification fonctionnelle significative doit être accompagnée de tests adaptés.

Avant de déclarer une tâche terminée :

* exécuter les tests pertinents ;
* exécuter `python manage.py check` lorsque pertinent ;
* exécuter `git diff --check`.

Les tests ne doivent pas dépendre d'Internet ou du téléchargement d'un modèle sauf demande explicite.

Ne pas supprimer ou désactiver des tests existants simplement pour faire passer la suite.

---

## 12. Git

Après une tâche importante :

* vérifier `git status --short --branch` ;
* vérifier `git diff --check` ;
* vérifier les fichiers modifiés ;
* ne commit que les fichiers liés à la tâche lorsque le commit est demandé ;
* utiliser un message de commit explicite et descriptif lorsque le commit est demandé.

Ne jamais modifier `main`.

Ne jamais utiliser sans demande explicite :

```text
git reset --hard
git clean -fd
git push --force
réécriture d'historique
suppression massive de fichiers
```

Ne jamais supprimer des modifications utilisateur existantes pour résoudre un problème.

---

## 13. Dépendances

Avant d'ajouter une dépendance :

* vérifier si elle est réellement nécessaire ;
* préférer une dépendance déjà présente lorsqu'elle convient ;
* éviter d'installer des bibliothèques appartenant aux étapes futures ;
* ne pas gonfler `requirements-m2.txt` sans justification.

Après l'ajout d'une dépendance, vérifier que son utilisation est réellement nécessaire à la fonctionnalité demandée.

---

## 14. Chemins et fichiers

Utiliser des chemins relatifs au projet lorsque possible.

Ne jamais coder de chemin `E:\...`.

Les chemins locaux doivent rester compatibles avec :

`D:\Venus_M2\Venus_project`

Ne pas introduire de dépendance à un ancien emplacement du projet.

Les fichiers générés, uploads, modèles locaux, caches et environnements virtuels ne doivent pas être commités.

---

## 15. Modèles et benchmarks

Ne pas choisir le LLM final par défaut.

Ne pas télécharger de gros modèles pour une simple validation de code.

Les comparaisons de modèles seront réalisées avec un protocole commun et reproductible.

Les critères de mesure pourront notamment inclure :

* qualité des réponses ;
* exactitude ;
* pertinence ;
* coût ;
* consommation mémoire ;
* latence ;
* facilité d'intégration.

Le choix final devra être fondé sur les résultats du protocole d'évaluation et non sur une préférence arbitraire.

---

## 16. Communication avec l'utilisateur

Quand une tâche est terminée, fournir un rapport court indiquant :

* ce qui a changé ;
* les fichiers modifiés ;
* les tests exécutés ;
* leur résultat ;
* les dépendances ajoutées si applicable ;
* le commit si un commit a été créé ;
* la prochaine étape logique.

La prochaine étape logique doit uniquement être indiquée à titre informatif et ne doit jamais être implémentée automatiquement.

Ne pas affirmer qu'une tâche est terminée sans validation.

Ne pas entreprendre une autre phase après avoir terminé celle demandée.

---

## 17. Principe général

Venus M2 doit être développé rapidement mais avec une architecture suffisamment propre pour être défendable dans un mémoire de Master 2.

Toute décision importante doit privilégier :

* reproductibilité ;
* simplicité ;
* traçabilité ;
* testabilité ;
* séparation des responsabilités ;
* maintenabilité ;
* possibilité d'évaluer scientifiquement le système.

En cas d'incertitude, préserver l'architecture existante et choisir la modification la plus petite permettant de satisfaire précisément la tâche demandée.

Ne pas inventer de fonctionnalités ou de contraintes qui n'ont pas été demandées.

Ne pas considérer une fonctionnalité comme terminée uniquement parce que le code semble correct : la validation doit être effectuée lorsque cela est possible.
## 18. Évolutivité du chunking

Le chunking doit être conçu pour évoluer vers un système réellement token-aware sans être couplé à un LLM ou à un modèle d'embedding définitif.

Principes :

* la taille des chunks doit être pensée comme une contrainte liée aux tokens ;
* ne pas coupler le chunker à un modèle LLM ou embedding particulier ;
* utiliser une abstraction/interface de comptage ou tokenisation injectable ;
* permettre de brancher ultérieurement le tokenizer réel du modèle d'embedding ou du modèle retenu ;
* ne pas télécharger ni choisir maintenant un modèle uniquement pour fournir son tokenizer ;
* préserver la possibilité de changer de modèle sans réécrire le service d'ingestion ;
* conserver une stratégie de découpage simple, déterministe et testable ;
* privilégier la conservation de la structure documentaire (sections, paragraphes, pages) avant de subdiviser un contenu qui dépasse la taille cible.

Toute évolution ultérieure vers un tokenizer réel doit pouvoir être réalisée par remplacement/configuration de l'adaptateur de tokenisation, sans refonte du pipeline d'ingestion.
