from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os

app = Flask(__name__)

# Constants
GOOGLE_DRIVE_CREDENTIALS = "client_secret_71595812752-87e6q719uk60gaa73pqa0f6eip0gd8er.apps.googleusercontent.com.json"
GOOGLE_DRIVE_FOLDER_ID = "1uCo660V9AqfNQlXtVYu2_fzR_JJIL10i"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'selfie' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['selfie']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = f"./uploads/{file.filename}"
    file.save(file_path)

    # Authenticate and upload to Google Drive
    creds = Credentials.from_authorized_user_file(GOOGLE_DRIVE_CREDENTIALS)
    drive_service = build('drive', 'v3', credentials=creds)

    media = MediaFileUpload(file_path, mimetype=file.content_type)
    uploaded_file = drive_service.files().create(
        body={"name": file.filename, "parents": [GOOGLE_DRIVE_FOLDER_ID]},
        media_body=media,
        fields='id'
    ).execute()

    os.remove(file_path)
    return jsonify({"message": "File uploaded successfully", "file_id": uploaded_file.get('id')}), 200

if __name__ == '__main__':
    os.makedirs("./uploads", exist_ok=True)
    app.run(debug=True)
