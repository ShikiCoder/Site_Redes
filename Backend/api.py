from flask import Flask, request, jsonify
from flask_cors import CORS
from netmiko import ConnectHandler
from parser import parse_show_interface_status
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/conectar', methods=['POST'])
def conectar_switch():
    data = request.get_json()

    if not data:
        return jsonify({'erro': 'Nenhum dado recebido no body da requisição'}), 400

    ip = data.get('ip')
    user = data.get('user')
    password = data.get('pass')

    if not ip or not user or not password:
        return jsonify({'erro': f'Campos faltando. Recebidos: IP={ip}, USER={user}, PASS={password}'}), 400

    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': user,
        'password': password,
        'port': 22,
    }

    try:
        net_connect = ConnectHandler(**device)
        output = net_connect.send_command('show interface status')
        net_connect.disconnect()

        interfaces_list = parse_show_interface_status(output)

        return jsonify(interfaces_list), 200

    except Exception as e:
        print("Erro detalhado no backend:", str(e))
        return jsonify({'erro': f'Falha ao conectar ao switch: {str(e)}'}), 500


@app.route('/analisar', methods=['POST'])
def analisar_status():
    data = request.get_json()
    if not data:
        return jsonify({'erro': 'Nenhum dado recebido'}), 400

    texto = data.get('texto')
    if not texto:
        return jsonify({'erro': 'Texto faltando'}), 400

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "Você é um engenheiro SRE especialista em troubleshooting."
            },
            {
                "role": "user",
                "content": f"Analise o problema e dê resposta curta com causa + comandos + solução:\n\n{texto}"
            }
        ],
        "temperature": 0.3
    }

    try:
        cmd = [
            "curl", "-s", "-X", "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {os.environ.get('GROQ_API_KEY', '')}",
            "-d", json.dumps(payload)
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return jsonify({'erro': f'Erro no curl: {stderr}'}), 500

        res_json = json.loads(stdout)

        if "error" in res_json:
            return jsonify({'erro': res_json}), 500

        result = res_json['choices'][0]['message']['content']
        return jsonify({'resultado': result}), 200

    except Exception as e:
        return jsonify({'erro': f'Erro ao conectar à IA: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
