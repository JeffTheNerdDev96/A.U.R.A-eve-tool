import os
import sys
import shutil
import json

# =======================================================================
# 1. MOUNT DRIVE & BUILD LLAMA.CPP TOOLCHAIN 
# =======================================================================
try:
    from google.colab import drive
    drive.mount('/content/drive/')
except ImportError:
    print("[Colab Pipeline] Running outside Google Colab environment.")

# Install Unsloth & training packages
os.system('pip install --upgrade --no-cache-dir "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"')
os.system('pip install --no-deps trl peft accelerate bitsandbytes datasets')

# Install CMake and build llama.cpp quantizer (RAM-safe 2 threads)
os.system('apt-get install -y cmake')
if os.path.exists('/content/llama.cpp'):
    shutil.rmtree('/content/llama.cpp', ignore_errors=True)
os.system('git clone https://github.com/ggerganov/llama.cpp /content/llama.cpp')
os.system('cd /content/llama.cpp && pip install -r requirements.txt')
os.system('cd /content/llama.cpp && cmake -B build && cmake --build build --config Release -j 2 --target llama-quantize')

# =======================================================================
# 2. LOAD PHI-4-MINI & CONFIGURE QLORA
# =======================================================================
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
import torch
import gc

max_seq_length = 2048
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Phi-4-mini-instruct",
    max_seq_length = max_seq_length,
    dtype = None,
    load_in_4bit = load_in_4bit,
)

# Apply Phi-4 chat template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "phi-4",
)

# Configure PEFT / LoRA target modules
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# =======================================================================
# 3. LOAD & UNIFY TRAINING DATASETS
# =======================================================================
import os
import glob
import json
import shutil
from datasets import Dataset

data_dir = "/content/drive/MyDrive/AURA/DATA"
all_samples = []

system_prompt = (
    "You are A.U.R.A. (Adaptive Underworld Recon Array), the elite tactical shipboard "
    "combat AI of the Angel Cartel in EVE Online. Provide concise, high-impact tactical advice."
)

for file_path in glob.glob(os.path.join(data_dir, "*.*")):
    fname = os.path.basename(file_path).lower()
    
    # Process JSONL files
    if fname.endswith(".jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    if "messages" in item:
                        all_samples.append({"messages": item["messages"]})
                        
    # Process JSON files
    elif fname.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if isinstance(data, list):
            for entry in data:
                if "messages" in entry:
                    all_samples.append({"messages": entry["messages"]})
                elif "name" in entry and "ship_class" in entry:
                    user_q = f"Tactical analysis and profile for {entry['name']} ({entry.get('ship_class', 'Vessel')})?"
                    asst_a = (
                        f"• Hull: {entry['name']} | Class: {entry.get('ship_class')} | Faction: {entry.get('faction')}\n"
                        f"• Role: {entry.get('role')} | Threat: {entry.get('threat_rating')}\n"
                        f"• Tank Doctrine: {entry.get('tank_doctrine')}\n"
                        f"• Engagement Range: {entry.get('optimal_engagement_range')}\n"
                        f"• Tactical Combat Notes: {entry.get('tactical_combat_notes')}"
                    )
                    all_samples.append({"messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_q},
                        {"role": "assistant", "content": asst_a}
                    ]})
                elif "name" in entry and "category" in entry:
                    user_q = f"Explain module specifications and tactical use for: {entry['name']}"
                    asst_a = (
                        f"• Module: {entry['name']} ({entry.get('category')})\n"
                        f"• Slot: {entry.get('slot_type')} | Size: {entry.get('size_class')}\n"
                        f"• Fitting: {entry.get('powergrid_mw')} MW PG, {entry.get('cpu_tf')} TF CPU\n"
                        f"• Tactical Doctrine: {entry.get('role_and_tactics')}"
                    )
                    all_samples.append({"messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_q},
                        {"role": "assistant", "content": asst_a}
                    ]})
                elif "hull" in entry and "eft" in entry:
                    user_q = f"Provide standard doctrine EFT fitting for {entry['hull']} ({entry.get('doctrine')})"
                    asst_a = f"• Role: {entry.get('role')}\n• EFT Fit:\n{entry.get('eft')}"
                    all_samples.append({"messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_q},
                        {"role": "assistant", "content": asst_a}
                    ]})
                elif "name" in entry and "region" in entry:
                    user_q = f"Intel report on solar system: {entry['name']}"
                    asst_a = (
                        f"• System: {entry['name']} | Region: {entry.get('region')} ({entry.get('constellation')})\n"
                        f"• Security Status: {entry.get('sec')} (TrueSec: {entry.get('truesec')})\n"
                        f"• Classification: {entry.get('class')} | Faction: {entry.get('faction')}"
                    )
                    all_samples.append({"messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_q},
                        {"role": "assistant", "content": asst_a}
                    ]})

