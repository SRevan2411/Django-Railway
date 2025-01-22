# firebase_config.py
import firebase_admin
from firebase_admin import credentials, storage

# Ruta al archivo JSON
cred = credentials.Certificate("reactvideos-291d3-firebase-adminsdk-6p17c-91ce80f2c3.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://reactvideos-291d3.appspot.com'
})