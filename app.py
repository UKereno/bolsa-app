import os
import requests

# Credenciais da Z-API
INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
TOKEN = os.getenv("ZAPI_TOKEN")
CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
GROUP_NAME = "UKereno Pre-Market VIP"

def obter_id_grupo():
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/groups"
    headers = {"Client-Token": CLIENT_TOKEN}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        grupos = response.json()
        for grupo in grupos:
            if grupo.get("name") == GROUP_NAME:
                return grupo.get("phone") # O Z-API retorna o ID do grupo no campo 'phone'
    print(f"Erro ao buscar grupos ou grupo não encontrado: {response.text}")
    return None

def enviar_mensagem(mensagem):
    group_id = obter_id_grupo()
    if not group_id:
        print("Não foi possível encontrar o ID do grupo.")
        return

    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-text"
    headers = {
        "Client-Token": CLIENT_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "phone": group_id,
        "message": mensagem
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print("Status do envio:", response.status_code)
    print("Resposta:", response.text)

if __name__ == "__main__":
    enviar_mensagem("🚀 Alerta automatizado: O UKereno Alerts está ativo e a funcionar perfeitamente!")
