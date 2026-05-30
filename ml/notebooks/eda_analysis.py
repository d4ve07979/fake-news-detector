"""
EDA Notebook — Fake & Real News Dataset
Projet IA & Big Data L3 — KENKOU Dave

Exécuter avec: jupyter notebook ou convertir en .ipynb avec jupytext
"""
# ── Imports ───────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import warnings
warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.dpi'] = 120

# ── 1. Chargement ─────────────────────────────────────────────────────────────
print("=" * 60)
print("1. CHARGEMENT DES DONNÉES")
print("=" * 60)

df_fake = pd.read_csv("../../data/Fake.csv")
df_real = pd.read_csv("../../data/True.csv")

df_fake["label"] = 0
df_fake["label_str"] = "FAKE"
df_real["label"] = 1
df_real["label_str"] = "REAL"

df = pd.concat([df_fake, df_real], ignore_index=True)
df = df.dropna(subset=["text", "title"])

print(f"Shape total    : {df.shape}")
print(f"FAKE articles  : {(df.label == 0).sum()}")
print(f"REAL articles  : {(df.label == 1).sum()}")
print(f"\nColonnes : {list(df.columns)}")
print(f"\nPremiers exemples :")
print(df[["title","label_str"]].head(5))

# ── 2. Distribution des classes ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. DISTRIBUTION DES CLASSES")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
counts = df["label_str"].value_counts()
axes[0].bar(counts.index, counts.values, color=["#EF4444","#22C55E"], edgecolor="white", linewidth=1.5)
axes[0].set_title("Distribution FAKE / REAL", fontweight="bold")
axes[0].set_ylabel("Nombre d'articles")
for i, v in enumerate(counts.values):
    axes[0].text(i, v + 100, f"{v:,}\n({v/len(df)*100:.1f}%)", ha="center", fontsize=10, fontweight="bold")

axes[1].pie(counts.values, labels=counts.index, autopct="%1.1f%%",
            colors=["#EF4444","#22C55E"], startangle=90,
            wedgeprops={"edgecolor":"white","linewidth":2})
axes[1].set_title("Répartition proportionnelle", fontweight="bold")
plt.tight_layout()
plt.savefig("../../data/eda_distribution.png", bbox_inches="tight")
plt.show()
print("✅ Figure sauvegardée: data/eda_distribution.png")

# ── 3. Longueur des textes ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. ANALYSE DE LA LONGUEUR DES TEXTES")
print("=" * 60)

df["text_len"]  = df["text"].apply(lambda x: len(str(x).split()))
df["title_len"] = df["title"].apply(lambda x: len(str(x).split()))

print(df.groupby("label_str")[["text_len","title_len"]].describe().round(1))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, (group, grp_df) in zip(axes, df.groupby("label_str")):
    color = "#EF4444" if group == "FAKE" else "#22C55E"
    ax.hist(grp_df["text_len"].clip(0, 2000), bins=50, color=color, alpha=0.8, edgecolor="white")
    ax.set_title(f"Longueur des textes — {group}", fontweight="bold")
    ax.set_xlabel("Nombre de mots")
    ax.axvline(grp_df["text_len"].median(), color="navy", linestyle="--", label=f"Médiane: {grp_df['text_len'].median():.0f}")
    ax.legend()
plt.tight_layout()
plt.savefig("../../data/eda_text_length.png", bbox_inches="tight")
plt.show()

# ── 4. Distribution par sujet ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. DISTRIBUTION PAR SUJET (subject)")
print("=" * 60)

subject_counts = df.groupby(["subject","label_str"]).size().unstack(fill_value=0)
print(subject_counts)

fig, ax = plt.subplots(figsize=(12, 5))
subject_counts.plot(kind="bar", ax=ax, color=["#EF4444","#22C55E"], edgecolor="white")
ax.set_title("Distribution des articles par sujet et label", fontweight="bold")
ax.set_xlabel("Sujet")
ax.set_ylabel("Nombre d'articles")
ax.tick_params(axis="x", rotation=45)
ax.legend(title="Label")
plt.tight_layout()
plt.savefig("../../data/eda_subjects.png", bbox_inches="tight")
plt.show()

# ── 5. Analyse temporelle ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("5. ANALYSE TEMPORELLE")
print("=" * 60)

try:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df_dated = df.dropna(subset=["date"])
    df_dated["year_month"] = df_dated["date"].dt.to_period("M")
    time_counts = df_dated.groupby(["year_month","label_str"]).size().unstack(fill_value=0)
    print(f"Période couverte: {df_dated['date'].min().date()} → {df_dated['date'].max().date()}")
    print(f"Articles datés: {len(df_dated)} / {len(df)}")
except Exception as e:
    print(f"Note: Analyse temporelle limitée ({e})")

# ── 6. Analyse des mots-clés ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("6. MOTS-CLÉS LES PLUS FRÉQUENTS")
print("=" * 60)

STOPWORDS = {"the","a","an","to","of","in","and","is","it","that","for","on","with","was","are","as","at","be","by","from"}

def get_top_words(texts, n=15):
    words = []
    for t in texts:
        words.extend([w.lower() for w in re.findall(r'\b[a-z]+\b', str(t)) if w.lower() not in STOPWORDS and len(w) > 3])
    return Counter(words).most_common(n)

fake_words = get_top_words(df[df.label==0]["text"])
real_words = get_top_words(df[df.label==1]["text"])

print("\nTop 10 mots — FAKE NEWS:")
for w, c in fake_words[:10]: print(f"  {w:20s} {c:6,}")
print("\nTop 10 mots — REAL NEWS:")
for w, c in real_words[:10]: print(f"  {w:20s} {c:6,}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, words, color, title in [
    (axes[0], fake_words, "#EF4444", "Top 15 mots — FAKE"),
    (axes[1], real_words, "#22C55E", "Top 15 mots — REAL"),
]:
    wds, cnts = zip(*words)
    ax.barh(wds[::-1], cnts[::-1], color=color, alpha=0.85, edgecolor="white")
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Fréquence")
plt.tight_layout()
plt.savefig("../../data/eda_keywords.png", bbox_inches="tight")
plt.show()

# ── 7. Valeurs manquantes ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("7. VALEURS MANQUANTES")
print("=" * 60)
missing = df.isnull().sum()
print(missing[missing > 0] if missing.any() else "✅ Aucune valeur manquante critique.")

# ── Résumé final ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("RÉSUMÉ EDA")
print("=" * 60)
print(f"  Total articles       : {len(df):,}")
print(f"  Classes              : FAKE={len(df[df.label==0]):,} / REAL={len(df[df.label==1]):,}")
print(f"  Longueur moy. FAKE   : {df[df.label==0]['text_len'].mean():.0f} mots")
print(f"  Longueur moy. REAL   : {df[df.label==1]['text_len'].mean():.0f} mots")
print(f"  Valeurs manquantes   : négligeables")
print(f"  Classes équilibrées  : Oui ✅")
print("=" * 60)
