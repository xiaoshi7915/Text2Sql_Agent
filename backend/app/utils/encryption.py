#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
加密工具
用于密码的加密和解密
"""

import os
import logging
import base64
from flask import current_app
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

# 使用固定密钥，确保重启应用后密码仍可解密
DEFAULT_KEY = b'uLYJeqGYsRcD8Qh8-N-m3ZbqJAaJDDiSN2UYkFcVBYA='

def get_encryption_key():
    """获取或生成加密密钥"""
    key_env = os.getenv('ENCRYPTION_KEY')
    if key_env:
        try:
            return base64.urlsafe_b64decode(key_env.encode())
        except Exception as e:
            logger.warning(f"环境变量中的加密密钥格式无效: {e}")
    
    # 如果没有环境变量，使用固定密钥
    return DEFAULT_KEY

def encrypt_password(password):
    """加密密码"""
    if not password:
        return ''
    
    try:
        key = get_encryption_key()
        cipher_suite = Fernet(key)
        return cipher_suite.encrypt(password.encode()).decode()
    except Exception as e:
        logger.error(f"密码加密失败: {e}")
        # 为了安全起见，加密失败时返回空字符串
        return ''

def decrypt_password(encrypted_password):
    """解密密码"""
    if not encrypted_password:
        return ''
    
    try:
        key = get_encryption_key()
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_password.encode()).decode()
    except InvalidToken:
        logger.error("无效的加密令牌或密钥不匹配")
        # 尝试使用默认密钥解密
        try:
            cipher_suite = Fernet(DEFAULT_KEY)
            return cipher_suite.decrypt(encrypted_password.encode()).decode()
        except Exception as e:
            logger.error(f"备用密钥解密失败: {e}")
            # 对于无法解密的情况，返回数据库默认密码
            logger.warning("解密失败，返回配置的默认密码")
            return os.getenv('DB_PASSWORD', 'admin123456!')
    except Exception as e:
        logger.error(f"密码解密失败: {e}")
        # 对于一般解密失败，返回默认密码
        logger.warning("解密失败，返回配置的默认密码")
        return os.getenv('DB_PASSWORD', 'admin123456!') 