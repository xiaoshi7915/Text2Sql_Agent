#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据源服务
负责处理数据源的CRUD操作和测试连接
"""

import logging
import json
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from ..models.datasource import DataSource
from ..utils.encryption import encrypt_password, decrypt_password
from .db_connector import ConnectorFactory
from .. import db
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DataSourceService:
    """数据源服务类"""
    
    @staticmethod
    def get_all_datasources():
        """获取所有数据源"""
        try:
            datasources = DataSource.query.all()
            return True, [ds.to_dict() for ds in datasources], None
        except Exception as e:
            logger.error(f"获取数据源列表失败: {str(e)}")
            return False, None, str(e)
    
    @staticmethod
    def get_datasource_by_id(datasource_id):
        """根据ID获取数据源"""
        try:
            datasource = DataSource.query.get(datasource_id)
            if not datasource:
                return False, None, f"数据源ID {datasource_id} 不存在"
            return True, datasource.to_dict(), None
        except Exception as e:
            logger.error(f"获取数据源详情失败: {str(e)}")
            return False, None, str(e)
    
    @staticmethod
    def create_datasource(data):
        """创建数据源"""
        try:
            # 验证必要字段
            required_fields = ['name', 'ds_type', 'host', 'port', 'database', 'username', 'password']
            for field in required_fields:
                if field not in data:
                    return False, None, f'缺少必要字段: {field}'
            
            # 加密密码
            encrypted_password = encrypt_password(data['password'])
            
            # 处理可选字段
            options = data.get('options', {})
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = {}
            
            # 创建数据源实例
            datasource = DataSource(
                name=data['name'],
                description=data.get('description', ''),
                ds_type=data['ds_type'],
                host=data['host'],
                port=data['port'],
                database=data['database'],
                username=data['username'],
                password=encrypted_password,
                options=options,
                include_views=data.get('include_views', False),
                format=data.get('format', 'public'),
                selected_fields=data.get('selected_fields', '')
            )
            
            # 测试连接并获取表数量
            success, table_count, error = DataSourceService.test_connection_internal(
                data['ds_type'],
                data['host'],
                data['port'],
                data['database'],
                data['username'],
                data['password']
            )
            
            if success:
                datasource.table_count = table_count
                datasource.connection_status = 'connected'
            else:
                datasource.connection_status = 'disconnected'
            
            db.session.add(datasource)
            db.session.commit()
            
            return True, datasource.to_dict(), None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"数据库错误: {str(e)}")
            return False, None, f"数据库错误: {str(e)}"
        except Exception as e:
            logger.error(f"创建数据源失败: {str(e)}")
            return False, None, f"创建数据源失败: {str(e)}"
    
    @staticmethod
    def update_datasource(datasource_id, data):
        """更新数据源"""
        try:
            datasource = DataSource.query.get(datasource_id)
            if not datasource:
                return False, None, f'数据源ID {datasource_id} 不存在'
            
            # 更新基本字段
            if 'name' in data:
                datasource.name = data['name']
            if 'description' in data:
                datasource.description = data['description']
            if 'host' in data:
                datasource.host = data['host']
            if 'port' in data:
                datasource.port = data['port']
            if 'database' in data:
                datasource.database = data['database']
            if 'username' in data:
                datasource.username = data['username']
            if 'ds_type' in data:
                datasource.ds_type = data['ds_type']
            
            # 如果提供了新密码，进行加密
            password_changed = False
            if 'password' in data and data['password'] and data['password'] != '******':
                datasource.password = encrypt_password(data['password'])
                password_changed = True
            
            # 更新可选字段
            if 'options' in data:
                options = data['options']
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except:
                        options = {}
                datasource.options = options
            
            if 'include_views' in data:
                datasource.include_views = data['include_views']
            if 'format' in data:
                datasource.format = data['format']
            if 'selected_fields' in data:
                datasource.selected_fields = data['selected_fields']
            
            # 如果连接信息有变化，测试连接
            connection_info_changed = any([
                'host' in data,
                'port' in data,
                'database' in data,
                'username' in data,
                password_changed,
                'ds_type' in data
            ])
            
            if connection_info_changed:
                # 如果密码没变，需要解密
                password = data.get('password', '')
                if not password_changed:
                    try:
                        password = decrypt_password(datasource.password)
                    except Exception as e:
                        return False, None, f"密码解密失败: {str(e)}"
                
                # 测试连接并更新表数量和连接状态
                success, table_count, error = DataSourceService.test_connection_internal(
                    datasource.ds_type,
                    datasource.host,
                    datasource.port,
                    datasource.database,
                    datasource.username,
                    password
                )
                
                if success:
                    datasource.table_count = table_count
                    datasource.connection_status = 'connected'
                else:
                    datasource.connection_status = 'disconnected'
            
            db.session.commit()
            
            return True, datasource.to_dict(), None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"数据库错误: {str(e)}")
            return False, None, f"数据库错误: {str(e)}"
        except Exception as e:
            logger.error(f"更新数据源失败: {str(e)}")
            return False, None, f"更新数据源失败: {str(e)}"
    
    @staticmethod
    def delete_datasource(datasource_id):
        """删除数据源"""
        try:
            datasource = DataSource.query.get(datasource_id)
            if not datasource:
                return False, f'数据源ID {datasource_id} 不存在'
            
            db.session.delete(datasource)
            db.session.commit()
            
            return True, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"数据库错误: {str(e)}")
            return False, f"数据库错误: {str(e)}"
        except Exception as e:
            logger.error(f"删除数据源失败: {str(e)}")
            return False, f"删除数据源失败: {str(e)}"
    
    @staticmethod
    def test_connection(data):
        """测试数据源连接"""
        try:
            # 详细记录请求数据（去除敏感信息）
            safe_data = data.copy()
            if 'password' in safe_data:
                safe_data['password'] = '******'
            logger.info(f"测试数据源连接请求: {safe_data}")
            
            # 验证必要字段
            required_fields = ['ds_type', 'host', 'port', 'database', 'username', 'password']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"缺少必要字段: {field}")
                    return {
                        'success': False,
                        'error': f'缺少必要字段: {field}'
                    }
            
            # 数据源ID，如果是已有数据源则需要
            datasource_id = data.get('id')
            ds_type = data['ds_type']
            host = data['host']
            port = data['port']
            database = data['database']
            username = data['username']
            password = data['password']
            
            logger.info(f"连接数据库: {ds_type}, {host}:{port}, {database}, 用户: {username}")
            
            # 如果是已有数据源，并且密码是占位符，则使用数据库中的密码
            if datasource_id and password == '******':
                logger.info(f"使用数据源ID: {datasource_id}的已存储密码")
                datasource = DataSource.query.get(datasource_id)
                if datasource:
                    try:
                        password = decrypt_password(datasource.password)
                    except Exception as e:
                        logger.error(f"密码解密失败: {str(e)}")
                        return {
                            'success': False,
                            'error': f'密码解密失败: {str(e)}'
                        }
            
            # 测试连接并获取表数量
            success, table_count, error = DataSourceService.test_connection_internal(
                ds_type, host, port, database, username, password
            )
            
            # 如果是已有数据源，更新表数量和连接状态
            if datasource_id:
                datasource = DataSource.query.get(datasource_id)
                if datasource:
                    if success:
                        datasource.table_count = table_count
                        datasource.connection_status = 'connected'
                    else:
                        datasource.connection_status = 'disconnected'
                    db.session.commit()
            
            if success:
                logger.info(f"连接成功，表数量: {table_count}")
                return {
                    'success': True,
                    'tables': table_count,
                    'message': f"连接成功，发现 {table_count} 个表"
                }
            else:
                logger.error(f"连接失败: {error}")
                # 格式化错误信息
                error_details = format_connection_error(str(error))
                return {
                    'success': False,
                    'error': error_details["friendly_message"],
                    'details': {
                        'original_error': error_details["original_error"],
                        'possible_solution': error_details["possible_solution"],
                        'error_type': error_details["error_type"]
                    }
                }
                
        except Exception as e:
            import traceback
            logger.error(f"测试连接异常: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f"测试连接失败: {str(e)}"
            }
    
    @staticmethod
    def test_connection_internal(ds_type, host, port, database, username, password):
        """内部方法：测试数据库连接并返回表数量"""
        try:
            # 创建数据库连接器
            connector = ConnectorFactory.create_connector(
                ds_type, host, port, database, username, password
            )
            
            # 测试连接并获取表数量
            success, table_count, error = connector.test_connection()
            
            return success, table_count, error
            
        except Exception as e:
            logger.error(f"测试连接失败: {str(e)}")
            return False, 0, str(e)
    
    @staticmethod
    def update_all_datasources_info():
        """更新所有数据源的表数量和连接状态"""
        try:
            # 获取所有数据源
            datasources = DataSource.query.all()
            logger.info(f"共找到 {len(datasources)} 个数据源")
            
            for ds in datasources:
                logger.info(f"更新数据源 ID: {ds.id}, 名称: {ds.name}")
                
                # 解密密码
                try:
                    password = decrypt_password(ds.password)
                except Exception as e:
                    logger.error(f"密码解密失败: {str(e)}")
                    ds.connection_status = 'disconnected'
                    continue
                
                # 测试连接并获取表数量
                success, table_count, error = DataSourceService.test_connection_internal(
                    ds.ds_type, ds.host, ds.port, ds.database, ds.username, password
                )
                
                if success:
                    ds.table_count = table_count
                    ds.connection_status = 'connected'
                    logger.info(f"数据源 {ds.name} 连接成功，发现 {table_count} 个表")
                else:
                    ds.connection_status = 'disconnected'
                    logger.error(f"数据源 {ds.name} 连接失败: {error}")
            
            # 提交更改
            db.session.commit()
            logger.info("更新完成")
            
            return True, None
            
        except Exception as e:
            logger.error(f"更新数据源信息失败: {str(e)}")
            return False, str(e)

def format_connection_error(error_str):
    """格式化连接错误信息，提供更友好的错误描述和解决方案

    Args:
        error_str: 原始错误信息

    Returns:
        dict: 包含错误详情和解决方案的字典
    """
    error_details = {
        "original_error": error_str,
        "friendly_message": error_str,
        "possible_solution": None,
        "error_type": "unknown"
    }
    
    # 认证错误
    if "Access denied for user" in error_str:
        if "(using password: NO)" in error_str:
            error_details["friendly_message"] = "用户名或密码错误：未提供密码"
            error_details["possible_solution"] = "请检查用户名和密码是否正确"
            error_details["error_type"] = "auth_error"
        elif "(using password: YES)" in error_str:
            error_details["friendly_message"] = "用户名或密码错误：密码不正确"
            error_details["possible_solution"] = "请检查用户名和密码是否正确，或确认用户是否有权限访问该数据库"
            error_details["error_type"] = "auth_error"
    
    # 认证插件问题
    elif "Authentication plugin 'caching_sha2_password'" in error_str:
        if "requires secure connection" in error_str:
            error_details["friendly_message"] = "MySQL 8.0+ 认证插件需要安全连接"
            error_details["possible_solution"] = "请尝试使用 fix_mysql_connection.py 工具修复认证插件或启用SSL连接"
            error_details["error_type"] = "auth_plugin_error"
    
    # 连接超时
    elif "Can't connect to MySQL server" in error_str or "Connection refused" in error_str:
        error_details["friendly_message"] = "无法连接到MySQL服务器"
        error_details["possible_solution"] = "请检查服务器地址和端口是否正确，服务器是否在线，以及网络连接是否正常"
        error_details["error_type"] = "connection_error"
    
    # 未知数据库
    elif "Unknown database" in error_str:
        error_details["friendly_message"] = "数据库不存在"
        error_details["possible_solution"] = "请检查数据库名称是否正确，或者是否有权限访问该数据库"
        error_details["error_type"] = "database_error"
    
    # SSL错误
    elif "SSL connection error" in error_str:
        error_details["friendly_message"] = "SSL连接错误"
        error_details["possible_solution"] = "请检查SSL配置是否正确，或尝试禁用SSL连接"
        error_details["error_type"] = "ssl_error"
        
    return error_details

def mask_password(data):
    """遮蔽数据中的密码信息，用于日志记录
    
    Args:
        data: 包含密码字段的数据字典
        
    Returns:
        dict: 密码被遮蔽后的数据字典
    """
    if not data or not isinstance(data, dict):
        return data
    
    # 创建数据的副本
    safe_data = data.copy()
    
    # 遮蔽密码字段
    if 'password' in safe_data:
        safe_data['password'] = '******'
    
    return safe_data

def test_connection(ds_info):
    """测试数据源连接
    
    Args:
        ds_info: 数据源信息，包含类型、连接参数等
        
    Returns:
        dict: 测试结果
    """
    # 使用本模块中已定义的mask_password函数
    safe_data = mask_password(ds_info)
    logger.info(f"测试数据源连接请求: {safe_data}")
    
    ds_type = ds_info.get('ds_type', '')
    host = ds_info.get('host', '')
    port = int(ds_info.get('port', 0))
    database = ds_info.get('database', '')
    username = ds_info.get('username', '')
    password = ds_info.get('password', '')
    
    # 如果提供了数据源ID且未提供密码，尝试使用存储的密码
    ds_id = ds_info.get('id')
    if ds_id and not password:
        stored_ds = get_datasource_by_id(ds_id)
        if stored_ds and 'connection' in stored_ds:
            stored_password = stored_ds['connection'].get('password', '')
            if stored_password:
                password = stored_password
                logger.info(f"使用数据源ID: {ds_id}的已存储密码")
    
    logger.info(f"连接数据库: {ds_type}, {host}:{port}, {database}, 用户: {username}")
    
    # 创建连接器并测试连接
    connector = ConnectorFactory.create_connector(ds_type, host, port, database, username, password)
    success, tables, error = connector.test_connection()
    
    # 如果连接成功
    if success:
        logger.info(f"连接成功，表数量: {tables}")
        result = {
            'success': True,
            'tables': tables,
            'message': f"连接成功，发现 {tables} 个表"
        }
        
        # 更新数据源状态
        if ds_id:
            update_datasource_status(ds_id, True)
            
        return result
    else:
        # 格式化错误信息
        error_details = format_connection_error(str(error))
        logger.error(f"连接失败: {error}")
        
        # 更新数据源状态
        if ds_id:
            update_datasource_status(ds_id, False)
            
        return {
            'success': False,
            'error': error_details["friendly_message"],
            'details': {
                'original_error': error_details["original_error"],
                'possible_solution': error_details["possible_solution"],
                'error_type': error_details["error_type"]
            }
        }

def get_datasource_path():
    """获取数据源文件存储路径
    
    Returns:
        str: 数据源文件存储目录的路径
    """
    try:
        # 从配置获取路径或使用默认路径
        path = current_app.config.get('DATASOURCE_PATH', '/opt/wenshu-mcp/data/datasources')
        
        # 确保目录存在
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
        return path
    except Exception as e:
        logger.error(f"获取数据源存储路径失败: {str(e)}")
        # 返回一个默认路径
        return '/tmp/datasources'

def update_datasource_status(ds_id, is_connected):
    """更新数据源连接状态
    
    Args:
        ds_id: 数据源ID
        is_connected: 是否连接成功
    """
    try:
        # 直接通过数据库模型更新状态，而不是读写JSON文件
        datasource = DataSource.query.get(ds_id)
        if not datasource:
            logger.warning(f"数据源ID {ds_id} 不存在")
            return False
        
        # 更新连接状态
        datasource.connection_status = 'connected' if is_connected else 'disconnected'
        
        # 提交更改
        db.session.commit()
        
        logger.info(f"已更新数据源 {ds_id} 的状态: {'连接成功' if is_connected else '连接失败'}")
        return True
        
    except Exception as e:
        logger.error(f"更新数据源状态失败: {e}")
        return False 