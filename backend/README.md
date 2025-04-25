# 问数MCP后端系统

## MySQL连接修复工具

### 背景

在使用MySQL 8.0+版本的过程中，可能会遇到以下连接问题：

1. **认证插件问题**：MySQL 8.0+默认使用`caching_sha2_password`作为认证插件，该插件需要SSL连接支持，否则会出现"Authentication plugin 'caching_sha2_password' reported error: Authentication requires secure connection"错误。

2. **密码解密失败**：尝试连接数据库时可能会出现"密码解密失败"的错误，这通常是由于连接参数配置问题导致的。

为解决上述问题，我们开发了MySQL连接修复工具（`fix_mysql_connection.py`），用于自动检测并修复这些连接问题。

### 准备工作

使用该工具前，请确保已安装以下Python依赖：

```bash
pip install mysql-connector-python flask
```

### 使用方法

工具位于`/opt/wenshu-mcp/backend/fix_mysql_connection.py`，可以通过以下命令运行：

```bash
python fix_mysql_connection.py [选项]
```

#### 命令选项

- `--fix-auth`：修复认证插件问题（默认启用）
- `--no-fix-auth`：不修复认证插件问题
- `--enable-ssl`：启用SSL连接（默认启用）
- `--no-enable-ssl`：不启用SSL连接
- `--root-user ROOT_USER`：MySQL root用户名（修改认证插件时必需）
- `--root-password ROOT_PASSWORD`：MySQL root密码（修改认证插件时必需）
- `--ca-file CA_FILE`：SSL CA证书文件路径（可选）
- `--no-verify`：不验证SSL证书（可选）

#### 使用示例

1. 仅启用SSL连接（不修复认证插件）：

```bash
python fix_mysql_connection.py --no-fix-auth --enable-ssl
```

2. 修复认证插件并启用SSL连接：

```bash
python fix_mysql_connection.py --fix-auth --enable-ssl --root-user=root --root-password=your_password
```

3. 使用自定义CA证书启用SSL连接：

```bash
python fix_mysql_connection.py --enable-ssl --ca-file=/path/to/ca.pem
```

### 执行过程

当运行该工具时，它会按照以下步骤执行：

1. **扫描数据源**：扫描`app/datasources`目录下的所有JSON文件，找出所有MySQL类型的数据源。
2. **测试连接**：对每个数据源尝试建立连接，检测是否存在认证插件或SSL连接问题。
3. **执行修复**：根据命令行参数，执行以下修复操作：
   - 如果启用了`--fix-auth`，会将用户的认证插件从`caching_sha2_password`更改为`mysql_native_password`
   - 如果启用了`--enable-ssl`，会更新数据源配置，启用SSL连接
4. **生成日志**：所有操作都会记录到日志文件中，格式为`mysql_fix_YYYYMMDD_HHMMSS.log`

### 重要说明

1. **权限要求**：修复认证插件需要MySQL root账户权限。
2. **应用重启**：修复完成后，可能需要重启应用才能使修改生效。
3. **日志查看**：执行过程中的所有操作都会记录到日志文件，可用于问题排查。
4. **备份建议**：在执行修复前，建议备份数据源配置文件。

### 常见问题

1. **认证插件修改失败**：
   - 检查root用户的权限是否足够
   - 确认数据库用户存在且密码正确
   - 检查日志文件以获取更详细的错误信息

2. **SSL连接问题**：
   - 确认MySQL服务器支持SSL连接
   - 如果使用了自定义CA证书，确保证书路径正确
   - 如果遇到证书验证问题，可以尝试使用`--no-verify`选项

## MySQL连接问题修复工具

### 背景说明

在使用MySQL 8.0及以上版本时，可能会遇到以下连接问题：

1. **认证插件问题**：MySQL 8.0+默认使用`caching_sha2_password`认证插件，该插件要求SSL连接。如果未配置SSL连接，可能会出现以下错误：
   ```
   Authentication plugin 'caching_sha2_password' reported error: Authentication requires secure connection.
   ```

2. **密码解密失败**：在连接过程中，如果密码解密失败，可能会导致连接失败。

### 修复工具说明

`fix_mysql_connection.py`脚本提供了两种解决方案：

1. **认证插件修改**：将MySQL用户的认证插件从`caching_sha2_password`更改为`mysql_native_password`，后者不要求SSL连接。
2. **启用SSL连接**：为数据源配置SSL连接，满足`caching_sha2_password`认证插件的要求。

### 准备工作

1. 确保已安装必要的Python依赖：
   ```bash
   pip install mysql-connector-python flask
   ```

2. 确保有MySQL的root用户权限（如需修改认证插件）。

### 使用方法

脚本位于`/opt/wenshu-mcp/backend/fix_mysql_connection.py`，使用以下命令运行：

```bash
python fix_mysql_connection.py [选项]
```

#### 命令选项

