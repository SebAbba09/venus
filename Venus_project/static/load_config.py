from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer, GenerationConfig

model = BlenderbotForConditionalGeneration.from_pretrained(r"D:/Download/HugginFace/VenusChatbot/Venus_project/static/model_blenderbot.pkl")
tokenizer = BlenderbotTokenizer.from_pretrained(r"D:/Download/HugginFace/VenusChatbot/Venus_project/static/token.pkl")
gen_config = GenerationConfig.from_pretrained("Venus_project/static/generation_config.py")

input_text = "Votre texte ici"
inputs = tokenizer(input_text, return_tensors="pt")

outputs = model.generate(**inputs, generation_config=gen_config)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(response)
