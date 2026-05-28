# ❓ FAQ & Guide Pratiche

## Domande Frequenti

### 1. Come cambio la password di un utente nel database?

```powershell
# Connettiti al database
psql -U postgres -d chat_ai_db

# Usa la funzione hash_password di Python
# Oppure nel database (con bcrypt extension):
UPDATE users 
SET password_hash = crypt('nuova_password', gen_salt('bf', 12))
WHERE username = 'john_doe';
```

### 2. Come reset tutte le tabelle?

```powershell
# ⚠️ ATTENZIONE: Cancella TUTTI i dati!

# Option 1: Drop e ricrea
psql -U postgres -d chat_ai_db
DROP TABLE users CASCADE;
\q

# Reinizializza
uv run python -c "from app.database import init_db; init_db()"

# Option 2: Truncate (mantiene struttura)
psql -U postgres -d chat_ai_db
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
```

### 3. Come vedo gli utenti registrati?

```powershell
# Con psql
psql -U postgres -d chat_ai_db
SELECT id, username, email, is_active, created_at FROM users;

# Con Python
uv run python << 'PYTHON'
from app.database import SessionLocal, list_all_users
db = SessionLocal()
users = list_all_users(db, limit=10)
for user in users:
    print(f"{user.id}: {user.username} ({user.email})")
db.close()
PYTHON
```

### 4. Come estendo il token JWT oltre 24 ore?

```python
# In app/main.py, modifica create_access_token:

def create_access_token(username: str, expires_delta: timedelta = None):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Cambia 24 hours a quello che vuoi
        expire = datetime.now(timezone.utc) + timedelta(days=7)  # 7 giorni
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
```

### 5. Come cambio i limiti di rate limiting?

```env
# In .env:
AUTH_RATE_LIMIT=10              # Da 5 a 10
AUTH_TIME_WINDOW_SECONDS=120    # Da 60 a 120 secondi
GLOBAL_RATE_LIMIT=5             # Da 3 a 5
GLOBAL_TIME_WINDOW_SECONDS=120
```

### 6. Come disabilito il rate limiting?

```python
# In app/auth/throttling.py:
def apply_rate_limit(user_id: str):
    # Commenta il contenuto
    pass  # Rate limiting disabilitato
```

### 7. Come aggiungo un nuovo campo alla tabella users?

```python
# In app/database/models.py:
class User(Base):
    __tablename__ = "users"
    
    # ... campi esistenti ...
    
    # Nuovo campo
    phone_number = Column(String(20), nullable=True)
    
    # O un boolean
    email_verified = Column(Boolean, default=False)
```

Poi crea la colonna nel database:
```sql
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20);
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
```

### 8. Come migro il database da SQLite a PostgreSQL?

Non usiamo SQLite, ma se volessi convertire da un'altra fonte:

```python
import sqlite3
import psycopg

# Leggi da SQLite
sqlite_conn = sqlite3.connect('old.db')
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT * FROM users")
users = sqlite_cursor.fetchall()

# Scrivi in PostgreSQL
pg_conn = psycopg.connect("postgresql://postgres:pass@localhost/chat_ai_db")
pg_cursor = pg_conn.cursor()

for user in users:
    pg_cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
        user
    )
pg_conn.commit()
```

### 9. Come faccio a loggare alle API come amministratore?

Attualmente non c'è role/admin system. Aggiungerlo:

```python
# In app/database/models.py:
class User(Base):
    # ... campi attuali ...
    role = Column(String(20), default="user")  # "user" o "admin"

# In app/routers/users.py:
async def create_admin_user(user_data, db):
    # ... validation ...
    new_user = create_user(...)
    new_user.role = "admin"
    db.commit()
```

### 10. Come posso loggare le query SQL?

```python
# In app/database/database.py:
engine = create_engine(
    settings.database_url,
    echo=True,  # Stampa SQL statements
    echo_pool=True,  # Stampa pool events
)
```

---

## 🔧 Guide Pratiche

### Come fare backup del database?

```powershell
# Backup completo
pg_dump -U postgres -d chat_ai_db -F custom -f backup.dump

# Backup SQL plain text
pg_dump -U postgres -d chat_ai_db > backup.sql

# Restore
pg_restore -U postgres -d chat_ai_db -F custom backup.dump
# Oppure
psql -U postgres -d chat_ai_db < backup.sql
```

### Come monitorare connessioni attive?

