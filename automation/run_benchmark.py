# automation/run_benchmark.py

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions # Import Google API exceptions
import os
import json
from datetime import datetime
from PIL import Image
import time # Import the time module

# --- CONFIGURATION ---
try:
    from config import API_KEY, SECONDS_BETWEEN_API_CALLS
except ImportError:
    print("ERROR: config.py not found or API_KEY / SECONDS_BETWEEN_API_CALLS not set.")
    print("Please create automation/config.py and add your API_KEY and SECONDS_BETWEEN_API_CALLS.")
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

# --- Global API Counters ---
api_calls_total = 0
api_calls_successful = 0
api_calls_failed_quota = 0
api_calls_failed_other = 0

# --- PARSING FUNCTIONS ---
def parse_md_file(file_path):
    print(f"DEBUG parse_md_file: Received path: {file_path}")
    if not os.path.exists(file_path):
        print(f"DEBUG parse_md_file: File does NOT exist at path: {file_path}")
        return []
    print(f"DEBUG parse_md_file: File exists. Attempting to read...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"DEBUG parse_md_file: Read {len(lines)} lines.")
        if len(lines) < 20:
            # Short file, print all
            pass # Already has detailed debug prints from original
        else:
            # Long file, print first 5
            pass # Already has detailed debug prints from original
    except Exception as e:
        print(f"DEBUG parse_md_file: Error reading file {file_path}: {e}")
        return []
    prompts = [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit()]
    print(f"DEBUG parse_md_file: Found {len(prompts)} prompts in {os.path.basename(file_path)} after filtering.")
    return prompts

def parse_visual_prompts(file_path):
    print(f"DEBUG parse_visual_prompts: Received path: {file_path}")
    if not os.path.exists(file_path):
        print(f"DEBUG parse_visual_prompts: File does NOT exist at path: {file_path}")
        return []
    print(f"DEBUG parse_visual_prompts: File exists. Attempting to read...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"DEBUG parse_visual_prompts: Read content of length {len(content)}.")
    except Exception as e:
        print(f"DEBUG parse_visual_prompts: Error reading file {file_path}: {e}")
        return []
    blocks = content.split('### ')[1:]
    prompts = []
    for block_idx, block in enumerate(blocks):
        lines = block.split('\n')
        try:
            prompt_text_lines = [line.split('"')[1] for line in lines if line.startswith('- **Prompt:**') or line.startswith('- Prompt:')]
            if not prompt_text_lines:
                print(f"DEBUG parse_visual_prompts: No prompt text found in block {block_idx}.")
                continue
            prompt_text = prompt_text_lines[0]
            image_path_lines = [line for line in lines if './images/' in line]
            if not image_path_lines:
                print(f"DEBUG parse_visual_prompts: No image path found in block {block_idx}.")
                continue
            image_path_line = image_path_lines[0]
            image_filename = image_path_line.split('./images/')[1].split(')')[0]
            full_image_path = os.path.join(ROOT_DIR, 'VISUAL', 'images', image_filename)
            if not os.path.exists(full_image_path):
                print(f"DEBUG parse_visual_prompts: Image file does NOT exist at path: {full_image_path}")
                continue
            prompts.append({"prompt": prompt_text, "image_path": full_image_path})
        except IndexError as e:
            print(f"DEBUG parse_visual_prompts: Error parsing block {block_idx}: {e}. Block content: {block[:100]}...")
            continue
    print(f"DEBUG parse_visual_prompts: Found {len(prompts)} visual prompts after parsing.")
    return prompts

# --- BENCHMARK EXECUTION FUNCTIONS ---
def run_enigma_benchmark(model):
    benchmark_name = "ENIGMA"
    print(f"\n--- Running {benchmark_name} Benchmark ---")
    prompts = parse_md_file(ENIGMA_PROMPTS_PATH)
    results = {}
    if not prompts: 
        print(f"DEBUG run_enigma_benchmark: No prompts returned. Skipping {benchmark_name} benchmark.")
        return results
    for i, prompt in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)}: {prompt[:70]}...")
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        try:
            response = model.generate_content(prompt)
            results[prompt] = response.text
            api_calls_successful += 1
        except google_exceptions.ResourceExhausted as e:
            error_message = f"API Error: Quota Exceeded (429) - {e.message}"
            print(f"DEBUG: Caught ResourceExhausted in {benchmark_name}: {e.message}")
            results[prompt] = error_message
            api_calls_failed_quota += 1
            quota_error_hit = True
        except google_exceptions.GoogleAPIError as e:
            error_message = f"API Error: {type(e).__name__} - {e.message}"
            print(f"DEBUG: Caught GoogleAPIError in {benchmark_name}: {type(e).__name__} - {e.message}")
            results[prompt] = error_message
            api_calls_failed_other += 1
        except Exception as e:
            error_message = f"Non-API Error: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name}: {type(e).__name__} - {str(e)}")
            results[prompt] = error_message
            api_calls_failed_other += 1 # Or a new counter for non-API errors if desired

        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit: # No need to sleep if we are about to break
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} benchmark. Skipping remaining prompts for this benchmark.")
            break
    return results

