import gradio as gr
from flask import Flask, jsonify, request
from flask_cors import CORS
import db

app_flask = Flask(__name__)
# CORS fixed for all origins to avoid browser blocks
CORS(app_flask, resources={r"/*": {"origins": "*"}})

@app_flask.route('/get-events')
def get_events_api():
    try:
        data = db.get_all_data_json()
        return jsonify(data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

# FIX: Changed route to /sync-user to match your HTML fetch call
@app_flask.route('/sync-user', methods=['POST'])
def sync_user_api():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name') # Added name field

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Updated to send both email and name to db.py
        success = db.add_user_email(email, name)
       
        if success:
            return jsonify({"message": "User synced successfully!"}), 201
        else:
            return jsonify({"error": "Failed to store user"}), 500

    except Exception as e:
        print(f"Error in sync_user: {e}")
        return jsonify({"error": str(e)}), 500

@app_flask.route('/check-mail', methods=['GET'])
def check_mail_api():
    try:
        users = db.get_all_users_json()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error":str(e)}), 500

def fetch_json_view():
    return db.get_all_data_json()

with gr.Blocks() as demo:
    gr.Markdown("# 🚀 Campus Backend API - Aiven DB Sync")
    json_display = gr.JSON(label="Live Data")
    refresh_btn = gr.Button("Refresh")
    refresh_btn.click(fn=fetch_json_view, outputs=json_display)
    demo.load(fn=fetch_json_view, outputs=json_display)

if __name__ == "__main__":
    # Hugging Face Spaces standard port
    app_flask.run(host="0.0.0.0", port=7860)