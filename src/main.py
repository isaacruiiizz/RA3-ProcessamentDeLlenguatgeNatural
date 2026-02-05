import os
import csv
# Importem la funció que hem creat al fitxer scraper.py
from scraper import neteja_html

def main():
    ruta_articles = '../data/raw'
    resultats = []

    # Comprovem si la carpeta existeix
    if not os.path.exists(ruta_articles):
        print(f"Error: No s'ha trobat la carpeta {ruta_articles}")
        return

    # PAS 1: PROCESSAMENT HTML
    print("Executant Pas 1: Extracció de text...")
    for fitxer in os.listdir(ruta_articles):
        if fitxer.endswith('.html'):
            ruta_completa = os.path.join(ruta_articles, fitxer)
            
            titol, text_net = neteja_html(ruta_completa)
            
            # Guardem les dades en un diccionari per passos posteriors
            article_data = {
                "fitxer": fitxer,
                "titol": titol,
                "text_original": text_net
            }
            resultats.append(article_data)
            print(article_data)

    ruta_csv = '../data/processed/articles_processats.csv'
    
    columnes = ["fitxer", "titol", "text_original"]

    try:
        with open(ruta_csv, 'w', encoding='utf-8', newline='') as f:
            # Fem servir QUOTE_ALL perquè les comes del text no trenquin les columnes
            writer = csv.DictWriter(f, fieldnames=columnes, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for art in resultats:
                # Eliminem salts de línia interns perquè cada article 
                # ocupi exactament una sola línia al fitxer CSV.
                art_net = art.copy()
                art_net["text_original"] = art["text_original"].replace('\n', ' ').replace('\r', '').strip()
                writer.writerow(art_net)
                
        print("Exportació neta completada a data/processed/articles_nets.csv")
    except Exception as e:
        print(f"Error en l'exportació: {e}")

if __name__ == "__main__":
    main()