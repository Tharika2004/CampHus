import os
import cloudinary
import cloudinary.uploader
from datetime import datetime
from telegram.ext import Updater, MessageHandler, Filters
from services.ocr_service import extract_text_from_image
from services.nlp_service import extract_event_name, extract_date_and_time, extract_metadata
from services.qr_service import extract_qr_data
from db import get_db_connection
from config import TELEGRAM_TOKEN
from db import is_event_duplicate
from email_service import send_event_notifications

# Cloudinary Configuration
cloudinary.config(
  cloud_name = "",
  api_key = "",
  api_secret = "" 
)

TEMP_FOLDER = "temp_posters"
if not os.path.exists(TEMP_FOLDER): 
    os.makedirs(TEMP_FOLDER)

def handle_poster(update, context):
    msg = update.effective_message
    if not msg: return
    conn = None
    try:
        photo_obj = msg.photo[-1] if msg.photo else msg.document
        u_id = photo_obj.file_unique_id 
        file_obj = photo_obj.get_file()
        filename = f"temp_{u_id}.jpg"
        local_path = os.path.join(TEMP_FOLDER, filename)
        file_obj.download(custom_path=local_path)

        # OCR Extraction
        ocr_res = extract_text_from_image(local_path)
        if not ocr_res:
            msg.reply_text("❌ Text detect panna mudiyala.")
            if os.path.exists(local_path): os.remove(local_path)
            return
        source_link = "https://t.me/+zvxEx4MfvrQ1Zjk1"
        name = extract_event_name(ocr_res)
        e_date, e_time = extract_date_and_time(ocr_res)
        e_type, city, state, venue, lat, lon, college, description, is_verified = extract_metadata(ocr_res)

        # --- STEP 2: Detail-based Duplicate Check (Before Cloudinary Upload) ---
        if is_event_duplicate(name, college, city, venue, e_date):
            msg.reply_text(f"⚠️ Event '{name}' already exists!No need to add again👍 ...")
            if os.path.exists(local_path): os.remove(local_path)
            return 

        # ☁️ Upload to Cloudinary (Duplicate illana mattum dhaan inga varum)
        print(f"☁️  telegram poster Uploading to Cloudinary...")
        upload_result = cloudinary.uploader.upload(local_path, folder="campus_events")
        cloud_url = upload_result.get('secure_url')
        qr_data = extract_qr_data(local_path)

        if os.path.exists(local_path): os.remove(local_path)

        # DB Insert
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """INSERT INTO events (event_name, event_type, college_name, city, state, venue,
                   event_date, event_time, latitude, longitude, poster_image, qr_data, description, 
                   source_platform, source_link, is_verified, created_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())"""
       
        # source_link-la u_id store pandroam duplicate find panna
        cursor.execute(query, (name, e_type, college, city, state, venue,
                               e_date, e_time, lat, lon, cloud_url, qr_data, description, 
                               "Telegram", source_link, is_verified ))
        conn.commit()
        msg.reply_text(f"✅ Event Saved!\n🏆 {name}\n📅 {e_date} | ⏰ {e_time}\n🏙️ City: {city}📍 {venue} ", parse_mode="Markdown")
                # 🔥 TRIGGER: Telegram-la event save aana udanae mail anuppum
        try:
            send_event_notifications(
                event_name=name,
                event_type=e_type,
                event_venue=venue
            )
            print(f"📧 Notification sent for {name}")
            
        except Exception as mail_err:
            print(f"⚠️ Mail Error: {mail_err}")
        print("DATA STORED SUCCESSFULLY✅")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    print("🤖----BOT 👾 STARTING----👽")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo | Filters.document.image, handle_poster))
    updater.start_polling()
    print("👽----BOT 👾 LISTENING 🤖----")
    updater.idle()