import os
import requests
import random
import cloudinary
import cloudinary.uploader
from datetime import datetime
from config import DB_CONFIG, ACCESS_TOKEN, INSTAGRAM_BUSINESS_ID
import mysql.connector
from db import get_db_connection
from email_service import send_event_notifications

# Services import (Ensure folders are correct)
from services.ocr_service import extract_text_from_image
from services.nlp_service import extract_event_name, extract_date_and_time, extract_metadata
from services.qr_service import extract_qr_data
from db import is_event_duplicate

# Cloudinary Setup (Same as your telegram_fetch.py)
cloudinary.config( 
  cloud_name = " ", 
  api_key = " ", 
  api_secret = " " 
)

TEMP_FOLDER = "temp_insta"
if not os.path.exists(TEMP_FOLDER): os.makedirs(TEMP_FOLDER)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_insta_posts():
    print("📸 Checking Instagram...")
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ID}/media?fields=id,caption,media_url,timestamp&access_token={ACCESS_TOKEN}"
    
    try:
        response = requests.get(url).json()
        if "data" not in response: return

        conn = get_db_connection()
        cursor = conn.cursor()

        for post in response["data"]:
            post_id = post.get("id")
            media_url = post.get("media_url")
            
            # --- STEP 1: Quick Post ID Check (Prevents Re-processing) ---
            cursor.execute("SELECT id FROM events WHERE source_link = %s", (post_id,))
            if cursor.fetchone():
                # Idhu dhaan 'Already processed' posters-ai skip pannum 
                continue 

            # Step 2: Download only if NEW
            img_data = requests.get(media_url).content
            local_path = os.path.join(TEMP_FOLDER, f"insta_{post_id}.jpg")
            with open(local_path, 'wb') as f: f.write(img_data)

            ocr_res = extract_text_from_image(local_path)
            if ocr_res:
                name = extract_event_name(ocr_res)
                e_date, e_time = extract_date_and_time(ocr_res)
                e_type, city, state, venue, lat, lon, college, desc, is_v = extract_metadata(ocr_res)

                # --- STEP 3: Detail Check (If same poster uploaded twice in different posts) ---
                if is_event_duplicate(name, college, city, venue, e_date):
                    if os.path.exists(local_path): os.remove(local_path)
                    continue
                
                upload_result = cloudinary.uploader.upload(local_path, folder="campus_events")
                print(f"☁️  instagram poster Uploading to Cloudinary...")
                cloud_url = upload_result.get('secure_url')
                qr_data = extract_qr_data(local_path)
                
                source_link = f"https://www.instagram.com/reels/{post_id}/"
                query = """INSERT INTO events (event_name, event_type, college_name, city, state, venue, 
                           event_date, event_time, latitude, longitude, poster_image, qr_data, description, 
                           source_platform, source_link, is_verified, created_at) 
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())"""
                
                cursor.execute(query, (name, e_type, college, city, state, venue, 
                                       e_date, e_time, lat, lon, cloud_url, qr_data, desc, 
                                       "Instagram", source_link, is_v ))
                conn.commit()
                print(f"✅ New Event Stored: {name}")
                                # 🔥 TRIGGER: Mail notification inga dhaan poodanum
                try:
                    send_event_notifications(
                        event_name=name,
                        event_type=e_type,
                        event_venue=venue
                    )
                    print(f"📧 Notification sent for {name}")
                except Exception as mail_err:
                    print(f"⚠️ Mail Error: {mail_err}")

            if os.path.exists(local_path): os.remove(local_path)
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Insta Script Error: {e}")

if __name__ == "__main__":
    fetch_insta_posts()