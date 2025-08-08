from datasets import load_dataset
from unsloth import FastLanguageModel
import torch

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="openai/gpt-oss-20b",
    max_seq_length=16384,
    dtype=torch.float16,
    load_in_4bit=True
)

# Prepare dataset (example: JSONL format with real estate prompts)
dataset = load_dataset("json", data_files="/app/json_data/real_estate_data.jsonl")

# Configure fine-tuning
model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=42
)

# Training arguments
from transformers import TrainingArguments
trainer = Trainer(
    model=model,
    train_dataset=dataset["train"],
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=50,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=1,
        output_dir="gpt-oss-20b-finetuned",
        optim="adamw_8bit"
    )
)

# Start fine-tuning
trainer.train()

# Save fine-tuned model
model.save_pretrained("gpt-oss-20b-finetuned")
tokenizer.save_pretrained("gpt-oss-20b-finetuned")