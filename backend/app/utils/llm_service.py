#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM服务，处理自然语言到SQL的转换
"""

import os
import json
import logging
import requests
import time
import traceback
import re

try:
    import anthropic
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# 延迟导入以避免循环依赖
_decrypt_api_key = None

def get_decrypt_function():
    """延迟加载decrypt_api_key函数"""
    global _decrypt_api_key
    if _decrypt_api_key is None:
        try:
            from ..api.models import decrypt_api_key as decrypt_func
            _decrypt_api_key = decrypt_func
        except ImportError:
            # 如果导入失败，使用一个空函数
            def dummy_decrypt(key):
                return key
            _decrypt_api_key = dummy_decrypt
    return _decrypt_api_key

class LLMService:
    """提供自然语言处理相关的服务"""
    
    def __init__(self, model_config=None):
        """初始化LLM服务
        
        Args:
            model_config (Model, optional): 模型配置对象，包含API密钥等信息
        """
        self.logger = logging.getLogger(__name__)
        
        # 如果提供了模型配置，使用模型配置中的信息
        if model_config:
            self.provider = model_config.provider.lower()
            # 解密API密钥
            try:
                decrypt_func = get_decrypt_function()
                self.api_key = decrypt_func(model_config.api_key) if model_config.api_key else None
                if not self.api_key:
                    self.logger.warning(f"模型 {model_config.name} 的API密钥为空或解密失败")
            except Exception as e:
                self.logger.error(f"解密API密钥失败: {str(e)}")
                self.api_key = None
                
            self.api_base = model_config.api_base or "https://api.deepseek.com"
            self.model_name = model_config.model_type  # 假设model_type字段存储具体模型名称
            self.temperature = model_config.temperature
            self.max_tokens = model_config.max_tokens
            
            # 记录模型配置信息（不包含敏感数据）
            self.logger.info(f"使用模型配置: 提供商={self.provider}, 模型={self.model_name}, API基础URL={self.api_base}")
        else:
            # 否则从环境变量获取
            self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
            self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
            self.provider = os.environ.get('LLM_PROVIDER', 'anthropic').lower()
            
        # 初始化客户端
        self.client = None
        if self.provider == 'anthropic':
            if model_config and self.api_key and ANTHROPIC_AVAILABLE:
                self.client = Anthropic(api_key=self.api_key)
                self.logger.info("已使用模型配置初始化Anthropic API客户端")
            elif self.anthropic_api_key and ANTHROPIC_AVAILABLE:
                self.client = Anthropic(api_key=self.anthropic_api_key)
                self.logger.info("已使用环境变量初始化Anthropic API客户端")
            else:
                self.logger.warning("未能初始化Anthropic客户端，API密钥未配置或缺少anthropic库")
        elif self.provider == 'deepseek':
            if model_config and self.api_key:
                self.deepseek_api_key = self.api_key
                self.deepseek_api_url = f"{self.api_base}/v1/chat/completions"
                self.logger.info("已使用模型配置初始化DeepSeek API客户端")
            elif self.deepseek_api_key:
                self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
                self.logger.info("已使用环境变量初始化DeepSeek API客户端")
            else:
                self.logger.warning("未能初始化DeepSeek客户端，API密钥未配置")
        else:
            self.logger.warning(f"不支持的模型提供商: {self.provider}")
    
    def _generate_system_message(self, metadata, sample_data=None):
        """
        生成系统消息，用于指导LLM生成SQL
        
        Args:
            metadata (dict): 数据库元数据
            sample_data (dict, optional): 样本数据
            
        Returns:
            str: 系统消息
        """
        system_message = """你是一个专业的数据库查询助手，能够将自然语言转换为精确的SQL查询。
        
你的主要职责是：
1. 理解用户的自然语言查询意图
2. 根据提供的数据库结构生成符合语法的SQL查询
3. 解释SQL查询的逻辑和预期结果