```powershell
psql -U postgres -d chat_ai_db

# Vedi tutte le connessioni
SELECT pid, usename, client_addr, query, query_start 
FROM pg_stat_activity 
WHERE datname = 'chat_ai_db';

# Uccidi una connessione
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE pid != pg_backend_pid() AND datname = 'chat_ai_db';
```

### Come metto in produzione?

```powershell
# 1. Build Docker image
docker build -t chat-ai:latest .

# 2. Run container
docker run -d \
  --name chat-ai \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e GEMINI_API_KEY=... \
  -e SECRET_KEY=... \
  chat-ai:latest

# 3. O deploy su cloud (Heroku, Railway, etc.)
# Vedi DEPLOYMENT.md
```

### Come testo endpoint con Postman?

```json
# Collection example

POST /api/users/register
Headers: Content-Type: application/json
Body:
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPassword123!",
  "full_name": "Test User"
}

---

POST /login
Headers: Content-Type: application/x-www-form-urlencoded
Body:
username=testuser&password=TestPassword123!

---

POST /api/chat
Headers: Content-Type: application/json
Body:
{
  "prompt": "Ciao, come stai?"
}
```

### Come disabilito temporaneamente un utente?

```python
# Via Python
from app.database import SessionLocal, update_user

db = SessionLocal()
update_user(db, user_id=1, is_active=False)
db.close()

# Via SQL
UPDATE users SET is_active = FALSE WHERE username = 'john_doe';

# L'utente non può più fare login (authenticate_user controlla is_active)
```

### Come aggiungo autenticazione OAuth2 (Google)?

```python
# Installa
pip install google-auth google-auth-oauthlib google-auth-httplib2

# In app/routers/auth.py (nuovo file):
from google.auth.transport.requests import Request
from google.oauth2 import id_token

# Configura client ID
GOOGLE_CLIENT_ID = "xxxxx.apps.googleusercontent.com"

@app.post("/auth/google")
async def google_auth(token: str, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
        
        # Estrai info
        email = idinfo['email']
        username = idinfo['email'].split('@')[0]
        
        # O crea utente
        user = get_user_by_email(db, email)
        if not user:
            user = create_user(db, username, email, password="google-oauth")
        
        # Crea JWT
        access_token = create_access_token(user.username)
        
        return {"access_token": access_token}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 🐛 Debug Common Issues

### Problema: "Column does not exist"

```
Causa: Model .py non sincronizzato con database
Soluzione: Aggiungi colonna manualmente nel DB:

ALTER TABLE users ADD COLUMN <column_name> <type>;
```

### Problema: "Relation does not exist"

```
Causa: Tabella non creata
Soluzione:
uv run python -c "from app.database import init_db; init_db()"
```

### Problema: "Connection refused"

```
Causa: PostgreSQL non in esecuzione
Soluzione Windows:
1. Apri Services (services.msc)
2. Cerca "postgresql-x64-18"
3. Clicca "Start service"

Oppure:
net start postgresql-x64-18
```

### Problema: "Authentication failed"

```
Causa: Username/password errato nel DATABASE_URL
Soluzione:
1. Verifica .env ha DATABASE_URL corretto
2. Testa connessione manuale:
   psql -U postgres -h localhost -d chat_ai_db
3. Se fallisce, reset password PostgreSQL:
   psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'newpass';"
```

### Problema: "HTTP 422 Unprocessable Entity"

```
Causa: Dati inviati non corrispondono schema Pydantic
Soluzione:
1. Leggi il messaggio di errore (ritorna quali campi falliscono)
2. Controlla types nei models/schemas
3. Usa /docs (Swagger) per test interattivi
4. Logga request body: print(request.json())
```

---

## 📚 Comandi Utili

```powershell
# Attivare venv
.venv\Scripts\Activate.ps1

# Installare dipendenze
uv sync

# Avviare server
uv run uvicorn app.main:app --reload

# Creare utente test
uv run python -c "from app.database import *; SessionLocal().close()"

# Reset database
psql -U postgres -d chat_ai_db -c "TRUNCATE TABLE users RESTART IDENTITY;"

# Backup database
pg_dump -U postgres -d chat_ai_db > backup.sql

# Vedere versione PostgreSQL
psql -U postgres -c "SELECT version();"

# Vedere logs applicazione
# Controlla console di uvicorn

# Test API
curl -X GET http://localhost:8000/docs
```

---

**Ultima modifica**: 28 Maggio 2026
