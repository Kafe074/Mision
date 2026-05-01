import hashlib
import secrets
import string
import os
import requests
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Generar nueva clave aleatoria (Sugerencia: minúsculas y números para evitar errores)
alphabet = string.ascii_lowercase + string.digits 
new_password = ''.join(secrets.choice(alphabet) for i in range(12))
new_hash = hashlib.sha256(new_password.encode()).hexdigest()

# --- SECCIÓN: ACTUALIZAR FIREBASE ---
service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
db.collection('config').document('acceso').update({
    'clave_mensual': new_password
})
print("✅ Firebase actualizado con la nueva clave.")

# --- SECCIÓN: NOTIFICAR Y LISTAR USUARIOS ---
solicitudes = db.collection('solicitudes').where('estado', '==', 'aprobado').stream()

usuarios_notificados = []

for doc in solicitudes:
    user = doc.to_dict()
    nombre = user.get('nombre', 'Misionero')
    correo = user.get('correo')
    
    if correo:
        usuarios_notificados.append(f"• {nombre} ({correo})")
        
        # Crear el correo en Firestore
        db.collection('correos_enviados').add({
            'to': correo,
            'from': 'Familiacusilayme@gmail.com', # <--- AGREGA ESTO (El verificado en Brevo)
            'message': {
                'subject': "🔑 Nueva Clave de Acceso - Luz en el Sudeste Asiático",
                'html': f"""
                    <div style="font-family: sans-serif; color: #333;">
                        <h2 style="color: #1B4332;">¡Hola {nombre}!</h2>
                        <p>Iniciamos un nuevo mes y la clave de acceso ha sido actualizada.</p>
                        <div style="background: #f4f4f4; padding: 20px; border-radius: 10px; border: 1px solid #D4AF37; text-align: center;">
                            <p style="margin: 0; font-size: 14px;">Tu clave para este mes es:</p>
                            <h2 style="color: #1B4332; letter-spacing: 2px; margin: 10px 0;">{new_password}</h2>
                        </div>
                        <p style="font-size: 0.9em; color: #666; margin-top: 20px;">
                            <i>Recuerda que esta clave es personal. Dios te bendiga.</i>
                        </p>
                    </div>
                """,
                'text': f"Hola {nombre}, la clave de este mes es: {new_password}"
            }
        })

# --- REPORTE FINAL DE TELEGRAM (Fuera del bucle for) ---
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('CHAT_ID')

lista_texto = "\n".join(usuarios_notificados) if usuarios_notificados else "Ningún usuario aprobado."

mensaje_final = (
    f"🔐 *ROTACIÓN COMPLETADA*\n\n"
    f"Nueva Clave: `{new_password}`\n\n"
    f"📧 *Se envió el correo a:*\n"
    f"{lista_texto}\n\n"
    f"✅ El sistema está actualizado."
)

url = f"https://api.telegram.org/bot{token}/sendMessage"
requests.post(url, data={'chat_id': chat_id, 'text': mensaje_final, 'parse_mode': 'Markdown'})

# 3. Actualizar index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'/\* PUBLIC_KEY \*/ "(.*?)"'
new_content = re.sub(pattern, f'/* PUBLIC_KEY */ "{new_hash}"', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Proceso completo: Telegram, Firebase y HTML sincronizados.")