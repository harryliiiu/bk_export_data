import datetime
config = {
    "BK_URL": "http://paas.bkxxx.com/",
    "BK_NOTIFY_URL": "http://paas.bkxxx.com/",
    "BK_APP_CODE": "bk_monitorv3",
    "BK_APP_SECRET": "02e3a356-2230-4ad2-a99a-b372cb36d346",
    "BK_TOKEN": "admin",
    "LOG_PATH_NAME": "logs/host_export.log",
    "BK_BIZ_ID": 2,
}
# 修改邮箱，多个邮箱可用逗号隔开
mail_config = {
    "RECEIVER": "xxx@xxx.com"
}

now = datetime.datetime.now() - datetime.timedelta(days=1)
staticstical_day_start_8 = now.strftime('%Y-%m-%d 00:00:00')
staticstical_day_end_8 = now.strftime('%Y-%m-%d 23:59:59')

now_utc = datetime.datetime.strptime(
    staticstical_day_start_8, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
staticstical_day_start = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
staticstical_day_end = (now_utc + datetime.timedelta(days=1)
                        ).strftime('%Y-%m-%dT%H:%M:%SZ')
