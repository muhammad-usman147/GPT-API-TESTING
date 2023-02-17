from revChatGPT.V1 import Chatbot
import pandas as pd 
import numpy as np 
import os 
bot = Chatbot(config = {
    "email": "eyolveofficial@gmail.com",
    "password": "eyolve1234"
})
df = pd.read_csv("CleanData.csv")
messages = df['message'].values
emails = df['From[Mail]'].values
classes = {"IsPromotional":[],
           "FromMail":[]}

for index, (mail,msg) in enumerate(zip(emails,messages)):
    prompt = "Is this message promotional? ({}) answer in Yes/No only".format(msg)
    print(f"Checking Message # {index+1}")
    for data in bot.ask(prompt):
        response = data['message']
    if 'yes' in response.lower():
        classes['IsPromotional'].append(1)
        
    if 'no' in response.lower():
        classes['IsPromotional'].append(1)
    else:
        classes['IsPromotional'].append(-1)
    classes['FromMail'].append(mail)
    os.system('cls' if os.name == 'nt' else 'clear')



pd.DataFrame(classes).to_csv("MailValidation.csv",index=False)


# for i in range(1000):

#     os.system('cls' if os.name == 'nt' else 'clear')
#     print(f"Checked Message # {i}")
