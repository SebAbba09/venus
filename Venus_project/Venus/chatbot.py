# Venus/chatbot.py

from transformers import AutoModelForCausalLM, AutoTokenizer, BlenderbotForConditionalGeneration, BlenderbotTokenizer
from django.conf import settings
import torch


# Charger le modèle et le tokenizer
model_name = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained("D:/Download/HugginFace/VenusChatbot/Venus_project/static/blender_train")


# Venus/chatbot.py

# Venus/chatbot.py

def get_chatbot_response(message):
    inputs = tokenizer.encode(message + tokenizer.eos_token, return_tensors="pt")
    attention_mask = torch.ones(inputs.shape, dtype=torch.long)
    chat_history_ids = model.generate(inputs, attention_mask=attention_mask, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(chat_history_ids[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    return response

