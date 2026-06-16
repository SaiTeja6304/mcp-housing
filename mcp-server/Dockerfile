FROM python:3.13.5-slim

WORKDIR /mcp-server

# Copy requirements.txt from root context
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy server application source
COPY mcp-server/apps/src/ /mcp-server/apps/src

CMD ["python", "apps/src/housing_server.py"]