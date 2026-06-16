cd "$(dirname "$0")/.."
docker build -t ssunku6/claude-mcp-server:latest -f mcp-server/Dockerfile .
docker push ssunku6/claude-mcp-server:latest