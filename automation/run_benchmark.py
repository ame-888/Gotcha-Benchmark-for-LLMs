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

# Define file paths relative to the repository root
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
ENIGMA_PROMPTS_PATH = os.path.join(ROOT_DIR, 'ENIGMA', 'prompts.md')
VISUAL_PROMPTS_PATH = os.path.join(ROOT_DIR, 'VISUAL', 'prompts.md')
CLOCK_PROMPTS_PATH = os.path.join(ROOT_DIR, 'CLOCK', 'prompts.md')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'RESULTS')

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)


# --- PARSING FUNCTIONS ---

def parse_md_file(file_path):
    """Parses a simple markdown file with prompts starting with a number."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    prompts = [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit()]
    return prompts

def parse_visual_prompts(file_path):
    """Parses the more complex VISUAL prompts markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by the '###' header for each test case
    blocks = content.split('### ')[1:]
    prompts = []
    for block in blocks:
        lines = block.split('\n')
        prompt_text = [line.split('"')[1] for line in lines if line.startswith('- **Prompt:**')][0]
        image_path_line = [line for line in lines if './images/' in line][0]
        image_filename = image_path_line.split('./images/')[1].split(')')[0]
        full_image_path = os.path.join(ROOT_DIR, 'VISUAL', 'images', image_filename)
        prompts.append({"prompt": prompt_text, "image_path": full_image_path})
    return prompts


# --- BENCHMARK EXECUTION FUNCTIONS ---

def run_enigma_benchmark(model):
    """Runs the ENIGMA (text-only) benchmark."""
    print("\n--- Running ENIGMA Benchmark ---")
    prompts = parse_md_file(ENIGMA_PROMPTS_PATH)
    results = {}
    for i, prompt in enumerate(prompts):
        print(f"  Processing ENIGMA prompt {i+1}/{len(prompts)}...")
        try:
            response = model.generate_content(prompt)
            results[prompt] = response.text
        except Exception as e:
            results[prompt] = f"ERROR: {e}"
    return results

def run_visual_benchmark(model):
    """Runs the VISUAL (multi-modal) benchmark."""
    print("\n--- Running VISUAL Benchmark ---")
    prompts_data = parse_visual_prompts(VISUAL_PROMPTS_PATH)
    results = {}
    for i, data in enumerate(prompts_data):
        print(f"  Processing VISUAL prompt {i+1}/{len(prompts_data)} ({os.path.basename(data['image_path'])})...")
        try:
            img = Image.open(data['image_path'])
            prompt_parts = [data['prompt'], img]
            response = model.generate_content(prompt_parts)
            results[f"{data['prompt']} [{os.path.basename(data['image_path'])}]"] = response.text
        except Exception as e:
            results[f"{data['prompt']} [{os.path.basename(data['image_path'])}]"] = f"ERROR: {e}"
    return results

def run_relogio_benchmark():
    """Placeholder for the RELÓGIO (image generation) benchmark."""
    print("\n--- Running RELÓGIO Benchmark ---")
    # This requires an image generation model and a different API (e.g., Imagen).
    # This is a placeholder to show where the logic would go.
    print("  SKIPPED: Image generation model API not implemented.")
    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    results = {prompt: "NOT IMPLEMENTED" for prompt in prompts}
    return results


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")

    # Initialize models
    # Use a vision model for the VISUAL benchmark
    vision_model = genai.GenerativeModel('gemini-pro-vision')
    # Use a standard text model for ENIGMA
    text_model = genai.GenerativeModel('gemini-pro')

    # Run benchmarks
    enigma_results = run_enigma_benchmark(text_model)
    visual_results = run_visual_benchmark(vision_model)
    relogio_results = run_relogio_benchmark()

    # Collate results
    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "enigma_results": enigma_results,
        "visual_results": visual_results,
        "relogio_results": relogio_results
    }

    # Save results to a timestamped JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(RESULTS_DIR, f"benchmark_results_{timestamp}.json")

    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Benchmark run complete. Results saved to:\n{results_filename}")
