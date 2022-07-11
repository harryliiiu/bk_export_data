import json
import requests
from config import config, staticstical_day_start, staticstical_day_end, staticstical_day_start_8, \
    staticstical_day_end_8
from component.logger import logger
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger.info("----------- begin -----------")
logger.info("获取主机监控数据接口时间：" + staticstical_day_start +
            " -- " + staticstical_day_end)
logger.info("获取告警数据接口时间：" + staticstical_day_start_8 +
            " -- " + staticstical_day_end_8)


def do_post(uri_path, data, log_info):
    '''
    post请求
    '''
    url = config.get("BK_URL") + uri_path
    resp = requests.post(url, json.dumps(data), verify=False)
    logger.info(log_info + resp.text)
    return json.loads(resp.text)


def get_biz_map_id_name():
    '''
    获取业务map<id, name>接口
    '''
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "bk_supplier_account": "0",
        "fields": [
            "bk_biz_id",
            "bk_biz_name"
        ],
        "page": {
            "start": 0,
            "limit": 200,
            "sort": ""
        }
    }
    return do_post("/api/c/compapi/v2/cc/search_business/", data, "业务接口报文： ")


# 业务map<id,name>

biz_map_id_name = get_biz_map_id_name()['data']['info']
# biz_map_id_name = [
#     {
#         "bk_biz_id": 4,
#         "default": 0,
#         "bk_biz_name": "广东政务服务网电子证照系统"
#     }
# ]


def get_search_inst(limit=10, start=0):
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_supplier_account": "0",
        "bk_username": config.get("BK_TOKEN"),
        "bk_obj_id": "host",
        "page": {"start": start, "limit": limit, "sort": "bk_inst_id"},
    }
    return do_post("/api/c/compapi/v2/cc/search_inst/", data, "主机实例报文： ")


def get_search_inst_names():
    page_size = 200
    datas = []
    data = get_search_inst(limit=200, start=0)['data']
    datas.extend(data['info'])
    instance_count = data["count"]
    if instance_count > page_size:
        for i in range(0, int(instance_count / page_size)):
            data_hosts = get_search_inst(
                page_size, (i + 1) * page_size)['data']['info']
            datas.extend(data_hosts)
    #    print(len(datas))
    #    for i in datas:
    #        if i['bk_host_innerip'] == "172.17.128.45":
    #            print(i['bk_host_name'])
    return datas


map_ip_name = get_search_inst_names()


def get_host_name_by_ip(ip):
    '''
    利用 ip 读取 主机名称
    '''
    for i in map_ip_name:
        if i['bk_host_innerip'] == ip:
            if i['bk_host_name']:
                return i['bk_host_name']


def get_biz_name_by_id(id):
    '''
    利用 id 读取 业务名称
    '''
    for i in biz_map_id_name:
        if i['bk_biz_id'] == id:
            return i['bk_biz_name']


def get_search_inst_topo(biz_id, limit=10, start=0):
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "bk_supplier_account": "0",
        "page": {"start": start, "limit": limit, "sort": "bk_inst_id"},
        "bk_biz_id": biz_id,
        "fields": [
            "bk_host_innerip"
        ]
    }
    return do_post("/api/c/compapi/v2/cc/list_biz_hosts_topo/", data, "实例拓扑报文： ")


def get_search_inst_topos():
    '''
    获取主机实例
    '''
    page_size = 200
    datas = []
    for i in biz_map_id_name:
        data = get_search_inst_topo(i['bk_biz_id'], limit=200, start=0)['data']
        datas.extend(data['info'])
        instance_count = data["count"]
        if instance_count > page_size:
            for j in range(0, int(instance_count / page_size)):
                data_hosts = get_search_inst_topo(
                    i['bk_biz_id'], page_size, (j + 1) * page_size)['data']['info']
                datas.extend(data_hosts)
    return datas


map_ip_set_name = get_search_inst_topos()


def get_set_name_by_ip(ip):
    '''
    利用 ip 读取 集群名称
    '''
    for i in map_ip_set_name:
        if i['host']['bk_host_innerip'] == ip:
            return '/'.join(j['bk_set_name'] for j in i['topo'])


#  ---------------- 获取时间 -------------------------
def do_post_max_cpu_time(biz_id, ip, max_use):
    '''
    获取最大的cpu使用时的时间
    '''
    sql = "Select usage from " + str(
        biz_id) + "_system_cpu_summary where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' and ip='" + ip + "' and usage=" + str(
        max_use)
    return do_post_ts_data(sql)


def do_post_max_mem_time(biz_id, ip, max_psc_pct_used):
    '''
    获取最大的内存使用时的时间
    '''
    sql = "Select psc_pct_used from " + str(
        biz_id) + "_system_mem where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' and ip='" + ip + "' and psc_pct_used=" + str(
        max_psc_pct_used)
    return do_post_ts_data(sql)


def do_post_max_app_mem_time(biz_id, ip, pct_used):
    '''
    获取最大的应用内存使用时的时间
    '''
    sql = "Select pct_used from " + str(
        biz_id) + "_system_mem where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' and ip='" + ip + "' and pct_used=" + str(
        pct_used)
    return do_post_ts_data(sql)


