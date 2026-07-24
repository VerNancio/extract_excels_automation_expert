# Usa uma imagem oficial do Python, versão slim (baseada em Debian)
FROM python:3.14.0-slim

# Evita que o Python grave arquivos .pyc e força a exibição dos logs no terminal em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as dependências do sistema: Chromium e o Chromium Driver
# O apt-get limpa o cache no final para manter a imagem leve
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as bibliotecas Python (Selenium, Pandas, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do seu código (seus scripts de extração)
COPY . .

# Comando para iniciar o seu script principal (ajuste 'main.py' para o nome real do seu script)
CMD ["python", "app.py"]
# CMD ["python", "run.py", "--client_name:coop", "--should_store_where:jestor", "--start_date:01/06/2026", "--end_date:01/07/2026"]