- `--fix-auth`: 修复认证插件问题（默认：启用）
- `--enable-ssl`: 启用SSL连接（默认：启用）
- `--root-user`: MySQL root用户名（修改认证插件时必需）
- `--root-password`: MySQL root密码（修改认证插件时必需）
- `--ca-file`: SSL CA证书文件路径
- `--no-verify`: 不验证SSL证书
- `--no-fix-auth`: 不修复认证插件问题
- `--no-enable-ssl`: 不启用SSL连接

#### 使用示例

1. 同时修复认证插件和启用SSL：
   ```bash
   python fix_mysql_connection.py --root-user=root --root-password=password
   ```

2. 仅修复认证插件，不启用SSL：
   ```bash
   python fix_mysql_connection.py --root-user=root --root-password=password --no-enable-ssl
   ```

3. 仅启用SSL连接，不修复认证插件：
   ```bash
   python fix_mysql_connection.py --no-fix-auth --enable-ssl
   ```

4. 指定SSL CA证书文件：
   ```bash
   python fix_mysql_connection.py --enable-ssl --ca-file=/path/to/ca-cert.pem
   ```

### 执行过程

脚本执行流程如下：

1. **扫描数据源**：脚本会自动扫描`app/datasources`目录下的所有MySQL类型数据源配置。
2. **测试连接**：对每个数据源进行连接测试，判断是否存在连接问题。
3. **执行修复**：根据测试结果和命令选项，分别执行认证插件修改或SSL配置更新。
4. **生成日志**：修复过程的详细日志保存在当前目录下，格式为`mysql_fix_YYYYMMDD_HHMMSS.log`。

### 重要说明

1. **权限要求**：修改认证插件需要MySQL root用户权限。
2. **应用重启**：修复完成后，建议重启应用以应用新的连接配置。
3. **日志文件**：工具会生成详细的执行日志，便于排查问题。
4. **备份建议**：执行修复前，建议备份数据源配置文件。

### 常见问题

1. **认证插件修改失败**：
   - 确保提供的root用户有足够权限修改用户认证方式
   - 检查数据库用户是否存在
   - 确认root用户的密码正确

2. **SSL连接问题**：
   - 确保MySQL服务器开启了SSL支持
   - 如使用SSL证书验证，确保提供了正确的CA证书文件
   - 如遇证书验证问题，可使用`--no-verify`选项

3. **配置更新失败**：
   - 检查数据源配置文件权限
   - 确保数据源ID与配置文件名称一致
   - 确认JSON格式正确

## MySQL连接问题修复工具

### 背景

在MySQL 8.0及以上版本中，可能会出现以下连接问题：

1. **认证插件问题**：MySQL 8.0+默认使用`caching_sha2_password`认证插件，该插件通常要求使用SSL连接。当应用程序尝试使用非SSL连接时，会出现以下错误：
   ```
   Authentication plugin 'caching_sha2_password' reported error: Authentication requires secure connection.
   ```

2. **密码解密失败**：有时在连接过程中可能出现密码解密失败的情况，导致连接无法建立。错误日志可能显示：
   ```
   密码解密失败: [具体错误信息]
   ```

`fix_mysql_connection.py`脚本提供了两种解决方案：

- 将用户认证插件从`caching_sha2_password`更改为`mysql_native_password`
- 为应用程序启用SSL连接，以满足`caching_sha2_password`插件的要求

### 准备工作

1. 安装必要的Python依赖：
   ```bash
   pip install mysql-connector-python
   ```

2. 确保有MySQL的root用户权限（如需修改认证插件）

### 使用说明

#### 命令参数

```bash
python fix_mysql_connection.py [选项]
```

**选项说明：**

- `--fix-auth`：修复认证插件问题（默认：启用）
- `--enable-ssl`：启用SSL连接（默认：启用）
- `--root-user 用户名`：MySQL root用户名（用于修改认证插件）
- `--root-password 密码`：MySQL root密码（用于修改认证插件）
- `--ca-file 文件路径`：SSL CA证书文件路径
- `--no-verify`：不验证SSL证书
- `--no-fix-auth`：不修复认证插件问题
- `--no-enable-ssl`：不启用SSL连接

#### 使用示例

1. 同时修复认证插件和启用SSL：
   ```bash
   python fix_mysql_connection.py --root-user=root --root-password=your_password
   ```

2. 仅启用SSL连接，不修改认证插件：
   ```bash
   python fix_mysql_connection.py --no-fix-auth
   ```

3. 仅修改认证插件，不启用SSL：
   ```bash
   python fix_mysql_connection.py --no-enable-ssl --root-user=root --root-password=your_password
   ```

4. 使用自定义CA证书并禁用证书验证：
   ```bash
   python fix_mysql_connection.py --ca-file=/path/to/ca.pem --no-verify
   ```

### 执行流程

脚本执行过程如下：

