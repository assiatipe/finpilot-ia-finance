
# FinPilot — téléchargement des vrais logos

1. Mets `download_real_logos.py` dans le même dossier que `app.py`.
2. Vérifie que tu as un dossier `assets/`.
3. Lance :

```bash
python download_real_logos.py
```

Le script va créer ou remplir automatiquement `assets/` avec les fichiers attendus par ton `app.py`, par exemple :
`apple.png`, `microsoft.png`, `nvidia.png`, `tesla.png`, `asml.png`, etc.

Ensuite relance :

```bash
streamlit run app.py
```

Remarque : ces logos sont des marques déposées. Utilise-les uniquement pour une maquette/projet académique, et évite de les présenter comme si FinPilot était affilié à ces entreprises.
