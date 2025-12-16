import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
WAMUNDO_API_KEY = os.getenv('WAMUNDO_API_KEY')
WAMUNDO_PHONE_ID = os.getenv('WAMUNDO_PHONE_ID')
PORT = int(os.getenv('PORT', 5000))

# URLs de las APIs
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
WAMUNDO_API_URL = "https://api.wamundo.com/send"

# Personalidad del bot
SYSTEM_PROMPT = """Eres Herasi AI Agent, un asistente virtual inteligente y amigable. 
Tu objetivo es ayudar a los usuarios de manera clara, concisa y profesional.
Responde siempre en español de manera natural y conversacional."""


def consultar_deepseek(mensaje_usuario):
    """Consulta a DeepSeek API y obtiene una respuesta"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensaje_usuario}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        respuesta = response.json()
        return respuesta['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Error al consultar DeepSeek: {e}")
        return "Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo."


def enviar_mensaje_whatsapp(numero_destino, mensaje):
    """Envía un mensaje por WhatsApp usando WaMundo API"""
    try:
        headers = {
            "secret": WAMUNDO_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "phone": numero_destino,
            "message": mensaje,
            "id": WAMUNDO_PHONE_ID
        }
        
        response = requests.post(WAMUNDO_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        return True
        
    except Exception as e:
        print(f"Error al enviar mensaje por WhatsApp: {e}")
        return False


@app.route('/', methods=['GET'])
def home():
    """Ruta de inicio - verifica que el servidor esté funcionando"""
    return jsonify({
        "status": "online",
        "bot": "Herasi AI Agent",
        "message": "Bot de WhatsApp con IA funcionando correctamente"
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para recibir mensajes de WaMundo"""
    try:
        # Obtener datos del webhook
        data = request.get_json()
        print(f"Webhook recibido: {data}")
        
        # Extraer información del mensaje
        mensaje_entrante = data.get('message', {}).get('body', '')
        numero_remitente = data.get('from', '')
        
        # Validar que tengamos los datos necesarios
        if not mensaje_entrante or not numero_remitente:
            return jsonify({"status": "error", "message": "Datos incompletos"}), 400
        
        # Obtener respuesta de DeepSeek
        respuesta_ia = consultar_deepseek(mensaje_entrante)
        
        # Enviar respuesta por WhatsApp
        enviado = enviar_mensaje_whatsapp(numero_remitente, respuesta_ia)
        
        if enviado:
            return jsonify({"status": "success", "message": "Respuesta enviada"}), 200
        else:
            return jsonify({"status": "error", "message": "Error al enviar respuesta"}), 500
            
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/test', methods=['POST'])
def test():
    """Ruta de prueba para enviar mensajes manualmente"""
    try:
        data = request.get_json()
        numero = data.get('numero')
        mensaje = data.get('mensaje')
        
        if not numero or not mensaje:
            return jsonify({"error": "Faltan parámetros"}), 400
        
        enviado = enviar_mensaje_whatsapp(numero, mensaje)
        
        if enviado:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print(f"🤖 Herasi AI Agent iniciando en puerto {PORT}...")
    print(f"📱 WhatsApp ID: {WAMUNDO_PHONE_ID}")
    app.run(host='0.0.0.0', port=PORT, debug=True)