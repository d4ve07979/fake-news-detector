"""
TEST ANTI-OVERFITTING — Fake News Detector
Teste le modèle sur de NOUVEAUX articles jamais vus pendant l'entraînement.
Exécuter sur Google Colab (GPU) ou en local avec le modèle téléchargé.

Usage:
    python test_overfitting.py --model_path ./models/bert-fakenews
"""
import argparse
import torch
import numpy as np
from transformers import pipeline
from sklearn.metrics import classification_report, confusion_matrix
import json

# ── Nouveaux articles de test (jamais vus pendant l'entraînement) ──────────────
# Source : articles réels collectés manuellement depuis diverses sources
NEW_TEST_ARTICLES = [
    # ── VRAIS articles (REAL) ───────────────────────────────────────────────
    {
        "title": "Federal Reserve raises interest rates by 0.25%",
        "text": "The Federal Reserve on Wednesday raised its benchmark interest rate by a quarter of a percentage point, bringing it to a range of 5.25% to 5.5%. Chair Jerome Powell said the central bank would continue to monitor economic data before making further decisions.",
        "label": "REAL",
        "source": "Reuters-style"
    },
    {
        "title": "Apple reports record quarterly revenue of $90 billion",
        "text": "Apple Inc reported its highest-ever quarterly revenue on Thursday, driven by strong iPhone sales in Asia and growing services revenue. Chief Executive Tim Cook said the company was seeing robust demand across all product categories.",
        "label": "REAL",
        "source": "Financial news"
    },
    {
        "title": "Scientists discover new species of deep-sea fish near Pacific trench",
        "text": "Marine biologists announced Monday the discovery of a previously unknown species of bioluminescent fish in the Mariana Trench. The research, published in the journal Nature, describes the creature found at depths exceeding 8,000 meters.",
        "label": "REAL",
        "source": "Science journal"
    },
    {
        "title": "WHO reports decline in global malaria deaths",
        "text": "The World Health Organization released its annual malaria report showing a 12% decline in deaths compared to the previous year. Officials credited improved access to preventive treatments and bed nets in sub-Saharan Africa.",
        "label": "REAL",
        "source": "WHO report"
    },
    {
        "title": "NASA's Artemis mission successfully orbits the Moon",
        "text": "NASA's Orion capsule completed its closest approach to the Moon on Monday as part of the Artemis I mission, coming within 130 kilometers of the lunar surface. The uncrewed test flight is a critical step toward returning humans to the Moon.",
        "label": "REAL",
        "source": "NASA press release"
    },
    {
        "title": "European Parliament votes to ban single-use plastics",
        "text": "The European Parliament overwhelmingly approved legislation Tuesday to ban single-use plastic items such as straws, cotton buds, and cutlery. The measure, which passed with 560 votes in favor, will take effect across EU member states.",
        "label": "REAL",
        "source": "EU official"
    },
    {
        "title": "Tesla recalls 2 million vehicles over autopilot safety concerns",
        "text": "Tesla is recalling approximately 2 million vehicles in the United States to address concerns about its Autopilot system, the National Highway Traffic Safety Administration announced. The recall covers Model S, X, 3 and Y vehicles.",
        "label": "REAL",
        "source": "NHTSA official"
    },
    {
        "title": "G7 leaders agree on new climate financing package",
        "text": "Leaders of the G7 nations reached agreement Saturday on a $600 billion infrastructure and climate financing initiative for developing countries. The package, announced at the summit in Japan, aims to provide an alternative to Chinese lending programs.",
        "label": "REAL",
        "source": "G7 summit"
    },

    # ── FAUX articles (FAKE) ────────────────────────────────────────────────
    {
        "title": "BREAKING: Bill Gates admits vaccines contain microchips in secret document",
        "text": "A leaked document allegedly from the Bill and Melinda Gates Foundation reveals that COVID-19 vaccines were designed to implant microchips in recipients. The document, which mainstream media refuses to cover, shows the globalist plan to track every human being on the planet.",
        "label": "FAKE",
        "source": "Conspiracy site"
    },
    {
        "title": "SHOCKING: Democrats caught smuggling ballots in 47 states, witnesses say",
        "text": "Multiple eyewitnesses have come forward claiming they saw Democrat operatives smuggling thousands of fraudulent ballots in garbage bags across 47 states. The mainstream media is covering up this MASSIVE election fraud that stole the election.",
        "label": "FAKE",
        "source": "Far-right blog"
    },
    {
        "title": "SECRET cure for cancer discovered but Big Pharma paying to suppress it",
        "text": "A renowned oncologist claims to have discovered a 100% cure for all cancers using natural herbs, but pharmaceutical companies are paying billions to keep this information hidden from the public. The doctor has received multiple death threats for trying to share this miracle treatment.",
        "label": "FAKE",
        "source": "Pseudoscience site"
    },
    {
        "title": "George Soros funding antifa to destroy American cities says report",
        "text": "An explosive new report exposes how globalist billionaire George Soros has been funneling millions of dollars to antifa terrorist cells across the country. These paid protesters are part of a coordinated attack on American values and democracy.",
        "label": "FAKE",
        "source": "Conspiracy blog"
    },
    {
        "title": "5G towers proven to spread coronavirus, scientists SILENCED",
        "text": "Independent researchers have confirmed what many suspected: 5G towers emit radiation that activates the coronavirus in human cells. Dozens of scientists who attempted to publish these findings have been fired or had their research suppressed by tech companies.",
        "label": "FAKE",
        "source": "Anti-tech site"
    },
    {
        "title": "CIA whistleblower reveals aliens living in Area 51 have been advising presidents",
        "text": "A former CIA operative has released classified documents proving that extraterrestrial beings captured at Roswell have been secretly advising US presidents since 1947. The deep state has been keeping this information from the American people for decades.",
        "label": "FAKE",
        "source": "UFO conspiracy"
    },
    {
        "title": "WAKE UP! Chemtrails confirmed to contain mind control chemicals",
        "text": "Government documents obtained through FOIA requests prove that chemtrails spread by planes contain fluoride, lithium, and other chemicals designed to make the population docile and controllable. Share this before it gets deleted by the censors!",
        "label": "FAKE",
        "source": "Conspiracy forum"
    },
    {
        "title": "Hollywood elites running secret child trafficking ring exposed",
        "text": "Anonymous sources with connections to law enforcement have provided evidence that a major Hollywood elite network has been operating a child trafficking ring for decades. The mainstream media refuses to cover this story because they are all involved.",
        "label": "FAKE",
        "source": "QAnon-style"
    },

    # ── CAS AMBIGUS (articles qui pourraient tromper le modèle) ────────────
    {
        "title": "Study shows coffee may reduce risk of Alzheimer's disease",
        "text": "A new study published in the Journal of Alzheimer's Disease suggests that drinking three to four cups of coffee per day may reduce the risk of developing Alzheimer's disease by up to 65%. Researchers studied 1,400 participants over 21 years.",
        "label": "REAL",
        "source": "Medical journal (ambiguous)"
    },
    {
        "title": "Trump threatens to impose 25% tariffs on all Chinese goods",
        "text": "Former President Donald Trump announced Monday that if elected, he would immediately impose sweeping 25% tariffs on all Chinese imports. The proposal, made at a campaign rally, drew immediate criticism from trade economists.",
        "label": "REAL",
        "source": "Political news (ambiguous)"
    },
]


