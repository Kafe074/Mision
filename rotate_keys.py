import hashlib
import secrets
import string
import os
import requests
import re

# 1. Generar nueva clave aleatoria (12 caracteres)
alphabet = string.ascii_letters + string.digits
new_password = ''.join(secrets.choice(alphabet) for i in range(12))

# 2. Crear el Hash SHA-256 de la nueva clave
new_hash = hashlib.sha256(new_password.encode()).hexdigest()

# 3. Notificar por Telegram
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('CHAT_ID')
mensaje = f"🔐 *Nueva Clave de Temporada Generada*\n\nLa clave para el acceso público este mes es:\n`{new_password}`\n\n_Ya ha sido actualizada en la web automáticamente._"

url = f"https://api.telegram.org/bot{token}/sendMessage"
requests.post(url, data={'chat_id': chat_id, 'text': mensaje, 'parse_mode': 'Markdown'})

# 4. Actualizar el archivo login.html (Buscando el hash de la clave pública)
# Buscaremos la tercera línea del array de claves en tu HTML
with open('login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Esta expresión regular busca la tercera posición del array de clavesAutorizadas
# Nota: Ajustaremos tu login.html para que tenga una marca fácil de encontrar
pattern = r'/\* PUBLIC_KEY \*/ "(.*?)"'
new_content = re.sub(pattern, f'/* PUBLIC_KEY */ "{new_hash}"', content)

with open('login.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Rotación completada con éxito.")