#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MySQL 连接修复工具
用于修复 MySQL 8.0+ 的连接问题，包括:
1. 认证插件问题: 将 caching_sha2_password 改为 mysql_native_password
2. SSL 连接问题: 配置 SSL 连接参数
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime

# 检查必要的依赖
try:
    import mysql.connector
except ImportError:
    print("错误: 缺少必要的依赖 'mysql-connector-python'")
    print("请安装依赖: pip install mysql-connector-python")
    sys.exit(1)

try:
    from flask import current_app
except ImportError:
    print("警告: 缺少 'flask' 依赖，将使用相对路径访问数据源")
    current_app = None

# 配置日志记录
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"mysql_fix_{timestamp}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mysql_fix")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='MySQL 8.0+ 连接问题修复工具')
    
    # 修复认证插件相关参数
    auth_group = parser.add_mutually_exclusive_group()
    auth_group.add_argument('--fix-auth', dest='fix_auth', action='store_true', 
                            help='修复认证插件问题 (默认)')
    auth_group.add_argument('--no-fix-auth', dest='fix_auth', action='store_false',
                            help='不修复认证插件问题')
    parser.set_defaults(fix_auth=True)
    
    # SSL 连接相关参数
    ssl_group = parser.add_mutually_exclusive_group()
    ssl_group.add_argument('--enable-ssl', dest='enable_ssl', action='store_true',
                         help='启用 SSL 连接 (默认)')
    ssl_group.add_argument('--no-enable-ssl', dest='enable_ssl', action='store_false',
                         help='不启用 SSL 连接')
    parser.set_defaults(enable_ssl=True)
    
    # root 用户信息，用于修改认证插件
    parser.add_argument('--root-user', help='MySQL root 用户名 (修改认证插件时必需)')
    parser.add_argument('--root-password', help='MySQL root 密码 (修改认证插件时必需)')
    
    # SSL 配置
    parser.add_argument('--ca-file', help='SSL CA 证书文件路径')
    parser.add_argument('--no-verify', action='store_true', help='不验证 SSL 证书')
    
    return parser.parse_args()

def get_datasource_path():
    """获取数据源文件的路径"""
    # 优先使用 Flask 应用配置的路径
    if current_app:
        try:
            return Path(current_app.config.get('DATASOURCE_PATH', 'app/datasources'))
        except Exception as e:
            logger.warning(f"无法获取 Flask 应用配置: {e}")
    
    # 回退到相对路径
    base_path = Path(__file__).parent
    
    # 尝试几种可能的路径
    possible_paths = [
        base_path / "app" / "datasources",
        base_path.parent / "app" / "datasources",
        Path("/opt/wenshu-mcp/app/datasources")
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    
    # 如果找不到路径，使用默认路径并发出警告
    logger.warning("无法找到数据源目录，将使用默认路径 'app/datasources'")
    return Path("app/datasources")

def get_mysql_datasources():
    """获取所有 MySQL 类型的数据源配置"""
    datasource_path = get_datasource_path()
    mysql_datasources = []
    
    logger.info(f"开始扫描数据源目录: {datasource_path}")
    
    try:
        # 确保目录存在
        if not datasource_path.exists():
            logger.error(f"数据源目录不存在: {datasource_path}")
            return []
        
        # 遍历所有 JSON 文件
        for file_path in datasource_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 检查是否为 MySQL 数据源
                    ds_type = data.get('type', '').lower()
                    if 'mysql' in ds_type:
                        data['file_path'] = file_path
                        mysql_datasources.append(data)
                        logger.info(f"找到 MySQL 数据源: {file_path.name}")
            except Exception as e:
                logger.error(f"读取数据源文件 {file_path} 失败: {e}")
    
    except Exception as e:
        logger.error(f"扫描数据源目录失败: {e}")
    
    logger.info(f"共找到 {len(mysql_datasources)} 个 MySQL 数据源")
    return mysql_datasources

def test_mysql_connection(host, port, user, password, database=None, ssl_config=None):
    """测试 MySQL 连接，返回连接状态和详细信息"""
    logger.info(f"测试连接 MySQL 服务器: {host}:{port} (用户: {user})")
    
    connection = None
    try:
        connect_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'connection_timeout': 10  # 10秒超时
        }
        
        # 如果提供了数据库名，添加到连接参数
        if database:
            connect_params['database'] = database
        
        # 如果提供了 SSL 配置，添加到连接参数
        if ssl_config:
            connect_params['ssl_ca'] = ssl_config.get('ca')
            connect_params['ssl_verify_cert'] = not ssl_config.get('no_verify', False)
            
            if 'ca' in ssl_config:
                logger.info(f"使用 SSL CA 证书: {ssl_config['ca']}")
            
            if ssl_config.get('no_verify', False):
                logger.info("SSL 证书验证已禁用")
        
        connection = mysql.connector.connect(**connect_params)
        
        # 检查认证插件
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT plugin FROM mysql.user WHERE User='{user}' AND Host='%' LIMIT 1;")
        user_data = cursor.fetchone()
        
        if not user_data:
            cursor.execute(f"SELECT plugin FROM mysql.user WHERE User='{user}' LIMIT 1;")
            user_data = cursor.fetchone()
        
        auth_plugin = user_data['plugin'] if user_data else "未知"
        cursor.close()
        
        logger.info(f"连接成功! 认证插件: {auth_plugin}")
        return True, {"auth_plugin": auth_plugin}
    
    except mysql.connector.Error as err:
        error_message = str(err)
        logger.error(f"连接失败: {error_message}")
        
        # 分析错误类型
        if "Authentication plugin 'caching_sha2_password' requires secure connection" in error_message:
            return False, {"error": "认证插件需要安全连接", "needs_ssl": True}
        elif "Access denied" in error_message:
            return False, {"error": "访问被拒绝，用户名或密码错误"}
        else:
            return False, {"error": error_message}
    
    except Exception as e:
        logger.error(f"发生未知错误: {str(e)}")
        return False, {"error": str(e)}
    
    finally:
        if connection:
            try:
                connection.close()
            except:
                pass

