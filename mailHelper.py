#_*_ coding: utf-8 _*_
import poplib
#import email
from email.parser import Parser
from email.header import decode_header
#from email.utils import parseaddr
import base64
import os

def decode_str(s):
	try:#下载pdf时候,文件名不用解码
		value, charset = decode_header(s)[0]
		if charset:
			value = value.decode(charset)
	except Exception:
			return s	
	return value
	
def guess_charset(msg):
	charset = msg.get_charset()
	if charset is None:
		#如果获取不到，再从Content-Type字段获取:
		content_type = msg.get('Content-Type', '').lower()
		pos = content_type.find('charset=')
		if pos >= 0:
			charset = content_type[pos + 8:].strip()
	return charset

#indent用于缩进显示
def download_attachment(msg, indent = 0):
	#先在当前目录创建保存本次作业的子目录
	if job_number:
		if os.path.exists(job_number) == False:
			os.mkdir(job_number)
	else:
		if os.path.exists("temp") == False:
			os.mkdir("temp")

	#若indent不等于0，则表示该部分不包含邮件头
	if indent == 0:
		subject = msg.get("Subject", "")
		if subject:
			subject = decode_str(subject)
		print "Subject: ", subject
		
		#提取姓名和学号
		if "-" in subject:
			subject = subject.split('-')
		else:
			subject = subject.split('_')
		if 3 != len(subject): #邮件主题格式不对就返回
			return
		times, s_number, s_name = subject
		if job_number:
			if times != job_number: #只下载指定的作业
				return
		if student_number:
			if s_number != student_number: #只下载指定的作业
				return
		
	if(msg.is_multipart()):
		#如果邮件对象是一个MIMEMultipart，
		#get_payload()返回list，包含所有的子对象
		parts = msg.get_payload()
		for n, part in enumerate(parts):
			#递归打印每一个子对象：
			download_attachment(part, indent + 1)
	else:
		#邮件对象不是一个MIMEMUltipart，就依据content_type判断
		content_type = msg.get_content_type()
		#处理附件
		if content_type not in ["text/plain", "text/html"]:
			#print('%sAttachment: %s' % (' ' * indent, content_type))
			filename = decode_str(msg.get_filename())
			#filename = msg.get_filename()
			print filename
			if job_number:
				f = open("%s/%s" % (job_number, filename), 'wb')
			else:
				f = open("temp/%s" % filename, 'wb')
			f.write(base64.decodestring(msg.get_payload()))
			f.close()

def analysis_mail(select):
	global job_number
	global student_number
	job_number = ''
	student_number = ''
	
	if select == "1":
		job_number = raw_input("please input the job number: ")
	else select =="2":
		student_number = raw_input("please input the student number: ")
	

	email = 'your_email'
	#这里输入的授权密码，不是登陆密码
	password = 'you_pass'
	pop3_server = 'pop.126.com'

	#connect to pop3 server
	server = poplib.POP3(pop3_server)

	#身份认证
	server.user(email)
	server.pass_(password)

	#list()返回所有邮件的编号
	resp, mails, octets = server.list()

	#获取最新的一封邮件， 注意索引号从1开始
	total_mail = len(mails)
	while total_mail > 0:
		#if total_mail !=4:
		#	total_mail = total_mail - 1
		#	continue
		print total_mail
		resp, lines, octets = server.retr(total_mail)
		#lines存储了邮件的原始文本的每一行，可以获得整个邮件的原始文本
		msg_content = '\r\n'.join(lines)
		#稍后解析出邮件
		msg = Parser().parsestr(msg_content)
		download_attachment(msg)
		total_mail = total_mail - 1

	server.quit()

def print_menu():
	print "Menu:"
	print "1.download the whole homework by job number"
	print "2.download specify homework by student number"
	print "3.download all the homework"
	print "4.exit"
	select = raw_input("")

if __name__ == "__main__":
	print_menu()
	while 1:
		if select == "3":
			break
		else:
			analysis_mail(select)
		
		print_menu()
	
