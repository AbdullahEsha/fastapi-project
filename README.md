<!-- To update your setup to use SQLAlchemy with database migrations, we need to integrate **SQLAlchemy** for ORM functionality and **Alembic** for migrations. Here's the updated structure for your project:

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

With this setup, you now use SQLAlchemy for ORM operations and Alembic for migrations, ensuring an efficient and maintainable database structure. -->

Here's the updated **README.md** that incorporates the SQLAlchemy and Alembic setup for database management:

````markdown
# FastAPI Project Setup Guide

This guide provides step-by-step instructions to set up and run the FastAPI project.

---

## Requirements

- Python (>= 3.8)
- PostgreSQL (for database integration)
- Git (optional but recommended)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-project-folder>
```

---

### 2. Install Python and Upgrade Pip

Ensure Python is installed on your system. Then upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

---

### 3. Set Up a Virtual Environment

Install `virtualenv` and create a virtual environment:

```bash
pip install virtualenv
python -m virtualenv venv
```

Activate the virtual environment:

- On **Windows**:
  ```bash
  .\venv\Scripts\activate
  ```
- On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

---

### 4. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

To include **SQLAlchemy** and **Alembic** for ORM and migrations, install them as well:

```bash
pip install sqlalchemy psycopg2 alembic
```

---

### 5. Configure Environment Variables

Create a `.env` file in the project root and add the following environment variables:

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
TOKEN_EXPIRES=15  # Token expiry time in minutes
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>
PG_HOST=localhost
PG_DATABASE=mydatabase
PG_USER=myuser
PG_PASSWORD=mypassword
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.brevo.com
```

Replace placeholder values with your actual credentials.

---

### 6. Database Configuration with SQLAlchemy

#### Update `config/dbConnect.py`:

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

#### Create a User Model in `models/User.py`:

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

#### Update migration `alembic\versions\4bf57b5f8ff2_create_users_table.py`

```python
def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), default='user', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###
```

---

### 7. Set Up Alembic for Database Migrations

#### Initialize Alembic:

```bash
alembic init alembic
```

#### Update `alembic.ini`:

Replace `sqlalchemy.url` in `alembic.ini` with your `DATABASE_URL`:

```ini
sqlalchemy.url = postgresql://<user>:<password>@<host>/<database>
```

#### Update `alembic/env.py`:

Set the `target_metadata` to use your `Base`:

```python
from config.dbConnect import Base
target_metadata = Base.metadata
```

#### Create and Apply Migrations:

1. Generate an initial migration:

   ```bash
   alembic revision --autogenerate -m "create users table"
   ```

2. Apply the migration to the database:
   ```bash
   alembic upgrade head
   ```

---

### 8. Run the Application

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --host localhost --port 5000
```

Access the application at `http://localhost:5000`.

To view the API documentation, visit:

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

---

## Example API Endpoint with Dependency Injection

Update `main.py` to include a route for creating a user:

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

## Directory Structure

```bash
fastapi-project/
│
├── alembic/                  # Database migrations
│   ├── versions/             # Migration files
│   │   └── 4bf57b5f8ff2_create_users_table.py
│   ├── env.py                # Alembic environment file
│   ├── README                # Alembic README
│   └── script.py.mako        # Alembic script template
│
├── config/                   # Configuration files
│   └── dbConnect.py          # Database connection logic
│
├── models/                   # Database models
│   └── User.py               # User model
│
├── routes/                   # API routes
│   └── authRouter.py         # Authentication-related routes
│
├── schemas/                  # Pydantic schemas
│   ├── authSchemas.py        # Authentication schemas
│   └── __init__.py
│
├── services/                 # Business logic
│   └── authService.py        # Authentication service
│
├── view/                     # Email templates
│   └── emailTemplate.html    # Email template file
│
├── .env                      # Environment variables
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── .gitignore                # Ignored files
```

---

## Commands Summary

| Command                           | Description                      |
| --------------------------------- | -------------------------------- |
| `pip install -r requirements.txt` | Install project dependencies     |
| `alembic upgrade head`            | Apply migrations to the database |
| `uvicorn main:app --reload`       | Start the development server     |

For any issues or contributions, feel free to raise an issue or submit a pull request.

```

This README.md now includes the SQLAlchemy and Alembic setup while maintaining the other project features. Let me know if you need further refinements!
```
````
