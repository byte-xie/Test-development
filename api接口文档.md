# API接口文档

---

## 1. 用户相关 /api/v1/users

### 1.1 获取所有用户
- **接口**：`GET /api/v1/users/`
- **权限**：仅超级用户
- **参数**：
  - `skip` (int, 可选)：跳过条数，默认0
  - `limit` (int, 可选)：返回条数，默认100
- **返回**：
  ```json
  {
    "data": [UserPublic, ...],
    "count": int
  }
  ```

### 1.2 创建新用户
- **接口**：`POST /api/v1/users/`
- **权限**：仅超级用户
- **Body参数**（JSON）：
  - `email` (str, 必填)：邮箱
  - `password` (str, 必填)：密码
  - `full_name` (str, 可选)：姓名
  - `is_active` (bool, 可选)：是否激活
  - `is_superuser` (bool, 可选)：是否超级用户
- **返回**：`UserPublic` 用户信息对象

### 1.3 获取当前用户信息
- **接口**：`GET /api/v1/users/me`
- **权限**：已登录用户
- **返回**：`UserPublic` 当前用户信息

### 1.4 更新当前用户信息
- **接口**：`PATCH /api/v1/users/me`
- **权限**：已登录用户
- **Body参数**（JSON）：
  - `email` (str, 可选)：新邮箱
  - `full_name` (str, 可选)：新姓名
- **返回**：`UserPublic` 更新后信息

### 1.5 修改当前用户密码
- **接口**：`PATCH /api/v1/users/me/password`
- **权限**：已登录用户
- **Body参数**（JSON）：
  - `current_password` (str, 必填)：当前密码
  - `new_password` (str, 必填)：新密码
- **返回**：
  ```json
  { "message": "Password updated successfully" }
  ```

### 1.6 删除当前用户
- **接口**：`DELETE /api/v1/users/me`
- **权限**：已登录用户（非超级用户）
- **返回**：
  ```json
  { "message": "User deleted successfully" }
  ```

### 1.7 注册新用户
- **接口**：`POST /api/v1/users/signup`
- **权限**：无需登录
- **Body参数**（JSON）：
  - `email` (str, 必填)：邮箱
  - `password` (str, 必填)：密码
  - `full_name` (str, 可选)：姓名
- **返回**：`UserPublic` 注册后用户信息

### 1.8 通过ID获取用户
- **接口**：`GET /api/v1/users/{user_id}`
- **权限**：已登录用户（仅超级用户可查他人）
- **返回**：`UserPublic` 用户信息

### 1.9 更新指定用户
- **接口**：`PATCH /api/v1/users/{user_id}`
- **权限**：仅超级用户
- **Body参数**（JSON）：同1.2
- **返回**：`UserPublic` 更新后信息

### 1.10 删除指定用户
- **接口**：`DELETE /api/v1/users/{user_id}`
- **权限**：仅超级用户
- **返回**：
  ```json
  { "message": "User deleted successfully" }
  ```

---

## 2. 登录与认证 /api/v1/login

### 2.1 登录获取Token     已完成
- **接口**：`POST /api/v1/login/access-token`
- **权限**：无需登录
- **Form参数**：
  - `username` (str, 必填)：邮箱
  - `password` (str, 必填)：密码
- **返回**：
  ```json
  { "access_token": "..." }
  ```

### 2.2 测试Token有效性   已完成
- **接口**：`POST /api/v1/login/test-token`
- **权限**：已登录用户
- **返回**：`UserPublic` 当前用户信息

### 2.3 发送找回密码邮件
- **接口**：`POST /api/v1/login/password-recovery/{email}`
- **权限**：无需登录
- **路径参数**：
  - `email` (str, 必填)：邮箱
- **返回**：
  ```json
  { "message": "Password recovery email sent" }
  ```

### 2.4 重置密码
- **接口**：`POST /api/v1/login/reset-password/`
- **权限**：无需登录
- **Body参数**（JSON）：
  - `token` (str, 必填)：重置密码token
  - `new_password` (str, 必填)：新密码
- **返回**：
  ```json
  { "message": "Password updated successfully" }
  ```

### 2.5 获取找回密码邮件HTML
- **接口**：`POST /api/v1/login/password-recovery-html-content/{email}`
- **权限**：仅超级用户
- **路径参数**：
  - `email` (str, 必填)：邮箱
- **返回**：HTML内容

---

## 3. 物品管理 /api/v1/items

### 3.1 获取物品列表
- **接口**：`GET /api/v1/items/`
- **权限**：已登录用户
- **参数**：
  - `skip` (int, 可选)：跳过条数
  - `limit` (int, 可选)：返回条数
- **返回**：
  ```json
  {
    "data": [ItemPublic, ...],
    "count": int
  }
  ```

### 3.2 获取单个物品
- **接口**：`GET /api/v1/items/{id}`
- **权限**：已登录用户（仅本人或超级用户）
- **返回**：`ItemPublic` 物品信息

### 3.3 创建物品
- **接口**：`POST /api/v1/items/`
- **权限**：已登录用户
- **Body参数**（JSON）：
  - `name` (str, 必填)：物品名
  - 其他物品相关字段
- **返回**：`ItemPublic` 新建物品信息

### 3.4 更新物品
- **接口**：`PUT /api/v1/items/{id}`
- **权限**：已登录用户（仅本人或超级用户）
- **Body参数**（JSON）：物品可更新字段
- **返回**：`ItemPublic` 更新后信息

### 3.5 删除物品
- **接口**：`DELETE /api/v1/items/{id}`
- **权限**：已登录用户（仅本人或超级用户）
- **返回**：
  ```json
  { "message": "Item deleted successfully" }
  ```

---

## 4. 私有接口 /api/v1/private

### 4.1 创建新用户（私有）
- **接口**：`POST /api/v1/private/users/`
- **权限**：内部使用
- **Body参数**（JSON）：
  - `email` (str, 必填)
  - `password` (str, 必填)
  - `full_name` (str, 必填)
  - `is_verified` (bool, 可选)
- **返回**：`UserPublic` 用户信息

---

## 5. 工具与健康检查 /api/v1/utils

### 5.1 发送测试邮件
- **接口**：`POST /api/v1/utils/test-email/`
- **权限**：仅超级用户
- **Body参数**：
  - `email_to` (str, 必填)：收件人邮箱
- **返回**：
  ```json
  { "message": "Test email sent" }
  ```

### 5.2 健康检查
- **接口**：`GET /api/v1/utils/health-check/`
- **权限**：公开
- **返回**：
  ```json
  true
  ```

---

> 所有接口的详细参数、权限和返回内容如上，具体字段类型和结构可参考后端Swagger文档 `/docs`。 