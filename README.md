To update your setup to use SQLAlchemy with database migrations, we need to integrate **SQLAlchemy** for ORM functionality and **Alembic** for migrations. Here's the updated structure for your project:

---

### Install Required Libraries:

```bash
pip install sqlalchemy psycopg2 alembic
```

---

### Update `config\dbConnect.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}/{os.getenv('PG_DATABASE')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### Update `models\User.py`:

```python
from sqlalchemy import Column, Integer, String
from config.dbConnect import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
```

---

### Add Alembic for Migrations:

1. **Initialize Alembic**:

   ```bash
   alembic init alembic
   ```

2. **Update `alembic.ini`**:
   Replace the `sqlalchemy.url` in `alembic.ini` with your `DATABASE_URL`:

   ```ini
   sqlalchemy.url = postgresql://<user>:<password>@<host>/<database>
   ```

3. **Update `env.py` in Alembic**:
   Inside `alembic/env.py`, update the `target_metadata` to reference your `Base`:

   ```python
   from config.dbConnect import Base
   target_metadata = Base.metadata
   ```

4. **Create an Initial Migration**:

   ```bash
   alembic revision --autogenerate -m "create users table"
   ```

5. **Apply the Migration**:
   ```bash
   alembic upgrade head
   ```

---

### Update `main.py` with Dependency Injection:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from config.dbConnect import get_db
from models.User import User

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    new_user = User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

---

### Directory Structure:

```plaintext
project/
├── alembic/
├── config/
│   └── dbConnect.py
├── models/
│   └── User.py
├── main.py
├── .env
└── requirements.txt
```

---

### `.env` Example:

```env
PG_HOST=localhost
PG_DATABASE=mydatabase
PG_USER=myuser
PG_PASSWORD=mypassword
```

With this setup, you now use SQLAlchemy for ORM operations and Alembic for migrations, ensuring an efficient and maintainable database structure.
