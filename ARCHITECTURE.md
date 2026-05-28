# 🏗️ Architettura dell'Applicazione

Documentazione dettagliata dell'architettura, flussi dati e decisioni di design.

## 📐 Panoramica dell'Architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Browser Web (HTML/CSS/JS)                              │   │
│  │  - Template Jinja2 (base.html, index.html, etc.)        │   │
│  │  - Client-side validation (JS vanilla)                  │   │
│  │  - Cookie management (JWT token)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI APPLICATION                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ main.py - Application Entry Point                       │   │
│  │ - Router inclusion                                      │   │
│  │ - Endpoint registration                                │   │
│  │ - Middleware setup                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐   │
│  │  auth/           │  │  routers/        │  │  ai/       │   │
│  │                  │  │                  │  │            │   │
│  │ • dependencies   │  │ • users.py       │  │ • gemini   │   │
│  │ • throttling     │  │                  │  │ • base      │   │
│  └──────────────────┘  └──────────────────┘  └────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  database/                                             │   │
│  │  - models.py (SQLAlchemy User ORM)                    │   │
│  │  - database.py (Engine, Sessions, Helpers)            │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  PostgreSQL 18   │  │  Google Gemini   │                   │
│  │  - Users table   │  │  - Chat API      │                   │
│  │  - Persistence   │  │  - AI responses  │                   │
│  └──────────────────┘  └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flussi Principali

### 1️⃣ Registrazione Utente

```
USER                     BROWSER              FASTAPI           DATABASE
 │                          │                    │                 │
 ├──(1) Fill form──────────>│                    │                 │
 │                          │                    │                 │
 │                          ├─(2) POST /register─────────>         │
 │                          │     {username,email,password}        │
 │                          │                    │                 │
 │                          │                    ├─(3) Validate   │
 │                          │                    │     input       │
 │                          │                    │                 │
 │                          │                    ├─(4) Hash pass  │
 │                          │                    │     bcrypt      │
 │                          │                    │                 │
 │                          │                    ├─(5) INSERT User─>
 │                          │                    │                 │
 │                          │<─(6) 201 Created───────────────────│
 │                          │     {user data}                     │
 │                          │                    │                 │
 │<─(7) Success alert───────│                    │                 │
 │                          │                    │                 │
 │──(8) Click login────────>│                    │                 │
```

### 2️⃣ Login & Authentication

```
USER                BROWSER              FASTAPI           DATABASE
 │                     │                    │                  │
 ├─(1) Username/──────>│                    │                  │
 │     Password        │                    │                  │
 │                     ├─(2) POST /login─────────>             │
 │                     │     form data              │           │
 │                     │                    │       │           │
 │                     │                    ├─(3) SELECT User──>
 │                     │                    │       username    │
 │                     │                    │<─────User object──
 │                     │                    │       │           │
 │                     │                    ├─(4) verify_password
 │                     │                    │       bcrypt.check │
 │                     │                    │                    │
 │                     │                    ├─(5) create_access_token
 │                     │                    │       JWT encode    │
 │                     │                    │                    │
 │                     │<─(6) Set-Cookie────────────────────────
 │                     │     token=<jwt>                        │
 │                     │                    │                    │
 │                     │<─(7) Redirect /────────────────────────
 │                     │     303 See Other                      │
 │                     │                    │                    │
 │<─(8) Home page──────│                    │                    │
 │     (logged in)     │                    │                    │
```

### 3️⃣ Chat Autenticato

```
USER              BROWSER           FASTAPI              GOOGLE GEMINI
 │                   │                  │                      │
 ├─(1) Type prompt──>│                  │                      │
 │                   │                  │                      │
 │                   ├─(2) POST /────────────────>              │
 │                   │     form data  │                        │
 │                   │     (with token)│                        │
 │                   │                  │                       │
 │                   │                  ├─(3) get_user_identifier
 │                   │                  │     (JWT verify)      │
 │                   │                  │                       │
 │                   │                  ├─(4) apply_rate_limit  │
 │                   │                  │                       │
 │                   │                  ├─(5) ai_platform.chat──>
 │                   │                  │     {prompt}          │
 │                   │                  │                       │
 │                   │                  │<─(6) {response}───────
 │                   │                  │                       │
 │                   │<─(7) Render chat.html──────────────────
 │                   │     {question, response}
 │                   │                  │                       │
 │<─(8) Display chat─│                  │                       │
```

---

## 🔐 Modello di Sicurezza

### Livelli di Protezione

```
┌─────────────────────────────────────────┐
│  1. PASSWORD HASHING                    │
│     Algoritmo: bcrypt (12 rounds)       │
│     - Never stored in plain text        │
│     - Resistant to rainbow tables       │
│     - Slow by design (brute force)      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  2. JWT AUTHENTICATION                  │
│     Algorithm: HS256 (HMAC-SHA256)      │
│     Duration: 24 hours                  │
│     - Stateless (no session storage)    │
│     - Verifiable (signature check)      │
│     - Expirable (timestamp)             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  3. SECURE COOKIE                       │
│     Flag: httponly                      │
│     - Not accessible from JS            │
│     - Protection from XSS               │
│     - Automatic send with requests      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  4. RATE LIMITING                       │
│     Tracking: In-memory (per user)      │
│     Auth: 5 req/60s                     │
│     Anon: 3 req/60s                     │
│     - Protection from abuse             │
│     - Per-user isolation                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  5. DATABASE VALIDATION                 │
│     - Unique constraints (username,email)
│     - Type validation (Pydantic)        │
│     - No SQL injection (ORM)            │
└─────────────────────────────────────────┘
```