生成SQL时应遵循以下原则：
- 仅使用SELECT语句进行查询，不执行任何修改数据的操作
- 确保SQL语法正确，考虑表关系和字段类型
- 优先使用表的主键或索引字段进行JOIN和WHERE条件
- 对于复杂查询，添加注释说明查询逻辑
- 必要时使用子查询、GROUP BY、HAVING等高级功能
- 如果存在多种可能的理解，选择最合理的一种并说明原因

输出格式要求：
1. 首先给出生成的SQL语句，使用```sql ```代码块格式
2. 然后解释SQL语句的逻辑和预期结果
3. 如果无法生成SQL或需要更多信息，清晰说明原因

数据库结构信息如下：
"""
        
        # 添加表和字段信息
        if metadata and "tables" in metadata:
            for table in metadata["tables"]:
                table_name = table.get("name", "")
                table_comment = table.get("comment", "")
                
                # 添加表信息
                system_message += f"\n表名: {table_name}"
                if table_comment:
                    system_message += f" (说明: {table_comment})"
                system_message += "\n"
                
                # 添加字段信息
                if "columns" in table and table["columns"]:
                    system_message += "字段:\n"
                    for column in table["columns"]:
                        col_name = column.get("name", "")
                        col_type = column.get("type", "")
                        col_comment = column.get("comment", "")
                        is_pk = "是" if column.get("is_primary", False) else "否"
                        nullable = "可空" if column.get("nullable", True) else "非空"
                        
                        system_message += f"- {col_name} ({col_type}, {nullable}, 主键: {is_pk})"
                        if col_comment:
                            system_message += f" 说明: {col_comment}"
                        
                        # 如果有外键信息，添加外键说明
                        if "foreign_key" in column:
                            fk = column["foreign_key"]
                            system_message += f" 外键 -> {fk['table']}.{fk['column']}"
                        
                        system_message += "\n"
                
                system_message += "\n"
        
        # 如果有样本数据，添加样本数据
        if sample_data:
            system_message += "\n部分表的样本数据:\n"
            
            # 限制只显示前几个表的样本数据，避免系统消息过长
            sample_tables = list(sample_data.keys())[:3]
            
            for table_name in sample_tables:
                rows = sample_data.get(table_name, [])
                if not rows:
                    continue
                
                system_message += f"\n表 {table_name} 样本数据:\n"
                
                # 添加表头
                if rows:
                    columns = list(rows[0].keys())
                    system_message += "| " + " | ".join(columns) + " |\n"
                    system_message += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                    
                    # 添加数据行
                    for row in rows:
                        system_message += "| " + " | ".join([str(row.get(col, "")) for col in columns]) + " |\n"
                
                system_message += "\n"
        
        return system_message

    def _call_anthropic_api(self, system, messages, max_tokens=2000, temperature=0.0):
        """
        调用Anthropic Claude API
        
        Args:
            system (str): 系统消息
            messages (list): 消息列表
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            dict: API响应
        """
        if not self.client:
            raise ValueError("未初始化Anthropic客户端")
            
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.content[0].text
    
    def _call_deepseek_api(self, system, messages, max_tokens=2000, temperature=0.0):
        """
        调用DeepSeek API
        
        Args:
            system (str): 系统消息
            messages (list): 消息列表
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            dict: API响应
        """
        if not self.deepseek_api_key:
            raise ValueError("未配置DeepSeek API密钥")
            
        # 格式化消息，包括系统消息
        formatted_messages = [{"role": "system", "content": system}]
        
        # 添加用户和助手的消息
        for message in messages:
            formatted_messages.append(message)
        
        # 准备请求体
        request_body = {
            "model": self.model_name if hasattr(self, 'model_name') and self.model_name else "deepseek-chat",
            "messages": formatted_messages,
            "max_tokens": self.max_tokens if hasattr(self, 'max_tokens') else max_tokens,
            "temperature": self.temperature if hasattr(self, 'temperature') else temperature
        }
        
        # 记录请求信息（不含敏感数据）
        self.logger.info(f"发送请求到DeepSeek API: URL={self.deepseek_api_url}, 模型={request_body['model']}")
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }
        
        response = requests.post(self.deepseek_api_url, headers=headers, json=request_body)
        
        # 检查响应
        if response.status_code != 200:
            error_msg = f"DeepSeek API请求失败: HTTP {response.status_code}, {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        response_data = response.json()
        if "choices" not in response_data or len(response_data["choices"]) == 0:
            error_msg = "DeepSeek API响应格式错误"
            self.logger.error(f"{error_msg}: {response_data}")
            raise Exception(error_msg)
            
        return response_data["choices"][0]["message"]["content"]
        
    def _call_llm_api(self, system, messages, max_tokens=2000, temperature=0.0):
        """
        根据配置调用相应的LLM API
        
        Args:
            system (str): 系统消息
            messages (list): 消息列表
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            str: 模型返回的文本
        """
        if self.provider == 'anthropic' and self.client:
            return self._call_anthropic_api(system, messages, max_tokens, temperature)
        elif self.provider == 'deepseek' and self.deepseek_api_key:
            return self._call_deepseek_api(system, messages, max_tokens, temperature)
        else:
            # 模拟LLM响应（用于开发测试）
            return """我已分析您的查询，为您生成以下SQL：

