# 问数智能体数据库设计文档

本文档详细说明了问数智能体系统的数据库设计，包括数据表结构、关系图、索引设计等内容。

## 数据库概述

问数智能体系统采用MySQL数据库作为主要的数据存储方案。数据库命名为`wenshu_ai`，字符集采用`utf8mb4`，排序规则为`utf8mb4_unicode_ci`，以支持完整的Unicode字符集和中文存储。

## 数据表设计

### 用户表 (users)

存储系统用户信息。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | INT | - | 否 | AUTO_INCREMENT | 用户ID，主键 |
| username | VARCHAR | 50 | 否 | - | 用户名，唯一 |
| password | VARCHAR | 255 | 否 | - | 密码（加密存储） |
| email | VARCHAR | 100 | 否 | - | 邮箱地址，唯一 |
| role | ENUM | - | 否 | 'user' | 角色：admin/user |
| status | ENUM | - | 否 | 'active' | 状态：active/inactive/locked |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |
| last_login | DATETIME | 是 | NULL | 最后登录时间 |

索引：
- PRIMARY KEY (`id`)
- UNIQUE KEY `idx_username` (`username`)
- UNIQUE KEY `idx_email` (`email`)
- KEY `idx_status` (`status`)

### 用户设置表 (user_settings)

存储用户个性化设置。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| user_id | INT | - | 否 | - | 用户ID，外键 |
| theme | VARCHAR | 20 | 否 | 'light' | 界面主题 |
| language | VARCHAR | 10 | 否 | 'zh_CN' | 界面语言 |
| notification_enabled | TINYINT | 1 | 否 | 1 | 是否启用通知 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

索引：
- PRIMARY KEY (`user_id`)
- FOREIGN KEY `fk_user_settings_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE

### 数据源表 (datasources)

存储连接的数据库信息。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | INT | - | 否 | AUTO_INCREMENT | 数据源ID，主键 |
| user_id | INT | - | 否 | - | 创建者用户ID，外键 |
| name | VARCHAR | 100 | 否 | - | 数据源名称 |
| type | ENUM | - | 否 | - | 类型：mysql/postgresql/oracle/sqlserver |
| host | VARCHAR | 255 | 否 | - | 主机地址 |
| port | INT | - | 否 | - | 端口号 |
| database | VARCHAR | 100 | 否 | - | 数据库名 |
| username | VARCHAR | 100 | 否 | - | 用户名 |
| password | VARCHAR | 255 | 否 | - | 密码（加密存储） |
| ssl_enabled | TINYINT | 1 | 否 | 0 | 是否启用SSL连接 |
| description | TEXT | - | 是 | NULL | 数据源描述 |
| status | ENUM | - | 否 | 'active' | 状态：active/inactive |
| last_connected_at | DATETIME | - | 是 | NULL | 最后连接时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_datasources_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
- KEY `idx_datasource_status` (`status`)
- UNIQUE KEY `idx_user_datasource_name` (`user_id`, `name`)

### 数据源权限表 (datasource_permissions)

存储用户对数据源的访问权限。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | INT | - | 否 | AUTO_INCREMENT | 权限ID，主键 |
| datasource_id | INT | - | 否 | - | 数据源ID，外键 |
| user_id | INT | - | 否 | - | 用户ID，外键 |
| permission | ENUM | - | 否 | - | 权限类型：read/write/admin |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

索引：
- PRIMARY KEY (`id`)
- UNIQUE KEY `idx_datasource_user` (`datasource_id`, `user_id`)
- FOREIGN KEY `fk_permissions_datasource_id` (`datasource_id`) REFERENCES `datasources` (`id`) ON DELETE CASCADE
- FOREIGN KEY `fk_permissions_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE

### 表元数据缓存表 (table_metadata_cache)

缓存数据源中的表结构信息。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | INT | - | 否 | AUTO_INCREMENT | 缓存ID，主键 |
| datasource_id | INT | - | 否 | - | 数据源ID，外键 |
| table_name | VARCHAR | 100 | 否 | - | 表名 |
| table_schema | VARCHAR | 100 | 否 | - | 模式名 |
| table_comment | TEXT | - | 是 | NULL | 表注释 |
| column_metadata | JSON | - | 否 | - | 列元数据（JSON格式） |
| index_metadata | JSON | - | 否 | - | 索引元数据（JSON格式） |
| row_count_estimate | BIGINT | - | 是 | NULL | 估计行数 |
| last_updated | DATETIME | - | 否 | CURRENT_TIMESTAMP | 最后更新时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

