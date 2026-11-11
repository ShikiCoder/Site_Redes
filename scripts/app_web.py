from flask import Flask, render_template_string, request, session, redirect, url_for
from main import (
    CONFIGURE_VLAN,
    SHOW_VLAN,
    SET_INTERFACE_STATE,
    SHOW_RUNNING_CONFIG,
    CONFIGURE_TRUNK
)

app = Flask(__name__)
# Chave secreta necessária para gerenciar sessões de login com segurança
app.secret_key = "sua_chave_secreta_super_segura_aqui"

# Defina aqui a senha de administrador do painel
ADMIN_PASSWORD = "admin"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Switch Manager</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --input-bg: #0f172a;
            --terminal-bg: #030712;
            --terminal-text: #38ef7d;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem 1rem;
        }

        .dashboard {
            width: 100%;
            max-width: 900px;
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }

        .header {
            padding: 2rem 2.5rem 1.5rem 2.5rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .header-icon {
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            color: white;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        }

        .header-text h1 {
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .header-text p {
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 2px;
        }

        .btn-logout {
            background-color: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .btn-logout:hover {
            background-color: #ef4444;
            color: white;
        }

        .nav-tabs {
            display: flex;
            background-color: rgba(15, 23, 42, 0.6);
            padding: 0.5rem 1.5rem;
            gap: 0.5rem;
            border-bottom: 1px solid var(--card-border);
            overflow-x: auto;
        }

        .nav-tabs a {
            text-decoration: none;
            color: var(--text-muted);
            font-size: 0.875rem;
            font-weight: 500;
            padding: 0.6rem 1rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            white-space: nowrap;
        }

        .nav-tabs a:hover {
            color: var(--text-main);
            background-color: rgba(255, 255, 255, 0.05);
        }

        .nav-tabs a.active {
            color: #38bdf8;
            background-color: rgba(56, 189, 248, 0.1);
            font-weight: 600;
        }

        .content {
            padding: 2rem 2.5rem;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.25rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .form-group.full-width {
            grid-column: span 2;
        }

        label {
            font-size: 0.825rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        input, select {
            background-color: var(--input-bg);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
            width: 100%;
        }

        input:focus, select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
        }

        button.action-btn {
            grid-column: span 2;
            margin-top: 0.5rem;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            border: none;
            padding: 0.85rem 1.5rem;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
            width: 100%;
        }

        button.action-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4);
        }

        .terminal-wrapper {
            margin-top: 2rem;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--card-border);
            background-color: var(--terminal-bg);
        }

        .terminal-header {
            background-color: rgba(255, 255, 255, 0.03);
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .dot { width: 10px; height: 10px; border-radius: 50%; }
        .dot-red { background-color: #ef4444; }
        .dot-yellow { background-color: #f59e0b; }
        .dot-green { background-color: #10b981; }

        .terminal-title {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-left: 0.5rem;
            font-family: 'Fira Code', monospace;
        }

        .terminal-body {
            padding: 1.25rem;
            color: var(--terminal-text);
            font-family: 'Fira Code', monospace;
            font-size: 0.875rem;
            line-height: 1.6;
            white-space: pre-wrap;
            max-height: 320px;
            overflow-y: auto;
        }

        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .alert-error {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }

        @media (max-width: 640px) {
            .form-grid { grid-template-columns: 1fr; }
            .form-group.full-width, button.action-btn { grid-column: span 1; }
        }
    </style>
</head>
<body>

    <div class="dashboard">
        <div class="header">
            <div class="header-left">
                <div class="header-icon">
                    <i class="ph ph-intersect"></i>
                </div>
                <div class="header-text">
                    <h1>Gerenciador de Switches</h1>
                    <p>Automação Cisco IOS via SSH</p>
                </div>
            </div>
            <a href="/logout" class="btn-logout"><i class="ph ph-sign-out"></i> Sair</a>
        </div>

        <div class="nav-tabs">
            <a href="/?tab=vlan" {% if tab == 'vlan' %}class="active"{% endif %}><i class="ph ph-rows"></i> Config. VLAN</a>
            <a href="/?tab=show_vlan" {% if tab == 'show_vlan' %}class="active"{% endif %}><i class="ph ph-list-bullets"></i> Ver VLANs</a>
            <a href="/?tab=state" {% if tab == 'state' %}class="active"{% endif %}><i class="ph ph-power"></i> Estado Porta</a>
            <a href="/?tab=status" {% if tab == 'status' %}class="active"{% endif %}><i class="ph ph-chart-bar"></i> Status Portas</a>
            <a href="/?tab=trunk" {% if tab == 'trunk' %}class="active"{% endif %}><i class="ph ph-git-fork"></i> Trunk</a>
        </div>

        <div class="content">
            <form method="POST" id="switchForm" onsubmit="showLoading()">
                <input type="hidden" name="tab" value="{{ tab }}">

                <div class="form-grid">
                    <div class="form-group {% if tab in ['show_vlan', 'status'] %}full-width{% endif %}">
                        <label>IP do Switch</label>
                        <input type="text" name="host" placeholder="Ex: 192.168.1.1" required value="{{ request.form.get('host', '') }}">
                    </div>

                    {% if tab == 'vlan' %}
                        <div class="form-group">
                            <label>ID da VLAN</label>
                            <input type="text" name="vlan" placeholder="Ex: 10" required value="{{ request.form.get('vlan', '') }}">
                        </div>
                        <div class="form-group">
                            <label>Nome da VLAN</label>
                            <input type="text" name="vlan_name" placeholder="Ex: VDS_DADOS" value="{{ request.form.get('vlan_name', '') }}">
                        </div>
                        <div class="form-group">
                            <label>Porta do Switch</label>
                            <input type="text" name="interface_switch" placeholder="Ex: Ethernet1/0" value="{{ request.form.get('interface_switch', 'Ethernet1/0') }}">
                        </div>
                        <div class="form-group">
                            <label>IP da SVI / VLAN</label>
                            <input type="text" name="vlan_ip" placeholder="Ex: 10.0.10.1" value="{{ request.form.get('vlan_ip', '') }}">
                        </div>
                        <div class="form-group">
                            <label>Máscara da Sub-rede</label>
                            <input type="text" name="vlan_mask" value="{{ request.form.get('vlan_mask', '255.255.255.0') }}">
                        </div>

                    {% elif tab == 'state' %}
                        <div class="form-group">
                            <label>Interface</label>
                            <input type="text" name="interface" placeholder="Ex: Ethernet1/0" value="{{ request.form.get('interface', 'Ethernet1/0') }}">
                        </div>
                        <div class="form-group full-width">
                            <label>Estado Desejado</label>
                            <select name="state">
                                <option value="UP">UP (no shutdown)</option>
                                <option value="DOWN">DOWN (shutdown)</option>
                            </select>
                        </div>

                    {% elif tab == 'trunk' %}
                        <div class="form-group">
                            <label>Interface</label>
                            <input type="text" name="interface" placeholder="Ex: Ethernet1/1" value="{{ request.form.get('interface', 'Ethernet1/1') }}">
                        </div>
                        <div class="form-group">
                            <label>Ação no Trunk</label>
                            <select name="action" id="trunkAction" onchange="toggleVlanInput()">
                                <option value="configure" {% if request.form.get('action') == 'configure' %}selected{% endif %}>Configurar Trunk</option>
                                <option value="remove" {% if request.form.get('action') == 'remove' %}selected{% endif %}>Remover Trunk (Voltar para Access)</option>
                            </select>
                        </div>
                        <div class="form-group full-width" id="vlanGroup">
                            <label>VLANs Permitidas (Apenas para Configuração)</label>
                            <input type="text" name="vlans" placeholder="Ex: 10,20,30" value="{{ request.form.get('vlans', '10,20,30') }}">
                        </div>
                    {% endif %}

                    <button type="submit" class="action-btn" id="btnSubmit">
                        <span class="spinner" id="spinner"></span>
                        <span id="btnText">Executar Configuração</span>
                        <i class="ph ph-paper-plane-right" id="btnIcon"></i>
                    </button>
                </div>
            </form>

            {% if output %}
                <div class="terminal-wrapper">
                    <div class="terminal-header">
                        <div class="dot dot-red"></div>
                        <div class="dot dot-yellow"></div>
                        <div class="dot dot-green"></div>
                        <span class="terminal-title">console_output.log</span>
                    </div>
                    <div class="terminal-body">{{ output }}</div>
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('spinner').style.display = 'block';
            document.getElementById('btnIcon').style.display = 'none';
            document.getElementById('btnText').innerText = 'Conectando ao Switch...';
            document.getElementById('btnSubmit').disabled = true;
        }

        function toggleVlanInput() {
            const actionSelect = document.getElementById('trunkAction');
            const vlanGroup = document.getElementById('vlanGroup');
            if (actionSelect && vlanGroup) {
                if (actionSelect.value === 'remove') {
                    vlanGroup.style.display = 'none';
                } else {
                    vlanGroup.style.display = 'flex';
                }
            }
        }

        // Executa ao carregar a página para respeitar o estado inicial
        document.addEventListener("DOMContentLoaded", function() {
            toggleVlanInput();
        });
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Cisco Switch Manager</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --accent: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --input-bg: #0f172a;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
        }
        .login-card {
            width: 100%;
            max-width: 400px;
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        .login-icon {
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
            width: 60px;
            height: 60px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: white;
            margin: 0 auto 1.5rem auto;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        }
        h2 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }
        p { color: var(--text-muted); font-size: 0.875rem; margin-bottom: 2rem; }
        .form-group { text-align: left; margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.4rem; }
        label { font-size: 0.825rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }
        input {
            background-color: var(--input-bg);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-size: 0.95rem;
            outline: none;
            width: 100%;
        }
        input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15); }
        button {
            width: 100%;
            margin-top: 1rem;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            border: none;
            padding: 0.85rem;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4); }
        .error-msg {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 0.75rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-icon"><i class="ph ph-lock-key"></i></div>
        <h2>Área Restrita</h2>
        <p>Insira a senha de administrador para gerenciar os switches</p>

        {% if error %}
            <div class="error-msg">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label>Senha de Administrador</label>
                <input type="password" name="password" placeholder="••••••••" required autofocus>
            </div>
            <button type="submit">Entrar no Painel</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "Senha incorreta. Tente novamente."
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    tab = request.args.get("tab", "vlan")
    output = None

    if request.method == "POST":
        tab = request.form.get("tab", "vlan")
        host = request.form.get("host")

        try:
            if tab == "vlan":
                vlan = request.form.get("vlan")
                vlan_name = request.form.get("vlan_name")
                interface_switch = request.form.get("interface_switch")
                vlan_ip = request.form.get("vlan_ip")
                vlan_mask = request.form.get("vlan_mask")
                output = CONFIGURE_VLAN(host, vlan, vlan_name, interface_switch, vlan_ip, vlan_mask)

            elif tab == "show_vlan":
                output = SHOW_VLAN(host)

            elif tab == "state":
                interface = request.form.get("interface")
                state = request.form.get("state")
                output = SET_INTERFACE_STATE(host, interface, state)

            elif tab == "status":
                output = SHOW_RUNNING_CONFIG(host)

            elif tab == "trunk":
                interface = request.form.get("interface")
                vlans = request.form.get("vlans")
                action = request.form.get("action", "configure")
                output = CONFIGURE_TRUNK(host, interface, vlans, action)

        except Exception as e:
            output = f"❌ Erro de conexão/execução:\n{str(e)}"

    return render_template_string(HTML_TEMPLATE, tab=tab, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