1. **扫描数据源**：扫描项目中所有MySQL类型的数据源配置。
2. **测试连接**：对每个数据源进行连接测试，检查认证插件和SSL状态。
3. **执行修复**：
   - 如果发现使用`caching_sha2_password`认证插件并启用了修复认证插件选项，则尝试将其更改为`mysql_native_password`
   - 如果SSL未启用并且启用了SSL选项，则更新数据源配置以启用SSL连接
4. **生成日志**：在当前目录生成带有时间戳的日志文件，记录修复过程和结果。

### 注意事项

1. **权限要求**：修改认证插件需要MySQL的root权限。
2. **应用重启**：修复完成后，建议重启应用程序以应用新的连接配置。
3. **日志文件**：脚本会生成详细的日志文件（`mysql_fix_YYYYMMDD_HHMMSS.log`），记录所有执行步骤和结果。
4. **备份建议**：在执行修复前，建议备份数据库和应用配置。

### 常见问题

1. **无法修改认证插件**：确保提供了正确的root用户凭据，并且该用户具有修改其他用户权限的能力。
2. **SSL连接问题**：如果启用SSL后仍然出现连接问题，可以尝试使用`--no-verify`选项禁用证书验证。
3. **配置更新失败**：检查应用程序对配置文件的写入权限，确保文件路径正确。

## MySQL连接修复工具

### 背景
在使用MySQL 8.0+版本作为数据源时，可能会遇到以下连接问题：
1. **认证插件问题**：MySQL 8.0+默认使用`caching_sha2_password`作为认证插件，而不是之前版本的`mysql_native_password`，这可能导致某些客户端无法连接。
2. **SSL连接要求**：`caching_sha2_password`认证插件通常要求使用SSL连接进行安全通信。
3. **密码解密失败**：如果未正确配置SSL或认证方式不匹配，可能导致密码解密失败。

### 准备工作
使用修复工具前，请确保安装了必要的Python依赖：
```bash
pip install mysql-connector-python flask
```

### 工具使用
位置: `/opt/wenshu-mcp/backend/fix_mysql_connection.py`

#### 命令选项
```bash
python fix_mysql_connection.py [选项]
```

选项说明:
- `--fix-auth`: 修复认证插件问题（默认启用）
- `--no-fix-auth`: 不修复认证插件问题
- `--enable-ssl`: 启用SSL连接（默认启用）
- `--no-enable-ssl`: 不启用SSL连接
- `--root-user ROOT_USER`: MySQL root用户名（修改认证插件时必需）
- `--root-password ROOT_PASSWORD`: MySQL root密码（修改认证插件时必需）
- `--ca-file CA_FILE`: SSL CA证书文件路径
- `--no-verify`: 不验证SSL证书

#### 使用示例
1. 修复认证插件并配置SSL（需要root权限）：
   ```bash
   python fix_mysql_connection.py --root-user root --root-password yourpassword
   ```

2. 仅配置SSL连接，不修改认证插件：
   ```bash
   python fix_mysql_connection.py --no-fix-auth --enable-ssl --ca-file /path/to/ca.pem
   ```

3. 仅修复认证插件，不配置SSL：
   ```bash
   python fix_mysql_connection.py --fix-auth --no-enable-ssl --root-user root --root-password yourpassword
   ```

### 执行过程
工具执行时会按照以下步骤进行：

1. **扫描数据源**：自动扫描项目中的MySQL数据源配置文件。
2. **测试连接**：对每个数据源进行连接测试，检测是否存在问题。
3. **修复认证插件**：如果检测到使用`caching_sha2_password`认证插件，将其修改为`mysql_native_password`（需要root权限）。
4. **配置SSL**：如果启用了SSL选项，将在数据源配置中添加SSL相关参数。
5. **验证修复**：修复后重新测试连接，确认问题是否解决。
6. **生成日志**：整个过程的详细日志将保存在脚本执行目录下，文件名格式为`mysql_fix_yyyyMMdd_HHmmss.log`。

### 重要提示
1. **权限要求**：修改认证插件需要MySQL root（或具有同等权限的用户）权限。
2. **应用重启**：修改数据源配置后，需要重启应用才能使更改生效。
3. **查看日志**：执行完成后，请查看生成的日志文件了解详细的执行结果和可能存在的问题。
4. **备份建议**：工具会在修改数据源配置前自动创建备份文件（.bak后缀），但仍建议手动备份重要配置文件。

### 常见问题
**问题1: 修改认证插件是否会影响现有应用？**  
答: 通常不会。修改认证插件仅改变用户的验证方式，不会影响权限和数据。但在特殊情况下，可能需要重新配置用户密码。

**问题2: 启用SSL连接后无法连接，怎么办？**  
答: 可能是SSL证书路径错误或证书无效。尝试使用`--no-verify`选项禁用证书验证，或确保提供了正确的CA证书路径。 