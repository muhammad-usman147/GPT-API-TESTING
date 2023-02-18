import pandas as pd 
import numpy as np 
import json 
import re

#add your filename here 
FILENAME = "data.csv" 

print(f"READING {FILENAME}")
df = pd.read_csv(FILENAME) #reading the raw email files 

class CleanData():
  """
  The purpose of this class is to execute the process of
  data cleaning in all of the columns with respect to their
  natures.
  For Example: 
  METHOD: clean_text{Returns text} <- is used to 
  1.    remove non-ASCII characters or those characters which 
        are not supporting by default.  
  2.    Removing URLS from the MSGs. As the Q/A contains queries
        that are related to helps & information. However, msgs
        that are promotionals do contains URLs 
  3.    Removing punctuations and special characters. 
  4.    Converting All Characters to lower cases.
        
  

  METHOD: GetEmails{Returns emails} <- is used to get emails from
  texts passed which are in the format of "TITLE <sample@site.com>


  Method: correct_spelling_and_abbreviations(Returns text) <- is 
  used to convert misspelled words from the texts into their true
  meaning for example: w/o(without), nxt(next), 2day(Today) 
  """
  def __init__(self) -> None:
    pass
  def clean_text(self,text):
    text = str(text)
    # remove non-ASCII characters
    text = text.encode("ascii", "ignore").decode()

    # remove URLs
    text = re.sub(r"http\S+", " ", text)

    # remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    # remove punctuation and special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # convert all characters to lowercase
    text = text.lower()

    # remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
  def GetEmails(self,mail):
    mail = str(mail)
    mail = mail.split()[-1]
 
    if mail.endswith('.com>') and '@' in mail:
      
      return mail[1:-1]

  def correct_spelling_and_abbreviations(self,text):
    # Define a dictionary of common misspellings and their correct forms
    misspellings = {
        "w/o": "without",
        "w/": "with",
        "thru": "through",
        "abt": "about",
        "nxt": "next",
        "2moro": "tomorrow",
        "2day": "today",
        "tnite": "tonight",
        "u": "you",
        "ur": "your"
    }
    
    # Replace misspellings and abbreviations with their correct forms
    for misspelling, correct in misspellings.items():
        text = re.sub(r"\b" + misspelling + r"\b", correct, text)

    return text



#creating the object of the above class so that their methods can be accessed
obj = CleanData() 

""" 
Below we are using the "map" method from PANDAS DATAFRAME
in order to pass the values in the called method efficiently.
We are also using lambda functions(single line functions) in 
order to process the data without taking more spaces.
"""

print("CLEANING THE DATA....")
df['subject'] = df['subject'].map(obj.clean_text) 
df['from[MAIL]']  = df['from'].map(obj.GetEmails)
df['message'] = df['message'].map(obj.clean_text)
#df['message'] = df['message'].map(obj.correct_spelling_and_abbreviations)

#getting the Title of the respondent
df['from[Name]'] = df['from'].map(lambda x: str(x).split()[0])
#getting the date of the message in YEAR-MONTH-DAY format
df['date']=df['date'].map(lambda x: str(x).split(':')[0][:10])

#creating a new DataFrame with new column names
new_df = pd.DataFrame({
    'date':df['date'],
    'Subject':df['subject'],
    'To':df['to'],
    #created a mew column to recognize the respondents name effectively.
    "From[Title]":df['from[Name]'],
    'From[Mail]':df['from[MAIL]'],
    'message':df['message'],
})


print("REMOVING PROMOTIONAL MSGS....")

'''
With this below line, we are able to extract the replies from the 
records and to remove all sorts of uncessary mails which do not have 
impact on the GPT model and cannot be used as a part of conversational 
data.
NOTE: Through this method, promotional EMAILS are also being removed.
'''
replies = new_df[new_df['Subject'].str.startswith("re")]

print(replies.head())
#creating new list DATA to add at the clients name into the list
data = []
#list comprehension to iterate all the clients names. Excluding Thunderstick
names = [i for i in replies['From[Title]'].unique() if 'Thunderstick' not in i] 

'''
NOTE the below dict of 'prompt' and 'completion' keys will be used to 
train/fine-tune the Open-ai model
'''
pairs = {'prompt':'', 'completion':''}
question = ''

print("GENERATING CONVERSATIONS.....")
#iterating title and messages to generate conversations of the data
for title,msg in zip(replies['From[Title]'], replies['message']):
  
  #to validate if the msg is not an error
  if 'address not found' not in  msg.lower():

    #if name belongs to client then adding their msg as questions
    if title in names:
      question += msg

    #if bane is Thunderstick, then it will be considered as their answers
    if title == 'Thunderstick' and question != '':
      pairs['prompt'] = question
      pairs['completion'] = msg
      #adding the DICT Question/Answer pair to the list
      data.append(pairs) 
      pairs = {'prompt':'',
         'completion':''}
      question = ''
    



print("SAVING RESULTS ARE [Fconversation.json].....")
#saving the conversations in the form of json data,
with open("MailsConversation.json",'w') as f:
  json.dump(data,f)