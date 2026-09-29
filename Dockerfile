FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY backend/ ./backend/
RUN printf '#!/bin/sh\nset -e\nalembic upgrade head\ncd backend/app\nexec uvicorn main:app --host 0.0.0.0 --port 8000\n' > docker-entrypoint.sh \
    && chmod +x docker-entrypoint.sh

EXPOSE 8000

CMD ["./docker-entrypoint.sh"]