import hashlib
import secrets
import string
import os
import requests
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Generar nueva clave aleatoria
alphabet = string.ascii_letters + string.digits
new_password = ''.join(secrets.choice(alphabet) for i in range(12))
new_hash = hashlib.sha256(new_password.encode()).hexdigest()

# --- NUEVA SECCIÓN: ACTUALIZAR FIREBASE ---
# Recuperamos el JSON de las credenciales desde el secreto de GitHub
service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)

# Evitar inicializar varias veces si se corre en local
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
# Actualizamos el documento que lee tu panel de admin
db.collection('config').document('acceso').update({
    'clave_mensual': new_password
})
print("✅ Firebase actualizado con la nueva clave.")
# ------------------------------------------

# 2. Notificar por Telegram (Tu código actual)
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('CHAT_ID')
mensaje = f"🔐 *Nueva Clave de Temporada*\n\nClave: `{new_password}`\n\n_Actualizada en Web y Firebase._"
url = f"https://api.telegram.org/bot{token}/sendMessage"
requests.post(url, data={'chat_id': chat_id, 'text': mensaje, 'parse_mode': 'Markdown'})

# 3. Actualizar login.html (Tu código actual)
with open('login.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'/\* PUBLIC_KEY \*/ "(.*?)"'
new_content = re.sub(pattern, f'/* PUBLIC_KEY */ "{new_hash}"', content)

with open('login.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Proceso completo: Telegram, Firebase y HTML sincronizados.")