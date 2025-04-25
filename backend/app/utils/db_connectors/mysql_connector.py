import logging
import mysql.connector
from mysql.connector import Error as MySQLError
from app.utils.db_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)

class MySQLConnector(BaseConnector):
    """MySQL数据库连接器"""

    def get_connection(self, host, port, user, password, database=None, **kwargs):
        """
        获取MySQL数据库连接
        
        Args:
            host (str): 主机地址
            port (int): 端口号
            user (str): 用户名
            password (str): 密码
            database (str, optional): 数据库名
            **kwargs: 其他连接参数
            
        Returns:
            tuple: (连接对象或None, 错误信息或None)
        """
        try:
            # 添加SSL参数和认证插件配置
            conn_params = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'use_pure': True,  # 使用纯Python实现，避免C扩展的兼容性问题
                'ssl_disabled': kwargs.get('ssl_disabled', True),  # 默认禁用SSL
                'auth_plugin': 'mysql_native_password'  # 指定使用旧的认证插件
            }
            
            # 添加数据库名，如果提供了
            if database:
                conn_params['database'] = database
                
            # 记录连接尝试
            logger.debug(f"尝试连接MySQL数据库: {host}:{port}, 用户: {user}, 数据库: {database}")
            
            # 创建连接
            connection = mysql.connector.connect(**conn_params)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.info(f"已成功连接到MySQL服务器版本：{db_info}")
                
                if database:
                    cursor = connection.cursor()
                    cursor.execute("SELECT DATABASE()")
                    db_name = cursor.fetchone()[0]
                    logger.debug(f"已连接到数据库: {db_name}")
                    cursor.close()
                
                return connection, None
            else:
                logger.error("MySQL连接创建失败")
                return None, "连接创建失败，但未引发异常"
                
        except MySQLError as err:
            # 如果是认证错误，尝试使用caching_sha2_password
            if "Authentication plugin 'caching_sha2_password'" in str(err):
                logger.warning("MySQL认证失败，尝试使用caching_sha2_password和SSL连接")
                try:
                    # 尝试使用SSL连接
                    conn_params = {
                        'host': host,
                        'port': port,
                        'user': user,
                        'password': password,
                        'use_pure': True,
                        'ssl_disabled': False,  # 启用SSL
                        'auth_plugin': 'caching_sha2_password'  # 使用新的认证插件
                    }
                    
                    if database:
                        conn_params['database'] = database
                    
                    connection = mysql.connector.connect(**conn_params)
                    
                    if connection.is_connected():
                        db_info = connection.get_server_info()
                        logger.info(f"通过SSL和caching_sha2_password成功连接到MySQL服务器版本：{db_info}")
                        return connection, None
                    
                except MySQLError as sec_err:
                    logger.error(f"MySQL第二次连接尝试失败: {sec_err}")
                    return None, f"MySQL连接错误: {sec_err}"
            
            logger.error(f"MySQL连接错误: {err}")
            return None, f"MySQL连接错误: {err}"
        except Exception as e:
            logger.error(f"连接MySQL时发生未知错误: {e}")
            return None, f"连接错误: {e}"

    def execute_query(self, connection, query, params=None):
        """
        执行SQL查询
        
        Args:
            connection: 数据库连接对象
            query (str): SQL查询语句
            params (tuple, optional): 查询参数
            
        Returns:
            tuple: (结果列表或None, 错误信息或None)
        """
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            logger.debug(f"执行MySQL查询: {query}")
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            results = cursor.fetchall()
            logger.debug(f"查询返回 {len(results)} 条结果")
            return results, None
            
        except MySQLError as err:
            logger.error(f"执行查询错误: {err}")
            return None, f"查询执行错误: {err}"
        except Exception as e:
            logger.error(f"执行查询时发生未知错误: {e}")
            return None, f"查询执行错误: {e}"
        finally:
            if cursor:
                cursor.close()

    def close_connection(self, connection):
        """
        关闭数据库连接
        
        Args:
            connection: 要关闭的连接对象
        """
        try:
            if connection and connection.is_connected():
                connection.close()
                logger.debug("MySQL连接已关闭")
        except Exception as e:
            logger.error(f"关闭MySQL连接时发生错误: {e}")

    def test_connection(self, host, port, user, password, database=None, **kwargs):
        """
        测试数据库连接
        
        Args:
            host (str): 主机地址
            port (int): 端口号
            user (str): 用户名
            password (str): 密码
            database (str, optional): 数据库名
            **kwargs: 其他连接参数
            
        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        connection, error = self.get_connection(host, port, user, password, database, **kwargs)
        
        if error:
            return False, error
            
        if connection:
            self.close_connection(connection)
            return True, None
            
        return False, "连接测试失败，但未返回错误"

    def list_databases(self, host, port, user, password, **kwargs):
        """
        列出所有数据库
        
        Args:
            host (str): 主机地址
            port (int): 端口号
            user (str): 用户名
            password (str): 密码
            **kwargs: 其他连接参数
            
        Returns:
            tuple: (数据库列表或None, 错误信息或None)
        """
        connection, error = self.get_connection(host, port, user, password, **kwargs)
        
        if error:
            return None, error
            
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            # 排除系统数据库
            user_databases = [db for db in databases if db.lower() not in ('mysql', 'performance_schema', 'information_schema', 'sys')]
            
            return user_databases, None
        except MySQLError as err:
            logger.error(f"列出数据库错误: {err}")
            return None, f"列出数据库错误: {err}"
        except Exception as e:
            logger.error(f"列出数据库时发生未知错误: {e}")
            return None, f"列出数据库错误: {e}"
        finally:
            self.close_connection(connection)

    def list_tables(self, host, port, user, password, database, **kwargs):
        """
        列出指定数据库中的所有表
        
        Args:
            host (str): 主机地址
            port (int): 端口号
            user (str): 用户名
            password (str): 密码
            database (str): 数据库名
            **kwargs: 其他连接参数
            
        Returns:
            tuple: (表列表或None, 错误信息或None)
        """
        connection, error = self.get_connection(host, port, user, password, database, **kwargs)
        
        if error:
            return None, error
            
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            return tables, None
        except MySQLError as err:
            logger.error(f"列出表错误: {err}")
            return None, f"列出表错误: {err}"
        except Exception as e:
            logger.error(f"列出表时发生未知错误: {e}")
            return None, f"列出表错误: {e}"
        finally:
            self.close_connection(connection) 