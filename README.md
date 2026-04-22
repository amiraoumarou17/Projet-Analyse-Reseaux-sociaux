
# Projet ARS2026 – Analyse des Réseaux Sociaux

**Étudiante** : AISSATOU AMIRA OUMAROU  
**Cours** : Analyse des Réseaux Sociaux – 2026

---

## Réseau étudié : Facebook Ego Network

| Propriété | Valeur |
|---|---|
| Source | [Stanford SNAP](https://snap.stanford.edu/data/ego-Facebook.html) |
| Nœuds | 4 039 utilisateurs Facebook (anonymisés) |
| Liens | 88 234 relations d'amitié |
| Type | Non dirigé, non pondéré |

---

## Téléchargement du dataset 

1. Allez sur : **https://snap.stanford.edu/data/facebook_combined.txt.gz**

---

## Installation des dépendances

```bash
pip install networkx cdlib matplotlib seaborn pandas numpy python-louvain leidenalg igraph
```

---

## Exécution

```bash
python analyse_reseau.py
```

Le script génère automatiquement un dossier `figures/` avec 10 figures.

---

## Fichiers du projet

```
ARS2026/
├── analyse_reseau.py          ← Script Python unique (toutes les 3 parties)
├── facebook_combined.txt      ← Dataset SNAP (à télécharger vous-même)
├── README.md                  ← Ce fichier
└── rapport/rapport.md         ← Rapport complet
```

---

## Technologies

Python 3 · NetworkX · CDlib · Matplotlib · Pandas  
Algorithmes : Louvain · Label Propagation · K-Clique (k=3) · Leiden
