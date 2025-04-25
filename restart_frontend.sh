#!/bin/bash
cd /opt/wenshu-mcp
pkill -f "vue-cli-service serve"
cd frontend
export NODE_OPTIONS=--max-old-space-size=4096
nohup npm run serve > frontend.log 2>&1 &
echo "前端服务已重启，查看日志: tail -f frontend.log" 