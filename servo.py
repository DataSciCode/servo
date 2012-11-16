#!/usr/bin/env python
import os, imaplib
from threading import Timer
from servo.models import *
from email.parser import Parser
from django.utils.html import strip_tags
import base64
from django.core.files.base import ContentFile
#from io import BytesIO

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "servo3.settings")

def hello():
	#t = Timer(60.0, hello)
	#t.start()
	print 'Running Servo task server at 60 second intervals...'

	c = Configuration.objects.get(pk=1)

	if c.imap_ssl:
		M = imaplib.IMAP4_SSL(c.imap_host)
	else:
		M = imaplib.IMAP4(c.imap_host)

	M.login(c.imap_user, c.imap_password)
	M.select()
	typ, data = M.search(None, 'ALL')

	for num in data[0].split():
		typ, data = M.fetch(num, '(RFC822)')
		# parsestr() seems to return an email.message?
		msg = Parser().parsestr(data[0][1])

		for part in msg.walk():
			#print part.get_params()
			t, s = part.get_content_type().split('/', 1)
			if t == 'text':
				body = part.get_payload()
				if s == 'html':
					body = strip_tags(body)
			else:
				if part.get_filename():
					filename = part.get_filename()
					content = base64.b64decode(part.get_payload())
					content = ContentFile(content, filename)
					attachment = Attachment(name=filename, content=content)
					attachment.content.save(filename, content)
					#attachment.save()

		message = Message(body=body, sender_id=4)
		message.subject = msg.get('Subject')

		try:
			(order, parent) = msg.get('In-Reply-To').split('/')
			parent = Message.objects.get(pk=parent)
			message.recipient = parent.sender
			message.parent = parent.sender
			message.order_id = order
		except Exception, e:
			raise e
		
		message.save()
		#M.copy(num, 'servo')
		#M.store(num, '+FLAGS', '\\Deleted')
	
	M.close()
	M.logout()

hello()
