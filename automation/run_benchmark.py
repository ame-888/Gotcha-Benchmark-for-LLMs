# automation/run_benchmark.py

import google.generativeai as genai
import os
import json
import re # Added for sanitizing filenames
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont # Added ImageDraw and ImageFont for text on placeholder

# --- CONFIGURATION ---
try:
    from config import API_KEY, IMAGE_API_KEY # Added IMAGE_API_KEY
except ImportError:
    # Attempt to import only API_KEY if IMAGE_API_KEY is missing, for partial functionality
    try:
        from config import API_KEY
        IMAGE_API_KEY = None # Set to None if not found
        print("WARNING: IMAGE_API_KEY not found in config.py. CLOCK benchmark will use placeholders.")
    except ImportError:
        print("ERROR: config.py not found or API_KEY not set.")
        print("Please create automation/config.py and add your API_KEY.")
        print("For CLOCK benchmark, also add IMAGE_API_KEY.")
        exit()

# Configure the Gemini API
if API_KEY and API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not configured in automation/config.py. ENIGMA and VISUAL benchmarks may fail or use defaults.")


# Define file paths relative to the repository root
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
ENIGMA_PROMPTS_PATH = os.path.join(ROOT_DIR, 'ENIGMA', 'prompts.md')
VISUAL_PROMPTS_PATH = os.path.join(ROOT_DIR, 'VISUAL', 'prompts.md')
CLOCK_PROMPTS_PATH = os.path.join(ROOT_DIR, 'CLOCK', 'prompts.md')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'RESULTS') # This is .../automation/RESULTS
CLOCK_IMAGE_DIR = os.path.join(RESULTS_DIR, 'CLOCK_IMAGES') # .../automation/RESULTS/CLOCK_IMAGES

# Create results directories if they don't exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CLOCK_IMAGE_DIR, exist_ok=True)


# --- UTILITY FUNCTIONS ---

def sanitize_filename(text, max_length=100):
    """Sanitizes text to be a valid filename."""
    # Remove invalid characters
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace whitespace with underscores
    text = re.sub(r'\s+', '_', text).strip('_')
    # Truncate to max_length
    return text[:max_length]

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

def run_clock_benchmark():
    """Runs the CLOCK (image generation) benchmark by creating placeholder images."""
    print("\n--- Running CLOCK Benchmark ---")
    if not os.path.exists(CLOCK_PROMPTS_PATH):
        print(f"  WARNING: CLOCK prompts file not found at {CLOCK_PROMPTS_PATH}")
        return {"error": "CLOCK prompts file not found."}

    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    if not prompts:
        print(f"  INFO: No prompts found in {CLOCK_PROMPTS_PATH}. Skipping CLOCK benchmark.")
        return {"info": "No prompts found."}

    results = {}
    # Ensure CLOCK_IMAGE_DIR exists (it's also created globally, but good to double-check)
    os.makedirs(CLOCK_IMAGE_DIR, exist_ok=True)

    # Try to load a default font, fallback to a basic one if not found
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()

    for i, prompt_text_full in enumerate(prompts):
        # Prompts from parse_md_file are like "1. Actual prompt text"
        # We need to extract the actual prompt text for filename and image content
        actual_prompt_text = prompt_text_full.split('.', 1)[-1].strip()
        print(f"  Processing CLOCK prompt {i+1}/{len(prompts)}: \"{actual_prompt_text[:50]}...\"")

        # Sanitize prompt for filename
        base_filename = sanitize_filename(actual_prompt_text, max_length=50)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_filename = f"{i+1:03d}_{base_filename}_{timestamp}.png"
        image_path = os.path.join(CLOCK_IMAGE_DIR, image_filename)

        # Simulate API call - Create a placeholder image
        try:
            if IMAGE_API_KEY and IMAGE_API_KEY != "YOUR_IMAGE_API_KEY_HERE":
                # NOTE: This is where you would add the actual API call
                # For example, using OpenAI DALL-E:
                # from openai import OpenAI
                # client = OpenAI(api_key=IMAGE_API_KEY)
                # response = client.images.generate(
                # model="dall-e-3", # or "dall-e-2"
                # prompt=actual_prompt_text,
                # size="1024x1024", # or other supported sizes
                # quality="standard", # or "hd"
                # n=1,
                # response_format="url" # or "b64_json"
                # )
                # image_url = response.data[0].url
                # # Download image from URL and save to image_path
                # import requests
                # img_data = requests.get(image_url).content
                # with open(image_path, 'wb') as handler:
                # handler.write(img_data)
                # results[prompt_text_full] = f"Image saved to: {image_path} (REAL API CALL - NOT IMPLEMENTED YET, placeholder used)"

                # For now, we fall through to placeholder if logic above is commented out
                raise NotImplementedError("Actual API call not implemented in this script version.")

            # Placeholder image generation
            img = Image.new('RGB', (256, 256), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            text_content = f"Placeholder for:\n{actual_prompt_text}"

            # Basic text wrapping
            lines = []
            words = text_content.split()
            current_line = ""
            for word in words:
                if d.textbbox((0,0), current_line + word, font=font)[2] < img.width - 20 : # Check width
                    current_line += word + " "
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            y_text = 10
            for line in lines:
                d.text((10,y_text), line.strip(), fill=(255,255,0), font=font)
                bbox = d.textbbox((0,0), line.strip(), font=font)
                y_text += bbox[3] - bbox[1] + 5 # Add line height + 5px spacing


            img.save(image_path)
            results[prompt_text_full] = f"Placeholder image saved to: {image_path}"
            print(f"    Placeholder image saved: {image_filename}")

        except NotImplementedError:
             # This block is hit if actual API call is intended but not implemented
            img = Image.new('RGB', (256, 256), color = (137, 73, 109)) # Different color for this case
            d = ImageDraw.Draw(img)
            d.text((10,10), f"Real API call not implemented.\nPrompt: {actual_prompt_text[:100]}...", fill=(255,255,255), font=font)
            img.save(image_path)
            results[prompt_text_full] = f"Placeholder (API not impl.) image saved to: {image_path}"
            print(f"    Placeholder image (API not impl.) saved: {image_filename}")

        except Exception as e:
            error_message = f"ERROR generating placeholder for '{actual_prompt_text[:50]}...': {e}"
            print(f"    {error_message}")
            results[prompt_text_full] = error_message

    if not prompts: # Handles case where CLOCK_PROMPTS_PATH exists but is empty
        results["info"] = "No prompts found to process."

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
    clock_results = run_clock_benchmark()

    # Collate results
    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "enigma_results": enigma_results,
        "visual_results": visual_results,
        "clock_results": clock_results
    }

    # Save results to a timestamped JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(RESULTS_DIR, f"benchmark_results_{timestamp}.json")

    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Benchmark run complete. Results saved to:\n{results_filename}")