def run_visual_benchmark(model):
    benchmark_name = "VISUAL"
    print(f"\n--- Running {benchmark_name} Benchmark ---")
    prompts_data = parse_visual_prompts(VISUAL_PROMPTS_PATH)
    results = {}
    if not prompts_data: 
        print(f"DEBUG run_visual_benchmark: No prompts data. Skipping {benchmark_name} benchmark.")
        return results
    for i, data in enumerate(prompts_data):
        prompt_key = f"{data['prompt']} [{os.path.basename(data['image_path'])}]"
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts_data)} ({os.path.basename(data['image_path'])})..." )
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        try:
            img = Image.open(data['image_path'])
            response = model.generate_content([data['prompt'], img])
            results[prompt_key] = response.text
            api_calls_successful += 1
        except google_exceptions.ResourceExhausted as e:
            error_message = f"API Error: Quota Exceeded (429) - {e.message}"
            print(f"DEBUG: Caught ResourceExhausted in {benchmark_name}: {e.message}")
            results[prompt_key] = error_message
            api_calls_failed_quota += 1
            quota_error_hit = True
        except google_exceptions.GoogleAPIError as e:
            error_message = f"API Error: {type(e).__name__} - {e.message}"
            print(f"DEBUG: Caught GoogleAPIError in {benchmark_name}: {type(e).__name__} - {e.message}")
            results[prompt_key] = error_message
            api_calls_failed_other += 1
        except Exception as e:
            error_message = f"Non-API Error: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name}: {type(e).__name__} - {str(e)}")
            results[prompt_key] = error_message
            api_calls_failed_other += 1

        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit: # No need to sleep if we are about to break
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} benchmark. Skipping remaining prompts for this benchmark.")
            break
    return results

def run_lipogram_benchmark(model):
    benchmark_name = "LIPOGRAM"
    print(f"\n--- Running {benchmark_name} Benchmark ---")
    prompts = parse_md_file(LIPOGRAM_PROMPTS_PATH)
    results = {}
    if not prompts: 
        print(f"DEBUG run_lipogram_benchmark: No prompts. Skipping {benchmark_name} benchmark.")
        return results
    for i, prompt in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)}: {prompt[:70]}...")
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        try:
            response = model.generate_content(prompt)
            results[prompt] = response.text
            api_calls_successful += 1
        except google_exceptions.ResourceExhausted as e:
            error_message = f"API Error: Quota Exceeded (429) - {e.message}"
            print(f"DEBUG: Caught ResourceExhausted in {benchmark_name}: {e.message}")
            results[prompt] = error_message
            api_calls_failed_quota += 1
            quota_error_hit = True
        except google_exceptions.GoogleAPIError as e:
            error_message = f"API Error: {type(e).__name__} - {e.message}"
            print(f"DEBUG: Caught GoogleAPIError in {benchmark_name}: {type(e).__name__} - {e.message}")
            results[prompt] = error_message
            api_calls_failed_other += 1
        except Exception as e:
            error_message = f"Non-API Error: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name}: {type(e).__name__} - {str(e)}")
            results[prompt] = error_message
            api_calls_failed_other += 1

        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit: # No need to sleep if we are about to break
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} benchmark. Skipping remaining prompts for this benchmark.")
            break
    return results

def run_relogio_benchmark():
    print("\n--- Running CLOCK Benchmark (Conceptual) ---")
    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    results = {}
    if not prompts: 
        print("DEBUG run_relogio_benchmark: No prompts for CLOCK. Skipping.")
        return results
    for i, prompt in enumerate(prompts):
        print(f"  Processing CLOCK prompt {i+1}/{len(prompts)} (Conceptual): {prompt[:70]}...")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # image_filename = f"conceptual_clock_prompt_{i+1}_{timestamp}.png" # No longer creating placeholder paths
        # saved_image_path = os.path.join(CLOCK_IMAGES_DIR, image_filename)
        results[prompt] = {
            "status": "EXCLUDED - Script does not implement image generation",
            "notes": "This script does not currently call an image generation API for the CLOCK test. Prompts are listed for potential manual use or future script enhancement.",
            # "intended_example_output_path": saved_image_path # Not relevant if not generating
        }
    print("  --> CLOCK benchmark: Image generation is not implemented in this script.")
    print("      Results for CLOCK prompts are marked as 'EXCLUDED'.")
    return results

if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")
    try:
        shared_model_name = 'gemini-1.5-flash-latest'
        text_model_for_script = genai.GenerativeModel(shared_model_name)
        vision_model_for_script = genai.GenerativeModel(shared_model_name)
        print(f"Using model: {shared_model_name} for all tasks.")
    except Exception as e:
        print(f"ERROR: Could not initialize generative models: {e}")
        print("Please ensure your API_KEY is valid and the model names are correct.")
        exit()
    
    enigma_results = run_enigma_benchmark(text_model_for_script)
    visual_results = run_visual_benchmark(vision_model_for_script)
    lipogram_results = run_lipogram_benchmark(text_model_for_script)
    relogio_results = run_relogio_benchmark()

    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "model_used": shared_model_name, 
        "enigma_results": enigma_results,
        "visual_results": visual_results,
        "lipogram_results": lipogram_results,
        "relogio_results": relogio_results
    }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(RESULTS_DIR, f"benchmark_results_{timestamp}.json")
    try:
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Benchmark run complete. Results saved to:\n{results_filename}")
    except Exception as e:
        print(f"ERROR: Could not save results to JSON file: {e}")
        print("Intermediate results (if any):")
        print(json.dumps(all_results, indent=4, ensure_ascii=False))

    print("\n--- API Call Summary ---")
    print(f"Total API Calls Attempted: {api_calls_total}")
    print(f"Successful API Calls: {api_calls_successful}")
    print(f"Failed API Calls (Quota): {api_calls_failed_quota}")
    print(f"Failed API Calls (Other): {api_calls_failed_other}")
    print("-------------------------")
