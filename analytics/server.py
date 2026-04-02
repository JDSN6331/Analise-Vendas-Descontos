"""
Servidor Web para Dashboard de Analytics
Cooxupé Sales Analytics

Execute este script para disponibilizar o dashboard na rede local.
Outros usuários podem acessar via: http://nome-da-maquina:5000 ou http://seu-ip:5000
"""

from flask import Flask, send_file, jsonify
import os
import socket
import subprocess
import sys

# Configurações
PORT = 5050  # Porta 5050 para não conflitar com outras aplicações
DASHBOARD_PATH = os.path.join(os.path.dirname(__file__), 'dashboard', 'dashboard.html')

app = Flask(__name__)


@app.route('/')
def serve_dashboard():
    """Serve o dashboard principal."""
    if os.path.exists(DASHBOARD_PATH):
        return send_file(DASHBOARD_PATH)
    else:
        return """
        <h1>Dashboard não encontrado</h1>
        <p>Execute primeiro o script de análise para gerar o dashboard:</p>
        <code>python analytics/main.py</code>
        """, 404


@app.route('/refresh')
def refresh_data():
    """Regenera o dashboard com dados atualizados."""
    try:
        # Executa o script de análise
        main_script = os.path.join(os.path.dirname(__file__), 'main.py')
        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'Dashboard atualizado com sucesso! Recarregue a página.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao atualizar: {result.stderr}'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/status')
def status():
    """Retorna o status do servidor."""
    return jsonify({
        'status': 'online',
        'dashboard_exists': os.path.exists(DASHBOARD_PATH),
        'hostname': socket.gethostname(),
        'ip': get_local_ip()
    })


def get_local_ip():
    """Obtém o IP local da máquina."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def print_access_info():
    """Imprime informações de acesso."""
    hostname = socket.gethostname()
    ip = get_local_ip()
    
    print("\n" + "="*60)
    print("[*] SERVIDOR DO DASHBOARD INICIADO")
    print("="*60)
    print(f"\n[+] Acesse o dashboard por:")
    print(f"   - http://localhost:{PORT}")
    print(f"   - http://{hostname}:{PORT}")
    print(f"   - http://{ip}:{PORT}")
    print(f"\n[+] Para atualizar os dados, acesse:")
    print(f"   - http://{ip}:{PORT}/refresh")
    print(f"\n[!] Mantenha este terminal aberto para o servidor funcionar!")
    print("   Pressione Ctrl+C para encerrar.\n")
    print("="*60 + "\n")


if __name__ == '__main__':
    print_access_info()
    
    # Executar servidor
    # host='0.0.0.0' permite acesso de outras máquinas na rede
    app.run(host='0.0.0.0', port=PORT, debug=False)
