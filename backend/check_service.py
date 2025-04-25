#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查后端服务是否正常运行
测试数据源API接口是否可用
"""

import requests
import sys
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 服务地址
BASE_URL = "http://localhost:5000"  # 默认端口
TEST_URL = "/api/datasources/list"  # 更新为新的API路径

def check_service(port=5000, retries=3, delay=2):
    """检查服务是否正常运行

    Args:
        port: 服务端口
        retries: 重试次数
        delay: 重试间隔（秒）
    
    Returns:
        bool: 服务是否正常
    """
    url = f"http://localhost:{port}{TEST_URL}"
    logging.info(f"开始检查服务，URL: {url}")
    
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                logging.info(f"服务正常运行，状态码: {response.status_code}")
                logging.info(f"接口返回数据: {response.json()}")
                return True
            else:
                logging.warning(f"请求成功但返回错误状态码: {response.status_code}")
                logging.warning(f"错误详情: {response.text}")
        
        except requests.RequestException as e:
            logging.error(f"请求失败 (尝试 {i+1}/{retries}): {str(e)}")
            
        # 如果不是最后一次尝试，则等待
        if i < retries - 1:
            logging.info(f"等待 {delay} 秒后重试...")
            time.sleep(delay)
    
    logging.error(f"服务检查失败，无法连接到 {url}")
    return False

def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logging.error(f"无效的端口号: {sys.argv[1]}")
            sys.exit(1)
    else:
        port = 5000  # 默认端口
    
    # 检查服务
    success = check_service(port)
    
    # 输出结果
    if success:
        logging.info("服务检查成功，API接口正常工作")
        sys.exit(0)
    else:
        logging.error("服务检查失败，API接口不可用")
        sys.exit(1)

if __name__ == "__main__":
    main() 