from bs4 import BeautifulSoup

def neteja_html(ruta_fitxer):
    with open(ruta_fitxer, 'r', encoding='utf-8') as f:
        contingut = f.read()
    
    soup = BeautifulSoup(contingut, 'html.parser')

    # 1. ELIMINAR EL "MENÚ AMAGAT" DE VILAWEB I ALTRES NOISES
    # El text del gas pebre està dins de 'navigation-layer'. L'eliminem directament.
    for noise in soup.select('#navigation-layer, #text_minut, header, footer, aside, nav, script, style'):
        noise.decompose()

    # 2. EXTRACCIÓ DEL TÍTOL
    # Prioritat: og:title (metadades) -> h1 -> title tag
    meta_titol = soup.find("meta", property="og:title")
    if meta_titol and meta_titol.get("content"):
        titol = meta_titol["content"]
    else:
        titol_tag = soup.find('h1') or soup.find('title')
        titol = titol_tag.get_text(strip=True) if titol_tag else "Sense títol"

    # 3. EXTRACCIÓ DEL COS (Targeting l'article real)
    # VilaWeb usa la classe 'content-noticia-body' o 'article-content-publi'
    article_principal = soup.find('article', class_='content-noticia-body') or \
                        soup.find('article', class_='article-content-publi') or \
                        soup.find('main')
    
    paragrafs = []
    if article_principal:
        # Busquem només els <p> que NO estiguin buits
        for p in article_principal.find_all('p'):
            text_p = p.get_text(strip=True)
            # Filtre de qualitat: paràgrafs reals solen tenir més de 40 caràcters
            if len(text_p) > 40:
                paragrafs.append(text_p)

    # Si després de tot seguim sense text, agafem el que sigui llarg del body
    if not paragrafs:
        paragrafs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 100]

    text_net = "\n\n".join(paragrafs)
    
    return titol, text_net

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