#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""应用启动脚本"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:application",
        host="0.0.0.0",
        port=9999,
        reload=True,
        log_level="info"
    )
