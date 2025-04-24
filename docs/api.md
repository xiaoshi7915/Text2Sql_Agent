# 问数智能体 API 文档

本文档提供了问数智能体系统的API接口说明，包括认证接口、对话接口、数据源管理接口等。

## API 基本信息

- 基础URL: `http://your-domain.com/api`
- 认证方式: JWT (JSON Web Token)
- 响应格式: JSON
- 编码: UTF-8

## 认证接口

### 用户登录

**请求**:
```
POST /auth/login
```

**请求体**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "your_username",
      "email": "user@example.com",
      "role": "admin",
      "created_at": "2023-01-01T00:00:00Z",
      "last_login": "2023-01-01T00:00:00Z"
    }
  }
}
```

### 刷新令牌

**请求**:
```
POST /auth/refresh
```

**请求头**:
```
Authorization: Bearer {refresh_token}
```

**响应**:
```json
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 注销登录

**请求**:
```
POST /auth/logout
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "注销成功"
}
```

## 用户管理接口

### 获取用户信息

**请求**:
```
GET /users/me
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com",
    "role": "admin",
    "created_at": "2023-01-01T00:00:00Z",
    "last_login": "2023-01-01T00:00:00Z",
    "preferences": {
      "theme": "light",
      "language": "zh_CN"
    }
  }
}
```

### 创建新用户 (仅管理员)

**请求**:
```
POST /users
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "username": "new_user",
  "email": "new_user@example.com",
  "password": "secure_password",
  "role": "user"
}
```

**响应**:
```json
{
  "code": 201,
  "message": "用户创建成功",
  "data": {
    "id": 2,
    "username": "new_user",
    "email": "new_user@example.com",
    "role": "user",
    "created_at": "2023-01-02T00:00:00Z"
  }
}
```

### 获取用户列表 (仅管理员)

**请求**:
```
GET /users?page=1&per_page=10
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "created_at": "2023-01-01T00:00:00Z",
        "last_login": "2023-01-01T00:00:00Z"
      },
      {
        "id": 2,
        "username": "user1",
        "email": "user1@example.com",
        "role": "user",
        "created_at": "2023-01-02T00:00:00Z",
        "last_login": "2023-01-02T00:00:00Z"
      }
    ],
    "total": 2,
    "page": 1,
    "per_page": 10,
    "pages": 1
  }
}
```

## 数据源管理接口

### 获取数据源列表

**请求**:
```
GET /datasources?page=1&per_page=10
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "生产数据库",
        "type": "mysql",
        "host": "mysql.example.com",
        "port": 3306,
        "database": "production",
        "user": "db_user",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "status": "active"
      },
      {
        "id": 2,
        "name": "分析数据仓库",
        "type": "postgresql",
        "host": "postgres.example.com",
        "port": 5432,
        "database": "analytics",
        "user": "db_user",
        "created_at": "2023-01-02T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "status": "active"
      }
    ],
    "total": 2,
    "page": 1,
    "per_page": 10,
    "pages": 1
  }
}
```

### 创建数据源

**请求**:
```
POST /datasources
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "name": "新数据源",
  "type": "mysql",
  "host": "db.example.com",
  "port": 3306,
  "database": "mydb",
  "user": "db_user",
  "password": "db_password",
  "ssl": false,
  "description": "新的数据库连接"
}
```

**响应**:
```json
{
  "code": 201,
  "message": "数据源创建成功",
  "data": {
    "id": 3,
    "name": "新数据源",
    "type": "mysql",
    "host": "db.example.com",
    "port": 3306,
    "database": "mydb",
    "user": "db_user",
    "created_at": "2023-01-03T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z",
    "status": "active",
    "description": "新的数据库连接"
  }
}
```

### 测试数据源连接

**请求**:
```
POST /datasources/test-connection
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "type": "mysql",
  "host": "db.example.com",
  "port": 3306,
  "database": "mydb",
  "user": "db_user",
  "password": "db_password",
  "ssl": false
}
```

**响应**:
```json
{
  "code": 200,
  "message": "连接成功",
  "data": {
    "status": "success",
    "connect_time": 0.235
  }
}
```

### 获取数据源元数据

**请求**:
```
GET /datasources/{datasource_id}/metadata
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "tables": [
      {
        "name": "users",
        "comment": "用户表",
        "columns": [
          {
            "name": "id",
            "type": "int",
            "comment": "用户ID",
            "is_primary": true,
            "is_nullable": false
          },
          {
            "name": "username",
            "type": "varchar(50)",
            "comment": "用户名",
            "is_primary": false,
            "is_nullable": false
          },
          {
            "name": "email",
            "type": "varchar(100)",
            "comment": "邮箱",
            "is_primary": false,
            "is_nullable": false
          }
        ],
        "indexes": [
          {
            "name": "idx_username",
            "columns": ["username"],
            "unique": true
          }
        ]
      },
      {
        "name": "orders",
        "comment": "订单表",
        "columns": [
          {
            "name": "id",
            "type": "int",
            "comment": "订单ID",
            "is_primary": true,
            "is_nullable": false
          },
          {
            "name": "user_id",
            "type": "int",
            "comment": "用户ID",
            "is_primary": false,
            "is_nullable": false
          },
          {
            "name": "created_at",
            "type": "datetime",
            "comment": "创建时间",
            "is_primary": false,
            "is_nullable": false
          }
        ],
        "indexes": [
          {
            "name": "idx_user_id",
            "columns": ["user_id"],
            "unique": false
          }
        ]
      }
    ]
  }
}
```

