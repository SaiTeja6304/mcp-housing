cd "$(dirname "$0")/.."
docker build -t ssunku6/claude-mcp-client:latest -f mcp-client/Dockerfile .
docker push ssunku6/claude-mcp-client:latest
