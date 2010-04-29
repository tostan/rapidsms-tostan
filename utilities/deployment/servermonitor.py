#!/usr/bin/python

# CONFIGURATION ##########################################################
# email address to use in the to field
recipient = 'jokkoinitiative@gmail.com'

# email address to use in the from field
sender = 'jokkoinitiative@gmail.com'

# template for the email message
# first '%s' is recipient, second is sender, third is problem details
message = '''To: %s
From: %s
Subject: SMS PROCESS FAILURE

One or more tests have failed:
%s'''

# number of minutes to wait between checks
sleeptime = 15

# url of the servermonitor2.php server-side script
url = 'http://172.16.10.28:8001/?uptimecheck=true'

# END CONFIGURATION ############################################################

import subprocess, urllib, time, re

def send_email(details):
    try:
        ssmtp = subprocess.Popen(('/usr/sbin/ssmtp', recipient), stdin=subprocess.PIPE)
    except OSError:
        print 'could not start sSMTP, email not sent'
    # pass the email contents to sSMTP over stdin
    ssmtp.communicate(message % (recipient, sender, details))
    # wait until the email has finished sending
    ssmtp.wait()
    
def main_loop():
    print "Starting..."
    try:
        responsepage = urllib.urlopen(url)
        response = responsepage.read()
    except IOError:
        # could not connect
        http_200 = False
        response = ''
    else:
        http_200 = True
    if response == 'success':
        http_success = True
    else:
        http_success = False
    if http_200 == True and http_success == True:
        print 'all tests passed'
    else:
        # one or more of the tests have failed
        print 'ALERT: '
        # create a list of tests that failed
        problemlist = ''
        if http_200 == False:
            problemlist = problemlist + 'SMS Process is not responding.\n'
        if http_success == False:
            problemlist = problemlist + 'SMS Process status is not available.\n'
        print problemlist
        send_email(problemlist)
        print 'attempted to send mail'
    
if __name__ == '__main__':
    main_loop()
