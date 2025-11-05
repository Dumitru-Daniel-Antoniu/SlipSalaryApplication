import os
import requests


domain = os.getenv("DOMAIN_NAME")
key = os.getenv("API_KEY")


async def send_email_message(to_email: str, subject: str, text: str, file_path: str, file_type: str):
	if file_type == "pdf":
		filename = "salary_report.pdf"
	else:
		filename = "employees_status.csv"

	with open(file_path, "rb") as content_file:
		return requests.post(
			f"https://api.mailgun.net/v3/{domain}/messages",
			auth=("api", key),
			data={
				# "from": f"postmaster@{domain}",
				"from": "ddumitru128@gmail.com",
				"to": to_email,
				"subject": subject,
				"text": text
			},
			files={"attachment": (filename, content_file)}
		)