```sql
SELECT * FROM users WHERE is_active = 1 LIMIT 1000;
```

这个查询将从users表中检索所有活跃用户的信息，并限制返回1000条记录。"""

    def natural_language_to_sql(self, query, metadata, sample_data=None, conversation_history=None):
        """
        将自然语言转换为SQL查询
        
        Args:
            query (str): 用户的自然语言查询
            metadata (dict): 数据库元数据
            sample_data (dict, optional): 样本数据
            conversation_history (list, optional): 对话历史
            
        Returns:
            dict: 包含生成的SQL和解释的字典
        """
        try:
            # 测试模式：如果未配置API密钥，使用模拟数据
            if (self.provider == 'anthropic' and not self.anthropic_api_key) or \
               (self.provider == 'deepseek' and not self.deepseek_api_key):
                self.logger.warning("使用模拟LLM响应（未配置API密钥）")
                # 模拟响应，仅用于开发测试
                mock_response = f"""根据您的查询"{query}"，我生成了以下SQL：

```sql
SELECT category_id, COUNT(*) as total_users
FROM products
WHERE category_id = 1;
```

这个SQL查询从products表中筛选出category_id为1的产品，并统计总数。"""
                
                # 提取SQL语句
                sql_block_pattern = r'```sql\s+(.*?)\s+```'
                sql_blocks = re.findall(sql_block_pattern, mock_response, re.DOTALL)
                sql = sql_blocks[0].strip() if sql_blocks else None
                
                return {
                    "sql": sql,
                    "explanation": mock_response
                }
            
            # 生成系统消息
            system_message = self._generate_system_message(metadata, sample_data)
            
            # 准备消息历史
            messages = []
            
            # 添加对话历史（如果有）
            if conversation_history:
                for message in conversation_history:
                    role = "user" if message.get("role") == "user" else "assistant"
                    content = message.get("content", "")
                    messages.append({"role": role, "content": content})
            
            # 添加当前查询
            messages.append({"role": "user", "content": query})
            
            # 调用LLM API
            content = self._call_llm_api(system_message, messages, 2000, 0.0)
            
            # 提取SQL语句（查找第一个SQL代码块）
            sql = None
            explanation = content
            
            # 查找```sql```代码块
            sql_block_pattern = r'```sql\s+(.*?)\s+```'
            sql_blocks = re.findall(sql_block_pattern, content, re.DOTALL)
            
            if sql_blocks:
                sql = sql_blocks[0].strip()
            
            return {
                "sql": sql,
                "explanation": explanation
            }
            
        except Exception as e:
            self.logger.error(f"LLM处理失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "error": f"LLM处理失败: {str(e)}",
                "sql": None,
                "explanation": None
            }
    
    def generate_system_message(self, task="nlsql", db_type="mysql"):
        """
        生成适合任务的系统消息
        
        Args:
            task (str): 任务类型，支持 nlsql (自然语言到SQL转换) 或 explain (SQL结果解释)
            db_type (str): 数据库类型，支持 mysql, postgresql
            
        Returns:
            str: 系统消息
        """
        if task == "nlsql":
            return f"""你是一个专业的数据库工程师，精通SQL语言。你的任务是将用户的自然语言查询转换为高质量的SQL语句。
