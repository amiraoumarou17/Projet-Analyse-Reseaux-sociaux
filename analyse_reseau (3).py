"""
=======================================================
  Analyse des Réseaux Sociaux – Projet ARS2026
  Réseau : Facebook Ego Network (SNAP)
  Source : https://snap.stanford.edu/data/ego-Facebook.html
  Nœuds  : 4 039 utilisateurs
  Liens  : 88 234 amitiés
=======================================================


"""

# ── Imports ───────────────────
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # mode sans affichage (serveur / colab)
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from collections import Counter
import warnings, time, os
warnings.filterwarnings('ignore')

from cdlib import algorithms

# ── Style des figures ─────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f0f1a', 'axes.facecolor':  '#1a1a2e',
    'axes.edgecolor':   '#444',    'text.color':       '#e0e0e0',
    'axes.labelcolor':  '#e0e0e0', 'xtick.color':      '#aaa',
    'ytick.color':      '#aaa',    'grid.color':       '#2a2a3e',
    'grid.alpha': 0.5,             'font.family':      'monospace',
})
PURPLE = '#7b2fff'
CYAN   = '#00d4ff'
GOLD   = '#ffd700'
RED    = '#ff6b6b'

FIGURES_DIR = 'figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, name), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [fig] {name} sauvegardée")

# ═══════════════════════════════════════════════════════════════
# PARTIE 1 – COLLECTE ET CONSTRUCTION DU RÉSEAU
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  PARTIE 1 – COLLECTE DES DONNÉES")
print("="*60)

# Chargement du fichier SNAP (format : "u v" par ligne, séparateur espace)
DATASET_PATH = 'facebook_combined.txt'

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"\n⚠ Fichier '{DATASET_PATH}' introuvable.\n"
        "Téléchargez-le depuis :\n"
        "  https://snap.stanford.edu/data/facebook_combined.txt.gz\n"
        "puis décompressez-le dans ce dossier."
    )

print(f"\n[1] Chargement de '{DATASET_PATH}' ...")
G = nx.read_edgelist(DATASET_PATH, nodetype=int, create_using=nx.Graph())
print(f"    Nœuds  : {G.number_of_nodes():,}")
print(f"    Liens  : {G.number_of_edges():,}")
print(f"    Dirigé : {nx.is_directed(G)}")

print("\n[2] Description du réseau :")
print("    • Entités (nœuds)   : utilisateurs Facebook anonymisés")
print("    • Relations (liens) : amitiés entre utilisateurs")
print("    • Type              : non dirigé, non pondéré")
print("    • Source            : Stanford SNAP (ego-Facebook)")
print("    • URL               : https://snap.stanford.edu/data/ego-Facebook.html")

# ═══════════════════════════════════════════════════════════════
# PARTIE 2 – ANALYSE DU RÉSEAU
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  PARTIE 2 – ANALYSE DU RÉSEAU")
print("="*60)

# ── A. Distribution des degrés ────────────────────────────────
print("\n[A] Distribution des degrés ...")
degrees  = [d for _, d in G.degree()]
deg_arr  = np.array(degrees)
deg_cnt  = Counter(degrees)
k_vals   = sorted(deg_cnt.keys())
pk_vals  = [deg_cnt[k] / G.number_of_nodes() for k in k_vals]

