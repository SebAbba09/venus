from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pickle

tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

# Sauvegarder le tokenizer et le modèle avec pickle
with open(r'D:\Download\HugginFace\VenusChatbot\Venus_project\Venus\static/token.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)

with open(r'D:\Download\HugginFace\VenusChatbot\Venus_project\Venus\static/model_blenderbot.pkl', 'wb') as f:
    pickle.dump(model, f)
