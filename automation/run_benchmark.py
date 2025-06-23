# automation/run_benchmark.py

import google.generativeai as genai
import os
import json
from datetime import datetime
from PIL import Image

# --- CONFIGURATION ---
try:
    from config import API_KEY
except ImportError:
    print("ERROR: config.py not found or API_KEY not set.")
    print("Please create automation/config.py and add your API_KEY.")
    exit()

# Configure the Gemini API
genai.configure(api_key=API_KEY)

# --- FILE & DIRECTORY PATHS ---
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
ENIGMA_PROMPTS_PATH = os.path.join(ROOT_DIR, 'ENIGMA', 'prompts.md')
VISUAL_PROMPTS_PATH = os.path.join(ROOT_DIR, 'VISUAL', 'prompts.md')
CLOCK_PROMPTS_PATH = os.path.join(ROOT_DIR, 'CLOCK', 'prompts.md')
LIPOGRAM_PROMPTS_PATH = os.path.join(ROOT_DIR, 'LIPOGRAM', 'prompts.md')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'RESULTS')
CLOCK_IMAGES_DIR = os.path.join(RESULTS_DIR, 'CLOCK_IMAGES')

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CLOCK_IMAGES_DIR, exist_ok=True)

# --- PARSING FUNCTIONS ---
def parse_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    prompts = [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit()]
    return prompts

def parse_visual_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = content.split('### ')[1:]
    prompts = []
    for block in blocks:
        lines = block.split('\n')
        prompt_text = [line.split('"')[1] for line in lines if line.startswith('- **Prompt:**') or line.startswith('- Prompt:')][0]
        image_path_line = [line for line in lines if './images/' in line][0]
        image_filename = image_path_line.split('./images/')[1].split(')')[0]
        full_image_path = os.path.join(ROOT_DIR, 'VISUAL', 'images', image_filename)
        prompts.append({"prompt": prompt_text, "image_path": full_image_path})
    return prompts

# --- BENCHMARK EXECUTION FUNCTIONS ---
def run_benchmark_on_model(model, prompts, is_visual=False):
    results = {}
    for i, data in enumerate(prompts):
        is_dict = isinstance(data, dict)
        prompt_text = data['prompt'] if is_dict else data
        print(f"  Processing prompt {i+1}/{len(prompts)}...")
        try:
            if is_visual:
                img = Image.open(data['image_path'])
                response = model.generate_content([prompt_text, img])
                results[f"{prompt_text} [{os.path.basename(data['image_path'])}]"] = response.text
            else:
                response = model.generate_content(prompt_text)
                results[prompt_text] = response.text
        except Exception as e:
            error_key = f"{prompt_text} [{os.path.basename(data['image_path'])}]" if is_dict else prompt_text
            results[error_key] = f"ERROR: {e}"
    return results

def run_relogio_benchmark():
    print("\n--- Running CLOCK Benchmark (Conceptual) ---")
    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    results = {prompt: {"status": "NOT RUN: Image generation API not configured."} for prompt in prompts}
    print("  --> CLOCK benchmark logic is conceptual. No actual images were generated.")
    return results

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")
    
    # Use a single, modern multi-modal model for all text and vision tasks
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    print("\n--- Running ENIGMA Benchmark ---")
    enigma_prompts = parse_md_file(ENIGMA_PROMPTS_PATH)
    enigma_results = run_benchmark_on_model(model, enigma_prompts)
    
    print("\n--- Running VISUAL Benchmark ---")
    visual_prompts = parse_visual_prompts(VISUAL_PROMPTS_PATH)
    visual_results = run_benchmark_on_model(model, visual_prompts, is_visual=True)

    print("\n--- Running LIPOGRAM Benchmark ---")
    lipogram_prompts = parse_md_file(LIPOGRAM_PROMPTS_PATH)
    lipogram_results = run_benchmark_on_model(model, lipogram_prompts)

    relogio_results = run_relogio_benchmark()
    
    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "model_used": 'gemini-1.5-flash-latest',
        "enigma_results": enigma_results,
        "visual_results": visual_results,
        "lipogram_results": lipogram_results,
        "relogio_results": relogio_results
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(RESULTS_DIR, f"benchmark_results_{timestamp}.json")
    
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Benchmark run complete. Results saved to:\n{results_filename}")
