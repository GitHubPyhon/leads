FROM python:3.11
WORKDIR /code
RUN pip install "poetry==1.4.2"
COPY poetry.lock pyproject.toml /code/
RUN poetry install --only main
COPY ./app /code/app
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
