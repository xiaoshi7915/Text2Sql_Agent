#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM连接器模块
负责处理与各种大语言模型提供商的连接和API请求
"""

import logging
import json
import requests
from requests.exceptions import RequestException
import openai

logger = logging.getLogger(__name__)

class BaseLLMConnector:
    """基础LLM连接器"""
    
    def __init__(self, api_key, api_base=None, **kwargs):
        """
        初始化LLM连接器
        
        Args:
            api_key (str): API密钥
            api_base (str, optional): API基础URL
            **kwargs: 额外参数
        """
        self.api_key = api_key
        self.api_base = api_base
        self.extra_params = kwargs
    
    def test_connection(self):
        """
        测试连接
        
        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        raise NotImplementedError("子类必须实现此方法")


class OpenAIConnector(BaseLLMConnector):
    """OpenAI API连接器"""
    
    def test_connection(self):
        """
        测试OpenAI API连接
        
        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        try:
            # 设置OpenAI客户端
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base if self.api_base else "https://api.openai.com/v1"
            )
            
            # 简单调用模型列表API来测试连接
            models = client.models.list()
            
            # 如果能获取到模型列表，则连接成功
            if models:
                logger.info("OpenAI API连接成功")
                return True, None
            
            return False, "无法获取模型列表"
            
        except Exception as e:
            logger.error(f"OpenAI API连接失败: {str(e)}")
            return False, str(e)


class DeepSeekConnector(BaseLLMConnector):
    """DeepSeek API连接器"""
    
    def test_connection(self):
        """
        测试DeepSeek API连接
        
        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        try:
            # 设置基础URL，如果没有提供则使用默认URL
            base_url = self.api_base if self.api_base else "https://api.deepseek.com/v1"
            
            # 创建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 请求模型列表来测试连接
            response = requests.get(f"{base_url}/models", headers=headers)
            
            # 如果响应状态码为200，则连接成功
            if response.status_code == 200:
                logger.info("DeepSeek API连接成功")
                return True, None
            
            # 返回错误信息
            return False, f"API请求失败: HTTP {response.status_code}, {response.text}"
            
        except RequestException as e:
            logger.error(f"DeepSeek API请求异常: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"DeepSeek API连接失败: {str(e)}")
            return False, str(e)


class ZhipuConnector(BaseLLMConnector):
    """智谱AI API连接器"""
    
    def test_connection(self):
        """
        测试智谱AI API连接
        
        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        try:
            # 设置基础URL，如果没有提供则使用默认URL
            base_url = self.api_base if self.api_base else "https://open.bigmodel.cn/api/paas/v3"
            
            # 创建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送简单的模型信息请求
            response = requests.get(f"{base_url}/models", headers=headers)
            
            # 如果响应状态码为200，则连接成功
            if response.status_code == 200:
                logger.info("智谱AI API连接成功")
                return True, None
            
            # 返回错误信息
            return False, f"API请求失败: HTTP {response.status_code}, {response.text}"
            
        except RequestException as e:
            logger.error(f"智谱AI API请求异常: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"智谱AI API连接失败: {str(e)}")
            return False, str(e)


# LLM连接器工厂
class LLMConnectorFactory:
    """LLM连接器工厂类"""
    
    @staticmethod
    def create_connector(provider, api_key, api_base=None, **kwargs):
        """
        创建LLM连接器
        
        Args:
            provider (str): 提供商名称
            api_key (str): API密钥
            api_base (str, optional): API基础URL
            **kwargs: 额外参数
            
        Returns:
            BaseLLMConnector: LLM连接器实例
        """
        provider = provider.lower() if provider else ""
        
        if provider == "openai":
            return OpenAIConnector(api_key, api_base, **kwargs)
        elif provider == "deepseek":
            return DeepSeekConnector(api_key, api_base, **kwargs)
        elif provider == "zhipu" or provider == "zhipuai":
            return ZhipuConnector(api_key, api_base, **kwargs)
        else:
            # 默认使用OpenAI连接器
            logger.warning(f"未知的LLM提供商: {provider}，使用OpenAI连接器作为默认")
            return OpenAIConnector(api_key, api_base, **kwargs) 