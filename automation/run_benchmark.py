# automation/run_benchmark.py

import google.generativeai as genai
import os
import json
from datetime import datetime
from PIL import Image

# --- CONFIGURATION ---
# This script uses the Google Gemini API. The CLOCK benchmark requires a separate
# image generation API (like Google's Imagen or OpenAI's DALL-E 3), which is
# conceptually implemented but not fully functional without the specific API setup.
try:
    from config import API_KEY
except ImportError:
    print("ERROR: config.py not found or API_KEY not set.")
    print("Please create automation/config.py and add your API_KEY.")
    exit()

# Configure the Gemini API
genai.configure(api_key=API_KEY)

# --- FILE & DIRECTORY PATHS ---
# Define file paths relative to the repository root for better portability
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
ENIGMA_PROMPTS_PATH = os.path.join(ROOT_DIR, 'ENIGMA', 'prompts.md')
VISUAL_PROMPTS_PATH = os.path.join(ROOT_DIR, 'VISUAL', 'prompts.md')
CLOCK_PROMPTS_PATH = os.path.join(ROOT_DIR, 'CLOCK', 'prompts.md')
LIPOGRAM_PROMPTS_PATH = os.path.join(ROOT_DIR, 'LIPOGRAM', 'prompts.md')

# Define output directories
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'RESULTS')
CLOCK_IMAGES_DIR = os.path.join(RESULTS_DIR, 'CLOCK_IMAGES')

# Create results directories if they don't exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CLOCK_IMAGES_DIR, exist_ok=True)


# --- PARSING FUNCTIONS ---
# These functions read the prompts from your markdown files.

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

def run_lipogram_benchmark(model):
    """Runs the new LIPOGRAM (text-only, constrained) benchmark."""
    print("\n--- Running LIPOGRAM Benchmark ---")
    prompts = parse_md_file(LIPOGRAM_PROMPTS_PATH)
    results = {}
    for i, prompt in enumerate(prompts):
        print(f"  Processing LIPOGRAM prompt {i+1}/{len(prompts)}...")
        try:
            # For this task, we can add a system prompt to reinforce the instruction
            full_prompt = f"Follow this instruction precisely:\n\n{prompt}"
            response = model.generate_content(full_prompt)
            results[prompt] = response.text
        except Exception as e:
            results[prompt] = f"ERROR: {e}"
    return results

def run_relogio_benchmark():
    """
    CONCEPTUAL IMPLEMENTATION for the CLOCK (image generation) benchmark.
    This function demonstrates the required logic but requires a specific image
    generation API (e.g., Google Imagen via Vertex AI, or OpenAI DALL-E 3)
    and separate authentication to be fully functional.
    """
    print("\n--- Running CLOCK Benchmark (Conceptual) ---")
    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    results = {}

    # --- SETUP FOR A REAL IMPLEMENTATION ---
    # 1. You would need to import the specific library, e.g.:
    #    from google.cloud import aiplatform
    #    from openai import OpenAI
    # 2. You would need to initialize the client with its own credentials:
    #    aiplatform.init(project='your-gcp-project', location='us-central1')
    #    client = OpenAI(api_key="YOUR_OPENAI_KEY")
    # 3. You would call the specific image generation model.

    for i, prompt in enumerate(prompts):
        print(f"  Processing CLOCK prompt {i+1}/{len(prompts)}...")

        # In a real implementation, you would uncomment and adapt this section:
        # try:
        #     # Example for DALL-E 3:
        #     # response = client.images.generate(
        #     #     model="dall-e-3",
        #     #     prompt=prompt,
        #     #     size="1024x1024",
        #     #     quality="standard",
        #     #     n=1,
        #     # )
        #     # image_url = response.data[0].url
        #     # Here you would download the image from the URL and save it.
        #     # For this placeholder, we just note the intended path.

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"clock_prompt_{i+1}_{timestamp}.png"
        saved_image_path = os.path.join(CLOCK_IMAGES_DIR, image_filename)

        # We store the *intended path* of the generated image in the results.
        # This confirms the script tried to run it and tells you where to find the image.
        results[prompt] = {
            "status": "NOT RUN: Image generation API not configured.",
            "expected_output_path": saved_image_path
        }
        # except Exception as e:
        #     results[prompt] = {"status": f"ERROR: {e}", "expected_output_path": ""}

    print("  --> CLOCK benchmark logic is conceptual. No actual images were generated.")
    return results


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")

    # Initialize models from the Gemini API
    vision_model = genai.GenerativeModel('gemini-pro-vision')
    text_model = genai.GenerativeModel('gemini-pro')

    # Run all benchmarks
    enigma_results = run_enigma_benchmark(text_model)
    visual_results = run_visual_benchmark(vision_model)
    lipogram_results = run_lipogram_benchmark(text_model)
    relogio_results = run_relogio_benchmark()

    # Collate all results into a single dictionary
    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "enigma_results": enigma_results,
        "visual_results": visual_results,
        "lipogram_results": lipogram_results,
        "relogio_results": relogio_results
    }

    # Save the consolidated results to a single timestamped JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(RESULTS_DIR, f"benchmark_results_{timestamp}.json")

    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Benchmark run complete. Results saved to:\n{results_filename}")
