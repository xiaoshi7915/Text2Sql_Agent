#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM服务模块
负责处理与大语言模型相关的服务功能
"""

import logging
from app.utils.llm_connectors import LLMConnectorFactory

logger = logging.getLogger(__name__)

class LLMService:
    """LLM服务类"""
    
    @staticmethod
    def test_connection(data):
        """
        测试LLM连接
        
        Args:
            data (dict): 包含连接信息的字典，必须包含provider、model_type和api_key
            
        Returns:
            dict: 测试结果
        """
        logger.info(f"测试LLM连接请求: {data.get('provider')} 类型: {data.get('model_type')}")
        
        provider = data.get('provider', '')
        model_type = data.get('model_type', '')
        api_key = data.get('api_key', '')
        api_base = data.get('api_base')
        
        # 验证必要参数
        if not provider:
            return {
                'status': 'error',
                'message': '缺少必要参数: provider'
            }
        
        if not api_key:
            return {
                'status': 'error',
                'message': '缺少必要参数: api_key'
            }
        
        try:
            # 创建LLM连接器
            connector = LLMConnectorFactory.create_connector(
                provider, 
                api_key, 
                api_base
            )
            
            # 测试连接
            success, error = connector.test_connection()
            
            if success:
                logger.info(f"LLM连接测试成功: {provider}")
                return {
                    'status': 'success',
                    'message': f'{provider} 连接测试成功'
                }
            else:
                logger.error(f"LLM连接测试失败: {provider}, 错误: {error}")
                return {
                    'status': 'error',
                    'message': f'连接失败: {error}'
                }
                
        except Exception as e:
            logger.error(f"LLM连接测试异常: {str(e)}")
            return {
                'status': 'error',
                'message': f'连接测试异常: {str(e)}'
            }
    
    @staticmethod
    def format_error(error_message):
        """
        格式化错误信息
        
        Args:
            error_message (str): 原始错误信息
            
        Returns:
            dict: 格式化的错误信息
        """
        # 根据不同的错误类型，提供友好的错误信息和可能的解决方案
        
        # API密钥无效
        if "invalid api key" in error_message.lower() or "unauthorized" in error_message.lower():
            return {
                "friendly_message": "API密钥无效或未授权",
                "original_error": error_message,
                "possible_solution": "请检查您的API密钥是否正确，或者尝试重新生成API密钥",
                "error_type": "auth_error"
            }
        
        # 连接超时
        elif "timeout" in error_message.lower() or "timed out" in error_message.lower():
            return {
                "friendly_message": "连接超时",
                "original_error": error_message,
                "possible_solution": "请检查您的网络连接，或者API服务器是否可用",
                "error_type": "timeout_error"
            }
        
        # 网络错误
        elif "connection" in error_message.lower() and "refused" in error_message.lower():
            return {
                "friendly_message": "连接被拒绝",
                "original_error": error_message,
                "possible_solution": "请检查API基础URL是否正确，或者服务器是否可用",
                "error_type": "connection_error"
            }
        
        # 默认错误
        else:
            return {
                "friendly_message": f"连接失败: {error_message}",
                "original_error": error_message,
                "possible_solution": "请检查连接配置，确保所有参数正确",
                "error_type": "unknown_error"
            } 