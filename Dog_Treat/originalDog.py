'''
File originated from NYC CNC Machining: http://www.nyccnc.com/judd-treat-machine.html
To be changed to meet new hardware and project intentions
'''

#!/usr/bin/python

#generic imports
import time
import os
import RPi.GPIO as GPIO
from time import sleep, strftime
from Adafruit_PWM_Servo_Driver import PWM  #for servo
from Adafruit_CharLCD import Adafruit_CharLCD  #for LCD screen
from subprocess import *
from Adafruit_CharLCD import Adafruit_CharLCD
from subprocess import call

#imports for email
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.parser import HeaderParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Utils import COMMASPACE, formatdate
from email import Encoders

#servo stuff
pwm = PWM(0x40, debug=True)
servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

transistor = 8  #gearmotor transistor gpio pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(transistor, GPIO.OUT)
GPIO.output(transistor, False)

USERNAME = "juddwouldlikeatreat@gmail.com"     #your gmail   #!/usr/bin/env python
PASSWORD = "password" 			#your gmail password	
programpause = 5   #pause for x seconds

temp_list = []

##########################################
#FUNCTION TO SEARCH TO BUILD LIST OF UNREAD EMAILS	
##########################################

def check_email():
    status, email_ids = imap_server.search(None, '(UNSEEN)')    #searches inbox for unseen aka unread emails ::The SEARCH command searches the mailbox for messages that match the given searching criteria.  Searching criteria consist of one or more search keys. The untagged SEARCH response from the server contains a listing of message sequence numbers corresponding to those messages that match the searching criteria. Status is result of the search command: OK - search completed, NO - search error: can't search that charset or criteria, BAD - command unknown or arguments invalid. Criteria we are using here is looking for unread emails
    if email_ids == ['']:
        print('No Unread Emails')
        mail_list = []
    else:
        mail_list = get_senders(email_ids)
        print('List of email senders: ', mail_list)         #FYI when calling the get_senders function, the email is marked as 'read'
        print len(mail_list),
        print("new treat emails!")

    imap_server.close()
    return mail_list
	
##########################################
#FUNCTION TO SCRAPE SENDER'S EMAIL ADDRESS	
##########################################

def get_senders(email_ids):
    senders_list = []          				   #creates senders_list list 
    for e_id in email_ids[0].split():   		   #Loops IDs of a new emails created from email_ids = imap_server.search(None, '(UNSEEN)')
    	resp, data = imap_server.fetch(e_id, '(RFC822)')   #FETCH command retrieves data associated with a message in the mailbox.  The data items to be fetched can be either a single atom or a parenthesized list. Returned data are tuples of message part envelope and data.
    	perf = HeaderParser().parsestr(data[0][1])	   #parsing the headers of message
    	senders_list.append(perf['From'])		   #Looks through the data parsed in "perf", extracts the "From" field 
    return senders_list

##########################################
#FUNCTION TO SEND THANK-YOU EMAILS
##########################################

def send_thankyou(mail_list):
    for item in mail_list:
        files = []
        files.append("simplify.py")
        text = 'This is the body of the email'
        assert type(files)==list
        msg = MIMEMultipart()
        msg['Subject'] = 'Thank you for the treat!'
        msg['From'] = USERNAME
        msg['To'] = item

        msg.attach ( MIMEText(text) )  

        for file in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(file,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                   % os.path.basename(file))
            msg.attach(part)


        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo_or_helo_if_needed()
        server.starttls()
        server.ehlo_or_helo_if_needed()
        server.login(USERNAME,PASSWORD)
        server.sendmail(USERNAME, item, msg.as_string() )
        server.quit()
        print('Email sent to ' + item + '!')

##########################################
#SERVO FUNCTIONALITY CODE
##########################################

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)


##########################################
#FUNCTION TO WIGGLE SERVO
##########################################

def wiggle():

  pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
  n=0
  while (n<7):
    pwm.setPWM(0, 0, 150)
    time.sleep(.1)
    pwm.setPWM(0, 0, 300)
    time.sleep(.1)
    n = n +1
  pwm.setPWM(0,0,150)
  time.sleep(1)
  
##########################################
#FUNCTION TO ROTATE DISPENSING TUBE
##########################################

def loadtreats():
    GPIO.output(transistor, True)
    sleep(10) 
    GPIO.output(transistor, False)

  
##########################################
#FUNCTION TO DUMP HOPPER OF TREATS
##########################################
def dumptreats():
  pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
  pwm.setPWM(0, 0, 150)
  time.sleep(1)
  pwm.setPWM(0, 0, 600)
  time.sleep(2)    
  pwm.setPWM(0, 0, 150)

##########################################
#FUNCTION TO TAKE PICTURE
##########################################

def takepicture():
    call(["uvccapture", "-v", "-S45", "-B190", "-C35", "-G50", "-x640", "-y480"])
    time.sleep(5)
    call(["uvccapture", "-v", "-S45", "-B190", "-C35", "-G50", "-x640", "-y480"])


##########################################
#FUNCTION for LCD Home Screen text
##########################################
def homescreen():
    lcd = Adafruit_CharLCD()
    lcd.begin(20,4)
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.message("Judd Treat Machine!")
    lcd.setCursor(0,1)
    lcd.message("Awaiting Emails!")
    lcd.setCursor(0,3)
    lcd.message("Hurry up!")
    #time.sleep(1)	#this causes problem because footpedal won't register if pressed during sleep


##########################################
#FUNCTION for LCD Home Screen text
##########################################
def dumpLCD():
    lcd = Adafruit_CharLCD()
    lcd.begin(20,4)
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.message("Yay!  Treats!")
    lcd.setCursor(0,1)
    lcd.message(" ")
    lcd.setCursor(0,3)
    lcd.message("Thank you!")
    #time.sleep(1)	

##########################################
#PROMPT USER TO CHECK INBOX FOR MESSAGES.  IF YES, CALLS FUNCTION FROM ABOVE, SEARCHES FOR UNREAD EMAILS WHICH ARE ADDED TO THE email_ids LIST
##########################################

while True:
    homescreen()
    check = raw_input("Type Yes to check email: ")
    if check == "yes":
        print "OK I'll Proceed"
	wiggle()
	time.sleep(1)
        imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
        imap_server.login(USERNAME, PASSWORD)
        imap_server.select('INBOX')
        mail_list = check_email()
        temp_list = temp_list + mail_list
        if mail_list :
            loadtreats()
	    dumpLCD()
	    dumptreats()
	    print "Dumping Hopper"
            sendthankyou = raw_input("Send thank you emails? (yes/no)")
            if sendthankyou == "yes":
		 takepicture() 
                send_thankyou(mail_list)
            else:
                print("OK I won't send thank you emails")
        else:
            print("OK I won't check emails")
            
    #time.sleep(programpause)
    