请遵循以下规则：
1. 只生成{db_type.upper()}兼容的SQL查询语句
2. 使用最优的查询方式，包括适当的索引和JOIN操作
3. 添加适当的条件限制，避免返回过多结果
4. 对生成的SQL添加中文注释解释语句的主要部分
5. 如果用户没有指定查询行数限制，默认添加LIMIT 1000来保护系统
6. 尽可能使用中文回复用户
7. 你的响应应包含：对用户查询的理解、生成的SQL、SQL的解释

请使用markdown格式组织你的回复：
1. 先用一句话概述用户要查询的内容
2. 使用SQL代码块提供SQL查询（带注释）
3. 解释SQL查询的关键部分和工作原理
4. 如果用户的查询不明确，请说明你做了哪些假设
"""
        elif task == "explain":
            return f"""你是一个专业的数据分析师，擅长解释SQL查询结果。你的任务是分析SQL查询结果，并以用户易懂的语言解释这些结果。
请遵循以下规则：
1. 解释{db_type.upper()}查询的结果含义
2. 总结结果中的关键信息和模式
3. 指出数据中的任何有趣的趋势、异常值或关系
4. 如果结果有统计信息，解释这些数值的含义
5. 使用清晰简洁的语言，避免技术术语
6. 如果结果为空，解释可能的原因
7. 尽可能使用中文回复用户

请使用markdown格式组织你的回复：
1. 先用一句话概述查询返回的主要内容
2. 列出关键发现和重要数据点
3. 如果适用，提供对数据的深入分析
4. 如果有统计信息，解释这些统计数据的意义
"""
        else:
            return "你是一个专业的数据库助手，请帮助用户解决数据库相关问题。"

    def chat_completion(self, messages, model=None):
        """
        处理通用对话，调用LLM API生成回复
        
        Args:
            messages (list): 消息列表，格式为[{"role": "user", "content": "消息内容"}, ...]
            model (str, optional): 模型名称，如果为None则使用默认模型
            
        Returns:
            dict: 包含回复内容的字典
        """
        try:
            # 系统提示，引导模型生成有帮助的回复
            system_message = """你是问数智能体，一个专业的数据库助手。
            
你具备以下能力和特点：
1. 擅长解释数据库概念、SQL查询和数据分析方法
2. 能够提供友好、准确和有帮助的回答
3. 使用清晰易懂的语言解释复杂概念
4. 在必要时提供SQL代码示例和解释
5. 对于不确定的问题，会诚实地表达自己的限制并提供建议

请根据用户的问题提供最相关、最有帮助的回答。如果问题涉及SQL或数据库操作，尽量提供示例和详细解释。
"""
            
            # 如果没有指定模型，使用默认模型
            if not model:
                if self.provider == 'anthropic':
                    model = "claude-3-sonnet-20240229"
                elif self.provider == 'deepseek':
                    model = "deepseek-chat"
            
            # 调用LLM API
            response_text = self._call_llm_api(system_message, messages)
            
            return {
                "content": response_text,
                "error": None
            }
            
        except Exception as e:
            self.logger.error(f"聊天完成请求失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "content": None,
                "error": str(e)
            } 