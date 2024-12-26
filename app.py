from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

app = Flask(__name__)

# Constants
GOOGLE_DRIVE_CREDENTIALS = "client_secret_71595812752-87e6q719uk60gaa73pqa0f6eip0gd8er.apps.googleusercontent.com.json"
GOOGLE_DRIVE_FOLDER_ID = "1uCo660V9AqfNQlXtVYu2_fzR_JJIL10i"
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Permission to upload files

# Function to get credentials
def get_credentials():
    creds = None
    # Check if the token exists (for authenticated users)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_DRIVE_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'selfie' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['selfie']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = f"./uploads/{file.filename}"
    file.save(file_path)

    try:
        # Get credentials and authenticate with Google Drive
        creds = get_credentials()
        drive_service = build('drive', 'v3', credentials=creds)

        # Upload file to Google Drive
        media = MediaFileUpload(file_path, mimetype=file.content_type)
        uploaded_file = drive_service.files().create(
            body={"name": file.filename, "parents": [GOOGLE_DRIVE_FOLDER_ID]},
            media_body=media,
            fields='id'
        ).execute()

        # Remove the file from the local storage
        os.remove(file_path)

        return jsonify({"message": "File uploaded successfully", "file_id": uploaded_file.get('id')}), 200
    
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    os.makedirs("./uploads", exist_ok=True)
    app.run(debug=True)