---

## 📊 Modello dei Dati

### User Entity

```python
User
├── id: int (PRIMARY KEY)
├── username: str (UNIQUE, INDEXED) [3-50 chars]
├── email: str (UNIQUE, INDEXED) [100 chars max]
├── password_hash: str [255 chars, bcrypt]
├── full_name: str [100 chars, nullable]
├── is_active: bool [default: True]
├── created_at: datetime [AUTO]
└── updated_at: datetime [AUTO]
```

### Relazioni
- One User → Many Chat Sessions (implicitamente, non tracciato)
- Password Hash ← User (1:1)
- JWT Token ← User (1:many, stateless)

---

## 🔌 Dependency Injection Pattern

FastAPI usa dependency injection per:
1. **Database access**: `Depends(get_db)`
2. **Authentication**: `Depends(get_user_identifier)`
3. **Protected endpoints**: `Depends(get_authenticated_user)`
4. **Rate limiting**: Applicato all'inizio di ogni endpoint

### Esempio

```python
@app.post("/logout")
async def logout(
    current_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    # FastAPI automaticamente:
    # 1. Chiama get_authenticated_user()
    # 2. Verifica token e cerca utente
    # 3. Se non trovato → 401
    # 4. Se trovato → passa current_user
    # 5. Stesso per db: SessionLocal()
    # 6. Chiude session automaticamente
    ...
```

---

## 🗄️ Strategia Database

### Connection Pool
- **Tipo**: NullPool
- **Motivo**: Ogni richiesta = nuova connessione
- **Vantaggi**: Isolamento, semplicità
- **Svantaggi**: Overhead su alta concorrenza

### Session Management
```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Passa session al endpoint
    finally:
        db.close()  # Chiude automaticamente
```

### Transactions
- Autocommit: False
- Autoflush: False
- Manual commit: Nel create_user, update_user, delete_user

---

## 🚦 Rate Limiting Strategy

### Algoritmo: Sliding Window (In-Memory)

```
request_timestamps = {
    "user1": [t1, t2, t3, t4, t5],
    "global_anonimous": [t1, t2, t3],
    ...
}

Quando arriva nuova richiesta:
1. Ottieni timestamp corrente (now)
2. Filtra timestamp vecchi (now - window)
3. Conta richieste nella finestra
4. Se count >= limit → 429
5. Altrimenti → aggiungi timestamp
```

### Vantaggi
- Semplice da implementare
- Accurato (no approssimazioni)
- O(n) per utente, n = piccolo

### Svantaggi
- In-memory (non persistente)
- Reset al restart app
- Usa memoria per ogni utente

### Alternativa (Future)
- Redis: Rate limit distribuito
- Database: Persistente ma lento

---

## 🎯 Design Decisions

### 1. Perché PostgreSQL?
✅ ACID compliance
✅ Scalabilità
✅ Relazioni complesse (future)
✅ Full-text search (future)
❌ Non serverless

### 2. Perché JWT vs Sessions?
✅ Stateless (no server-side storage)
✅ Scalabile (multi-server)
✅ Mobile-friendly
✅ Revoca via token list (implementabile)
❌ Non immediate revocation

### 3. Perché bcrypt vs scrypt/argon2?
✅ Standard industry
✅ Lento (protezione brute-force)
✅ Libreria bcrypt ben supportata
❌ Argon2 è più nuovo/moderno

### 4. Perché Jinja2?
✅ Integrato in FastAPI
✅ Sintassi simile a Django
✅ Performante
❌ Non reactive (come React)

### 5. Perché NullPool?
✅ Semplice per app piccola
✅ Niente connection leak
❌ Overhead su alta concorrenza

---

## 🔮 Miglioramenti Futuri

### Phase 2: Scaling
- [ ] Implementare Redis per rate limiting
- [ ] Aggiungere connection pooling (QueuePool)
- [ ] Setup load balancer (nginx)
- [ ] Caching responses (Redis/Memcached)

### Phase 3: Features
- [ ] Email verification (SMTP)
- [ ] Password reset flow
- [ ] OAuth2 social login (Google, GitHub)
- [ ] User profiles (avatar, bio)
- [ ] Chat history per utente
- [ ] Admin dashboard

### Phase 4: Infra
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Database migrations (Alembic)
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Logging (ELK stack)

---

## 📈 Performance Considerations

### Bottlenecks Attuali
1. **Database**: NullPool (connessione per request)
   - Fix: QueuePool con max 20 connections
   
2. **Rate Limiting**: In-memory dict
   - Fix: Redis with TTL
   
3. **Gemini API**: Network latency
   - Fix: Implement caching + queue
   
4. **Session creation**: Bcrypt (slow)
   - Fix: Normal (è intenzionale)

### Load Testing
```bash
# Aprox 50-100 req/sec con uvicorn singolo
# Su 8 CPU cores: ~400-800 req/sec con workers

# Test:
ab -n 1000 -c 10 http://localhost:8000/
```

---

## 🐛 Error Handling

### HTTP Status Codes
- `200 OK` - Successo
- `201 Created` - Risorsa creata
- `303 See Other` - Redirect (POST)
- `400 Bad Request` - Input invalido
- `401 Unauthorized` - Auth fallito
- `429 Too Many Requests` - Rate limit
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "detail": "Username 'john' is already taken"
}
```

---

**Ultima modifica**: 28 Maggio 2026
