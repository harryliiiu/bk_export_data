#! /usr/bin/env python
# #coding=utf-8
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL
from config import mail_config
# server
host_server = mail_config.get('HOST_SERVER')
# sender
sender = mail_config.get('SENDER')
pwd = mail_config.get('PWD')

sender_mail = mail_config.get('SENDER')
# receiver
receiver = mail_config.get('RECEIVER')


def send_email(path_name='./export/test.log'):
    #邮件标题
    mail_title = '主机监控数据'
    #邮件的正文内容
    mail_content = '主机监控数据和告警数据'

    #ssl登录
    smtp = SMTP_SSL(host_server) # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender, pwd)

    msg = MIMEMultipart()
    msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
    # msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_mail
    msg["To"] = receiver

    #构造附件1，传送当前目录下的test.txt文件
    filename = "test"
    att1 = MIMEText(open(path_name,'rb').read(),'base64','utf-8')
    att1['Content-Type'] = 'application/octet-stream'
    #这里的filename可以任意写，写什么名字 邮件中就显示什么名字
    att1['Content-Disposition'] = 'attachment;filename="{}.log"'.format(
                filename.encode('utf-8').decode('ISO-8859-1'))
    msg.attach(att1)

    smtp.sendmail(sender_mail, receiver, msg.as_string())
    smtp.quit()