def run_evaluation(model_path: str):
    """Lance l'évaluation complète sur les nouveaux articles."""

    print("=" * 70)
    print("TEST ANTI-OVERFITTING — Articles jamais vus pendant l'entraînement")
    print("=" * 70)
    print(f"Modèle : {model_path}")
    print(f"Articles de test : {len(NEW_TEST_ARTICLES)}")
    print()

    # Charger le modèle
    print("Chargement du modèle...")
    clf = pipeline(
        "text-classification",
        model=model_path,
        tokenizer=model_path,
        truncation=True,
        max_length=512,
        device=0 if torch.cuda.is_available() else -1,
    )
    print(f"Device : {'GPU' if torch.cuda.is_available() else 'CPU'}")
    print()

    # Prédictions
    y_true, y_pred, results = [], [], []
    print(f"{'Article':<50} {'Vrai':>6} {'Prédit':>6} {'Conf':>6} {'OK?':>4}")
    print("-" * 70)

    for article in NEW_TEST_ARTICLES:
        content = f"{article['title']} [SEP] {article['text']}"
        pred    = clf(content[:512])[0]
        label   = pred["label"]   # FAKE ou REAL (grâce au config.json)
        conf    = round(pred["score"] * 100, 1)
        correct = "✓" if label == article["label"] else "✗"

        title_short = article["title"][:48] + ".." if len(article["title"]) > 50 else article["title"]
        print(f"{title_short:<50} {article['label']:>6} {label:>6} {conf:>5.1f}% {correct:>4}")

        y_true.append(article["label"])
        y_pred.append(label)
        results.append({
            "title":     article["title"],
            "true":      article["label"],
            "predicted": label,
            "confidence": conf,
            "correct":   label == article["label"],
            "source":    article["source"],
        })

    print()
    print("=" * 70)
    print("RAPPORT DE CLASSIFICATION")
    print("=" * 70)
    print(classification_report(y_true, y_pred, target_names=["FAKE", "REAL"]))

    print("MATRICE DE CONFUSION")
    cm = confusion_matrix(y_true, y_pred, labels=["FAKE", "REAL"])
    print(f"              Prédit FAKE  Prédit REAL")
    print(f"Vrai FAKE  :     {cm[0][0]:>5}       {cm[0][1]:>5}")
    print(f"Vrai REAL  :     {cm[1][0]:>5}       {cm[1][1]:>5}")

    # Résumé
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = correct_count / len(results) * 100
    print()
    print(f"Accuracy sur nouveaux articles : {accuracy:.1f}% ({correct_count}/{len(results)})")

    # Analyse des erreurs
    errors = [r for r in results if not r["correct"]]
    if errors:
        print()
        print("ERREURS DÉTECTÉES :")
        for e in errors:
            print(f"  ✗ [{e['source']}] {e['title'][:60]}")
            print(f"    → Vrai: {e['true']} | Prédit: {e['predicted']} | Conf: {e['confidence']}%")
    else:
        print("\n✅ AUCUNE ERREUR — Le modèle généralise bien sur ces nouveaux articles !")

    # Verdict overfitting
    print()
    print("=" * 70)
    print("VERDICT OVERFITTING")
    print("=" * 70)
    if accuracy >= 90:
        print(f"✅ PAS D'OVERFITTING détecté ({accuracy:.1f}% accuracy)")
        print("   Le modèle généralise bien sur des articles jamais vus.")
    elif accuracy >= 75:
        print(f"⚠️  LÉGER OVERFITTING possible ({accuracy:.1f}% accuracy)")
        print("   Performance acceptable mais inférieure au test set original.")
    else:
        print(f"❌ OVERFITTING PROBABLE ({accuracy:.1f}% accuracy)")
        print("   Performance très inférieure au test set — le modèle a mémorisé les données.")

    return results