## 对话接口

### 创建新对话

**请求**:
```
POST /conversations
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "title": "新对话",
  "datasource_id": 1
}
```

**响应**:
```json
{
  "code": 201,
  "message": "对话创建成功",
  "data": {
    "id": "conv_123456789",
    "title": "新对话",
    "datasource_id": 1,
    "created_at": "2023-01-03T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z",
    "user_id": 1
  }
}
```

### 发送消息

**请求**:
```
POST /conversations/{conversation_id}/messages
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "content": "查询最近7天的订单数量"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "消息发送成功",
  "data": {
    "id": "msg_123456789",
    "conversation_id": "conv_123456789",
    "role": "user",
    "content": "查询最近7天的订单数量",
    "created_at": "2023-01-03T00:00:05Z"
  }
}
```

### 获取AI响应

**请求**:
```
GET /conversations/{conversation_id}/messages?after=msg_123456789
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "messages": [
      {
        "id": "msg_987654321",
        "conversation_id": "conv_123456789",
        "role": "assistant",
        "content": "根据您的需求，我已生成以下SQL查询来获取最近7天的订单数量：\n\n```sql\nSELECT DATE(created_at) as date, COUNT(*) as order_count\nFROM orders\nWHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)\nGROUP BY DATE(created_at)\nORDER BY date DESC;\n```\n\n执行结果如下：\n\n| date | order_count |\n|------|-------------|\n| 2023-01-02 | 125 |\n| 2023-01-01 | 118 |\n| 2022-12-31 | 132 |\n| 2022-12-30 | 95 |\n| 2022-12-29 | 105 |\n| 2022-12-28 | 110 |\n| 2022-12-27 | 98 |\n\n最近7天的总订单数为783个，日均订单量约为112个。",
        "sql": "SELECT DATE(created_at) as date, COUNT(*) as order_count\nFROM orders\nWHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)\nGROUP BY DATE(created_at)\nORDER BY date DESC;",
        "created_at": "2023-01-03T00:00:07Z",
        "query_result": {
          "columns": ["date", "order_count"],
          "rows": [
            ["2023-01-02", 125],
            ["2023-01-01", 118],
            ["2022-12-31", 132],
            ["2022-12-30", 95],
            ["2022-12-29", 105],
            ["2022-12-28", 110],
            ["2022-12-27", 98]
          ]
        }
      }
    ]
  }
}
```

### 获取对话列表

**请求**:
```
GET /conversations?page=1&per_page=10
```

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [
      {
        "id": "conv_123456789",
        "title": "销售数据分析",
        "datasource_id": 1,
        "created_at": "2023-01-03T00:00:00Z",
        "updated_at": "2023-01-03T00:10:00Z",
        "last_message": "查询最近7天的订单数量",
        "message_count": 6
      },
      {
        "id": "conv_987654321",
        "title": "用户增长分析",
        "datasource_id": 2,
        "created_at": "2023-01-02T00:00:00Z",
        "updated_at": "2023-01-02T00:30:00Z",
        "last_message": "计算上月新增用户转化率",
        "message_count": 8
      }
    ],
    "total": 2,
    "page": 1,
    "per_page": 10,
    "pages": 1
  }
}
```

## SQL执行接口

### 执行SQL查询

**请求**:
```
POST /datasources/{datasource_id}/query
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "sql": "SELECT DATE(created_at) as date, COUNT(*) as order_count FROM orders WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY DATE(created_at) ORDER BY date DESC;",
  "max_rows": 1000
}
```

**响应**:
```json
{
  "code": 200,
  "message": "查询执行成功",
  "data": {
    "columns": ["date", "order_count"],
    "rows": [
      ["2023-01-02", 125],
      ["2023-01-01", 118],
      ["2022-12-31", 132],
      ["2022-12-30", 95],
      ["2022-12-29", 105],
      ["2022-12-28", 110],
      ["2022-12-27", 98]
    ],
    "query_time": 0.1234,
    "row_count": 7,
    "truncated": false
  }
}
```

### 校验SQL安全性

**请求**:
```
POST /datasources/{datasource_id}/validate-sql
```

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "sql": "SELECT * FROM users WHERE id = 1;"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "SQL验证通过",
  "data": {
    "valid": true,
    "readonly": true,
    "tables": ["users"],
    "warnings": [
      "SELECT * 使用了所有列，建议指定具体需要的列名"
    ]
  }
}
```

## 错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 请求参数验证失败 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

## 通用响应格式

成功响应:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    // 具体数据
  }
}
```

错误响应:
```json
{
  "code": 400,
  "message": "请求参数错误",
  "errors": {
    "field_name": ["错误描述1", "错误描述2"]
  }
}
```

## API版本管理

API版本通过URL路径前缀进行管理，例如:
- `/api/v1/users` - API v1版本
- `/api/v2/users` - API v2版本

当前文档描述的是v1版本的API。 