import subprocess
import sys
import os

def run_instagram_once():
    """Instagram-ai scan panni mudikkum varai wait pannum"""
    print("\n" + "="*40)
    print("📸 [STEP 1] SCANNING INSTAGRAM POSTS...")
    print("="*40)
    
    # Check panni mudiikkum varai script ingaye irukkum
    subprocess.run([sys.executable, "insta.py"])
    
    print("\n✅ [Instagram] Scan process finished successfully!")
    print("-" * 40)

def run_telegram_live():
    """Instagram mudinjadhukku appram idhu start aagi activ
    e-ah irukkum"""
    print("\n" + "="*40)
    print("🤖 [STEP 2] STARTING TELEGRAM LIVE BOT...")
    print("="*40)
    print("👽 Bot is now listening for new posters...")
    
    # Telegram bot-ai start pandrom (idhu run aagittey irukkum)
    subprocess.run([sys.executable, "telegram_fetch.py"])

if __name__ == "__main__":
    print("\n🚀 --- CampHus Master Entry Point --- 🚀")
    
    # 1. First Instagram-ai run panni mudikkirom
    run_instagram_once()
    
    # 2. Athu mudinjadhukku appram dhaan Telegram start aagum
    run_telegram_live()