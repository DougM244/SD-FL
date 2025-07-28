# orchestrator/Dockerfile

# 1. Use a mesma imagem base do Python.
FROM python:3.11-slim

# 2. Defina o diretório de trabalho.
WORKDIR /app
ENV PYTHONPATH="/app"

# 3. Copie o arquivo de dependências e instale-as.
COPY orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie o código compartilhado e o código específico do serviço.
COPY ./common/ /app/common/
COPY ./orchestrator/ /app/orchestrator/

# 5. Defina o comando para executar a aplicação.
CMD ["python", "-u", "orchestrator/orchestrator.py"]