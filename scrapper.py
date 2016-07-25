import urllib2
import json
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_SERVER = "smtp.gmail.com"
ACCOUNT = "acc@gmail.com"
PASSOWRD = "pass"

EMAIL_BODY = """
<html>
<head></head>
	<body>
	    <p>Hey there,<br><br>
			<q> I came across your Github account and felt compelled to reach out. </q> <br><br>

			I am just a simple bot built to spam github users who have a public email on their github profile like you.<br> 
			I was created by a github user who got a spam email like this from a person called Sara Hincapie from careerscore.com.
			He think that they use github api to spam users and invite them to their website so he tried to write a scrapper like them. <br><br>
			
			So if I passed your spam filter, and you read this message then I succeeded in my only mission in life. <br><br>

			sorry to bother you,<br><br>

			Cheers,<br><br>
			Scrapper of Github
			
			<h6> careerscore.com-like bot </h6>
		</p>
	</body>
</html>

"""

def get_all_users_api(last_id=0):
	response = urllib2.urlopen("https://api.github.com/users?since=" + str(last_id))
	if response.getcode() == 200: # success
		users_list = json.load(response)
		return users_list

def get_single_user(username):
	if username: # not empty
		response = urllib2.urlopen("https://api.github.com/users/" + username)
		user = {}
		if response.getcode() == 200: # success
			user = json.load(response)
		return user

def get_last_id(filename="last_id.txt"):
	try:
		file = open(filename)
		return int(file.readline())
	except:
		return 0
	return 0

def save_last_id(last_id=0, filename="last_id.txt"):
	file = open(filename, 'w')
	if file:
		file.write(str(last_id))
		file.close()

def smtp_server_init(server_address, account, password):
	try:  
	    server = smtplib.SMTP_SSL(server_address)
	    server.ehlo()
	    server.login(account, password)
	    return server
	except:  
	    print 'Something went wrong connecting to smtp server...'

def send_email_to(server, from_email, to_email, subject, html_content):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = from_email
	msg['To'] = to_email
	msg.attach(MIMEText(html_content, 'html'))
	
	server.sendmail(from_email, to_email, msg.as_string())

def send_email_to_github(email, name=""):
	send_email_to(send_email_to_github.server, send_email_to_github.me, email, "I came across your Github again", EMAIL_BODY)

def main_loop():
	# init
	last_id = get_last_id()
	send_email_to_github.server = smtp_server_init(smtp_SERVER, ACCOUNT, PASSOWRD)
	send_email_to_github.me = ACCOUNT

	while 1:
		try:
			users_list = get_all_users_api(last_id)
			if users_list:
				for short_user in users_list:
					try:
						if short_user['login']:
							user = get_single_user(short_user['login'])
							if user and user['email'] and user['name'] and user['public_repos'] >= 2:
								send_email_to_github(user['email'], user['name'])
								print ("Success: email sent to: %s - name: %s - login: %s" %(user['email'], user['name'], user['login']))
								last_id = user['id']
					except:
						print ("Error: sending email to: %s - name: %s - login: %s" %(user['email'], user['name'], user['login']))
				save_last_id(last_id)
			else: # list is empty, we finished
				save_last_id(last_id)
				break
		except Exception as err:
			print (err)
			save_last_id(last_id)
			# error may be our quota/hour finnished or connection error
			# halt for 30 minutes
			print ("\nwait for 30 minuites")
			time.sleep(30 * 60)

	send_email_to_github.server.close()

main_loop()