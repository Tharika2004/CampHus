import smtplib
from email.message import EmailMessage
import db # Unga db.py-ai import pannunga

def send_event_notifications(event_name, event_type, event_venue):
    # 1. DB-la irundhu verum email list-ai mattum fetch pandroam
    receiver_list = db.get_all_user_emails() 
    
    if not receiver_list:
        print("⚠️ No users found in database to notify.")
        return

    # 2. Unga Gmail Details
    # Google Account-la generate panna 16-digit 'App Password' inga poodunga
    sender_email = "tharikadoss@gmail.com" 
    app_password = "pndi zjwv pnau gmbc" 

    for receiver in receiver_list:
        msg = EmailMessage()
        msg['Subject'] = f"🚀 New Event Alert: {event_name} on CampHus!"
        msg['From'] = f"CampHus Team <{sender_email}>"
        msg['To'] = receiver

        # HTML Content for a Professional Look
        html_content = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
                <div style="text-align: center; background-color: #2c3e50; padding: 40px 20px;">
                    <h1 style="color: #ffffff; font-size: 45px; margin: 0; letter-spacing: 2px;">CAMPHUS</h1>
                    <p style="color: #ecf0f1; font-size: 18px;">Empowering Students, One Event at a Time</p>
                </div>
                
                <div style="padding: 30px; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-top: none;">
                    <h2 style="color: #2c3e50;">Hello!!! 👋</h2>
                    <p style="font-size: 18px;">Great news! A <b>new event</b> has just been listed on our website that you might be interested in.</p>
                    
                    <div style="background-color: #f9f9f9; padding: 20px; border-left: 6px solid #e74c3c; margin: 25px 0; border-radius: 4px;">
                        <p style="margin: 10px 0; font-size: 17px;"><b>📌 Event Name:</b> {event_name}</p>
                        <p style="margin: 10px 0; font-size: 17px;"><b>🏷️ Event Type:</b> {event_type}</p>
                        <p style="margin: 10px 0; font-size: 17px;"><b>📍 Venue:</b> {event_venue}</p>
                    </div>

                    <p style="font-size: 16px; color: #555;">
                        Participating in events like this is the best way to <b>level up your skills</b> and build your network. 
                        Don't let this opportunity slip away! Be proactive and stay ahead in your career.
                    </p>

                    <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
                        <a href="https://tharika2094-evwnt-project.hf.space" 
                           style="background-color: #e74c3c; color: #ffffff; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 18px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                           Visit Website Now 🚀
                        </a>
                    </div>
                </div>

                <div style="text-align: center; padding: 30px; font-size: 13px; color: #95a5a6; background-color: #f4f7f6;">
                    <p style="margin: 5px 0;">You received this because you are a registered user of CampHus.</p>
                    <p style="margin: 5px 0;"><b>Keep Learning, Keep Growing!</b><br>Team CampHus</p>
                </div>
            </body>
        </html>
        """
        
        # Fallback plain text
        msg.set_content(f"Hello! A new event '{event_name}' ({event_type}) has been added at {event_venue}. Visit CampHus to know more!")
        
        # Add HTML version
        msg.add_alternative(html_content, subtype='html')

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)
                print(f"✅ Professional Mail successfully sent to: {receiver}")
        except Exception as e:
            print(f"❌ Could not send mail to {receiver}. Error: {e}")
