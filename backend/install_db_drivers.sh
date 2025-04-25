#!/bin/bash

# 数据库驱动安装脚本
echo "开始安装数据库驱动..."

# MySQL驱动
echo "安装MySQL驱动..."
pip install mysql-connector-python==8.2.0

# PostgreSQL驱动
echo "安装PostgreSQL驱动..."
pip install psycopg2-binary==2.9.5

# SQL Server驱动
echo "安装SQL Server驱动..."
pip install pyodbc==5.0.1

# Oracle驱动
echo "安装Oracle驱动..."
pip install cx_Oracle==8.3.0

echo "所有数据库驱动安装完成" 