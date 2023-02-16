from revChatGPT.V1 import Chatbot

bot = Chatbot(config = {
    "email": "xxx@xxx",
    "password": "xxxx"
})

prompt = "Is this message promotional? (Limited time offer! Get 20% off all items in our store today. Don't miss out!) answer in Yes/No only"
for data in bot.ask(prompt):
    response = data['message']

print(response)