dataset = Dataset.from_list(all_samples)
print(f"Total processed samples: {len(dataset)}")

def formatting_prompts_func(examples):
    convos = examples["messages"]
    texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in convos]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# =======================================================================
# 4. TRAINING WITH DRIVE & VRAM PROTECTION
# =======================================================================
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

# Output intermediate checkpoints to local VM disk to save Google Drive storage
local_chk_dir = "/content/checkpoints"

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        num_train_epochs = 3,
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = local_chk_dir,
        save_strategy = "no", # Prevents filling up drive with multi-GB intermediate checkpoints
    ),
)

trainer.train()

# =======================================================================
# 5. MERGE WEIGHTS TO LOCAL SCRATCH DISK (SAVES GOOGLE DRIVE QUOTA)
# =======================================================================
# 1. Save lightweight LoRA adapters (~50MB) directly to Drive for backup
drive_lora_dir = "/content/drive/MyDrive/AURA/model-tuned/lora_adapters"
os.makedirs(drive_lora_dir, exist_ok=True)
model.save_pretrained(drive_lora_dir)
tokenizer.save_pretrained(drive_lora_dir)
print(f"LoRA adapters saved to Drive: {drive_lora_dir}")

# 2. Save heavy merged 16-bit model (~7.5GB) to LOCAL disk instead of Drive
local_merged_dir = "/content/merged_16bit"
os.makedirs(local_merged_dir, exist_ok=True)
model.save_pretrained_merged(local_merged_dir, tokenizer, save_method="merged_16bit")

# 3. Patch tokenizer_config.json on local scratch disk
tok_cfg_path = os.path.join(local_merged_dir, "tokenizer_config.json")
if os.path.exists(tok_cfg_path):
    with open(tok_cfg_path, "r", encoding="utf-8") as f:
        tok_cfg = json.load(f)
    tok_cfg["tokenizer_class"] = "GPT2Tokenizer"
    with open(tok_cfg_path, "w", encoding="utf-8") as f:
        json.dump(tok_cfg, f, indent=2)
    print("Patched local tokenizer_config.json for BPE compatibility.")

# =======================================================================
# 6. SYSTEM MEMORY & SCRATCH CLEANUP
# =======================================================================
# Free PyTorch tensors, datasets, and optimizer states from System RAM & VRAM
for var in ['model', 'tokenizer', 'trainer', 'dataset', 'all_samples']:
    if var in globals():
        del globals()[var]

gc.collect()
torch.cuda.empty_cache()
print("System RAM and VRAM cleared.")

# Remove intermediate training checkpoints
if os.path.exists(local_chk_dir):
    shutil.rmtree(local_chk_dir)
    print("Deleted local training checkpoints.")

# =======================================================================
# 7. GGUF CONVERSION & DIRECT WRITE TO GOOGLE DRIVE
# =======================================================================
local_f16_gguf = "/content/AURA-F16.gguf"
drive_output_dir = "/content/drive/MyDrive/AURA/model-tuned/gguf"
drive_q4_gguf = os.path.join(drive_output_dir, "model_q4.gguf")

os.makedirs(drive_output_dir, exist_ok=True)

# Convert local 16-bit weights to intermediate F16 GGUF on local disk
os.system(f"python /content/llama.cpp/convert_hf_to_gguf.py {local_merged_dir} --outfile {local_f16_gguf} --outtype f16")

# Quantize directly into Google Drive as Q4_K_M (~2.2 - 2.4 GB)
os.system(f"/content/llama.cpp/build/bin/llama-quantize {local_f16_gguf} {drive_q4_gguf} q4_k_m")

# =======================================================================
# 8. FINAL SCRATCH DISK PURGE
# =======================================================================
# Delete 7.5GB F16 GGUF and 7.5GB merged safetensors from Colab VM
if os.path.exists(local_f16_gguf):
    os.remove(local_f16_gguf)
if os.path.exists(local_merged_dir):
    shutil.rmtree(local_merged_dir)

print("Purged all local scratch files.")

# Final verification
if os.path.exists(drive_q4_gguf):
    size_gb = os.path.getsize(drive_q4_gguf) / (1024 ** 3)
    print(f"\nSUCCESS! Quantized model ready in your Google Drive ({size_gb:.2f} GB):")
    print(f"-> {drive_q4_gguf}")
else:
    print("\nError: Final GGUF file was not generated.")