# 🌐 Network Monitor Pro

Sistema de monitoramento de switches Cisco em tempo real com análise inteligente via IA (Groq/LLaMA).

## 📁 Estrutura do Projeto

```
├── backend/          # API Flask (Python)
│   ├── api.py        # Endpoints REST
│   ├── parser.py     # Parser de saída do switch
│   └── requirements.txt
├── frontend/         # Interface React + Vite
│   ├── src/
│   └── public/
└── scripts/          # Scripts CLI de configuração
    ├── main.py       # Funções de conexão (Netmiko)
    └── interface.py  # Menu interativo
```

## ⚙️ Pré-requisitos

- **Python 3.8+**
- **Node.js 18+**
- **Chave de API Groq** — [Obtenha aqui](https://console.groq.com/keys)

## 🚀 Como Rodar

### Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env   # Preencha com sua chave
python api.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Scripts CLI

```bash
cd scripts
python interface.py
```

## 🔧 Variáveis de Ambiente

Copie o arquivo `.env.example` para `backend/.env` e preencha:

| Variável       | Descrição                  |
|----------------|----------------------------|
| `GROQ_API_KEY` | Chave de API do Groq Cloud |

## 📡 Funcionalidades

- **Monitoramento em tempo real** — Atualização automática a cada 3 segundos
- **Análise por IA** — Diagnóstico inteligente de problemas de rede via Groq
- **Configuração via CLI** — VLANs, Trunk, interfaces (scripts)
- **Conexão SSH** — Netmiko para switches Cisco IOS

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).
