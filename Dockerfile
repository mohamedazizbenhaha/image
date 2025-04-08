# Utiliser l'image officielle Python comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY scraper.py /app/scraper.py
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande par défaut pour exécuter le script
CMD ["python", "scraper.py"]
