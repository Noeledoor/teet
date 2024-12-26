from flask import Flask, request, jsonify, send_from_directory
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os
import json

app = Flask(__name__)

# Constants
GOOGLE_DRIVE_FOLDER_ID = "1uCo660V9AqfNQlXtVYu2_fzR_JJIL10i"

@app.route('/')
def index():
    # Serve the HTML file for the root route
    return send_from_directory('.', 'run.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'selfie' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['selfie']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    # Save the file locally
    file_path = f"./uploads/{file.filename}"
    os.makedirs("./uploads", exist_ok=True)
    file.save(file_path)

    try:
        # Load Google Drive credentials from an environment variable
        creds_json = json.loads(os.environ["GOOGLE_DRIVE_CREDENTIALS"])
        creds = Credentials.from_authorized_user_info(creds_json)
        drive_service = build('drive', 'v3', credentials=creds)

        # Upload the file to Google Drive
        media = MediaFileUpload(file_path, mimetype=file.content_type)
        uploaded_file = drive_service.files().create(
            body={"name": file.filename, "parents": [GOOGLE_DRIVE_FOLDER_ID]},
            media_body=media,
            fields='id'
        ).execute()

        # Clean up the local file
        os.remove(file_path)

        return jsonify({"message": "File uploaded successfully", "file_id": uploaded_file.get('id')}), 200
    except Exception as e:
        # Clean up the local file in case of failure
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

if __name__ == '__main__':
    # Ensure the 'uploads' directory exists
    os.makedirs("./uploads", exist_ok=True)
    app.run(debug=True)