print(f"    Degré moyen  ⟨k⟩ : {deg_arr.mean():.2f}")
print(f"    Degré médian     : {np.median(deg_arr):.0f}")
print(f"    Degré max        : {deg_arr.max()}")
print(f"    Degré min        : {deg_arr.min()}")
print(f"    Écart-type       : {deg_arr.std():.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Distribution des Degrés – Facebook Ego Network', fontsize=13, color='white')

ax1.bar(k_vals[:100], pk_vals[:100], color=PURPLE, alpha=0.85, width=0.9)
ax1.set(xlabel='Degré k', ylabel='P(k)', title='Distribution P(k)')
ax1.grid(True)

ax2.scatter(k_vals, pk_vals, s=12, color=CYAN, alpha=0.7)
ax2.set_xscale('log'); ax2.set_yscale('log')
ax2.set(xlabel='log k', ylabel='log P(k)', title='Log-log (loi de puissance ?)')
log_k  = np.array([np.log(k) for k in k_vals if k > 0])
log_pk = np.array([np.log(p) for k, p in zip(k_vals, pk_vals) if k > 0 and p > 0])
valid  = np.isfinite(log_k) & np.isfinite(log_pk)
if valid.sum() > 2:
    coefs = np.polyfit(log_k[valid], log_pk[valid], 1)
    x_fit = np.linspace(1, max(k_vals), 200)
    ax2.plot(x_fit, np.exp(coefs[1]) * x_fit**coefs[0], color=RED, lw=2,
             label=f'γ ≈ {-coefs[0]:.2f}')
    ax2.legend(facecolor='#1a1a2e', labelcolor='white')
ax2.grid(True)
savefig('fig1_degree_distribution.png')

# ── B. Composants connectés ────────────────────────────────────
print("\n[B] Composants connectés ...")
components = list(nx.connected_components(G))
comp_sizes = sorted([len(c) for c in components], reverse=True)
print(f"    Nombre de composants    : {len(components)}")
print(f"    Composant géant (GCC)   : {comp_sizes[0]:,} nœuds "
      f"({100*comp_sizes[0]/G.number_of_nodes():.1f}%)")

GCC = G.subgraph(max(components, key=len)).copy()

fig, ax = plt.subplots(figsize=(10, 4))
comp_cnt = Counter(comp_sizes)
ax.bar(range(len(comp_cnt)), list(comp_cnt.values()), color=PURPLE, alpha=0.85)
ax.set_xticks(range(len(comp_cnt)))
ax.set_xticklabels([str(s) for s in comp_cnt.keys()], rotation=45)
ax.set(xlabel='Taille du composant', ylabel='Nombre', title='Distribution des Composants Connectés')
ax.grid(True)
savefig('fig2_components.png')

# ── C. Analyse des chemins ─────────────────────────────────────
print("\n[C] Analyse des chemins (échantillon 300 nœuds) ...")
sample_nodes = list(GCC.nodes())[:300]
path_lengths = []
for n in sample_nodes:
    lengths = nx.single_source_shortest_path_length(GCC, n)
    path_lengths.extend(v for v in lengths.values() if v > 0)

avg_path    = np.mean(path_lengths)
diam_approx = max(path_lengths)
print(f"    Longueur moyenne des chemins : {avg_path:.4f}")
print(f"    Diamètre approximatif        : {diam_approx}")
print(f"    ln(N) = {np.log(GCC.number_of_nodes()):.2f}  →  "
      f"Petit-monde : {'OUI ✓' if avg_path < np.log(GCC.number_of_nodes()) else 'NON'}")

fig, ax = plt.subplots(figsize=(10, 4))
pl_cnt = Counter(path_lengths)
ax.bar(pl_cnt.keys(), pl_cnt.values(), color=CYAN, alpha=0.85)
ax.axvline(avg_path, color=RED, lw=2, linestyle='--', label=f'μ = {avg_path:.2f}')
ax.set(xlabel='Longueur du chemin', ylabel='Fréquence',
       title=f'Distribution des Longueurs de Chemins (avg={avg_path:.2f})')
ax.legend(facecolor='#1a1a2e', labelcolor='white')
ax.grid(True)
savefig('fig3_path_lengths.png')

# ── D. Clustering et densité ───────────────────────────────────
print("\n[D] Clustering et densité ...")
avg_clustering = nx.average_clustering(GCC)
transitivity   = nx.transitivity(GCC)
density        = nx.density(GCC)
print(f"    Coefficient de clustering moyen : {avg_clustering:.4f}")
print(f"    Transitivité globale            : {transitivity:.4f}")
print(f"    Densité                         : {density:.6f}")
print(f"    Sparse ?                        : {'OUI ✓' if density < 0.01 else 'NON'}")

clust_dict = nx.clustering(GCC)
clust_vals  = list(clust_dict.values())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Analyse du Clustering', fontsize=13, color='white')
ax1.scatter([GCC.degree(n) for n in GCC.nodes()],
            [clust_dict[n] for n in GCC.nodes()],
            s=3, alpha=0.3, color=PURPLE)
ax1.set(xlabel='Degré', ylabel='Clustering', title='Clustering vs Degré')
ax1.set_xscale('log'); ax1.grid(True)

ax2.hist(clust_vals, bins=40, color=CYAN, alpha=0.85, edgecolor='#0f0f1a')
ax2.axvline(avg_clustering, color=RED, lw=2, linestyle='--',
            label=f'μ = {avg_clustering:.3f}')
ax2.set(xlabel='Coefficient de clustering', ylabel='Fréquence',
        title='Distribution du Clustering')
ax2.legend(facecolor='#1a1a2e', labelcolor='white'); ax2.grid(True)
savefig('fig4_clustering.png')

# ── E. Centralité ──────────────────────────────────────────────
print("\n[E] Centralité ...")
dc     = nx.degree_centrality(GCC)
bc     = nx.betweenness_centrality(GCC, k=500, seed=42)
cc_c   = nx.closeness_centrality(GCC)
pr     = nx.pagerank(GCC, alpha=0.85, max_iter=300)

top_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:10]
top_dc = sorted(dc.items(), key=lambda x: x[1], reverse=True)[:5]
print(f"    Top-5 degré        : {[n for n,_ in top_dc]}")
print(f"    Top-5 intermédiarité: {[n for n,_ in top_bc[:5]]}")

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle('Mesures de Centralité – Facebook Ego Network', fontsize=13, color='white')
for ax, (name, cent, col) in zip(axes.flat, [
    ('Centralité de degré',         dc,    PURPLE),
    ("Centralité d'intermédiarité", bc,    CYAN),
    ('Centralité de proximité',     cc_c,  RED),
    ('PageRank',                    pr,    GOLD),
]):
    ax.hist(list(cent.values()), bins=50, color=col, alpha=0.85, edgecolor='#0f0f1a')
    ax.set(title=name, xlabel='Valeur', ylabel='Fréquence')
    ax.grid(True)
