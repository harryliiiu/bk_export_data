# 前置条件

```
1. 环境需要安装python3
2. 安装pip3软件
3. 需要先安装pip包，参考下面安装步骤
4. 建议其他服务器运行脚本，需能访问蓝鲸域名
```

# pip包安装

```
cd pkg/
pip3 install et_xmlfile-1.1.0-py3-none-any.whl 
pip3 install openpyxl-3.0.7-py2.py3-none-any.whl
```

# 执行前修改配置
# config.py可修改统计时间、邮箱配置
```
# 蓝鲸url，
# 开发者中心，S-mart应用，随便点击一个应用，填入应用ID，比如bk_monitorv3
# 填入应用TOKEN，比如62aaaaaa5-8c6f-4bae-a1e7-f0bbbbbb4e371

# vim config.py
"BK_URL": "http://xxx.canway.xxx:8082",
"BK_APP_CODE": "",
"BK_APP_SECRET": "",
"BK_TOKEN": "admin",
邮箱接收者：mail_config
```
# 监控数据统计时间
```
统计开始时间 staticstical_day_start
统计结束时间 staticstical_day_end
```
# 告警数据统计时间
```
告警统计开始时间 staticstical_day_start_8
告警统计结束时间 staticstical_day_end_8
```

# 运行命令

```
python3 export_data.py
```

# 报表及日志位置
```
1. 报表生成位置：host_export/export，脚本当前执行时间命名
2. 日志生成位置：host_export/logs/host_export.log
```

