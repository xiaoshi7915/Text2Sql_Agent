#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
聊天服务模块
负责处理用户消息和生成AI回复
"""

import os
import json
import logging
import requests
import time
import traceback
from app.models.model import Model
from app.models.datasource import DataSource
from app.services.datasource_service import DataSourceService

class ChatService:
    """聊天服务类，处理用户消息并生成回复"""
    
    def __init__(self):
        """初始化聊天服务"""
        self.logger = logging.getLogger(__name__)
        self.datasource_service = DataSourceService()
    
    def process_message(self, message_content, model, datasources=None):
        """
        处理用户消息并生成回复
        
        Args:
            message_content (str): 用户消息内容
            model (Model): 使用的LLM模型
            datasources (list, optional): 关联的数据源列表
            
        Returns:
            dict: 处理结果，包含生成的回复和其他信息
        """
        try:
            if not model:
                return {
                    "content": "请先选择一个AI模型才能进行对话",
                    "error": None
                }
            
            # 获取LLM服务
            llm_service = self._get_llm_service(model)
            
            if not llm_service:
                return {
                    "content": f"无法初始化{model.provider}服务，请检查模型配置",
                    "error": "模型服务初始化失败"
                }
            
            # 如果是SQL相关查询且有数据源，增强系统提示
            is_sql_query = self._is_sql_query(message_content)
            
            if is_sql_query and datasources:
                # 获取数据库元数据
                metadata = {}
                sample_data = {}
                
                # 只处理第一个数据源
                if datasources:
                    primary_datasource = datasources[0]
                    
                    # 获取数据库结构
                    tables_info = self.datasource_service.get_tables(primary_datasource.id)
                    
                    if tables_info and 'tables' in tables_info:
                        metadata = tables_info
                        
                        # 获取部分表的样本数据（前5行）
                        for table in tables_info['tables'][:3]:  # 只处理前3个表
                            table_name = table.get('name')
                            if table_name:
                                sample_rows = self.datasource_service.get_sample_data(
                                    primary_datasource.id, 
                                    table_name, 
                                    limit=5
                                )
                                if sample_rows:
                                    sample_data[table_name] = sample_rows
                
                # 构建增强消息，包含数据库信息
                system_message = f"您正在查询数据源: {datasources[0].name}，包含{len(metadata.get('tables', []))}个表。"
                
                # 调用自然语言到SQL转换
                result = llm_service.natural_language_to_sql(
                    query=message_content,
                    metadata=metadata,
                    sample_data=sample_data
                )
                
                # 如果生成了SQL
                if 'sql' in result and result['sql']:
                    # 执行SQL查询
                    sql = result['sql']
                    explanation = result.get('explanation', '')
                    
                    response_content = explanation
                    
                    # 添加SQL代码块
                    if sql:
                        response_content = f"```sql\n{sql}\n```\n\n{explanation}"
                        
                        # 如果有数据源，尝试执行SQL
                        if datasources:
                            try:
                                query_result = self.datasource_service.execute_read_query(
                                    datasources[0].id, 
                                    sql
                                )
                                
                                if query_result:
                                    # 将查询结果添加到响应
                                    result_str = json.dumps(query_result, ensure_ascii=False, indent=2)
                                    response_content += f"\n\n查询结果:\n```json\n{result_str}\n```"
                            except Exception as e:
                                response_content += f"\n\n执行查询时出错: {str(e)}"
                    
                    return {
                        "content": response_content,
                        "sql_query": sql,
                        "error": None
                    }
            
            # 通用对话处理
            return llm_service.chat_completion(
                messages=[{"role": "user", "content": message_content}],
                model=model.provider
            )
                
        except Exception as e:
            self.logger.error(f"处理消息失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "content": f"处理您的消息时出现错误: {str(e)}",
                "error": str(e)
            }
    
    def _is_sql_query(self, message):
        """
        判断消息是否为SQL相关查询
        
        Args:
            message (str): 用户消息
            
        Returns:
            bool: 是否为SQL相关查询
        """
        # 简单判断是否包含查询关键词
        sql_keywords = ["查询", "数据", "表", "字段", "统计", "分析", "SQL", "select", "查找", "搜索"]
        return any(keyword in message.lower() for keyword in sql_keywords)
    
    def _get_llm_service(self, model):
        """
        根据模型配置获取LLM服务
        
        Args:
            model (Model): 模型配置
            
        Returns:
            LLMService: LLM服务对象
        """
        try:
            from app.utils.llm_service import LLMService
            
            if model.provider.lower() in ['openai', 'anthropic', 'deepseek']:
                # 传递模型配置对象给LLMService
                self.logger.info(f"正在初始化{model.provider}服务，使用模型: {model.model_type}")
                return LLMService(model_config=model)
            else:
                self.logger.warning(f"不支持的模型提供商: {model.provider}")
                return None
        except Exception as e:
            self.logger.error(f"初始化LLM服务失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None 