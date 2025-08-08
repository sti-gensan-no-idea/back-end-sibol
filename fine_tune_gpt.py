from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch
import os

model_name = "openai/gpt-oss-20b"
output_dir = "./gpt-oss-20b-finetuned"

# Check if model directory exists
if not os.path.exists("gpt-oss-20b"):
    raise FileNotFoundError("Model directory 'gpt-oss-20b' not found. Run setup_gpt.sh to download.")

# Load tokenizer with fallback
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
except Exception as e:
    print(f"Error loading tokenizer: {e}")
    print("Attempting to download tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    local_files_only=True
)

# Load and preprocess dataset
if not os.path.exists("real_estate_data.jsonl"):
    raise FileNotFoundError("Dataset 'real_estate_data.jsonl' not found.")
dataset = load_dataset("json", data_files="real_estate_data.jsonl")
def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Define training arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    save_steps=1000,
    save_total_limit=2,
    logging_steps=100,
    learning_rate=2e-5,
    fp16=torch.backends.mps.is_available(),
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
)

# Train
trainer.train()

# Save model and tokenizer
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
