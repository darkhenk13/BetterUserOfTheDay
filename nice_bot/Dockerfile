FROM python:3.11 as builder

COPY . .

RUN pip wheel --no-cache-dir --no-deps --wheel /wheels install -r requirements.txt

FROM python:3.11.9-alpine3.19

WORKDIR /wheels

COPY --from=builder /wheels /wheels
CMD ["python", "run.py"]