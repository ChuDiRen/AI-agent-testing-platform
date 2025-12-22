"""启动 MCP 服务"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "testengine_mcp.main:app",
        host="0.0.0.0",
        port=8100,
        reload=False
    )
