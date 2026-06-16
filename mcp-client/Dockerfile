FROM python:3.13.5-slim

WORKDIR /mcp-client

# Copy requirements.txt from root context
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy client application source
COPY mcp-client/apps/src/ /mcp-client/apps/src

CMD ["python", "apps/src/housing_client.py"]