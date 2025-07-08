class ValidationError(Exception):
    def __init__(self, message, field, value):
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self):
        return f"{super().__str__()} (字段: {self.field}, 值: {self.value})"


def validate_user(data):
    if "name" not in data:
        raise ValidationError("缺少必填字段", "name", None)
    if len(data.get("password", "")) < 8:
        raise ValidationError("密码长度不足", "password", data.get("password"))


try:
    user = {"email": "test@example.com", "password": "123"}
    validate_user(user)
except ValidationError as e:
    print(f"验证失败: {e}")
    print(f"问题字段: {e.field}, 当前值: {e.value}")