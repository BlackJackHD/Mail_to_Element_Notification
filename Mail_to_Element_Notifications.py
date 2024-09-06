from requests import get
import time
import config
import os
import requests
import imaplib
import email
from email.header import decode_header
import base64
import re

#Переименовал time.speep, для удобства
def wait(t):
	time.sleep(t)
# Проверка непрочитанных сообщений в почте
def mail_check_unseen():
	# Подключение к почте
	imap = imaplib.IMAP4_SSL(config.m_server)
	imap.login(config.m_login, config.m_pass)
	imap.select("INBOX")
	# Поиск прочитанных и не прочитанных писем
	b = imap.uid('search', "UNSEEN")
	# print('====', b)
	s = str(b[1][0])
	s = s[2:-1]
	s = s.split(' ')
	return(s)
# Извлечение тела непрочитанного письма
def mail_insert(unseen_mail_uid):
	imap = imaplib.IMAP4_SSL(config.m_server)
	imap.login(config.m_login, config.m_pass)
	imap.select("INBOX")
	# Извлечение текста из конкретного письма.
	unseen_mail_uid=bytes(unseen_mail_uid, encoding = 'utf-8') #Преобразование номера письма в байты
	res, msg = imap.uid('fetch', unseen_mail_uid , '(RFC822)')
	msg = email.message_from_bytes(msg[0][1])
	# print(msg)
	letter_date = msg["Delivery-date"] # Дата доставки
	letter_from = msg["X-SA-Exim-Mail-From"] # E-mail отправителя
	letter_to = msg["To"] # E-mail получателя
	letter_cc = msg["Cc"] # E-mail копии
	letter_subject = msg["Subject"] # Тема
	# Дополнительные данные, для обработки
	# print('\n\nДата: ', letter_date, '\nОтправитель: ',letter_from, '\nПолучатель: ', letter_to, '\nТема: ', letter_subject)
	# Извлечение тела(работает только с text/plain)
	# print('\nТело письма:\n',)
	m_payload = str()
	if msg.is_multipart() == True:
		for part in msg.get_payload():
			m_payload = m_payload + str(part.get_payload())
	else:
		m_payload = str(msg.get_payload())	
	# print(m_payload)
	return(m_payload, letter_date, letter_to, letter_from, letter_cc,letter_subject)
# Декодировка объекта text/plain
def plain_decode(text): #дешифратор Base64
	try:
		# text = text[:-104]
		text = re.sub(r'\<[^<>]*\>', '', text)
		text = base64.b64decode(text)
		text = text.decode('utf-8')
	except Exception as ex:
		print(ex)
	return(text)
# Форматирование текста
def form_text(text):
	# Удаление лишних переходов на новую строку(до 256)
	i = 0
	while i < 8:
		# text = text.replace("","")
		text = re.sub("&#(\d+);", lambda match: chr(int(match.group(1))), text)
		text = re.sub(r'<br>', '\n', text)
		text = re.sub(r'&nbsp;', ' ', text)
		text = re.sub(r'\<[^<>]*\>', '', text)
		text = text.replace("\s\s"," ")
		text = text.replace("\r\n","\n")
		text = text.replace("\n\n","\n")
		i += 1
	# text = re.sub(r'--.', ' ', text)
	# text = re.compile('(С уважением=?)+[\W\w\s\d]').sub('',text)
	text = text.split('--', maxsplit = 1)
	text = str(text[0])
	return(text)
# Поиск тэга
def find_tag(text):
	index = text.find(config.e_tag)
	return(index)
# Добавление отправителя и получателя письма
def to_from_text(text, from_t, to_t, cc_t):
	z = str('Отправитель: ') + str(from_t) + str('\nПолучатель: ') + str(to_t) + str('\nКопия: ') + str(cc_t) + str('\n\n') + str(text)
	return(z)
# Отправление письма в Element
def message_el(message, room):
	access_token = config.e_token
	room_id = room
	url = 'https://*server_name*/_matrix/client/r0/rooms/' + room_id + '/send/m.room.message'
	headers = {'Authorization': ' '.join(['Bearer', access_token])}
	data = {
	    'body': message,
	    'format': 'org.matrix.custom.html',
	    # 'formatted_body': 'hello <b>matrix</b>',
	    'msgtype': 'm.text'
	}

	r = requests.post(url, json=data, headers=headers)


y = 0
z = 0
while z == 0:
	mes = mail_check_unseen()
	if len(mes[0]) > 0:	
		for x in mes:
			try:
				if y > 10:
					quit()
				p = mail_insert(x)
				message = str(p[0])
				# print('|'*10, message, '|'*10)
				message = plain_decode(message)
				message = form_text(message)
				# print(message, p[3], p[2])
				message = to_from_text(message, p[3], p[2], p[4])
				print('\n||||||||||||||\n', message, '\n', '+'*10)
				message_el(message, config.svn_room)
			except Exception as e:
				print('-',y,e)
				y += 1
	else:
		nns = time.time() % 100 // 10
		print('Нет непрочитанных писем ', '%.0f' % nns)
		wait(10)












# z = 0
# while z == 0:
# 	mes = mail_check_unseen()
# 	if len(mes[0]) > 0:	
# 		for x in mes:
# 			try:
# 				p = mail_insert(x)
# 				message = p[0]
# 				message = form_text(message)
# 				recipient = p[2]
# 				recipient = find_recipient(recipient)
# 				print(recipient, '\n', message)
# 				for rec in recipient:
# 					options = webdriver.FirefoxOptions()
# 					driver = webdriver.Firefox(options=options)
# 					try_login_el()
# 					message_el(message, rec)
# 					driver.close()
# 					driver.quit()
# 				wait(10)
# 			except Exception as e:
# 				print(e)
# 	else:
# 		print('Нет непрочитанных писем')
# 		wait(10)










# 	# driver.close()
# 	# driver.quit()


# 	# EsTX 3t3z 7Bi4 AUgN vKHT UBjy 8t97 MKUD oiA6 c94w fEi5 SUP9
# 	# EsTX 3t3z 7Bi4 AUgN vKHT UBjy 8t97 MKUD oiA6 c94w fEi5 SUP9
# 	# opts = FirefoxOptions()
# 	# opts.add_argument("--headless")
# 	# options = webdriver.FirefoxOptions()
# 	# driver = webdriver.Firefox(options=options)
# 	# driver.get("https://my.beeline.ru/login.xhtml")







# Пример поиска комнат
# recipient_list = 'polishchuk@dsol.ru makarski@dsol.ru admin@dsol.ru vp@dsol.ru'
# room = find_recipient(recipient_list)
# print(room)