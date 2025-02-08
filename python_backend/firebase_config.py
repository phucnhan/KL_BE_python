import os
import json
import base64
import firebase_admin
from dotenv import load_dotenv
load_dotenv()
from firebase_admin import credentials, firestore

# 🔹 Giải mã Firebase credentials từ biến môi trường
firebase_credentials = base64.b64decode(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"))
service_account_info = json.loads(firebase_credentials)

# 🔹 Khởi tạo Firebase Admin SDK
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

# 🔹 Kết nối Firestore
db = firestore.client()