savefig('fig5_centrality.png')

# Top 10 betweenness bar chart
fig, ax = plt.subplots(figsize=(11, 5))
nodes_b = [str(n) for n, _ in top_bc]
vals_b  = [v for _, v in top_bc]
ax.barh(nodes_b[::-1], vals_b[::-1], color=PURPLE, alpha=0.9)
ax.set(xlabel="Centralité d'intermédiarité",
       title='Top 10 Nœuds – Centralité d\'Intermédiarité')
ax.grid(True, axis='x')
savefig('fig6_top_betweenness.png')

# Visualisation réseau (sous-graphe top 200)
print("\n[VIZ] Génération de la visualisation réseau ...")
top_nodes = [n for n, _ in sorted(pr.items(), key=lambda x: x[1], reverse=True)[:200]]
subG = GCC.subgraph(top_nodes)
pos  = nx.spring_layout(subG, seed=42, k=0.5)

fig, ax = plt.subplots(figsize=(14, 12))
fig.set_facecolor('#0a0a16'); ax.set_facecolor('#0a0a16')
nx.draw_networkx_edges(subG, pos, alpha=0.12, edge_color='#555', ax=ax, width=0.5)
sc = nx.draw_networkx_nodes(subG, pos,
                             node_color=[pr[n] for n in subG.nodes()],
                             node_size=[300*dc[n] + 20 for n in subG.nodes()],
                             cmap=plt.cm.plasma, alpha=0.9, ax=ax)
plt.colorbar(sc, ax=ax, label='PageRank', fraction=0.03)
ax.set_title('Facebook Ego Network – Top 200 nœuds (couleur = PageRank)',
             fontsize=13, color='white', pad=12)
ax.axis('off')
savefig('fig7_network_viz.png')

# ═══════════════════════════════════════════════════════════════
# PARTIE 3 – DÉTECTION DES COMMUNAUTÉS
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  PARTIE 3 – DÉTECTION DES COMMUNAUTÉS")
print("="*60)

results = {}

# ── 1. Louvain ────────────────────────────────────────────────
print("\n[1/4] Louvain ...")
t0 = time.time()
louvain_coms = algorithms.louvain(G, resolution=1.0, randomize=False)
t1 = time.time() - t0
mod_l = louvain_coms.newman_girvan_modularity().score
sizes_l = sorted([len(c) for c in louvain_coms.communities], reverse=True)
print(f"    Communautés : {len(louvain_coms.communities)}  |  Q = {mod_l:.4f}  |  {t1:.2f}s")
results['Louvain'] = {'coms': louvain_coms, 'n': len(louvain_coms.communities),
                      'Q': mod_l, 't': t1, 'sizes': sizes_l}

# ── 2. Label Propagation ──────────────────────────────────────
print("[2/4] Label Propagation ...")
t0 = time.time()
lp_coms = algorithms.label_propagation(G)
t2 = time.time() - t0
mod_lp = lp_coms.newman_girvan_modularity().score
sizes_lp = sorted([len(c) for c in lp_coms.communities], reverse=True)
print(f"    Communautés : {len(lp_coms.communities)}  |  Q = {mod_lp:.4f}  |  {t2:.2f}s")
results['Label Propagation'] = {'coms': lp_coms, 'n': len(lp_coms.communities),
                                'Q': mod_lp, 't': t2, 'sizes': sizes_lp}

# ── 3. K-Clique (k=3) ─────────────────────────────────────────
print("[3/4] K-Clique (k=3) ...")
t0 = time.time()
kc_coms = algorithms.kclique(G, k=3)
t3 = time.time() - t0
try:
    mod_kc = kc_coms.newman_girvan_modularity().score
except Exception:
    mod_kc = None
sizes_kc = sorted([len(c) for c in kc_coms.communities], reverse=True)
print(f"    Communautés : {len(kc_coms.communities)}  |  Q = {mod_kc}  |  {t3:.2f}s")
results['K-Clique (k=3)'] = {'coms': kc_coms, 'n': len(kc_coms.communities),
                              'Q': mod_kc, 't': t3, 'sizes': sizes_kc}

