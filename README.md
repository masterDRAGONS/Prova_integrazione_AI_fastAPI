# 🤖 FastAPI Chat AI con Autenticazione

Un'applicazione di chat moderna integrata con **Google Gemini AI** e un **sistema di autenticazione robusto** basato su PostgreSQL e JWT.

## 📋 Indice

- [Panoramica](#panoramica)
- [Stack Tecnologico](#stack-tecnologico)
- [Requisiti di Sistema](#requisiti-di-sistema)
- [Setup e Installazione](#setup-e-installazione)
- [Configurazione](#configurazione)
- [Struttura del Progetto](#struttura-del-progetto)
- [Database](#database)
- [API Endpoints](#api-endpoints)
- [Sistema di Autenticazione](#sistema-di-autenticazione)
- [Rate Limiting](#rate-limiting)
- [Esecuzione](#esecuzione)
- [Development](#development)

---

## 🎯 Panoramica

Questa applicazione fornisce:

✅ **Chat con IA**: Interfaccia web per chattare con Google Gemini AI
✅ **Autenticazione**: Sistema di login/registrazione con JWT e bcrypt
✅ **Persistenza**: Database PostgreSQL per utenti e dati
✅ **Rate Limiting**: Protezione contro l'abuso con limiti per utente
✅ **API REST**: Endpoint JSON per integrazione programmatica

---

## 🛠️ Stack Tecnologico

### Backend
- **FastAPI** 0.136.3+ - Framework web moderno e veloce
- **SQLAlchemy** 2.0+ - ORM per database
- **psycopg** 3.0+ - Driver PostgreSQL
- **python-jose** 3.3.0+ - JWT per autenticazione
- **bcrypt** 4.0+ - Hashing sicuro delle password

### Frontend
- **Jinja2** - Template HTML
- **HTML5/CSS3** - UI responsive
- **JavaScript vanilla** - Client-side validation

### Database
- **PostgreSQL** 18 - Database relazionale

### External APIs
- **Google Gemini AI** - LLM per chat

---

## 📦 Requisiti di Sistema

- Python 3.12+
- PostgreSQL 18+
- Windows 11/10 Pro

---

## 🚀 Setup e Installazione

### 1. Virtual Environment
```powershell
uv venv
.venv\Scripts\Activate.ps1
```

### 2. Installare Dipendenze
```powershell
uv sync
```

### 3. Configurare .env
Crea file `.env`:

```env
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your-very-long-random-secret-key-change-in-production
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/chat_ai_db
ALGORITHM=HS256
AUTH_RATE_LIMIT=5
AUTH_TIME_WINDOW_SECONDS=60
GLOBAL_RATE_LIMIT=3
GLOBAL_TIME_WINDOW_SECONDS=60
```

### 4. Database PostgreSQL
```powershell
psql -U postgres
CREATE DATABASE chat_ai_db ENCODING 'UTF8';
\q
```

### 5. Inizializzare Tabelle
```powershell
uv run python -c "from app.database import init_db; init_db()"
```

---

## 📂 Struttura del Progetto

```
app/
├── main.py                    # Entry point FastAPI
├── config.py                  # Pydantic Settings
├── schemas.py                 # Pydantic models
├── auth/
│   ├── dependencies.py        # JWT dependency injection
│   └── throttling.py          # Rate limiting
├── database/
│   ├── models.py              # SQLAlchemy User model
│   └── database.py            # Engine e helpers
├── routers/
│   └── users.py               # User registration API
├── ai/
│   ├── base.py                # Base AI class
│   └── gemini.py              # Google Gemini implementation
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── chat.html
└── prompts/
    └── system_prompt.md
```

---

## 🗄️ Database

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: int (PK)
    username: str (UNIQUE)
    email: str (UNIQUE)
    password_hash: str (bcrypt)
    full_name: str (optional)
    is_active: bool (default: True)
    created_at: datetime
    updated_at: datetime
```

### Helper Functions

```python
create_user(db, username, email, password, full_name=None)
get_user_by_id(db, user_id)
get_user_by_username(db, username)
get_user_by_email(db, email)
authenticate_user(db, username, password)
hash_password(password)
verify_password(password, hash)
```

---

## 🔌 API Endpoints

### Web Endpoints (HTML)

| Metodo | Endpoint | Descrizione | Protetto |
|--------|----------|-------------|----------|
| GET | `/` | Home page / Chat | ❌ |
| POST | `/` | Invia prompt | ❌ |
| GET | `/login` | Login page | ❌ |
| POST | `/login` | Autentica utente | ❌ |
| GET | `/register` | Registration page | ❌ |
| POST | `/logout` | Logout | ✅ Sì |
| GET | `/token` | Genera JWT | ❌ |

### API Endpoints (JSON)

| Metodo | Endpoint | Descrizione | Protetto |
|--------|----------|-------------|----------|
| POST | `/api/chat` | Chat con IA | ❌ |
| POST | `/api/users/register` | Registra utente | ❌ |

### POST /api/users/register

**Request**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

---

## 🔐 Sistema di Autenticazione

### JWT Token
- **Algoritmo**: HS256
- **Durata**: 24 ore
- **Payload**: `{"sub": username, "exp": timestamp}`

### Password Hashing
- **Algoritmo**: bcrypt (12 rounds)
- **Salt**: Generato casualmente

### Protezione Endpoint
```python
@app.post("/logout")
async def logout(current_user: User = Depends(get_authenticated_user)):
    # Endpoint protetto - richiede token valido
    ...
```

---

## 🚦 Rate Limiting

### Limiti
- **Autenticato**: 5 req/60s
- **Anonimo**: 3 req/60s

### Configurazione
```env
AUTH_RATE_LIMIT=10
GLOBAL_RATE_LIMIT=5
```

---

## 🏃 Esecuzione

### Development
```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Accesso**:
- Web: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 💻 Testing

### cURL
```bash
# Register
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test1234"}'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=Test1234" \
  -c cookies.txt

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt":"Hello!"}'
```

---

## 🐛 Troubleshooting

| Errore | Soluzione |
|--------|-----------|
| "No module named 'psycopg'" | `uv sync` |
| "Database does not exist" | Crea DB: `CREATE DATABASE chat_ai_db;` |
| "Invalid or expired token" | Effettua nuovo login |
| "Rate limit exceeded" | Attendi 60s per reset |

---

**Autore**: Daniele (masterDRAGONS)
**Ultima modifica**: 28 Maggio 2026
