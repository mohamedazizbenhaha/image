import instascrape
from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
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
        raise

def scrape_instagram_posts(hashtag, max_posts=100):
    """Scrape les publications Instagram pour un hashtag donné et les stocke dans MongoDB."""
    # Connexion à MongoDB
    collection = connect_to_mongodb()

    # Création d'un profil Instagram
    profile = instascrape.Profile(f"https://www.instagram.com/explore/tags/{hashtag}/")

    # Extraction des posts
    posts = profile.get_posts()

    count = 0
    for post in posts:
        if count >= max_posts:
            break

        try:
            # Extraction des données du post
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

            # Extraction des commentaires
            comments = []
            for comment in post.comments:
                comment_data = {
                    'comment_id': comment.id,
                    'text': comment.text,
                    'created_at': datetime.fromtimestamp(comment.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    'owner_username': comment.owner_username,
                    'like_count': comment.like_count
                }
                comments.append(comment_data)

            post_data['comments'] = comments

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
    scrape_instagram_posts(hashtag)