# ── 4. Leiden ─────────────────────────────────────────────────
print("[4/4] Leiden ...")
t0 = time.time()
leiden_coms = algorithms.leiden(G)
t4 = time.time() - t0
mod_ld = leiden_coms.newman_girvan_modularity().score
sizes_ld = sorted([len(c) for c in leiden_coms.communities], reverse=True)
print(f"    Communautés : {len(leiden_coms.communities)}  |  Q = {mod_ld:.4f}  |  {t4:.2f}s")
results['Leiden'] = {'coms': leiden_coms, 'n': len(leiden_coms.communities),
                     'Q': mod_ld, 't': t4, 'sizes': sizes_ld}

# ── Visualisation : réseau coloré par Louvain ─────────────────
print("\n[VIZ] Réseau coloré par communautés Louvain ...")
node2com = {}
for i, com in enumerate(louvain_coms.communities):
    for n in com: node2com[n] = i

n_c = results['Louvain']['n']
cmap_c = cm.get_cmap('tab20', n_c)
top250 = [n for n, _ in sorted(G.degree(), key=lambda x: x[1], reverse=True)[:250]]
subG2  = G.subgraph(top250)
pos2   = nx.spring_layout(subG2, seed=77, k=0.4)

fig, ax = plt.subplots(figsize=(15, 12))
fig.set_facecolor('#0a0a16'); ax.set_facecolor('#0a0a16')
nx.draw_networkx_edges(subG2, pos2, alpha=0.1, edge_color='#555', ax=ax, width=0.4)
nx.draw_networkx_nodes(subG2, pos2,
                       node_color=[cmap_c(node2com.get(n,0) % n_c) for n in subG2.nodes()],
                       node_size=[15 + 4*subG2.degree(n) for n in subG2.nodes()],
                       alpha=0.92, ax=ax)
ax.set_title(f'Facebook Ego Network – {n_c} Communautés Louvain (Q={mod_l:.3f})',
             fontsize=13, color='white', pad=12)
ax.axis('off')
savefig('fig8_louvain_communities.png')

# ── Tableau comparatif ─────────────────────────────────────────
print("\n[VIZ] Distribution des tailles de communautés ...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Distribution des Tailles de Communautés', fontsize=12, color='white')
for ax, (name, col) in zip(axes, [('Louvain', PURPLE),
                                   ('Label Propagation', CYAN),
                                   ('Leiden', GOLD)]):
    r = results[name]
    ax.bar(range(len(r['sizes'])), r['sizes'], color=col, alpha=0.85)
    q_str = f"{r['Q']:.3f}" if r['Q'] is not None else 'N/A'
    ax.set_title(f"{name}\n({r['n']} comm., Q={q_str})")
    ax.set(xlabel='Communauté', ylabel='Nœuds'); ax.grid(True)
savefig('fig9_community_sizes.png')

# Modularité bar chart
valid_q = [(n, r['Q']) for n, r in results.items() if r['Q'] is not None]
fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar([n for n,_ in valid_q], [q for _,q in valid_q],
              color=[PURPLE, CYAN, GOLD], alpha=0.9)
for bar, (_, q) in zip(bars, valid_q):
    ax.text(bar.get_x()+bar.get_width()/2, max(q+0.005, 0.005),
            f'{q:.4f}', ha='center', color='white', fontsize=10, fontweight='bold')
ax.set(ylabel='Modularité Q', title='Modularité par Algorithme', ylim=(0, 1))
ax.grid(True, axis='y')
savefig('fig10_modularity.png')

# ═══════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  RÉSUMÉ FINAL")
print("="*60)
print(f"\n  Réseau   : Facebook Ego Network (SNAP)")
print(f"  Nœuds    : {G.number_of_nodes():,}")
print(f"  Liens    : {G.number_of_edges():,}")
print(f"  ⟨k⟩      : {deg_arr.mean():.2f}  |  k_max = {deg_arr.max()}")
print(f"  GCC      : {GCC.number_of_nodes():,} nœuds ({100*GCC.number_of_nodes()/G.number_of_nodes():.0f}%)")
print(f"  Avg path : {avg_path:.4f}  |  Diam ≈ {diam_approx}")
print(f"  C moyen  : {avg_clustering:.4f}  |  Densité = {density:.6f}")
print(f"\n  Algorithme          | Comm. |   Q     | Temps")
print(f"  " + "-"*50)
for name, r in results.items():
    q_str = f"{r['Q']:.4f}" if r['Q'] is not None else "  N/A "
    print(f"  {name:<20} | {r['n']:>5} | {q_str} | {r['t']:.2f}s")
print("="*60)
print("\n[✓] Toutes les figures ont été sauvegardées dans ./figures/")
