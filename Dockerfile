# Utiliser l'image officielle Python comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de l'application
COPY scraper.py /app/scraper.py
COPY requirements.txt /app/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Définir les variables d'environnement par défaut
ENV MONGO_HOST=mongodb
ENV MONGO_PORT=27017
ENV MONGO_DB=instagram
ENV MONGO_COLLECTION=posts
ENV HASHTAG=donaldtrump
ENV MAX_POSTS=100

# Commande par défaut pour exécuter le script
CMD ["python", "scraper.py"]
