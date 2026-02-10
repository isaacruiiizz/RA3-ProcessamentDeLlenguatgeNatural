# -*- coding: utf-8 -*-
"""
PAS 3: Identificació del tema de l'article (4 punts)

- Solució 1: Bag of Words (BoW)
- Solució 2: TF-IDF
- Solució 3 (obligatòria): Embeddings amb HuggingFace (sense fine-tuning)
  -> Similaritat coseno entre articles

Entrada recomanada: data/processed/articles_preprocessats_B_spacy.csv
Columna usada com a text: "tokens"
"""

import os
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer


INPUT_CSV = os.path.join("data", "processed", "articles_preprocessats_B_spacy.csv")
OUT_DIR = os.path.join("data", "processed")

BOW_OUT = os.path.join(OUT_DIR, "pas3_bow_top_terms.csv")
TFIDF_OUT = os.path.join(OUT_DIR, "pas3_tfidf_top_terms.csv")
SIM_OUT = os.path.join(OUT_DIR, "pas3_hf_similarity.csv")

TOP_N = 12


def top_terms_from_vector(vec, feature_names, top_n=10):
    """Retorna top terms d'un vector (1D)"""
    series = pd.Series(vec, index=feature_names)
    series = series[series > 0].sort_values(ascending=False)
    return list(series.head(top_n).items())


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_CSV)
    if "tokens" not in df.columns:
        raise RuntimeError("El CSV no té la columna 'tokens'. Revisa el PAS 2 o adapta el nom.")

    # Texts (ja preprocessats)
    texts = df["tokens"].fillna("").astype(str).tolist()

    # Etiqueta del document (fitxer o titol)
    label_col = "fitxer" if "fitxer" in df.columns else "titol"
    labels = df[label_col].fillna("").astype(str).tolist()

    # -------------------------
    # 1) BAG OF WORDS
    # -------------------------
    bow = CountVectorizer()
    X_bow = bow.fit_transform(texts)
    bow_features = bow.get_feature_names_out()

    bow_rows = []
    for i, label in enumerate(labels):
        vec = X_bow[i].toarray().ravel()
        top = top_terms_from_vector(vec, bow_features, TOP_N)
        bow_rows.append({
            "document": label,
            "top_terms": ", ".join([f"{w}({int(c)})" for w, c in top])
        })

    pd.DataFrame(bow_rows).to_csv(BOW_OUT, index=False, encoding="utf-8")
    print(f"[OK] BoW guardat a: {BOW_OUT}")

    # -------------------------
    # 2) TF-IDF
    # -------------------------
    tfidf = TfidfVectorizer()
    X_tfidf = tfidf.fit_transform(texts)
    tfidf_features = tfidf.get_feature_names_out()

    tfidf_rows = []
    for i, label in enumerate(labels):
        vec = X_tfidf[i].toarray().ravel()
        top = top_terms_from_vector(vec, tfidf_features, TOP_N)
        tfidf_rows.append({
            "document": label,
            "top_terms": ", ".join([f"{w}({score:.3f})" for w, score in top])
        })

    pd.DataFrame(tfidf_rows).to_csv(TFIDF_OUT, index=False, encoding="utf-8")
    print(f"[OK] TF-IDF guardat a: {TFIDF_OUT}")

    # -------------------------
    # 3) HUGGINGFACE EMBEDDINGS (sense fine-tuning)
    # -------------------------
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    model = SentenceTransformer(model_name)

    embeddings = model.encode(texts, normalize_embeddings=True)
    sim = cosine_similarity(embeddings)

    # Guardem similituds en format taula (parelles)
    sim_rows = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            sim_rows.append({
                "doc_a": labels[i],
                "doc_b": labels[j],
                "similarity": float(sim[i, j])
            })

    sim_df = pd.DataFrame(sim_rows).sort_values("similarity", ascending=False)
    sim_df.to_csv(SIM_OUT, index=False, encoding="utf-8")
    print(f"[OK] Similaritats HF guardades a: {SIM_OUT}")

    # Mostra ràpida per fer captura terminal
    print("\n=== TOP 5 similaritats (HuggingFace) ===")
    print(sim_df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
