from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

# Nom du modèle et chemins de fichier
model_name = "facebook/blenderbot-400M-distill"
model_save_path = "D:/Download/HugginFace/VenusChatbot/Venus_project/static/blender_train"

# Charger le tokenizer et le modèle
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_save_path)

# Vérifier le chargement du modèle
print(f"Model loaded successfully from {model_save_path}")

# Tester le modèle avec une entrée de test
test_input = "Hello, how are you?"
inputs = tokenizer(test_input, return_tensors="pt")

# Définir max_new_tokens pour éviter l'avertissement
reply_ids = model.generate(**inputs, max_new_tokens=150)
reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)

print(f"Input: {test_input}")
print(f"Reply: {reply}")