def do_post_max_speed_time(biz_id, ip, max_speed):
    '''
    获取最大的内存使用时的时间
    '''
    sql = "Select speed_recv from " + str(
        biz_id) + "_system_net where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' and ip='" + ip + "' and speed_recv=" + str(
        max_speed)
    return do_post_ts_data(sql)


def do_post_max_speed_send_time(biz_id, ip, max_speed):
    '''
    获取最大的内存使用时的时间
    '''
    sql = "Select speed_sent from " + str(
        biz_id) + "_system_net where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' and ip='" + ip + "' and speed_sent=" + str(
        max_speed)
    return do_post_ts_data(sql)


# ---------------------------  -----------------------
def do_post_cpu(biz_id):
    '''
    获取cpu平均使用，最大使用
    '''
    sql = "Select max(usage) as max_use,avg(usage) as avg_use from " + str(
        biz_id) + "_system_cpu_summary where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, bk_cloud_id, ip"
    return do_post_ts_data(sql)


def do_post_mem(biz_id):
    '''
    获取内存平均使用，最大使用
    '''
    sql = "Select max(psc_pct_used) as max_psc_pct_used,avg(psc_pct_used) as avg_psc_pct_used from " + str(
        biz_id) + "_system_mem where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, bk_cloud_id, ip"
    return do_post_ts_data(sql)


def do_post_application_mem(biz_id):
    '''
    获取应用内存平均使用，最大使用
    '''
    sql = "Select max(pct_used) as max_pct_used,avg(pct_used) as avg_pct_used from " + str(
        biz_id) + "_system_mem where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, bk_cloud_id, ip"
    return do_post_ts_data(sql)


def do_post_disk(biz_id):
    '''
    获取disk平均使用，最大使用
    '''
    sql = "Select max(in_use) as max_in_use,avg(in_use) as avg_in_use from " + str(
        biz_id) + "_system_disk where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, ip, bk_cloud_id, mount_point"
    return do_post_ts_data(sql)


def do_post_io(biz_id):
    '''
    获取io平均使用，最大使用
    '''
    sql = "Select max(util) as max_util,avg(util) as avg_util from " + str(
        biz_id) + "_system_io where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, ip, bk_cloud_id, device_name"
    return do_post_ts_data(sql)


def do_post_net(biz_id):
    '''
    获取net平均使用，最大使用
    '''
    sql = "Select max(speed_recv) as max_speed_recv,avg(speed_recv) as avg_speed_recv from " + str(
        biz_id) + "_system_net where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, bk_cloud_id, ip"
    return do_post_ts_data(sql)


def do_post_net_send(biz_id):
    '''
    获取net平均使用，最大使用
    '''
    sql = "Select max(speed_sent) as max_speed_sent,avg(speed_sent) as avg_speed_sent from " + str(
        biz_id) + "_system_net where time >= '" + staticstical_day_start + "' and time <= '" + staticstical_day_end + "' group by bk_biz_id, bk_cloud_id, ip"
    return do_post_ts_data(sql)


def do_post_ts_data(sql):
    '''
    获取主机监控数据接口
    '''
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "sql": sql
    }
    return do_post("/api/c/compapi/v2/monitor_v3/get_ts_data/", data, "主机监控数据报文： ")


# -------------------------------告警-------------------------

def do_post_abnormal_event():
    '''
    获取告警数据接口
    '''
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "bk_biz_ids": [i['bk_biz_id'] for i in biz_map_id_name],
        "time_range": staticstical_day_start_8 + " -- " + staticstical_day_end_8,
        "conditions": [
            {
                "key": "event_status",
                "value": [
                    "ABNORMAL"
                ]
            }
        ]
    }
    return do_post_notify("/api/c/compapi/v2/monitor_v3/search_event/", data, "告警数据报文： ")


def do_post_notify(uri_path, data, log_info):
    '''
    告警post请求
    '''
    url = config.get("BK_NOTIFY_URL") + uri_path
    resp = requests.post(url, json.dumps(data), verify=False)
    logger.info(log_info + resp.text)
    return json.loads(resp.text)


def get_agent_status(ip, bk_cloud_id):
    """
    获取agent状态
    """
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "bk_supplier_account": "0",
        "hosts": [{"ip": ip, "bk_cloud_id": bk_cloud_id}],
    }
    resp = do_post("/api/c/compapi/v2/gse/get_agent_status/", data, "业务报文： ")
    agent_status = False
    try:
        agent_status = bool(resp.get("data").get(
            str(bk_cloud_id) + ":" + ip).get("bk_agent_alive"))
    except Exception:
        return False
    return agent_status


def list_biz_hosts(id, rules=[]):
    '''
    获取业务下全部主机
    '''
    data = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "bk_supplier_account": "0",
        "page": {"start": 0, "limit": 500, "sort": "bk_host_id"},
        "bk_biz_id": id,
        "fields": ["bk_host_id", "bk_cloud_id", "bk_host_innerip", "bk_os_type", "bk_mac"],
    }
    if rules:
        data["host_property_filter"] = rules
    return do_post("/api/c/compapi/v2/cc/list_biz_hosts/", data, "获取biz_id全部ip：")
