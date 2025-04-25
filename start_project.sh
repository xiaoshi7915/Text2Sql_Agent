#!/bin/bash

# 问数智能体系统一键启动脚本
# 作者: 陈小石
# 日期: 2025-04-25

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 恢复默认颜色

# 项目根目录
PROJECT_DIR="/opt/wenshu-mcp"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="$PROJECT_DIR/logs"
BACKEND_PORT=5000
FRONTEND_PORT=8083

# 创建日志目录
mkdir -p "$LOG_DIR"
BACKEND_LOG="$LOG_DIR/backend_$(date +%Y%m%d_%H%M%S).log"
FRONTEND_LOG="$LOG_DIR/frontend_$(date +%Y%m%d_%H%M%S).log"

# 显示标题
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}          问数智能体系统启动脚本             ${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# 检查端口占用情况并杀死进程
kill_process_on_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}端口 $port 已被进程 $pid 占用，正在尝试结束该进程...${NC}"
        kill -9 $pid
        sleep 1
        echo -e "${GREEN}端口 $port 已释放${NC}"
    fi
}

# 检查服务状态
check_service() {
    local url=$1
    local max_attempts=$2
    local attempt=1
    local wait_time=2
    
    echo -e "${YELLOW}正在检查服务 $url 是否可访问...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --head "$url" > /dev/null; then
            echo -e "${GREEN}服务 $url 已成功启动！${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}尝试 $attempt/$max_attempts: 服务尚未就绪，等待 ${wait_time}s...${NC}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}服务 $url 在 $((max_attempts * wait_time))s 内未能成功启动！${NC}"
    return 1
}

# 清理日志文件
cleanup_logs() {
    # 保留最近10个日志文件
    find "$LOG_DIR" -name "backend_*.log" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null
    find "$LOG_DIR" -name "frontend_*.log" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null
}

# 启动后端
start_backend() {
    echo -e "${BLUE}[1/3] 正在启动后端服务...${NC}"
    
    # 检查端口占用并结束进程
    kill_process_on_port $BACKEND_PORT
    
    # 进入后端目录并启动服务
    cd "$BACKEND_DIR" || { echo -e "${RED}无法进入后端目录！${NC}"; exit 1; }
    
    # 启动后端服务
    nohup python run.py > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    
    echo -e "${GREEN}后端服务已启动，进程ID: $BACKEND_PID${NC}"
    echo -e "${GREEN}后端日志将保存至: $BACKEND_LOG${NC}"
    
    # 等待后端服务启动
    if check_service "http://localhost:$BACKEND_PORT/api/datasources/list" 10; then
        echo -e "${GREEN}后端服务已就绪！${NC}"
    else
        echo -e "${RED}后端服务启动超时，请检查日志: $BACKEND_LOG${NC}"
        echo -e "${YELLOW}尝试继续启动前端...${NC}"
    fi
}

# 启动前端
start_frontend() {
    echo -e "${BLUE}[2/3] 正在启动前端服务...${NC}"
    
    # 检查端口占用并结束进程
    kill_process_on_port $FRONTEND_PORT
    
    # 进入前端目录并启动服务
    cd "$FRONTEND_DIR" || { echo -e "${RED}无法进入前端目录！${NC}"; exit 1; }
    
    # 启动前端服务
    nohup npm run serve > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    
    echo -e "${GREEN}前端服务已启动，进程ID: $FRONTEND_PID${NC}"
    echo -e "${GREEN}前端日志将保存至: $FRONTEND_LOG${NC}"
    
    # 等待前端服务启动
    if check_service "http://localhost:$FRONTEND_PORT" 20; then
        echo -e "${GREEN}前端服务已就绪！${NC}"
    else
        echo -e "${RED}前端服务启动超时，请检查日志: $FRONTEND_LOG${NC}"
    fi
}

# 完成启动
finish_startup() {
    echo -e "${BLUE}[3/3] 启动过程已完成${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}   问数智能体系统已启动！   ${NC}"
    echo -e "${GREEN}   后端地址: http://localhost:$BACKEND_PORT   ${NC}"
    echo -e "${GREEN}   前端地址: http://localhost:$FRONTEND_PORT   ${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    echo -e "${YELLOW}要停止系统，请运行: ./stop_project.sh${NC}"
    echo -e "${YELLOW}或者使用以下命令手动停止:${NC}"
    echo -e "${YELLOW}  kill -9 $BACKEND_PID $FRONTEND_PID${NC}"
    
    # 创建停止脚本
    create_stop_script "$BACKEND_PID" "$FRONTEND_PID"
    
    # 清理旧日志
    cleanup_logs
}

# 创建停止脚本
create_stop_script() {
    local backend_pid=$1
    local frontend_pid=$2
    
    cat > "$PROJECT_DIR/stop_project.sh" << EOF
#!/bin/bash
echo "正在停止问数智能体系统..."
kill -9 $backend_pid 2>/dev/null
kill -9 $frontend_pid 2>/dev/null

# 确保端口被释放
kill \$(lsof -ti:$BACKEND_PORT) 2>/dev/null
kill \$(lsof -ti:$FRONTEND_PORT) 2>/dev/null

echo "问数智能体系统已停止！"
EOF
    
    chmod +x "$PROJECT_DIR/stop_project.sh"
}

# 主函数
main() {
    start_backend
    start_frontend
    finish_startup
}

# 执行主函数
main 