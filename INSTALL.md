# Guia de Instalação — UNION GROWTH OS

## 1. Pré-requisitos

- **Python**: 3.12+
- **Node.js**: 20+ / 22+ e npm
- **Banco de Dados**: PostgreSQL 15+ (produção) ou SQLite nativo (desenvolvimento/fallback automático)

---

## 2. Instalação Local (Desenvolvimento)

### Passo 1: Configurar variáveis de ambiente
```bash
cp .env.example .env
```

### Passo 2: Instalar dependências Python (Backend)
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\pip install -r backend/requirements.txt
# Linux/macOS:
source .venv/bin/activate && pip install -r backend/requirements.txt
```

### Passo 3: Compilar Frontend Next.js
```bash
cd frontend
npm install
npm run build
cd ..
```

### Passo 4: Executar Testes Automatizados
```bash
.\.venv\Scripts\pytest backend/tests -v
```

### Passo 5: Iniciar Servidor Unificado (API + Scheduler + Frontend)
```bash
cd backend
..\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acesse:
- Painel Executivo: `http://localhost:8000`
- Documentação OpenAPI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/ready`
