# _*_ utf-8 _*_
from datetime import datetime
from openpyxl import Workbook
import io
from component.logger import logger
from component.sendEmail import cover_file, send_mail
from component.excel_utils import add_agent_status_sheet, add_new_monitor_sheet, add_new_notify_sheet
from config import mail_config
import traceback


def export(path, name):
    '''
    程序入口
    '''
    wb = Workbook()
    # 主机监控
    try:
        add_new_monitor_sheet(wb)
    except:
        logger.error("获取主机监控数据异常出错")
    # 告警
    try:
        add_new_notify_sheet(wb)
    except:
        logger.error("获取告警数据异常出错")
    try:
        add_agent_status_sheet(wb)
    except:
        logger.error("获取agent数据异常出错")
        traceback.print_exc()
    wb.save(path + "/" + name)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    attachment = cover_file(output, name)
    subject = datetime.now().strftime("%Y-%m-%d") + "主机监控数据"
    content = "主机监控数据",
    send_mail(subject, content, mail_config['RECEIVER'], [attachment])
    logger.info("----------- end -------------")


if __name__ == "__main__":
    export('./export', 'bk_export_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.xlsx')