def fix_auth_plugin(host, port, root_user, root_password, target_user, target_host='%'):
    """修复认证插件，将 caching_sha2_password 改为 mysql_native_password"""
    if not root_user or not root_password:
        logger.error("需要提供 root 用户和密码才能修改认证插件")
        return False, "需要提供 root 用户和密码才能修改认证插件"
    
    logger.info(f"开始修复用户 {target_user} 的认证插件...")
    
    connection = None
    try:
        # 使用 root 用户连接
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=root_user,
            password=root_password
        )
        
        cursor = connection.cursor()
        
        # 检查用户是否存在
        cursor.execute(f"SELECT User, Host, plugin FROM mysql.user WHERE User='{target_user}';")
        users = cursor.fetchall()
        
        if not users:
            logger.error(f"用户 {target_user} 不存在")
            return False, f"用户 {target_user} 不存在"
        
        # 找出需要修改的用户记录
        user_hosts = [user[1] for user in users]
        logger.info(f"用户 {target_user} 存在于以下主机: {', '.join(user_hosts)}")
        
        # 如果目标主机不在列表中，使用第一个记录
        if target_host not in user_hosts:
            target_host = user_hosts[0]
            logger.info(f"将使用主机 {target_host} 的用户记录")
        
        # 执行ALTER USER语句修改认证插件
        alter_sql = f"ALTER USER '{target_user}'@'{target_host}' IDENTIFIED WITH mysql_native_password BY PASSWORD('*');;"
        logger.info(f"执行SQL: {alter_sql}")
        
        # 查询用户密码的哈希值
        cursor.execute(f"SELECT authentication_string FROM mysql.user WHERE User='{target_user}' AND Host='{target_host}';")
        auth_string = cursor.fetchone()[0]
        
        # 使用正确的ALTER USER语句
        if auth_string:
            alter_sql = f"ALTER USER '{target_user}'@'{target_host}' IDENTIFIED WITH mysql_native_password;"
        else:
            # 如果没有密码，设置一个空密码
            alter_sql = f"ALTER USER '{target_user}'@'{target_host}' IDENTIFIED WITH mysql_native_password BY '';"
        
        logger.info(f"执行SQL: {alter_sql}")
        cursor.execute(alter_sql)
        
        # 刷新权限
        cursor.execute("FLUSH PRIVILEGES;")
        
        # 验证修改结果
        cursor.execute(f"SELECT plugin FROM mysql.user WHERE User='{target_user}' AND Host='{target_host}';")
        new_plugin = cursor.fetchone()[0]
        
        if new_plugin == 'mysql_native_password':
            logger.info(f"成功将用户 {target_user}@{target_host} 的认证插件修改为 mysql_native_password")
            return True, f"成功将认证插件修改为 mysql_native_password"
        else:
            logger.warning(f"认证插件仍为 {new_plugin}，修改可能未成功")
            return False, f"认证插件仍为 {new_plugin}，修改可能未成功"
        
    except mysql.connector.Error as err:
        error_message = str(err)
        logger.error(f"修改认证插件失败: {error_message}")
        return False, f"修改认证插件失败: {error_message}"
    
    except Exception as e:
        logger.error(f"发生未知错误: {str(e)}")
        return False, f"发生未知错误: {str(e)}"
    
    finally:
        if connection:
            try:
                connection.close()
            except:
                pass

def update_datasource_ssl_config(datasource, ssl_config):
    """更新数据源的 SSL 配置"""
    file_path = datasource.get('file_path')
    if not file_path:
        logger.error("数据源没有关联的文件路径")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新连接参数中的 SSL 配置
        if 'connection' not in data:
            data['connection'] = {}
        
        # 添加 SSL 配置
        if 'ssl_ca' not in data['connection'] and ssl_config.get('ca'):
            data['connection']['ssl_ca'] = ssl_config['ca']
            logger.info(f"添加 SSL CA 证书: {ssl_config['ca']}")
        
        if 'ssl_verify_cert' not in data['connection'] and 'no_verify' in ssl_config:
            data['connection']['ssl_verify_cert'] = not ssl_config['no_verify']
            logger.info(f"设置 SSL 证书验证: {not ssl_config['no_verify']}")
        
        # 备份原文件
        backup_path = str(file_path) + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(datasource, f, ensure_ascii=False, indent=2)
        logger.info(f"已备份原数据源文件到: {backup_path}")
        
        # 写入更新后的配置
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已更新数据源 SSL 配置: {file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"更新数据源 SSL 配置失败: {str(e)}")
        return False