索引：
- PRIMARY KEY (`id`)
- UNIQUE KEY `idx_datasource_table` (`datasource_id`, `table_schema`, `table_name`)
- FOREIGN KEY `fk_metadata_datasource_id` (`datasource_id`) REFERENCES `datasources` (`id`) ON DELETE CASCADE
- KEY `idx_table_last_updated` (`last_updated`)

### 对话表 (conversations)

存储用户与AI的对话会话。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | VARCHAR | 36 | 否 | - | 对话ID，主键（UUID） |
| user_id | INT | - | 否 | - | 用户ID，外键 |
| datasource_id | INT | - | 否 | - | 数据源ID，外键 |
| title | VARCHAR | 200 | 否 | - | 对话标题 |
| description | TEXT | - | 是 | NULL | 对话描述 |
| is_pinned | TINYINT | 1 | 否 | 0 | 是否置顶 |
| status | ENUM | - | 否 | 'active' | 状态：active/archived/deleted |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_conversations_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
- FOREIGN KEY `fk_conversations_datasource_id` (`datasource_id`) REFERENCES `datasources` (`id`) ON DELETE CASCADE
- KEY `idx_conversation_status` (`status`)
- KEY `idx_conversation_user_updated` (`user_id`, `updated_at`)

### 消息表 (messages)

