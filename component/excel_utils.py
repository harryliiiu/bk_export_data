import datetime
import time

from component.net_utils import do_post_cpu, do_post_max_app_mem_time, do_post_mem, do_post_disk, do_post_max_cpu_time, \
    do_post_io, do_post_net, do_post_max_mem_time, do_post_max_speed_time, do_post_net_send, \
    do_post_max_speed_send_time, do_post_application_mem, get_agent_status, list_biz_hosts, get_set_name_by_ip, \
    get_biz_map_id_name
# from test.test_data import test_datas
from component.net_utils import do_post_abnormal_event, biz_map_id_name, get_biz_name_by_id, get_host_name_by_ip
from openpyxl.styles import Alignment, Font

align = Alignment(horizontal='left', vertical='center', wrap_text=True)


# -------------------------------1、 主机监控 ---------------------------------
def add_new_monitor_sheet(wb):
    '''
    添加主机监控数据
    '''
    work_sheet = wb.active
    work_sheet.title = "主机监控数据统计"
    add_header(work_sheet, ["业务", "集群名", "主机名", "ip", "cpu(峰值)",
                            "cpu(均值)", "物理内存(峰值)", "物理内存(均值)", "应用内存(峰值)", "应用内存(均值)", "/ 容量（峰值）", "/ 容量（均值）",
                            "IO（峰值）", "IO（均值）", "接收带宽（峰值）/Mb", "接收带宽(均值) /Mb",
                            "发送带宽（峰值）/Mb", "发送带宽(均值) /Mb", "备注"])
    for row in work_sheet['A1:U1']:
        for cell in row:
            cell.font = Font(bold=True)
    work_sheet.freeze_panes = 'A2'  # 冻结首行
    append_datas(work_sheet)
    # 设置自动换行
    # colC = work_sheet['A1:A2000']
    # for items in colC:
    #     for item in items:
    #         item.alignment = align
    # 设置宽度
    for i in 'ABCDEFGHIJKLMNOPQRSTU':
        work_sheet.column_dimensions[i].width = 30


def add_new_notify_sheet(wb):
    '''
    添加告警数据
    '''
    abnormal_sheet = wb.create_sheet('告警通知', 1)
    add_header(abnormal_sheet, ["发生时间", "业务", "主机名", "ip",
                                "持续时长", "告警内容", "通知组", "告警等级"])
    for row in abnormal_sheet['A1:U1']:
        for cell in row:
            cell.font = Font(bold=True)
    abnormal_sheet.freeze_panes = 'A2'  # 冻结首行
    append_datas2event(abnormal_sheet)


def add_agent_status_sheet(wb):
    '''
    添加agent数据
    '''
    abnormal_sheet = wb.create_sheet('agent异常', 2)
    add_header(abnormal_sheet, ["业务", "主机名", "ip", "备注"])
    for row in abnormal_sheet['A1:U1']:
        for cell in row:
            cell.font = Font(bold=True)
    abnormal_sheet.freeze_panes = 'A2'  # 冻结首行
    append_agent_status_error(abnormal_sheet)


def add_header(work_sheet, headers):
    '''
    sheet header
    '''
    work_sheet.append(headers)


def append_datas(work_sheet):
    '''
    封装主机监控数据
    '''
    for business in biz_map_id_name:
        biz_id = business['bk_biz_id']
        for data in union_cpu_mem_disk(biz_id):
            # print(data)
            result = [business['bk_biz_name'],  # 业务
                      get_set_name_by_ip(data['ip']),  # 集群名
                      get_host_name_by_ip(data['ip']),  # 主机名
                      data['ip'],  # ip
                      # datetime.datetime.fromtimestamp(data['use_time'] / 1000).strftime("%Y-%m-%d %H:%M:%S") + " " +
                      str(round(data['max_use'], 2)) + "%",  # 最大cpu
                      str(round(data['avg_use'], 2)) + "%",  # 平均cpu
                      # datetime.datetime.fromtimestamp(data['psc_pct_used_time'] / 1000).strftime("%Y-%m-%d %H:%M:%S") + " " +
                      str(round(data['max_psc_pct_used'], 2)) + "%",  # 最大内存
                      str(round(data['avg_psc_pct_used'], 2)) + "%",  # 内存
                      # datetime.datetime.fromtimestamp(data['pct_used_time'] / 1000).strftime("%Y-%m-%d %H:%M:%S") + " " +
                      str(round(data['max_pct_used'], 2)) + "%",  # 应用内存
                      str(round(data['avg_pct_used'], 2)) + "%",  # 应用内存
                      "\n".join([i['mount_point'] + " " + str(round(i['max_in_use'], 2)
                                                              ) + "%" for i in data['mount_points_in_use']]),
                      "\n".join([i['mount_point'] + " " + str(round(i['avg_in_use'], 2)
                                                              ) + "%" for i in data['mount_points_in_use']]),
                      "\n".join([i['device_name'] + " " + str(round(i['max_util']
                                * 100, 2)) + "%" for i in data['mount_points_util']]),
                      "\n".join([i['device_name'] + " " + str(round(i['avg_util']
                                * 100, 2)) + "%" for i in data['mount_points_util']]),
                      # datetime.datetime.fromtimestamp(data['speed_recv_time'] / 1000).strftime("%Y-%m-%d %H:%M:%S") + " " +
                      # 带宽
                      str(round(data['max_speed_recv'] / 1024 / 1024, 2)),
                      # 带宽
                      str(round(data['avg_speed_recv'] / 1024 / 1024, 2)),
                      # datetime.datetime.fromtimestamp(data['speed_sent_time'] / 1000).strftime("%Y-%m-%d %H:%M:%S") + " " +
                      # 带宽
                      str(round(data['max_speed_sent'] / 1024 / 1024, 2)),
                      # 带宽
                      str(round(data['avg_speed_sent'] / 1024 / 1024, 2)),
                      ]
            work_sheet.append(result)


