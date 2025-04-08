import instaloader
from pymongo import MongoClient
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Établit la connexion à MongoDB et retourne la collection cible."""
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    mongo_port = int(os.getenv('MONGO_PORT', 27017))
    mongo_db = os.getenv('MONGO_DB', 'instagram')
    mongo_collection = os.getenv('MONGO_COLLECTION', 'posts')

    client = MongoClient(mongo_host, mongo_port)
    db = client[mongo_db]
    return db[mongo_collection]

def scrape_hashtag(hashtag, max_posts=100):
    """Scrape les publications Instagram pour un hashtag donné."""
    L = instaloader.Instaloader()

    # Authentification (facultatif mais recommandé pour éviter les limitations)
    username = os.getenv('INSTA_USERNAME')
    password = os.getenv('INSTA_PASSWORD')
    if username and password:
        try:
            L.login(username, password)
            logger.info("Authentification réussie.")
        except Exception as e:
            logger.error(f"Échec de l'authentification : {e}")
            return

    # Connexion à MongoDB
    collection = connect_to_mongodb()

    # Scraping des publications
    logger.info(f"Début du scraping pour le hashtag #{hashtag}")
    posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()
    count = 0

    for post in posts:
        if count >= max_posts:
            break

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

    logger.info(f"Scraping terminé. {count} publications ont été sauvegardées.")

if __name__ == "__main__":
    hashtag = os.getenv('HASHTAG', 'donaldtrump')
    max_posts = int(os.getenv('MAX_POSTS', 100))
    scrape_hashtag(hashtag, max_posts)