存储对话中的每条消息。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | VARCHAR | 36 | 否 | - | 消息ID，主键（UUID） |
| conversation_id | VARCHAR | 36 | 否 | - | 对话ID，外键 |
| role | ENUM | - | 否 | - | 角色：user/assistant/system |
| content | TEXT | - | 否 | - | 消息内容 |
| sql | TEXT | - | 是 | NULL | SQL查询（当AI生成SQL时） |
| token_count | INT | - | 是 | NULL | 令牌数量 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_messages_conversation_id` (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE
- KEY `idx_messages_created_at` (`created_at`)
- KEY `idx_messages_conversation_created` (`conversation_id`, `created_at`)

### 查询结果表 (query_results)

存储执行的SQL查询结果。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | VARCHAR | 36 | 否 | - | 结果ID，主键（UUID） |
| message_id | VARCHAR | 36 | 否 | - | 消息ID，外键 |
| datasource_id | INT | - | 否 | - | 数据源ID，外键 |
| sql | TEXT | - | 否 | - | 执行的SQL |
| result_data | LONGTEXT | - | 是 | NULL | 查询结果（JSON格式） |
| error_message | TEXT | - | 是 | NULL | 错误信息（如果有） |
| execution_time | DECIMAL | (10,4) | 是 | NULL | 执行时间（秒） |
| row_count | INT | - | 是 | NULL | 结果行数 |
| is_truncated | TINYINT | 1 | 否 | 0 | 结果是否被截断 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_results_message_id` (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE
- FOREIGN KEY `fk_results_datasource_id` (`datasource_id`) REFERENCES `datasources` (`id`) ON DELETE CASCADE
- KEY `idx_query_results_created_at` (`created_at`)

### SQL执行历史表 (sql_execution_history)

记录所有执行的SQL历史。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 历史ID，主键 |
| user_id | INT | - | 否 | - | 用户ID，外键 |
| datasource_id | INT | - | 否 | - | 数据源ID，外键 |
| conversation_id | VARCHAR | 36 | 是 | NULL | 对话ID，外键（可能不关联对话） |
| sql | TEXT | - | 否 | - | 执行的SQL |
| status | ENUM | - | 否 | - | 状态：success/error |
| error_message | TEXT | - | 是 | NULL | 错误信息（如果有） |
| execution_time | DECIMAL | (10,4) | 是 | NULL | 执行时间（秒） |
| row_count | INT | - | 是 | NULL | 结果行数 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| client_ip | VARCHAR | 50 | 是 | NULL | 客户端IP地址 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_history_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
- FOREIGN KEY `fk_history_datasource_id` (`datasource_id`) REFERENCES `datasources` (`id`) ON DELETE CASCADE
- FOREIGN KEY `fk_history_conversation_id` (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE SET NULL
- KEY `idx_sql_history_created_at` (`created_at`)
- KEY `idx_sql_history_user_datasource` (`user_id`, `datasource_id`)

### 标签表 (tags)

用于对话分类的标签。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | INT | - | 否 | AUTO_INCREMENT | 标签ID，主键 |
| user_id | INT | - | 否 | - | 创建者用户ID，外键 |
| name | VARCHAR | 50 | 否 | - | 标签名称 |
| color | VARCHAR | 20 | 否 | '#0078D7' | 标签颜色 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_tags_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
- UNIQUE KEY `idx_user_tag_name` (`user_id`, `name`)

### 对话标签关联表 (conversation_tags)

对话与标签的多对多关系表。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| conversation_id | VARCHAR | 36 | 否 | - | 对话ID，外键 |
| tag_id | INT | - | 否 | - | 标签ID，外键 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

索引：
- PRIMARY KEY (`conversation_id`, `tag_id`)
- FOREIGN KEY `fk_conversation_tags_conversation_id` (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE
- FOREIGN KEY `fk_conversation_tags_tag_id` (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE

### 模板表 (templates)

预设的SQL查询模板。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | INT | - | 否 | AUTO_INCREMENT | 模板ID，主键 |
| user_id | INT | - | 否 | - | 创建者用户ID，外键 |
| title | VARCHAR | 100 | 否 | - | 模板标题 |
| prompt | TEXT | - | 否 | - | 模板提示内容 |
| sql_template | TEXT | - | 否 | - | SQL模板 |
| description | TEXT | - | 是 | NULL | 模板描述 |
| is_public | TINYINT | 1 | 否 | 0 | 是否公开 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_templates_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
- KEY `idx_templates_public` (`is_public`)

### 系统设置表 (system_settings)

存储系统级别的配置。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| key | VARCHAR | 100 | 否 | - | 配置键，主键 |
| value | TEXT | - | 是 | NULL | 配置值 |
| description | TEXT | - | 是 | NULL | 配置说明 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |
| updated_by | INT | - | 是 | NULL | 更新者用户ID |

索引：
- PRIMARY KEY (`key`)
- FOREIGN KEY `fk_settings_updated_by` (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL

### 导出任务表 (export_tasks)

记录导出数据的任务。

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|-------|------|------|-------|-------|------|
| id | VARCHAR | 36 | 否 | - | 任务ID，主键（UUID） |
| user_id | INT | - | 否 | - | 用户ID，外键 |
| task_type | ENUM | - | 否 | - | 任务类型：conversation/query_result |
| related_id | VARCHAR | 36 | 否 | - | 相关资源ID |
| format | ENUM | - | 否 | - | 导出格式：csv/excel/pdf/json |
| status | ENUM | - | 否 | 'pending' | 状态：pending/processing/completed/failed |
| file_path | VARCHAR | 255 | 是 | NULL | 导出文件路径 |
| error_message | TEXT | - | 是 | NULL | 错误信息（如果有） |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |
| completed_at | DATETIME | - | 是 | NULL | 完成时间 |

索引：
- PRIMARY KEY (`id`)
- FOREIGN KEY `fk_export_user_id` (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
- KEY `idx_export_status` (`status`)
- KEY `idx_export_user_created` (`user_id`, `created_at`)

## 数据库关系图

```
users ──────┐
  │         │
  ├─────────┼──────────────┐
  │         │              │
  ▼         ▼              ▼
user_settings datasources  tags
                 │          │
                 │          │
                 ▼          │
       datasource_permissions│
                 │          │
                 │          │
                 ▼          │
        table_metadata_cache│
                 │          │
                 │          │
                 ▼          ▼
            conversations ──┬─► conversation_tags
                 │          │
                 │          │
                 ▼          │
              messages      │
                 │          │
                 │          │
                 ▼          │
           query_results    │
                 │          │
                 │          │
                 ▼          │
        sql_execution_history
```

## 数据库索引策略

1. 所有主键均建立索引
2. 所有外键均建立索引
3. 常用于查询条件的字段建立索引
4. 对于复合查询条件，建立复合索引
5. 对于大文本字段，不建立索引
6. 对于经常更新的字段，谨慎建立索引
7. 对于频繁关联查询的字段，建立索引提高连接性能

## 数据库维护建议

1. 定期进行数据库备份
2. 定期优化数据库表结构和索引
3. 监控查询性能，对慢查询进行优化
4. 设置适当的数据库参数，如连接池大小、缓存大小等
5. 定期清理历史数据，避免数据库过大影响性能
6. 根据业务增长情况，考虑分库分表或读写分离策略

## 敏感数据处理

1. 用户密码使用不可逆加密算法（如bcrypt）存储
2. 数据库连接密码使用可逆加密算法存储，确保系统能够正常连接数据源
3. 权限控制确保用户只能访问被授权的数据源
4. SQL执行记录完整保存，便于审计和问题追踪
5. 数据库备份文件需加密存储 