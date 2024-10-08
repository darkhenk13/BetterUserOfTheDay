FROM python:3.11.9-alpine3.19 AS builder

ARG PYTHONUNBUFFERED 1

WORKDIR /app

RUN python -m venv /opt/venv

ARG PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -Ur requirements.txt



FROM python:3.11.9-alpine3.19 AS runner

COPY --from=builder /opt/venv /opt/venv

ARG PATH="/opt/venv/bin:$PATH" PYTHONPATH="/app/nice_bot"

WORKDIR /app/nice_bot

COPY . .

CMD ["python", "run.py"]