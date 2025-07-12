# 增强版系统监控工具 - 配置文件说明

## 概述

本工具提供了两个配置文件格式：
- `monitor_config.json` - 标准JSON格式配置文件
- `monitor_config.jsonc` - 带详细注释的JSONC格式配置文件

## 配置文件结构

### 1. 基础监控阈值设置

| 参数名 | 类型 | 默认值 | 说明 | 建议值 |
|--------|------|--------|------|--------|
| `cpu_warning_threshold` | 整数 | 80 | CPU使用率警告阈值（百分比） | 70-90 |
| `memory_warning_threshold` | 整数 | 80 | 内存使用率警告阈值（百分比） | 70-85 |
| `disk_warning_threshold` | 整数 | 90 | 磁盘使用率警告阈值（百分比） | 85-95 |
| `network_speed_warning` | 整数 | 104857600 | 网络速度警告阈值（字节/秒） | 根据带宽调整 |
| `process_cpu_warning` | 整数 | 50 | 进程CPU使用率警告阈值（百分比） | 30-70 |
| `process_memory_warning` | 整数 | 10 | 进程内存使用率警告阈值（百分比） | 5-20 |

### 2. 监控间隔设置

| 参数名 | 类型 | 默认值 | 说明 | 建议值 |
|--------|------|--------|------|--------|
| `monitor_interval` | 整数 | 1 | 监控间隔时间（秒） | 1-5 |

### 3. 日志系统设置

| 参数名 | 类型 | 默认值 | 说明 | 可选值 |
|--------|------|--------|------|--------|
| `log_level` | 字符串 | "INFO" | 日志级别 | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `enable_console_output` | 布尔值 | true | 是否启用控制台日志输出 | true/false |
| `enable_file_output` | 布尔值 | true | 是否启用文件日志输出 | true/false |

#### 日志轮转设置

| 参数名 | 类型 | 默认值 | 说明 | 建议值 |
|--------|------|--------|------|--------|
| `log_rotation.max_size_mb` | 整数 | 10 | 单个日志文件最大大小（MB） | 5-50 |
| `log_rotation.backup_count` | 整数 | 5 | 保留的日志文件备份数量 | 3-10 |

### 4. 警报系统设置

| 参数名 | 类型 | 默认值 | 说明 | 可选值 |
|--------|------|--------|------|--------|
| `alert_settings.enable_email_alerts` | 布尔值 | false | 是否启用邮件警报 | true/false |
| `alert_settings.enable_sound_alerts` | 布尔值 | true | 是否启用声音警报 | true/false |
| `alert_settings.alert_cooldown_seconds` | 整数 | 300 | 警报冷却时间（秒） | 300-1800 |

### 5. 显示设置

| 参数名 | 类型 | 默认值 | 说明 | 可选值 |
|--------|------|--------|------|--------|
| `display_settings.show_per_core_cpu` | 布尔值 | true | 是否显示每个CPU核心的使用率 | true/false |
| `display_settings.show_network_interfaces` | 布尔值 | true | 是否显示网络接口信息 | true/false |
| `display_settings.show_process_details` | 布尔值 | false | 是否显示进程详细信息 | true/false |
| `display_settings.refresh_rate` | 整数 | 1 | 显示刷新率（秒） | 1-5 |

### 6. 数据导出设置

| 参数名 | 类型 | 默认值 | 说明 | 建议值 |
|--------|------|--------|------|--------|
| `data_export.enable_csv_export` | 布尔值 | true | 是否启用CSV数据导出 | true/false |
| `data_export.export_interval` | 整数 | 60 | 导出间隔（秒） | 60-3600 |
| `data_export.csv_directory` | 字符串 | "exports" | 导出目录 | 任意有效目录名 |

## 配置示例

### 高性能服务器配置
```json
{
    "cpu_warning_threshold": 90,
    "memory_warning_threshold": 85,
    "disk_warning_threshold": 95,
    "monitor_interval": 2,
    "log_level": "WARNING",
    "alert_settings": {
        "enable_sound_alerts": true,
        "alert_cooldown_seconds": 600
    }
}
```

### 开发环境配置
```json
{
    "cpu_warning_threshold": 70,
    "memory_warning_threshold": 75,
    "disk_warning_threshold": 85,
    "monitor_interval": 1,
    "log_level": "DEBUG",
    "enable_console_output": true,
    "enable_file_output": false,
    "display_settings": {
        "show_per_core_cpu": true,
        "show_network_interfaces": true,
        "show_process_details": true
    }
}
```

### 生产环境配置
```json
{
    "cpu_warning_threshold": 80,
    "memory_warning_threshold": 80,
    "disk_warning_threshold": 90,
    "monitor_interval": 5,
    "log_level": "INFO",
    "enable_console_output": false,
    "enable_file_output": true,
    "log_rotation": {
        "max_size_mb": 50,
        "backup_count": 10
    },
    "alert_settings": {
        "enable_sound_alerts": false,
        "alert_cooldown_seconds": 1800
    },
    "data_export": {
        "enable_csv_export": true,
        "export_interval": 3600,
        "csv_directory": "monitoring_data"
    }
}
```

## 使用建议

### 1. 首次使用
- 建议保持默认设置
- 观察系统运行情况
- 根据实际需求逐步调整

### 2. 性能调优
- **CPU阈值**：高性能服务器可设置90%，普通服务器建议80%
- **内存阈值**：根据内存大小调整，大内存系统可设置85%
- **磁盘阈值**：重要数据建议90%，临时数据可设置95%

### 3. 日志管理
- **开发环境**：使用DEBUG级别，启用控制台输出
- **测试环境**：使用INFO级别，同时启用文件和控制台输出
- **生产环境**：使用WARNING级别，只启用文件输出

### 4. 警报设置
- **开发环境**：启用声音警报，冷却时间300秒
- **生产环境**：禁用声音警报，冷却时间1800秒
- **高负载环境**：适当提高冷却时间，避免频繁警报

### 5. 数据导出
- **开发环境**：禁用数据导出，减少磁盘占用
- **生产环境**：启用数据导出，定期备份监控数据
- **长期监控**：设置较长的导出间隔，如3600秒

## 注意事项

1. **配置文件格式**：确保JSON格式正确，可以使用在线JSON验证工具检查
2. **权限设置**：确保程序有权限读取配置文件和写入日志目录
3. **路径设置**：使用相对路径或绝对路径，避免路径错误
4. **数值范围**：确保数值在合理范围内，避免设置过小或过大的值
5. **系统兼容性**：某些功能可能在不同操作系统上表现不同

## 故障排除

### 常见问题

1. **配置文件无法加载**
   - 检查JSON格式是否正确
   - 确认文件路径是否正确
   - 检查文件权限

2. **日志文件过大**
   - 调整`log_rotation.max_size_mb`
   - 减少`log_rotation.backup_count`
   - 提高`log_level`级别

3. **警报过于频繁**
   - 增加`alert_cooldown_seconds`
   - 调整监控阈值
   - 禁用不必要的警报

4. **监控数据不准确**
   - 检查`monitor_interval`设置
   - 确认系统权限
   - 查看错误日志

## 版本历史

- **v3.0 (增强版)**：添加了数据导出、日志轮转、显示设置等功能
- **v2.0**：添加了警报系统、声音提醒等功能
- **v1.0**：基础监控功能

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。 