"""
PAS 2: PREPROCESSAMENT DEL TEXT

Metodologia A (Python Standard):
- Normalització: minúscules
- Eliminació de puntuació: string.punctuation (+ alguns signes típics)
- Tokenització simple: split per espais

Metodologia B (spaCy - ca_core_news_sm):
- Tokenització intel·ligent
- Eliminació de stopwords (diccionari oficial spaCy català)
- Lematització (millora extra)

SORTIDES:
- articles_preprocessats_A_python.csv
- articles_preprocessats_B_spacy.csv
"""

from __future__ import annotations

import os
import csv
import string
import argparse
from typing import List, Dict

# FUNCIONS AUXILIARS
def read_csv_dicts(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_dicts(path: str, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def join_title_article(title: str, text: str) -> str:
    title = (title or "").strip()
    text = (text or "").strip()
    if title and text:
        return f"{title}. {text}"
    return title or text

# METODOLOGIA A — PYTHON STANDARD
def preprocess_python_standard(text: str) -> List[str]:
    """
    - lower()
    - eliminar puntuació
    - tokenització simple: split
    """
    text = (text or "").lower()

    # Afegim alguns signes típics catalans/periodístics a més de string.punctuation
    extra_punct = "“”«»…–—·’"
    trans_table = str.maketrans("", "", string.punctuation + extra_punct)
    text = text.translate(trans_table)

    tokens = text.split()
    tokens = [t for t in tokens if t.strip() and not t.isdigit()]
    return tokens

# METODOLOGIA B — SPACY AVANÇAT
def load_spacy(model_name: str = "ca_core_news_sm"):
    try:
        import spacy
    except ImportError as e:
        raise RuntimeError("Falta spaCy. Instal·la: pip install spacy") from e

    try:
        return spacy.load(model_name)
    except Exception as e:
        raise RuntimeError(
            f"No es pot carregar el model '{model_name}'. "
            f"Prova: python -m spacy download {model_name}"
        ) from e

# PAS 2: PREPROCESSAMENT DEL TEXT
def preprocess_spacy_advanced(nlp, text: str) -> List[str]:
    """
    - tokenització intel·ligent
    - eliminar stopwords (token.is_stop)
    - eliminar puntuació (token.is_punct)
    - lematitzar i normalitzar (lemma_.lower())
    """
    doc = nlp(text or "")

    tokens = []
    for token in doc:
        if token.is_stop:
            continue
        if token.is_punct:
            continue
        if not token.is_alpha:
            continue

        lemma = token.lemma_.strip().lower()
        if lemma:
            tokens.append(lemma)

    return tokens

# MAIN
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=os.path.join("data", "processed", "articles_processats.csv"),
        help="CSV d'entrada amb: fitxer,titol,text_original",
    )
    parser.add_argument(
        "--out_dir",
        default=os.path.join("data", "processed"),
        help="Carpeta de sortida",
    )
    args = parser.parse_args()

    rows = read_csv_dicts(args.input)
    if not rows:
        raise RuntimeError(f"CSV buit o no llegible: {args.input}")

    required = {"fitxer", "titol", "text_original"}
    missing = required - set(rows[0].keys())
    if missing:
        raise RuntimeError(f"Falten columnes al CSV: {missing} (calen {required})")

    # Carreguem spaCy 1 cop
    nlp = load_spacy("ca_core_news_sm")

    out_a = []
    out_b = []

    for r in rows:
        fitxer = r.get("fitxer", "")
        titol = r.get("titol", "")
        text_original = r.get("text_original", "")
        full_text = join_title_article(titol, text_original)

        # A) Python Standard
        tokens_a = preprocess_python_standard(full_text)
        out_a.append({
            "fitxer": fitxer,
            "titol": titol,
            "text_original": text_original,
            "text_len_chars": len(full_text),
            "n_tokens": len(tokens_a),
            "exemple_20_tokens": " ".join(tokens_a[:20]),
            "tokens": " ".join(tokens_a),
        })

        # B) spaCy
        tokens_b = preprocess_spacy_advanced(nlp, full_text)
        out_b.append({
            "fitxer": fitxer,
            "titol": titol,
            "text_original": text_original,
            "text_len_chars": len(full_text),
            "n_tokens": len(tokens_b),
            "exemple_20_tokens": " ".join(tokens_b[:20]),
            "tokens": " ".join(tokens_b),
        })

    # Guardem CSV A
    out_path_a = os.path.join(args.out_dir, "articles_preprocessats_A_python.csv")
    fieldnames = ["fitxer", "titol", "text_original", "text_len_chars", "n_tokens", "exemple_20_tokens", "tokens"]
    write_csv_dicts(out_path_a, out_a, fieldnames)

    # Guardem CSV B
    out_path_b = os.path.join(args.out_dir, "articles_preprocessats_B_spacy.csv")
    write_csv_dicts(out_path_b, out_b, fieldnames)

    print(f"[OK] PAS 2 completat. Articles processats: {len(rows)}")
    print(f"[OK] CSV Metodologia A (Python): {out_path_a}")
    print(f"[OK] CSV Metodologia B (spaCy):  {out_path_b}\n")

    print("=== EXEMPLE (primer registre) ===")
    print("Fitxer:", out_a[0]["fitxer"])
    print("A) n_tokens:", out_a[0]["n_tokens"])
    print("A) exemple:", out_a[0]["exemple_20_tokens"])
    print("B) n_tokens:", out_b[0]["n_tokens"])
    print("B) exemple:", out_b[0]["exemple_20_tokens"])

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
