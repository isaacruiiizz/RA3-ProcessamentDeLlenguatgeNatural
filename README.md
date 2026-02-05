# Pràctica M5071_RA3: Processament de Llenguatge Natural (NLP)

Aquest projecte forma part del mòdul **M5071: Models d'Intel·ligència Artificial** del curs d'especialització en **IA i Big Data**. L'objectiu és aplicar diverses tècniques de NLP per extreure, netejar, classificar i resumir informació d'articles web en format HTML.

## Autors
* **Isaac Ruiz**
* **Pau Miró Fàbregas**

---

## Estructura del Projecte

El repositori s'organitza de la següent manera per garantir la reproductibilitat de l'exercici:

```text
/
├── data/
│   └── raw/                # Conté els 5 fitxers .html originals per a les proves
│   └── processed/          # Conté els fitxers ja netejats
├── src/                    # Codi font principal
│   ├── main.py             # Script principal per executar tot el pipeline
│   ├── scraper.py          # Pas 1: Extracció de text des d'HTML
│   ├── preprocess.py       # Pas 2: Tokenització i neteja (NLTK/SpaCy)
│   └── models.py           # Pas 3 i 4: Vectorització i models de HuggingFace
├── requirements.txt        # Llibreries necessàries per executar el projecte
└── README.md               # Documentació general