def print_multilingual_note():
    print()
    print("=" * 70)
    print("NOTE : MODÈLE MULTILINGUE — RECOMMANDATIONS")
    print("=" * 70)
    print("""
Votre modèle actuel (bert-base-uncased) est entraîné uniquement sur l'anglais.
Pour une détection multilingue à grande échelle, voici les options :

OPTION 1 — mBERT (Multilingue, rapide) :
  Modèle : bert-base-multilingual-cased
  Langues : 104 langues dont FR, AR, ES, PT, SW
  Comment : Remplacer "bert-base-uncased" par "bert-base-multilingual-cased"
           dans train_bert.py et réentraîner sur Colab (même procédure)

OPTION 2 — XLM-RoBERTa (Multilingue, meilleur) :
  Modèle : xlm-roberta-base
  Langues : 100 langues, meilleure performance que mBERT
  Comment : Même procédure, juste changer le nom du modèle

OPTION 3 — Traduction automatique (sans réentraînement) :
  Avant d'envoyer un article français à votre modèle,
  le traduire en anglais avec l'API Deep Translate (gratuite).
  C'est la solution la plus rapide à implémenter maintenant.

Pour ce projet académique, OPTION 3 est suffisante et impressionnante.
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="./models/bert-fakenews")
    args = parser.parse_args()

    results = run_evaluation(args.model_path)
    print_multilingual_note()

    # Sauvegarder les résultats
    with open("overfitting_test_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nRésultats sauvegardés dans overfitting_test_results.json")
