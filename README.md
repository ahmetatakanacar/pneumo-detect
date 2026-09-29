# PneumoDetect

AI-powered chest X-ray pneumonia detection. A ResNet50 transfer-learning model served through a FastAPI backend with JWT authentication and role-based access control, plus a small web frontend to try it out.

## Screenshots

<img src="images/homepage.png" width="700" alt="Homepage"/>

<table>
<tr>
<td><img src="images/login.png" width="420" alt="Login screen"/></td>
<td><img src="images/register.png" width="420" alt="Register screen"/></td>
</tr>
<tr>
<td><img src="images/upload.png" width="420" alt="Upload screen"/></td>
<td><img src="images/normal.png" width="420" alt="Normal result"/></td>
</tr>
<tr>
<td colspan="2" align="center"><img src="images/pneumo.png" width="420" alt="Pneumonia result"/></td>
</tr>
</table>

## Overview

A user uploads a chest X-ray image and gets a prediction — **NORMAL** or **PNEUMONIA** — with a confidence score, in seconds. The project is split into three parts:

- **Model** — a ResNet50 CNN, fine-tuned via transfer learning to classify chest X-rays.
- **Backend** — a FastAPI service that authenticates users, enforces role-based permissions, runs inference, and persists results to PostgreSQL.
- **Frontend** — a lightweight vanilla JS single-page app for logging in, uploading an X-ray, and viewing the result.

## Model

- **Architecture:** ResNet50, pretrained on ImageNet, fine-tuned for binary classification
- **Framework:** PyTorch
- **Task:** chest X-ray image → `NORMAL` / `PNEUMONIA`

### Performance

| Metric    | Score  |
|-----------|--------|
| Precision | 0.8630 |
| Recall    | 0.9692 |
| F1 Score  | 0.9130 |
| AUC-ROC   | 0.9586 |

### Dataset

Trained on the [Chest X-Ray Images (Pneumonia)](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) dataset (Kermany et al.) — labeled pediatric chest X-rays split into `NORMAL` and `PNEUMONIA` classes.

## Tech Stack

**Backend:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · JWT (python-jose) · bcrypt (passlib) · pytest
**ML:** PyTorch · torchvision (ResNet50 transfer learning)
**Frontend:** HTML · CSS · JavaScript (vanilla, no framework)
**Infra:** Docker · Docker Compose

## API Endpoints

| Method | Endpoint          | Auth                 | Description                                  |
|--------|-------------------|-----------------------|-----------------------------------------------|
| POST   | `/auth/register`  | —                     | Register a new user (always created as `READONLY`) |
| POST   | `/auth/login`     | —                     | Log in, returns a JWT access token           |
| GET    | `/auth/me`        | Bearer token          | Current authenticated user's info            |
| POST   | `/upload-xray`    | Bearer token (`DOCTOR`/`ADMIN`) | Upload an X-ray, run inference, store & return the result |
| GET    | `/get-result/{id}`| Bearer token          | Retrieve a stored result by ID               |
| GET    | `/health`         | —                     | Health check                                 |

Interactive docs (Swagger UI) are available at `/docs` once the API is running.

## Roles & Access Control

Three roles: `READONLY`, `DOCTOR`, `ADMIN`. Only `DOCTOR` and `ADMIN` can upload and analyze X-rays; `READONLY` accounts can authenticate but get a `403` on `/upload-xray`.

Every account is created as `READONLY` at registration — **the API never lets a user pick their own role**. This closes off a self-assigned-privilege-escalation path that would otherwise let anyone register straight into `DOCTOR`/`ADMIN`. In this demo, promoting a user is done by hand in the database (see [Setup](#6-promote-a-user-to-doctor-optional)); a real deployment would put that behind an admin-only endpoint instead.

## Project Structure

```
pneumo-detect/
├── alembic/                  # DB migration scripts
├── alembic.ini
├── backend/
│   └── app/
│       ├── api/               # auth.py, xray.py — route handlers
│       ├── core/              # config.py — env/settings
│       ├── db/                # database.py, models.py
│       ├── schemas/           # Pydantic request/response models
│       ├── services/          # prediction.py — model inference
│       ├── tests/              # pytest suite
│       └── main.py
├── frontend/                  # vanilla HTML/CSS/JS SPA
│   ├── index.html
│   ├── style.css
│   └── app.js
├── model/
│   ├── checkpoints/            # trained weights (best_model.pth, gitignored)
│   └── data/                   # dataset (gitignored)
├── images/                     # screenshots used in this README
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
└── .env                         # not committed
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### 1. Clone

```bash
git clone https://github.com/ahmetatakanacar/pneumo-detect.git
cd pneumo-detect
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://pneumodetect:pneumodetect_dev_pw@localhost:5432/pneumodetect
SECRET_KEY=<a-long-random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> When running via Docker Compose, `DATABASE_URL` and `CHECKPOINT_PATH` are overridden automatically to point at the `postgres` service and the mounted checkpoint — the values above are used for local (non-Docker) runs, e.g. the test suite.

### 3. Add the trained model checkpoint

Place `best_model.pth` under `model/checkpoints/` (not included in the repo due to size).

### 4. Run with Docker Compose

```bash
docker compose up --build -d
```

This starts two services:

- `postgres` — PostgreSQL 16
- `api` — the FastAPI backend (runs Alembic migrations automatically on startup, then serves on port 8000)

The API is now available at `http://localhost:8000` (docs at `http://localhost:8000/docs`).

### 5. Run the frontend

```bash
cd frontend
python -m http.server 5500
```

Open `http://localhost:5500` in your browser.

### 6. Promote a user to DOCTOR (optional)

New accounts are always created as `READONLY`. To try the upload flow, promote one directly in the database:

```bash
docker exec -it pneumodetect-postgres psql -U pneumodetect -d pneumodetect
```

```sql
UPDATE users SET role = 'DOCTOR' WHERE email = 'your@email.com';
```

### Running tests

```bash
pip install -r requirements.txt
cd backend/app
pytest -v
```

Tests run against the same PostgreSQL instance configured in `.env` — no separate test database.