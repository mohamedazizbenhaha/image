import instaloader
from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
import sys

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Établit la connexion à MongoDB et retourne la collection cible."""
    try:
        mongo_host = os.getenv('MONGO_HOST', 'localhost')
        mongo_port = int(os.getenv('MONGO_PORT', 27017))
        mongo_db = os.getenv('MONGO_DB', 'instagram')
        mongo_collection = os.getenv('MONGO_COLLECTION', 'posts')

        client = MongoClient(mongo_host, mongo_port)
        db = client[mongo_db]
        logger.info("Connexion à MongoDB établie avec succès.")
        return db[mongo_collection]
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à MongoDB : {e}")
        sys.exit(1)

def authenticate_instaloader(loader):
    """Authentifie Instaloader avec les identifiants fournis."""
    username = os.getenv('INSTA_USERNAME')
    password = os.getenv('INSTA_PASSWORD')
    if username and password:
        try:
            loader.login(username, password)
            logger.info("Authentification réussie.")
        except instaloader.exceptions.BadCredentialsException:
            logger.error("Identifiants invalides. Vérifiez votre nom d'utilisateur et votre mot de passe.")
            sys.exit(1)
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Erreur de connexion lors de l'authentification : {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'authentification : {e}")
            sys.exit(1)
    else:
        logger.warning("Aucun identifiant fourni. Certaines données peuvent ne pas être accessibles.")

def scrape_hashtag(hashtag, max_posts=100):
    """Scrape les publications Instagram pour un hashtag donné et les stocke dans MongoDB."""
    loader = instaloader.Instaloader()

    # Authentification
    #authenticate_instaloader(loader)

    # Connexion à MongoDB
    collection = connect_to_mongodb()

    # Scraping des publications
    logger.info(f"Début du scraping pour le hashtag #{hashtag}")
    try:
        posts = instaloader.Hashtag.from_name(loader.context, hashtag).get_posts()
    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Erreur lors de la récupération des publications : {e}")
        sys.exit(1)

    count = 0
    for post in posts:
        if count >= max_posts:
            break

        try:
            post_data = {
                'post_id': post.shortcode,
                'username': post.owner_username,
                'caption': post.caption,
                'url': f"https://www.instagram.com/p/{post.shortcode}/",
                'image_url': post.url,
                'likes': post.likes,
                'comments_count': post.comments,
                'date': post.date_utc.isoformat()
            }

            # Insertion dans MongoDB
            collection.update_one({'post_id': post_data['post_id']}, {'$set': post_data}, upsert=True)
            logger.info(f"Publication sauvegardée : {post_data['url']}")
            count += 1
        except Exception as e:
            logger.error(f"Erreur lors du traitement d'une publication : {e}")
            continue

    logger.info(f"Scraping terminé. {count} publications ont été sauvegardées.")

if __name__ == "__main__":
    hashtag = os.getenv('HASHTAG', 'usa')
    scrape_hashtag(hashtag)
