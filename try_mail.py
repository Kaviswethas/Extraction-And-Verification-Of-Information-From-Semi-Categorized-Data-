import smtplib

HOST="smtp.gmail.com"
PORT=587

FROM_EMAIL="gokulnathramesh25@gmail.com"
TO_EMAIL=""
PASSWORD="jingtxqoyndtopya"

MESSAGE="""SUBJECT: RAC ADMIN CREDENTIALS
Hi user,

xxxxxxxxx

"""

smtp=smtplib.SMTP(HOST,PORT)
Status_code,response=smtp.ehlo()
print(Status_code,"\n\n yooo\n\n",response)

Status_code,response=smtp.starttls()
print(Status_code,"\n\n yooo\n\n",response)
Status_code,response=smtp.login(FROM_EMAIL,PASSWORD)

print(FROM_EMAIL,"\n\n yooo\n\n",PASSWORD)

smtp.sendmail(FROM_EMAIL,TO_EMAIL,MESSAGE)

smtp.quit()