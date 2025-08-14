FROM python:3.11-slim-bookworm

RUN apt update && \
    apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 &&  \
    pip install --upgrade setuptools pip &&  \
    pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

EXPOSE 5000

CMD ["uv", "run", "app.py"]