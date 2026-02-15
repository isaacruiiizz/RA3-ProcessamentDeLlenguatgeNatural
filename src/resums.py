import pandas as pd
import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Rutes 
PATH_PAS1 = os.path.join("data", "processed", "articles_processats.csv")
PATH_PAS2 = os.path.join("data", "processed", "articles_preprocessats_B_spacy.csv")
OUTPUT_PATH = os.path.join("data", "processed", "pas4_resums_comparativa.csv")

def carregar_model_i_tokenizer(model_name):
    print(f"Carregant: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer

def resumir_text(text, model, tokenizer, max_l=130):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"], 
        max_length=max_l, 
        min_length=40, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def generar_resums():
    if not os.path.exists(PATH_PAS1) or not os.path.exists(PATH_PAS2):
        print("Error: Revisa que els fitxers del Pas 1 i Pas 2 existeixin.")
        return

    df_p1 = pd.read_csv(PATH_PAS1)
    df_p2 = pd.read_csv(PATH_PAS2)

    col_text_p2 = [c for c in df_p2.columns if 'text' in c.lower()][0]
    print(f"Columna detectada al Pas 2: '{col_text_p2}'")

    print("\n--- INICIALITZANT MODELS ---")
    model_a, tok_a = carregar_model_i_tokenizer("facebook/bart-large-cnn")
    model_b, tok_b = carregar_model_i_tokenizer("csebuetnlp/mT5_multilingual_XLSum")

    resultats = []

    for i in range(len(df_p1)):
        nom = df_p1.iloc[i]['fitxer']
        text_p1 = str(df_p1.iloc[i]['text_original'])
        
        # Filtrem per fitxer i agafem el text de la columna detectada
        text_p2_row = df_p2[df_p2['fitxer'] == nom]
        if text_p2_row.empty:
            print(f"Advertència: No s'ha trobat {nom} al Pas 2. Saltant...")
            continue
            
        text_p2 = str(text_p2_row[col_text_p2].values[0])

        print(f"Generant resums per a l'article de {nom}...")

        resum_a = resumir_text(text_p1, model_a, tok_a)
        resum_b = resumir_text(text_p2, model_b, tok_b)

        resultats.append({
            "fitxer": nom,
            "metode_A_BART_Pas1": resum_a,
            "metode_B_mT5_Pas2": resum_b
        })

    df_final = pd.DataFrame(resultats)
    df_final.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print(f"\n[OK] Pas 4 completat! Resultats a: {OUTPUT_PATH}")

if __name__ == "__main__":
    generar_resums()