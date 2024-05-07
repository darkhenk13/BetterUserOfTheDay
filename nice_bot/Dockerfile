FROM python:3.11.9-alpine3.19 as builder

ENV PYTHONUNBUFFERED 1

WORKDIR /app/

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY ./nice_bot/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -Ur requirements.txt



FROM python:3.11.9-alpine3.19 as runner

WORKDIR /app/

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY ./nice_bot /app/

CMD ["python", "run.py"]