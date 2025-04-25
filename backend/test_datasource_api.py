#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据源API测试脚本
用于测试数据源相关API是否正常工作
"""

import requests
import json
import sys
import os

# 服务端URL
BASE_URL = "http://localhost:5000/api"

# 测试获取数据源列表
def test_get_datasources():
    """测试获取数据源列表API"""
    url = f"{BASE_URL}/datasource/list"
    print(f"请求 GET {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("获取数据源列表成功")
            return response.json()
        else:
            print("获取数据源列表失败")
            return None
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return None

# 测试创建数据源
def test_create_datasource():
    """测试创建数据源API"""
    url = f"{BASE_URL}/datasource/"
    
    # 测试数据
    data = {
        "name": "测试数据源",
        "ds_type": "MySQL",
        "description": "这是一个测试数据源",
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "username": "root",
        "password": "password"
    }
    
    print(f"请求 POST {url}")
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code in [200, 201]:
            print("创建数据源成功")
            return response.json()
        else:
            print("创建数据源失败")
            return None
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return None

# 测试数据源连接
def test_connection():
    """测试数据源连接API"""
    url = f"{BASE_URL}/datasource/test-connection"
    
    # 测试数据
    data = {
        "ds_type": "MySQL",
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "username": "root",
        "password": "password"
    }
    
    print(f"请求 POST {url}")
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("测试连接成功")
            return True
        else:
            print("测试连接失败")
            return False
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 数据源API测试 ===")
    
    # 测试获取数据源列表
    print("\n--- 测试获取数据源列表 ---")
    datasources = test_get_datasources()
    
    # 测试创建数据源
    print("\n--- 测试创建数据源 ---")
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        new_datasource = test_create_datasource()
    
    # 测试数据源连接
    print("\n--- 测试数据源连接 ---")
    if len(sys.argv) > 1 and sys.argv[1] == "--test-connection":
        test_connection() 