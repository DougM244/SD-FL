# client-service/Dockerfile

# 1. Use uma imagem base do Python. A versão 3.11-slim é leve e corresponde ao que instalamos.
FROM python:3.11-slim

# 2. Defina o diretório de trabalho dentro do contêiner.
WORKDIR /app
ENV PYTHONPATH="/app"

# 3. Copie o arquivo de dependências e instale-as.
#    Copiar e instalar as dependências primeiro aproveita o cache do Docker.
COPY client-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie o código compartilhado e o código específico do serviço para dentro do contêiner.
COPY ./common/ /app/common/
COPY ./client-service/ /app/client-service/

# 5. Exponha a porta que o Flask usará.
EXPOSE 5000

# 6. Defina o comando para executar a aplicação quando o contêiner iniciar.
CMD ["python", "-m", "client-service.client_app"]