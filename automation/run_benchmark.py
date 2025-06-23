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
    print(f"DEBUG parse_md_file: Received path: {file_path}")
    if not os.path.exists(file_path):
        print(f"DEBUG parse_md_file: File does NOT exist at path: {file_path}")
        return []
    print(f"DEBUG parse_md_file: File exists. Attempting to read...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"DEBUG parse_md_file: Read {len(lines)} lines.")
        if len(lines) < 20: # If file is short (like ENIGMA/prompts.md should be if empty or with few prompts)
            print(f"DEBUG parse_md_file: --- Entire content of {os.path.basename(file_path)} ---")
            for i, line_content in enumerate(lines):
                print(f"DEBUG parse_md_file: Raw Line {i}: {line_content.rstrip()}")
            print(f"DEBUG parse_md_file: --- End of content ---")
        else: # If file is longer, just print first 5
            print(f"DEBUG parse_md_file: First 5 lines raw:")
            for i in range(min(5, len(lines))):
                print(f"DEBUG parse_md_file: Line {i}: {lines[i].strip()[:150]}")
    except Exception as e:
        print(f"DEBUG parse_md_file: Error reading file {file_path}: {e}")
        return []

    prompts = [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit()]
    print(f"DEBUG parse_md_file: Found {len(prompts)} prompts in {os.path.basename(file_path)} after filtering.")
    return prompts

def parse_visual_prompts(file_path):
    """Parses the more complex VISUAL prompts markdown file."""
    # Adding similar debug lines for visual prompts parsing for consistency, though it wasn't the issue.
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
    """Runs the ENIGMA (text-only) benchmark."""
    print("\n--- Running ENIGMA Benchmark ---")
    print(f"DEBUG run_enigma_benchmark: ENIGMA_PROMPTS_PATH is defined as: {ENIGMA_PROMPTS_PATH}")
    absolute_enigma_path = os.path.abspath(ENIGMA_PROMPTS_PATH)
    print(f"DEBUG run_enigma_benchmark: Absolute path for ENIGMA prompts: {absolute_enigma_path}")
    print(f"DEBUG run_enigma_benchmark: File exists at this absolute path? {os.path.exists(absolute_enigma_path)}")

    prompts = parse_md_file(ENIGMA_PROMPTS_PATH)
    results = {}
    if not prompts:
        print("DEBUG run_enigma_benchmark: No prompts returned from parse_md_file for ENIGMA. Skipping ENIGMA benchmark processing loop.")
        return results # Ensure we return empty results if no prompts
    for i, prompt in enumerate(prompts):
        print(f"  Processing ENIGMA prompt {i+1}/{len(prompts)}: {prompt[:70]}...") # Log part of prompt
        try:
            response = model.generate_content(prompt)
            results[prompt] = response.text
            # print(f"DEBUG: ENIGMA Prompt {i+1} - Response: {response.text[:100]}...")
        except Exception as e:
            print(f"DEBUG run_enigma_benchmark: ERROR processing ENIGMA prompt {i+1} ({prompt[:70]}...): {e}")
            results[prompt] = f"ERROR: {e}"
    return results

def run_visual_benchmark(model):
    """Runs the VISUAL (multi-modal) benchmark."""
    print("\n--- Running VISUAL Benchmark ---")
    prompts_data = parse_visual_prompts(VISUAL_PROMPTS_PATH)
    results = {}
    if not prompts_data:
        print("DEBUG run_visual_benchmark: No prompts data returned from parse_visual_prompts. Skipping VISUAL benchmark.")
        return results
    for i, data in enumerate(prompts_data):
        print(f"  Processing VISUAL prompt {i+1}/{len(prompts_data)} ({os.path.basename(data['image_path'])})...")
        try:
            img = Image.open(data['image_path'])
            # Note: The model variable here should be the multimodal one.
            # If using separate models, ensure 'model' is the correct one.
            response = model.generate_content([data['prompt'], img]) # Pass prompt and image directly
            results[f"{data['prompt']} [{os.path.basename(data['image_path'])}]"] = response.text
        except Exception as e:
            print(f"DEBUG run_visual_benchmark: ERROR processing VISUAL prompt {i+1} ({data['prompt'][:70]}...): {e}")
            results[f"{data['prompt']} [{os.path.basename(data['image_path'])}]"] = f"ERROR: {e}"
    return results

def run_lipogram_benchmark(model):
    """Runs the LIPOGRAM (text-only, constrained) benchmark."""
    print("\n--- Running LIPOGRAM Benchmark ---")
    prompts = parse_md_file(LIPOGRAM_PROMPTS_PATH)
    results = {}
    if not prompts:
        print("DEBUG run_lipogram_benchmark: No prompts found for LIPOGRAM. Skipping.")
        return results
    for i, prompt in enumerate(prompts):
        print(f"  Processing LIPOGRAM prompt {i+1}/{len(prompts)}: {prompt[:70]}...")
        try:
            # For this task, we can add a system prompt to reinforce the instruction
            # full_prompt = f"Follow this instruction precisely:\n\n{prompt}" # This was an older approach
            response = model.generate_content(prompt) # Simpler, direct prompt
            results[prompt] = response.text
        except Exception as e:
            print(f"DEBUG run_lipogram_benchmark: ERROR processing LIPOGRAM prompt {i+1} ({prompt[:70]}...): {e}")
            results[prompt] = f"ERROR: {e}"
    return results

def run_relogio_benchmark():
    """
    CONCEPTUAL IMPLEMENTATION for the CLOCK (image generation) benchmark.
    This function demonstrates the required logic but requires a specific image
    generation API (e.g., Google Imagen via Vertex AI, or OpenAI DALL-E 3)
    and separate authentication to be fully functional.
    The API_KEY from config.py is for Gemini (text/vision understanding),
    not for image generation services like Imagen.
    """
    print("\n--- Running CLOCK Benchmark (Conceptual) ---")
    # Ensure CLOCK_PROMPTS_PATH is parsed.
    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    results = {}
    if not prompts:
        print("DEBUG run_relogio_benchmark: No prompts found for CLOCK. Skipping.")
        return results

    # --- SETUP FOR A REAL IMPLEMENTATION ---
    # The Gemini API (using google-generativeai with API_KEY) is for multimodal
    # understanding (text, image input) and text generation.
    # For IMAGE GENERATION (creating an image from a prompt), a separate API
    # and model are needed (e.g., Google's Imagen via Vertex AI, DALL-E, etc.).
    # The IMAGE_API_KEY in config.py is a placeholder for such a service.

    # 1. You would need to import the specific library for the image generation service.
    #    e.g., from google.cloud import aiplatform (for Imagen)
    #    e.g., from openai import OpenAI (for DALL-E)
    # 2. Initialize the client with its specific credentials (e.g., IMAGE_API_KEY from config.py if it were for this).
    #    e.g., aiplatform.init(project='your-gcp-project', location='us-central1')
    #    e.g., client = OpenAI(api_key=config.IMAGE_API_KEY) # If IMAGE_API_KEY was for OpenAI
    # 3. Call the image generation model with the prompt.

    for i, prompt in enumerate(prompts):
        print(f"  Processing CLOCK prompt {i+1}/{len(prompts)} (Conceptual): {prompt[:70]}...")

        # This section remains conceptual. No API call for image generation is made.
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_filename = f"conceptual_clock_prompt_{i+1}_{timestamp}.png"
        saved_image_path = os.path.join(CLOCK_IMAGES_DIR, image_filename)

        results[prompt] = {
            "status": "CONCEPTUAL: Image generation not implemented. Requires a separate image generation API/service.",
            "notes": "This script does not perform image generation. The CLOCK test prompts are listed, but no images are created with the current Gemini API setup.",
            "intended_example_output_path": saved_image_path
        }
        # Example of error handling if an API call was made:
        # except Exception as e:
        #     results[prompt] = {"status": f"ERROR during image generation: {e}", "expected_output_path": ""}

    print("  --> CLOCK benchmark is conceptual and does not generate images with the current setup.")
    print("      To implement image generation, integrate a dedicated service like Imagen or DALL-E.")
    return results


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")

    # --- Model Initialization ---
    # Option 1: Use a single, modern multi-modal model for all text and vision tasks if appropriate
    # model_name = 'gemini-1.5-flash-latest' # or 'gemini-1.5-pro-latest'
    # main_model = genai.GenerativeModel(model_name)
    # text_model_for_script = main_model
    # vision_model_for_script = main_model

    # Option 2: Use specific models as in an older version (if preferred or for specific capabilities)
    # Ensure these model names are correct and available for your API_KEY.
    try:
        # Using gemini-1.5-flash-latest for all as per user's last provided script.
        # If issues arise, can revert to specific text/vision models if needed.
        shared_model_name = 'gemini-1.5-flash-latest'
        text_model_for_script = genai.GenerativeModel(shared_model_name)
        vision_model_for_script = genai.GenerativeModel(shared_model_name) # Flash is multimodal
        print(f"Using model: {shared_model_name} for all tasks.")
    except Exception as e:
        print(f"ERROR: Could not initialize generative models: {e}")
        print("Please ensure your API_KEY is valid and the model names are correct.")
        exit()
    
    # Run all benchmarks
    # Pass the appropriate model to each benchmark function.
    # If using a single model for all:
    # enigma_results = run_enigma_benchmark(main_model)
    # visual_results = run_visual_benchmark(main_model)
    # lipogram_results = run_lipogram_benchmark(main_model)
    
    # If using separate text/vision models (as per an older structure):
    enigma_results = run_enigma_benchmark(text_model_for_script)
    visual_results = run_visual_benchmark(vision_model_for_script) # visual_model should handle multimodal
    lipogram_results = run_lipogram_benchmark(text_model_for_script)
    
    relogio_results = run_relogio_benchmark() # This is conceptual, doesn't use a model yet.

    # Collate all results into a single dictionary
    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "model_used": shared_model_name if 'shared_model_name' in locals() else "gemini-pro/gemini-pro-vision", # Adjust if model init changes
        "enigma_results": enigma_results,
        "visual_results": visual_results,
        "lipogram_results": lipogram_results,
        "relogio_results": relogio_results
    }

    # Save the consolidated results to a single timestamped JSON file
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
