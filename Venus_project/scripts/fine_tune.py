import json
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import Trainer, TrainingArguments, BlenderbotTokenizer, BlenderbotForConditionalGeneration
from sklearn.model_selection import train_test_split

def preprocess_function(examples):
    inputs = tokenizer(examples['input_text'], max_length=128, truncation=True, padding="max_length")
    targets = tokenizer(examples['target_text'], max_length=128, truncation=True, padding="max_length")
    inputs['labels'] = targets['input_ids']
    return inputs

model_name = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

# Charger les données depuis le fichier JSON
with open(r'D:\Download\HugginFace\VenusChatbot\Venus_project\combined_file.json', 'r') as f:
    data = json.load(f)

# Extraire les dialogues et les transformer en paires (input_text, target_text)
dialogues = []
for dialog_key, dialog_value in data.items():
    for turn in dialog_value['log']:
        if turn["system response"]:
            dialogues.append({
                "input_text": turn["user utterance"],
                "target_text": turn["system response"]
            })

# Créer un DataFrame et le diviser en ensembles d'entraînement et de validation
df = pd.DataFrame(dialogues)
train_df, eval_df = train_test_split(df, test_size=0.1)
train_dataset = Dataset.from_pandas(train_df)
eval_dataset = Dataset.from_pandas(eval_df)

# Tokeniser les ensembles d'entraînement et de validation
tokenized_train_dataset = train_dataset.map(preprocess_function, batched=True)
tokenized_eval_dataset = eval_dataset.map(preprocess_function, batched=True)

# Créer un DatasetDict pour les ensembles d'entraînement et de validation
dataset = DatasetDict({
    'train': tokenized_train_dataset,
    'validation': tokenized_eval_dataset
})

# Définir les arguments de formation
training_args = TrainingArguments(
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    output_dir="./results",
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=10,
    evaluation_strategy="steps",
    save_steps=10,
    save_total_limit=2,
    learning_rate=5e-5,
    lr_scheduler_type="linear",
    weight_decay=0.01,
)

# Créer un Trainer et lancer l'entraînement
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['validation'],
)

trainer.train()

# Sauvegarder le modèle et le tokenizer
model_save_path = r"D:/Download/HugginFace/VenusChatbot/Venus_project/static/blender_train"
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)

print(dataset)