def union_cpu_mem_disk(biz_id):
    '''
    合并cpu, mem, disk数据
    '''
    # 获取cpu数据
    cpu_datas = do_post_cpu(biz_id)['data']['list']
    time.sleep(0.5)
    # 获取内存数据
    mem_datas = do_post_mem(biz_id)['data']['list']
    time.sleep(0.5)
    # 获取应用内存数据
    app_mem_datas = do_post_application_mem(biz_id)['data']['list']
    time.sleep(0.5)
    # 获取磁盘数据
    disk_datas = do_post_disk(biz_id)['data']['list']
    time.sleep(0.5)
    # 获取io数据
    io_datas = do_post_io(biz_id)['data']['list']
    time.sleep(0.5)
    # 获取net数据
    net_datas = do_post_net(biz_id)['data']['list']
    time.sleep(0.5)
    # 获取net_send数据
    net_send_datas = do_post_net_send(biz_id)['data']['list']
    time.sleep(0.5)
    s = set([str(i['ip']) + "_" + str(i['bk_cloud_id']) for i in cpu_datas]) | \
        set([str(i['ip']) + "_" + str(i['bk_cloud_id']) for i in mem_datas]) | \
        set([str(i['ip']) + "_" + str(i['bk_cloud_id']) for i in disk_datas]) | \
        set([str(i['ip']) + "_" + str(i['bk_cloud_id']) for i in io_datas]) | \
        set([str(i['ip']) + "_" + str(i['bk_cloud_id']) for i in net_datas]) | \
        set([str(i['ip']) + "_" + str(i['bk_cloud_id'])
            for i in net_send_datas])
    datas = [
        {
            'ip': i.split('_')[0],
            "bk_cloud_id": i.split('_')[1],
            'mount_points_in_use': [],
            'mount_points_util': []
        }
        for i in s
    ]

    union_all_data(datas, cpu_datas, "use")
    union_all_data(datas, mem_datas, "psc_pct_used")
    union_all_data(datas, app_mem_datas, "pct_used")
    union_all_data(datas, disk_datas, "in_use", True)
    union_all_data(datas, io_datas, "util", True)
    union_all_data(datas, net_datas, "speed_recv")
    union_all_data(datas, net_send_datas, "speed_sent")

    return datas


def union_all_data(ip_datas, datas, column,
                   has_mounted_point=False):
    for data in datas:
        for ip_data in ip_datas:
            if data['ip'] == ip_data['ip'] and int(data['bk_cloud_id']) == int(ip_data['bk_cloud_id']):
                if has_mounted_point and column == "in_use":
                    mounted_data = {
                        'mount_point': data['mount_point'],
                        'avg_' + column: data['avg_' + column],
                        'max_' + column: data['max_' + column],
                        column + '_time': data['time']
                    }
                    ip_data['mount_points_' + column].append(mounted_data)
                    break
                if has_mounted_point and column == "util":
                    mounted_data = {
                        'device_name': data['device_name'],
                        'avg_' + column: data['avg_' + column],
                        'max_' + column: data['max_' + column],
                        column + '_time': data['time']
                    }
                    ip_data['mount_points_' + column].append(mounted_data)
                    break
                ip_data['avg_' + column] = data['avg_' + column]
                ip_data['max_' + column] = data['max_' + column]
                ip_data[column + '_time'] = data['time']


# ------------------------------- 告警---------------------------------
def append_datas2event(work_sheet):
    '''
    告警中心数据
    '''
    datas = do_post_abnormal_event()
    # datas = test_datas
    if not datas['data']:
        return
    for data in datas['data']:
        date_exist = (
            datetime.datetime.now() - datetime.datetime.strptime(data['create_time'], "%Y-%m-%d %H:%M:%S+0800"))
        msg = data['origin_alarm']['anomaly'].get(str(data['level']))[
            'anomaly_message'] if data['origin_alarm']['anomaly'].get(str(data['level'])) else ""
        levels = ["致命", "预警", "提醒"]
        result = [data['create_time'].split('+')[0],
                  get_biz_name_by_id(int(data['bk_biz_id'])),
                  get_host_name_by_ip(
                      data['origin_alarm']['dimension_translation']['bk_target_ip']['value']),
                  data['origin_alarm']['dimension_translation']['bk_target_ip']['value'],
                  format_date(date_exist),
                  msg,
                  " ".join([group['name'] for group in data['origin_config']
                           ["action_list"][0]['notice_group_list']]),
                  levels[data['level'] - 1]]
        work_sheet.append(result)


def format_date(date_exist):
    result = ''
    if str(date_exist.days) != '0':
        result = result + str(date_exist.days) + '天'
    if str(date_exist.seconds // 3600) != '0':
        result = result + str(date_exist.seconds // 3600) + '时'
    if str(((date_exist.seconds // 60) % 60)) != '0':
        result = result + str(((date_exist.seconds // 60) % 60)) + '分'
    if not result:
        result = '1分'
    return result


# ----------------------- 异常agent -----------------------
def append_agent_status_error(work_sheet):
    for business in biz_map_id_name:
        biz_id = business['bk_biz_id']
        for data in list_biz_hosts(biz_id)['data']['info']:
            result = [
                business['bk_biz_name'],  # 业务
                get_host_name_by_ip(data['bk_host_innerip']),
                data['bk_host_innerip'],
                "agent异常,请检查"  # ip
            ]
            if not get_agent_status(data['bk_host_innerip'], data['bk_cloud_id']):
                work_sheet.append(result)