def main():
    """主函数"""
    args = parse_arguments()
    
    logger.info("===== MySQL 连接修复工具启动 =====")
    logger.info(f"日志文件: {os.path.abspath(log_file)}")
    
    # 构建 SSL 配置
    ssl_config = {}
    if args.enable_ssl:
        if args.ca_file:
            ssl_config['ca'] = args.ca_file
        
        if args.no_verify:
            ssl_config['no_verify'] = True
    
    # 获取所有 MySQL 数据源
    datasources = get_mysql_datasources()
    if not datasources:
        logger.error("未找到任何 MySQL 数据源，程序将退出")
        return
    
    # 检查 root 用户信息
    if args.fix_auth and (not args.root_user or not args.root_password):
        logger.warning("未提供 root 用户或密码，将无法修复认证插件问题")
        logger.warning("如需修复认证插件，请使用 --root-user 和 --root-password 参数")
    
    # 处理每个数据源
    for datasource in datasources:
        ds_name = datasource.get('name', '未命名数据源')
        logger.info(f"\n===== 处理数据源: {ds_name} =====")
        
        # 提取连接信息
        conn_info = datasource.get('connection', {})
        host = conn_info.get('host', 'localhost')
        port = int(conn_info.get('port', 3306))
        user = conn_info.get('user', '')
        password = conn_info.get('password', '')
        database = conn_info.get('database', '')
        
        if not user:
            logger.error(f"数据源 {ds_name} 未配置用户名，跳过处理")
            continue
        
        # 测试连接
        success, result = test_mysql_connection(host, port, user, password, database, ssl_config if args.enable_ssl else None)
        
        # 如果连接成功，检查是否需要修改认证插件
        if success:
            auth_plugin = result.get('auth_plugin', '')
            
            if auth_plugin == 'caching_sha2_password' and args.fix_auth:
                logger.info(f"用户 {user} 使用 caching_sha2_password 认证插件，尝试修改为 mysql_native_password")
                
                fix_success, fix_message = fix_auth_plugin(
                    host, port, args.root_user, args.root_password, user
                )
                
                if fix_success:
                    logger.info(f"成功修复 {user} 的认证插件")
                else:
                    logger.error(f"修复 {user} 的认证插件失败: {fix_message}")
            
            elif auth_plugin == 'mysql_native_password':
                logger.info(f"用户 {user} 已使用 mysql_native_password 认证插件，无需修改")
            
            # 如果已启用 SSL，更新数据源配置
            if args.enable_ssl:
                logger.info("更新数据源的 SSL 配置")
                if update_datasource_ssl_config(datasource, ssl_config):
                    logger.info(f"成功更新数据源 {ds_name} 的 SSL 配置")
                else:
                    logger.error(f"更新数据源 {ds_name} 的 SSL 配置失败")
        
        # 如果连接失败，尝试修复问题
        else:
            error = result.get('error', '')
            
            # 认证插件需要安全连接
            if result.get('needs_ssl', False):
                logger.info("检测到认证插件需要安全连接")
                
                # 修复认证插件
                if args.fix_auth and args.root_user and args.root_password:
                    logger.info(f"尝试修复用户 {user} 的认证插件")
                    
                    fix_success, fix_message = fix_auth_plugin(
                        host, port, args.root_user, args.root_password, user
                    )
                    
                    if fix_success:
                        logger.info(f"成功修复 {user} 的认证插件")
                    else:
                        logger.error(f"修复 {user} 的认证插件失败: {fix_message}")
                
                # 启用 SSL 连接
                if args.enable_ssl:
                    logger.info("尝试更新 SSL 配置")
                    if update_datasource_ssl_config(datasource, ssl_config):
                        logger.info(f"成功更新数据源 {ds_name} 的 SSL 配置")
                    else:
                        logger.error(f"更新数据源 {ds_name} 的 SSL 配置失败")
                
                # 重新测试连接
                logger.info("重新测试连接")
                retest_success, retest_result = test_mysql_connection(
                    host, port, user, password, database, 
                    ssl_config if args.enable_ssl else None
                )
                
                if retest_success:
                    logger.info("修复后连接成功!")
                else:
                    logger.error(f"修复后连接仍然失败: {retest_result.get('error', '')}")
            
            else:
                logger.error(f"连接失败，但不是由于认证插件或 SSL 问题: {error}")
    
    logger.info("\n===== MySQL 连接修复工具完成 =====")
    logger.info(f"详细日志已保存到: {os.path.abspath(log_file)}")

if __name__ == "__main__":
    main() 