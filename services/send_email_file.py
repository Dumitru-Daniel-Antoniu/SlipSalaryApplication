# import requests
# domain = os.getenv("DOMAIN_NAME")
# key = os.getenv("API_KEY")


import logging
import os
import mimetypes
import smtplib

from email.message import EmailMessage


logging.basicConfig(level=logging.INFO)

host_email = os.getenv("EMAIL_ADDRESS")
host_password = os.getenv("EMAIL_PASSWORD")


async def send_email_message(to_email: str, subject: str, text: str, file_path: str, file_type: str):
	message = EmailMessage()
	message['Subject'] = subject
	message['From'] = host_email
	message['To'] = to_email
	message.set_content(text)

	if file_type == "pdf":
		filename = "salary_report.pdf"
	else:
		filename = "employees_status.csv"

	mime_type, _ = mimetypes.guess_type(file_path)
	if mime_type is None:
		mime_type = 'application/octet-stream'

	maintype, subtype = mime_type.split('/', 1)

	with open(file_path, 'rb') as file:
		logging.info("File read")
		file_data = file.read()
		message.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)

	try:
		with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
			logging.info("SMTP connection established")
			logging.info("Logging in as %s", host_email)
			logging.info("Using password: %s", host_password)
			smtp.login(host_email, host_password)
			smtp.send_message(message)
			logging.info("Message sent successfully")
		return 200
	except Exception as e:
		logging.error("Failed to send email: %s", e)
		return 401

	# with open(file_path, "rb") as content_file:
	# 	return requests.post(
	# 		f"https://api.mailgun.net/v3/{domain}/messages",
	# 		auth=("api", key),
	# 		data={
	# 			# "from": f"postmaster@{domain}",
	# 			"from": "ddumitru128@gmail.com",
	# 			"to": to_email,
	# 			"subject": subject,
	# 			"text": text
	# 		},
	# 		files={"attachment": (filename, content_file)}
	# 	)
