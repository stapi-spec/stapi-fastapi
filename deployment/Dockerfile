FROM python:3.12-slim

WORKDIR /code

COPY ./ /code/

RUN pip install fastapi uvicorn mangum

# Run uvicorn when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
