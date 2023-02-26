import openai
import os
import json 
# Set OpenAI API key
openai.api_key ='<API-KEY-HERE>'

# Read JSON file
print("CONVERTING Json to Jsonl")
with open('MailsConversation.json', 'r') as f:
    data = json.load(f)

# Convert JSON to JSONL
with open('ConvertedJsonl.jsonl', 'w') as f:
    for item in data:
        json.dump(item, f)
        f.write('\n')

# Configure training parameters
model_id = "text-davinci-002"
temperature = 0.5
max_tokens = 50

print("Training Started")
# Train the model
with open('ConvertedJsonl.jsonl', 'r') as f:
    response = openai.Completion.create(
     model="text-davinci-003",
     prompt=f.read(),
     temperature=1,
     max_tokens=500,
     top_p=1,
     frequency_penalty=0,
     presence_penalty=0
    )

# Print training results
print(response)
