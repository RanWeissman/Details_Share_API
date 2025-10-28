FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# (אופציונלי אבל שימושי) התקנת תלויות אם יש requirements.txt בשורש הפרויקט
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ /app/scripts/

CMD ["python", "-m", "scripts.run_server"]

