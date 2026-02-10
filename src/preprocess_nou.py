# -*- coding: utf-8 -*-
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
"""

from __future__ import annotations

import os
import csv
import string
import argparse
from typing import List, Dict


# -----------------------------
# I/O CSV
# -----------------------------
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


# -----------------------------
# METODOLOGIA A — PYTHON STANDARD
# -----------------------------
def preprocess_python_standard(text: str) -> List[str]:
    """
    - lower()
    - eliminar puntuació
    - tokenització simple: split
    """
    # 1) Minúscules
    text = (text or "").lower()

    # 2) Treure puntuació bàsica
    # Afegim alguns signes típics catalans/periodístics a més de string.punctuation
    extra_punct = "“”«»…–—·’"
    trans_table = str.maketrans("", "", string.punctuation + extra_punct)
    text = text.translate(trans_table)

    # 3) Tokenització simple
    tokens = text.split()

    # (Opcional però útil) Treure tokens buits i números sols
    tokens = [t for t in tokens if t.strip() and not t.isdigit()]

    return tokens


# -----------------------------
# METODOLOGIA B — SPACY AVANÇAT
# -----------------------------
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


# -----------------------------
# COMPARATIVA
# -----------------------------
def compare_for_row(nlp, title: str, article: str) -> Dict[str, str]:
    full_text = join_title_article(title, article)

    tokens_a = preprocess_python_standard(full_text)
    tokens_b = preprocess_spacy_advanced(nlp, full_text)

    return {
        "text_len_chars": str(len(full_text)),
        "n_tokens_A_python": str(len(tokens_a)),
        "n_tokens_B_spacy": str(len(tokens_b)),
        "exemple_20_tokens_A": " ".join(tokens_a[:20]),
        "exemple_20_tokens_B": " ".join(tokens_b[:20]),
        # per si després ho vols per BoW/embeddings
        "tokens_A_python": " ".join(tokens_a),
        "tokens_B_spacy": " ".join(tokens_b),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=os.path.join("data", "processed", "articles_processats.csv"),
        help="CSV d'entrada amb: fitxer,titol,text_original",
    )
    parser.add_argument(
        "--output",
        default=os.path.join("data", "processed", "articles_preprocessats_pas2.csv"),
        help="CSV de sortida (PAS 2) amb comparativa A vs B",
    )
    args = parser.parse_args()

    rows = read_csv_dicts(args.input)
    if not rows:
        raise RuntimeError(f"CSV buit o no llegible: {args.input}")

    required = {"fitxer", "titol", "text_original"}
    missing = required - set(rows[0].keys())
    if missing:
        raise RuntimeError(f"Falten columnes al CSV: {missing} (calen {required})")

    # spaCy nlp una sola vegada
    nlp = load_spacy("ca_core_news_sm")

    out = []
    for r in rows:
        comp = compare_for_row(nlp, r.get("titol", ""), r.get("text_original", ""))
        out.append({
            "fitxer": r.get("fitxer", ""),
            "titol": r.get("titol", ""),
            "text_original": r.get("text_original", ""),
            **comp
        })

    fieldnames = [
        "fitxer",
        "titol",
        "text_original",
        "text_len_chars",
        "n_tokens_A_python",
        "n_tokens_B_spacy",
        "exemple_20_tokens_A",
        "exemple_20_tokens_B",
        "tokens_A_python",
        "tokens_B_spacy",
    ]

    write_csv_dicts(args.output, out, fieldnames)

    # Sortida per consola (captura “EXECUCIÓ MAIN.PY”)
    print(f"[OK] PAS 2 completat. Articles processats: {len(out)}")
    print(f"[OK] Fitxer sortida: {args.output}\n")

    first = out[0]
    print("=== COMPARATIVA (primer registre) ===")
    print("Fitxer:", first["fitxer"])
    print("Tokens A (Python):", first["n_tokens_A_python"])
    print("Tokens B (spaCy):", first["n_tokens_B_spacy"])
    print("Exemple A:", first["exemple_20_tokens_A"])
    print("Exemple B:", first["exemple_20_tokens_B"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
