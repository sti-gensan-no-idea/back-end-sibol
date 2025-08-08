#!/bin/bash

# Detect operating system and architecture
OS=$(uname -s)
ARCH=$(uname -m)

# Read ENV from .env file
if [ -f ".env" ]; then
    ENV=$(python3 -c "from dotenv import load_dotenv; from os import environ; load_dotenv(); print(environ.get('ENV', 'local'))" 2>/dev/null || echo "local")
else
    echo "Warning: .env file not found. Defaulting to ENV=local. Create .env with ENV=local or ENV=prod for production."
    ENV="local"
fi

# Validate ENV
if [ "$ENV" != "local" ] && [ "$ENV" != "prod" ]; then
    echo "Error: ENV must be 'local' or 'prod', got '$ENV'."
    exit 1
fi

# Check if running as root in production
if [ "$ENV" = "prod" ] && [ "$EUID" -ne 0 ]; then
    echo "Error: Production setup requires root privileges. Run with sudo."
    exit 1
fi

# Function to fix permissions
fix_permissions() {
    echo "Fixing permissions for cache and bin directories..."
    mkdir -p /Users/hades/.local/bin /Users/hades/.cache/huggingface
    chown -R "$USER:staff" /Users/hades/.local/bin /Users/hades/.cache/huggingface
    chmod -R u+rwX /Users/hades/.local/bin /Users/hades/.cache/huggingface
}

# Function to clear caches and previous installations
clear_caches() {
    echo "Clearing previous virtual environment, caches, and model directory..."
    rm -rf gpt_oss_env
    rm -rf /Users/hades/Library/Caches/pip
    rm -rf /Users/hades/Library/Caches/Homebrew
    rm -rf /Users/hades/.cache/huggingface
    rm -rf gpt-oss-20b gpt-oss-20b-finetuned
    mkdir -p /Users/hades/Library/Caches/pip /Users/hades/.cache/huggingface
    chown -R "$USER:staff" /Users/hades/Library/Caches/pip /Users/hades/.cache/huggingface
    chmod -R u+rwX /Users/hades/Library/Caches/pip /Users/hades/.cache/huggingface
}

# Function to install dependencies for Linux (Ubuntu)
install_linux_deps() {
    echo "Installing dependencies for Linux (Ubuntu)..."
    apt-get update
    apt-get install -y python3-pip python3-venv git curl build-essential cmake libcurl4-openssl-dev libprotobuf-dev protobuf-compiler pkg-config
}

# Function to install dependencies for macOS (M1)
install_macos_deps() {
    echo "Installing dependencies for macOS (M1)..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    brew install python@3.12 git curl cmake libomp protobuf pkg-config
    if ! xcode-select -p &> /dev/null; then
        echo "Installing Xcode Command Line Tools..."
        xcode-select --install
    fi
    brew uninstall --ignore-dependencies pipx || true
    /opt/homebrew/bin/python3.12 -m pip install pipx
    /opt/homebrew/bin/pipx ensurepath --force
    /opt/homebrew/bin/pipx install python-dotenv --force --python /opt/homebrew/bin/python3.12
}

# Create and activate virtual environment
setup_venv() {
    echo "Creating virtual environment with Python 3.12..."
    /opt/homebrew/bin/python3.12 -m venv gpt_oss_env
    chmod -R u+rwX gpt_oss_env
    source gpt_oss_env/bin/activate
}

# Install Python dependencies
install_python_deps() {
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install torch==2.4.0 torchvision
    pip install transformers==4.44.2 accelerate openai-harmony datasets "huggingface_hub[cli]"==0.24.7
    pip install supabase==2.18.0 python-dotenv==1.1.1 fastapi==0.116.1 uvicorn==0.35.0 requests==2.32.3 sentencepiece==0.2.0 numpy==2.0.2
    pip install git+https://github.com/triton-lang/triton.git@main#subdirectory=python/triton_kernels
    python -c "import transformers; print(transformers.__version__)"
    transformers --version
}

# Download model
download_model() {
    echo "Downloading model openai/gpt-oss-20b..."
    huggingface-cli download openai/gpt-oss-20b --include "*" --local-dir gpt-oss-20b/
    echo "Checking tokenizer files..."
    ls -l gpt-oss-20b/ | grep -E 'tokenizer.*\.json'
}

# Create fine-tuning script
create_fine_tune_script() {
    echo "Creating fine-tuning script for gpt-oss-20b..."
    cat > fine_tune_gpt.py << 'EOF'
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch
import os

model_name = "openai/gpt-oss-20b"
output_dir = "./gpt-oss-20b-finetuned"

# Check if model directory exists
if not os.path.exists("gpt-oss-20b"):
    raise FileNotFoundError("Model directory 'gpt-oss-20b' not found. Run setup_gpt.sh to download.")

# Load tokenizer with fallback to gpt2
try:
    tokenizer = AutoTokenizer.from_pretrained("gpt-oss-20b", local_files_only=True)
except Exception as e:
    print(f"Error loading tokenizer: {e}")
    print("Falling back to gpt2 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")

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
    gradient_accumulation_steps=8,
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
EOF
}

# Start Transformers Serve server
start_transformers_serve() {
    echo "Starting Transformers Serve server..."
    if python -c "import torch; exit(0 if torch.backends.mps.is_available() else 1)"; then
        device="auto"
        dtype="bfloat16"
        echo "MPS available, using device=auto and dtype=bfloat16"
    else
        device="cpu"
        dtype="float32"
        echo "MPS unavailable, using CPU with dtype=float32"
    fi
    if [ -d "gpt-oss-20b-finetuned" ]; then
        model_path="gpt-oss-20b-finetuned"
    else
        model_path="openai/gpt-oss-20b"
    fi
    if [ "$ENV" = "prod" ]; then
        transformers serve --host 0.0.0.0 --port 8002 --model-name-or-path "$model_path" --torch-dtype "$dtype" --device-map "$device" &
        ufw allow 8002
    else
        transformers serve --host 127.0.0.1 --port 8002 --model-name-or-path "$model_path" --torch-dtype "$dtype" --device-map "$device"
    fi
}

# Verify Transformers Serve server
verify_transformers_serve() {
    echo "Verifying Transformers Serve server..."
    sleep 10
    if [ "$ENV" = "prod" ]; then
        curl http://localhost:8002/v1/models
    else
        curl http://127.0.0.1:8002/v1/models
    fi
}

# Main execution
echo "Setting up environment for $ENV environment on $OS ($ARCH) at $(date)..."

fix_permissions
clear_caches
if [ "$OS" = "Linux" ]; then
    install_linux_deps
elif [ "$OS" = "Darwin" ]; then
    install_macos_deps
else
    echo "Error: Unsupported OS: $OS"
    exit 1
fi
setup_venv
install_python_deps
download_model
create_fine_tune_script
start_transformers_serve
verify_transformers_serve

echo "Setup complete! Transformers Serve server is running on port 8002."
echo "To fine-tune the model, run: source gpt_oss_env/bin/activate && python fine_tune_gpt.py"
if [ "$ENV" = "prod" ]; then
    echo "Ensure FastAPI is running on port 8001 and Supabase is configured."
fi