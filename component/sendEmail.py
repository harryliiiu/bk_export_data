import base64
import io
import requests
import json
from config import config

def cover_file(output, name):
    """
    文件格式转换
    """
    
    filename = "{}".format(
        str(name.encode('utf-8'), encoding='utf-8')
    )

    return {
        'filename': filename,
        "content": str(
            base64.b64encode(output.read()), encoding='utf-8'
            ),
    }


def send_mail(subject, content, email, attachments=[]):
    url = config['BK_URL'] + "/api/c/compapi/cmsi/send_mail/"
    receiver = email
    params = {
        "bk_app_code": config.get("BK_APP_CODE"),
        "bk_app_secret": config.get("BK_APP_SECRET"),
        "bk_username": config.get("BK_TOKEN"),
        "receiver": receiver,
        "title": subject,
        "content": content,
        "attachments": attachments,
    }
    result = requests.post(url, json.dumps(params), verify=False)
    return result