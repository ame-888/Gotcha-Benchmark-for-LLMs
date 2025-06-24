# automation/run_benchmark.py

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import openai # Import OpenAI library
import os
import json
from datetime import datetime
from PIL import Image
import time

# --- CONFIGURATION ---
try:
    from config import API_KEY as GEMINI_API_KEY, OPENAI_API_KEY, IMAGEN_API_KEY, SECONDS_BETWEEN_API_CALLS
except ImportError:
    print("ERROR: config.py not found or API keys / SECONDS_BETWEEN_API_CALLS not set.")
    print("Please create automation/config.py and add your GEMINI_API_KEY, OPENAI_API_KEY, IMAGEN_API_KEY, and SECONDS_BETWEEN_API_CALLS.")
    exit()

# Configure APIs
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
# Note: openai.api_key is deprecated for openai >= 1.0.
# Client instances are now created with the API key.
# if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
#     openai.api_key = OPENAI_API_KEY # This line will be removed

# TODO: Add configuration for Imagen API if it's different and requires initialization

# --- DEFAULT SETTINGS ---
DEFAULT_IMAGE_GENERATION_SIZE = "1024x1024" # Default size for DALL-E, etc.

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

# --- MODEL DEFINITIONS ---
# Define the models to be benchmarked
# type can be 'text', 'vision' (text + image input), 'image_generation'
MODELS_TO_BENCHMARK = []

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    MODELS_TO_BENCHMARK.extend([
        {"name": "gemini-1.5-flash-latest", "type": "vision", "provider": "google"}, # Assumed to be multimodal
        {"name": "gemini-pro", "type": "text", "provider": "google"}, # Example text-only Gemini
        # Add other Gemini models as needed, specifying their type
    ])

if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
    MODELS_TO_BENCHMARK.extend([
        {"name": "gpt-4", "type": "text", "provider": "openai"}, # Example OpenAI text model
        {"name": "gpt-3.5-turbo", "type": "text", "provider": "openai"},
        {"name": "dall-e-3", "type": "image_generation", "provider": "openai"}, # DALL-E for image generation (defaults to 1024x1024)
        {"name": "dall-e-2", "type": "image_generation", "provider": "openai", "image_params": {"size": "512x512"}}, # Example specific size
        # Add other OpenAI models as needed
    ])

# Placeholder for Imagen - assuming it might be via Google or another provider
# This will need to be updated once Imagen integration details are clear
if IMAGEN_API_KEY and IMAGEN_API_KEY != "YOUR_IMAGEN_API_KEY_HERE": # And potentially other checks
    MODELS_TO_BENCHMARK.append(
        {"name": "imagen-preview", "type": "image_generation", "provider": "google_imagen"} # Example
    )


# --- Global API Counters ---
api_calls_total = 0
api_calls_successful = 0
api_calls_failed_quota = 0
api_calls_failed_other = 0
api_calls_pending_implementation = 0 # New counter

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
def run_enigma_benchmark(model_info, client, prompts_list):
    benchmark_name = "ENIGMA"
    model_name = model_info['name']
    model_type = model_info['type']
    provider = model_info['provider']

    print(f"\n--- Running {benchmark_name} Benchmark for {model_name} ({provider}) ---")
    # Prompts are now passed as an argument: prompts_list
    results = {}

    if not prompts_list:
        print(f"DEBUG run_enigma_benchmark: No prompts provided. Skipping {benchmark_name} for {model_name}.")
        return results

    if model_type == "image_generation":
        print(f"INFO: {model_name} is an image generation model. Skipping {benchmark_name} text benchmark.")
        for prompt in prompts:
            results[prompt] = "EXCLUDED - Model is for image generation"
        return results

    for i, prompt in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)} for {model_name}: {prompt[:70]}...")
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        response_text = None

        try:
            if provider == "google":
                response = client.generate_content(prompt)
                response_text = response.text
            elif provider == "openai":
                # Assuming client is an OpenAI client instance
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = completion.choices[0].message.content
            else:
                results[prompt] = f"ERROR: Unknown provider '{provider}' for model {model_name}"
                api_calls_failed_other += 1
                continue

            results[prompt] = response_text
            api_calls_successful += 1

        except google_exceptions.ResourceExhausted as e:
            error_message = f"API Error (Google): Quota Exceeded (429) - {e.message}"
            print(f"DEBUG: Caught ResourceExhausted in {benchmark_name} for {model_name}: {e.message}")
            results[prompt] = error_message
            api_calls_failed_quota += 1
            quota_error_hit = True
        except google_exceptions.GoogleAPIError as e:
            error_message = f"API Error (Google): {type(e).__name__} - {e.message}"
            print(f"DEBUG: Caught GoogleAPIError in {benchmark_name} for {model_name}: {type(e).__name__} - {e.message}")
            results[prompt] = error_message
            api_calls_failed_other += 1
        except openai.APIStatusError as e: # Catch OpenAI specific API errors
            error_message = f"API Error (OpenAI): {type(e).__name__} - {e.status_code} - {e.message}"
            print(f"DEBUG: Caught APIStatusError in {benchmark_name} for {model_name}: {e.message}")
            if e.status_code == 429: # Quota error for OpenAI
                api_calls_failed_quota += 1
                quota_error_hit = True
            else:
                api_calls_failed_other += 1
            results[prompt] = error_message
        except openai.APIConnectionError as e: # Catch OpenAI connection errors
            error_message = f"API Error (OpenAI): ConnectionError - {e.message}"
            print(f"DEBUG: Caught APIConnectionError in {benchmark_name} for {model_name}: {e.message}")
            results[prompt] = error_message
            api_calls_failed_other += 1
        except Exception as e:
            error_message = f"Non-API Error: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name} for {model_name}: {type(e).__name__} - {str(e)}")
            results[prompt] = error_message
            api_calls_failed_other += 1

        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} for {model_name}. Skipping remaining prompts for this model in this benchmark.")
            # Fill remaining prompts as "SKIPPED_DUE_TO_QUOTA"
            for remaining_prompt_idx in range(i + 1, len(prompts)):
                results[prompts[remaining_prompt_idx]] = "SKIPPED_DUE_TO_QUOTA"
            break
    return results

def run_visual_benchmark(model_info, client, visual_prompts_data): # Argument changed
    benchmark_name = "VISUAL"
    model_name = model_info['name']
    model_type = model_info['type']
    provider = model_info['provider']

    print(f"\n--- Running {benchmark_name} Benchmark for {model_name} ({provider}) ---")
    # Prompts_data is now passed as an argument: visual_prompts_data
    results = {}

    if not visual_prompts_data: # Check the passed argument
        print(f"DEBUG run_visual_benchmark: No visual prompts data provided. Skipping {benchmark_name} for {model_name}.")
        return results

    # If a model is purely 'text', it's excluded from visual tasks.
    # Multimodal models should have type 'vision'.
    if model_type == "text":
        print(f"INFO: {model_name} is a text-only model. Skipping {benchmark_name} (visual understanding task).")
        for data in prompts_data:
            prompt_key = f"{data['prompt']} [{os.path.basename(data['image_path'])}]"
            results[prompt_key] = "EXCLUDED - Model is text-only, not suited for visual understanding"
        return results
    elif model_type == "image_generation":
        print(f"INFO: {model_name} is an image generation model. Skipping {benchmark_name} (vision understanding).")
        for data in prompts_data:
            prompt_key = f"{data['prompt']} [{os.path.basename(data['image_path'])}]"
            results[prompt_key] = "EXCLUDED - Model is for image generation, not vision understanding"
        return results


    for i, data in enumerate(prompts_data):
        prompt_key = f"{data['prompt']} [{os.path.basename(data['image_path'])}]"
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts_data)} for {model_name} ({os.path.basename(data['image_path'])})..." )
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        response_text = None

        try:
            img = Image.open(data['image_path'])
            if provider == "google": # Assumes Gemini vision model
                if model_type != "vision": # Double check, though filtered above
                     results[prompt_key] = "EXCLUDED - Model not configured for vision"
                     api_calls_failed_other +=1 # Or a better counter
                     continue
                response = client.generate_content([data['prompt'], img])
                response_text = response.text
            # Add OpenAI vision model handling here if/when available and different from text
            # For now, assuming OpenAI vision would be handled by a model type 'vision' and use a similar structure
            # or that a multimodal GPT-4 would just accept image data differently.
            # This part needs to be more concrete once we know how OpenAI vision models (non-DALL-E) are called.
            elif provider == "openai" and model_type == "vision":
                # Placeholder: Actual OpenAI vision call would depend on their API
                # This might involve base64 encoding the image and sending it as part of the prompt
                # For example:
                # import base64
                # with open(data['image_path'], "rb") as image_file:
                #    b64_image = base64.b64encode(image_file.read()).decode('utf-8')
                # response = client.chat.completions.create(
                #    model=model_name,
                #    messages=[{ "role": "user", "content": [
                #        {"type": "text", "text": data['prompt']},
                #        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                #    ]}]
                # )
                # response_text = response.choices[0].message.content
                results[prompt_key] = "PENDING_IMPLEMENTATION - OpenAI vision model call not fully implemented"
                global api_calls_pending_implementation
                api_calls_pending_implementation += 1
                continue # Skip actual call until implemented
            else:
                results[prompt_key] = f"ERROR: Provider '{provider}' or model type '{model_type}' not supported for {benchmark_name}"
                api_calls_failed_other += 1
                continue

            results[prompt_key] = response_text
            api_calls_successful += 1

        except google_exceptions.ResourceExhausted as e:
            error_message = f"API Error (Google): Quota Exceeded (429) - {e.message}"
            print(f"DEBUG: Caught ResourceExhausted in {benchmark_name} for {model_name}: {e.message}")
            results[prompt_key] = error_message
            api_calls_failed_quota += 1
            quota_error_hit = True
        except google_exceptions.GoogleAPIError as e:
            error_message = f"API Error (Google): {type(e).__name__} - {e.message}"
            print(f"DEBUG: Caught GoogleAPIError in {benchmark_name} for {model_name}: {type(e).__name__} - {e.message}")
            results[prompt_key] = error_message
            api_calls_failed_other += 1
        except openai.APIStatusError as e: # Catch OpenAI specific API errors
            error_message = f"API Error (OpenAI): {type(e).__name__} - {e.status_code} - {e.message}"
            print(f"DEBUG: Caught APIStatusError in {benchmark_name} for {model_name}: {e.message}")
            if e.status_code == 429: # Quota error for OpenAI
                api_calls_failed_quota += 1
                quota_error_hit = True
            else:
                api_calls_failed_other += 1
            results[prompt_key] = error_message
        except openai.APIConnectionError as e: # Catch OpenAI connection errors
            error_message = f"API Error (OpenAI): ConnectionError - {e.message}"
            print(f"DEBUG: Caught APIConnectionError in {benchmark_name} for {model_name}: {e.message}")
            results[prompt_key] = error_message
            api_calls_failed_other += 1
        except Exception as e:
            error_message = f"Non-API Error: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name} for {model_name}: {type(e).__name__} - {str(e)}")
            results[prompt_key] = error_message
            api_calls_failed_other += 1

        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} for {model_name}. Skipping remaining prompts for this model in this benchmark.")
            for remaining_idx in range(i + 1, len(prompts_data)):
                remaining_data = prompts_data[remaining_idx]
                prompt_key_skipped = f"{remaining_data['prompt']} [{os.path.basename(remaining_data['image_path'])}]"
                results[prompt_key_skipped] = "SKIPPED_DUE_TO_QUOTA"
            break
    return results

def run_lipogram_benchmark(model_info, client, prompts_list):
    benchmark_name = "LIPOGRAM"
    model_name = model_info['name']
    model_type = model_info['type']
    provider = model_info['provider']

    print(f"\n--- Running {benchmark_name} Benchmark for {model_name} ({provider}) ---")
    # Prompts are now passed as an argument: prompts_list
    results = {}

    if not prompts_list:
        print(f"DEBUG run_lipogram_benchmark: No prompts provided. Skipping {benchmark_name} for {model_name}.")
        return results

    if model_type == "image_generation":
        print(f"INFO: {model_name} is an image generation model. Skipping {benchmark_name} text benchmark.")
        for prompt in prompts_list: # Iterate over prompts_list
            results[prompt] = "EXCLUDED - Model is for image generation"
        return results

    # Potentially add exclusion for 'vision' if it's strictly vision and not text too.
    # For now, assuming 'vision' models like Gemini 1.5 Flash can also handle text.

    for i, prompt in enumerate(prompts_list): # Iterate over prompts_list
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)} for {model_name}: {prompt[:70]}...")
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        response_text = None
        try:
            if provider == "google":
                response = client.generate_content(prompt)
                response_text = response.text
            elif provider == "openai":
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = completion.choices[0].message.content
            else:
                results[prompt] = f"ERROR: Unknown provider '{provider}' for model {model_name}"
                api_calls_failed_other += 1
                continue

            results[prompt] = response_text
            api_calls_successful += 1
        except google_exceptions.ResourceExhausted as e:
            error_message = f"API Error (Google): Quota Exceeded (429) - {e.message}"
            print(f"DEBUG: Caught ResourceExhausted in {benchmark_name} for {model_name}: {e.message}")
            results[prompt] = error_message
            api_calls_failed_quota += 1
            quota_error_hit = True
        except google_exceptions.GoogleAPIError as e:
            error_message = f"API Error (Google): {type(e).__name__} - {e.message}"
            print(f"DEBUG: Caught GoogleAPIError in {benchmark_name} for {model_name}: {type(e).__name__} - {e.message}")
            results[prompt] = error_message
            api_calls_failed_other += 1
        except openai.APIStatusError as e:
            error_message = f"API Error (OpenAI): {type(e).__name__} - {e.status_code} - {e.message}"
            print(f"DEBUG: Caught APIStatusError in {benchmark_name} for {model_name}: {e.message}")
            if e.status_code == 429:
                api_calls_failed_quota += 1
                quota_error_hit = True
            else:
                api_calls_failed_other += 1
            results[prompt] = error_message
        except openai.APIConnectionError as e:
            error_message = f"API Error (OpenAI): ConnectionError - {e.message}"
            print(f"DEBUG: Caught APIConnectionError in {benchmark_name} for {model_name}: {e.message}")
            results[prompt] = error_message
            api_calls_failed_other += 1
        except Exception as e:
            error_message = f"Non-API Error: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name} for {model_name}: {type(e).__name__} - {str(e)}")
            results[prompt] = error_message
            api_calls_failed_other += 1

        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} for {model_name}. Skipping remaining prompts for this model in this benchmark.")
            for remaining_prompt_idx in range(i + 1, len(prompts)):
                results[prompts[remaining_prompt_idx]] = "SKIPPED_DUE_TO_QUOTA"
            break
    return results

def run_relogio_benchmark(model_info, client, clock_prompts_list): # Argument changed
    benchmark_name = "CLOCK"
    model_name = model_info['name']
    model_type = model_info['type']
    provider = model_info['provider']

    print(f"\n--- Running {benchmark_name} Benchmark for {model_name} ({provider}) ---")
    # Prompts are now passed as an argument: clock_prompts_list
    results = {}

    if not clock_prompts_list: # Check the passed argument
        print(f"DEBUG run_relogio_benchmark: No CLOCK prompts provided. Skipping for {model_name}.")
        return results

    # Check if the model is suitable for image generation
    is_image_generation_model = model_type == "image_generation"
    can_generate_images_flag = model_info.get("can_generate_images", False)

    if not (is_image_generation_model or can_generate_images_flag):
        print(f"INFO: {model_name} (type: {model_type}, can_generate_images: {can_generate_images_flag}) "
              f"is not configured for image generation. Skipping {benchmark_name}.")
        for prompt in prompts:
            results[prompt] = {
                "status": f"EXCLUDED - Model not configured for image generation",
                "notes": f"Type: {model_type}, Can Generate Images Flag: {can_generate_images_flag}",
                "image_path": ""
            }
        return results

    # Specific exclusion for gemini-1.5-flash-latest if it's primarily for vision understanding,
    # even if it were to have can_generate_images = True, one might want to override.
    # For now, the general check above should suffice if its `can_generate_images` is False or not set.
    # If gemini-1.5-flash-latest had `can_generate_images: True` but we still wanted to exclude it here,
    # a more specific check would be needed. The current code has a specific check for it as a vision model.
    # Let's simplify: if can_generate_images is explicitly set, it should be honored unless a specific override exists.
    # The previous specific exclusion for gemini-1.5-flash-latest (lines 485-494 in old code) will be removed
    # in favor of relying on `model_info`'s `can_generate_images` flag.
    # If 'gemini-1.5-flash-latest' is type 'vision' and 'can_generate_images' is false/unset, it will be excluded by the check above.

    for i, prompt_text in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)} for {model_name}: {prompt_text[:70]}...")
        global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
        api_calls_total += 1
        quota_error_hit = False
        image_path_or_url = None
        status_message = "Error"
        error_notes = ""

        try:
            if provider == "openai" and model_type == "image_generation": # DALL-E
                # Ensure client is OpenAI client
                image_params = model_info.get("image_params", {})
                image_size = image_params.get("size", DEFAULT_IMAGE_GENERATION_SIZE)

                response = client.images.generate(
                    model=model_name, # e.g., "dall-e-3"
                    prompt=prompt_text,
                    n=1,
                    size=image_size
                )
                image_url = response.data[0].url
                # Optional: Download the image and save locally
                # For now, just storing the URL
                image_path_or_url = image_url
                status_message = "Generated via OpenAI"
                api_calls_successful += 1
            elif provider == "google_imagen": # Placeholder for Imagen
                 # This block needs to be implemented with actual Imagen API calls
                status_message = "PENDING_IMPLEMENTATION - Imagen call not implemented"
                error_notes = "Imagen API call needs to be added."
                print(f"    SKIPPING Imagen call for {prompt_text[:30]}... (not implemented)")
                global api_calls_pending_implementation
                api_calls_pending_implementation +=1
            # Add Gemini image generation here if a model supports it (e.g. Gemini 2.0 Flash with image gen)
            # elif provider == "google" and model_info.get("can_generate_images", False): # Ensure this key exists in model_info
            #     # Call Gemini image generation API
            #     status_message = "PENDING_IMPLEMENTATION - Gemini Image Gen not implemented"
            #     error_notes = "Gemini image generation API call needs to be added."
            #     global api_calls_pending_implementation
            #     api_calls_pending_implementation +=1
            else:
                status_message = f"EXCLUDED - Provider '{provider}' or model '{model_name}' not configured for image generation in this script."
                error_notes = f"Model type is '{model_type}'."
                # This is an exclusion, not a pending item or failure in the usual sense.
                # It might not need to increment api_calls_failed_other unless it's unexpected.
                # For now, let's assume it's an expected exclusion.

            if image_path_or_url: # Successfully generated
                 # Create a filename for the image (even if it's a URL, for consistency in reporting)
                clean_prompt = "".join(c if c.isalnum() else "_" for c in prompt_text[:50])
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                image_filename = f"{i+1:03d}_{clean_prompt}_{model_name.replace('-','_')}_{timestamp}.png" # .png may not be accurate if URL
                saved_image_path = os.path.join(CLOCK_IMAGES_DIR, image_filename) # This is a conceptual path if URL

                results[prompt_text] = {
                    "status": status_message,
                    "notes": f"Image URL: {image_path_or_url}" if image_path_or_url.startswith("http") else "Image saved conceptually",
                    "image_path": saved_image_path # Store our conceptual local path or the URL itself
                }
            else: # No image generated due to error or pending implementation
                 results[prompt_text] = {
                    "status": status_message,
                    "notes": error_notes,
                    "image_path": ""
                }

        except openai.APIStatusError as e:
            error_message = f"API Error (OpenAI DALL-E): {type(e).__name__} - {e.status_code} - {e.message}"
            print(f"DEBUG: Caught APIStatusError in {benchmark_name} for {model_name}: {e.message}")
            if e.status_code == 429:
                api_calls_failed_quota += 1
                quota_error_hit = True
            else:
                api_calls_failed_other += 1
            results[prompt_text] = {"status": error_message, "notes": str(e), "image_path": ""}
        # Add specific error handling for Imagen API if different
        except Exception as e:
            error_message = f"Non-API Error during image generation: {type(e).__name__} - {str(e)}"
            print(f"DEBUG: Caught generic Exception in {benchmark_name} for {model_name}: {type(e).__name__} - {str(e)}")
            results[prompt_text] = {"status": error_message, "notes": str(e), "image_path": ""}
            api_calls_failed_other +=1


        if SECONDS_BETWEEN_API_CALLS > 0 and not quota_error_hit:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

        if quota_error_hit:
            print(f"INFO: API Quota Exceeded in {benchmark_name} for {model_name}. Skipping remaining prompts.")
            for remaining_prompt_idx in range(i + 1, len(prompts)):
                results[prompts[remaining_prompt_idx]] = {
                    "status": "SKIPPED_DUE_TO_QUOTA", "notes": "", "image_path": ""
                }
            break
    return results

if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")

    # Pre-parse all prompt files
    print("Parsing prompt files...")
    enigma_prompts_list = parse_md_file(ENIGMA_PROMPTS_PATH)
    visual_prompts_data_list = parse_visual_prompts(VISUAL_PROMPTS_PATH)
    lipogram_prompts_list = parse_md_file(LIPOGRAM_PROMPTS_PATH)
    clock_prompts_list = parse_md_file(CLOCK_PROMPTS_PATH)
    print("Prompt files parsed.")

    # Initialize clients for each provider based on MODELS_TO_BENCHMARK
    clients = {}
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        # genai.configure already called
        pass # Gemini models are initialized per-model later
    if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
        clients["openai"] = openai.OpenAI(api_key=OPENAI_API_KEY)
    # Initialize Imagen client if necessary
    # if IMAGEN_API_KEY and IMAGEN_API_KEY != "YOUR_IMAGEN_API_KEY_HERE":
    #    clients["google_imagen"] = SomeImagenClient(api_key=IMAGEN_API_KEY)


    all_benchmark_results = {} # Store results per model

    for model_info in MODELS_TO_BENCHMARK:
        model_name = model_info["name"]
        provider = model_info["provider"]
        model_type = model_info["type"]
        client_instance = None

        print(f"\n===== Starting benchmarks for model: {model_name} (Provider: {provider}, Type: {model_type}) =====")

        try:
            if provider == "google":
                client_instance = genai.GenerativeModel(model_name)
            elif provider == "openai":
                client_instance = clients.get("openai")
                if not client_instance:
                    print(f"WARNING: OpenAI client not initialized for {model_name}. Skipping.")
                    continue
            elif provider == "google_imagen":
                # client_instance = clients.get("google_imagen")
                # if not client_instance:
                # print(f"WARNING: Imagen client not initialized for {model_name}. Skipping image generation.")
                # For now, image generation for Imagen is handled as PENDING_IMPLEMENTATION within run_relogio_benchmark
                pass # No separate client instance needed if handled within function or using google common client
            else:
                print(f"WARNING: Unknown provider '{provider}' for model {model_name}. Skipping.")
                continue
        except Exception as e:
            print(f"ERROR: Could not initialize model {model_name}: {e}")
            all_benchmark_results[model_name] = {
                "error": f"Failed to initialize model: {e}",
                "enigma_results": {}, "visual_results": {},
                "lipogram_results": {}, "relogio_results": {}
            }
            continue

        current_model_results = {
            "enigma_results": {},
            "visual_results": {},
            "lipogram_results": {},
            "relogio_results": {}
        }

        # Run benchmarks based on model type
        if model_type in ["text", "vision"]:
            current_model_results["enigma_results"] = run_enigma_benchmark(model_info, client_instance, enigma_prompts_list)
            current_model_results["lipogram_results"] = run_lipogram_benchmark(model_info, client_instance, lipogram_prompts_list)

        if model_type == "vision":
            current_model_results["visual_results"] = run_visual_benchmark(model_info, client_instance, visual_prompts_data_list)
            # Potentially, vision models could also do image generation (e.g. Gemini 2.0 with image gen)
            # This logic might need to be more granular if a model is both "vision" and "image_generation"
            if model_name == "gemini-1.5-flash-latest": # Example: if this specific model can also do image gen
                 # current_model_results["relogio_results"] = run_relogio_benchmark(model_info, client_instance)
                 # For now, run_relogio_benchmark has specific exclusion for gemini-1.5-flash used as vision.
                 # If it were to be tested for image generation, a different model_info or capability flag would be better.
                 pass


        if model_type == "image_generation":
            current_model_results["relogio_results"] = run_relogio_benchmark(model_info, client_instance, clock_prompts_list)
            # Image generation models typically don't do text or vision understanding benchmarks
            # The benchmark functions themselves handle the "EXCLUDED" part.
            # To be explicit here, you could ensure other results are empty or marked using the pre-parsed prompt lists.
            if not current_model_results["enigma_results"]: # if not already run and excluded by type
                current_model_results["enigma_results"] = {p: "EXCLUDED - Model is for image generation" for p in enigma_prompts_list}
            if not current_model_results["lipogram_results"]:
                current_model_results["lipogram_results"] = {p: "EXCLUDED - Model is for image generation" for p in lipogram_prompts_list}
            if not current_model_results["visual_results"]:
                 current_model_results["visual_results"] = {f"{data['prompt']} [{os.path.basename(data['image_path'])}]": "EXCLUDED - Model is for image generation" for data in visual_prompts_data_list}


        all_benchmark_results[model_name] = current_model_results

    # Consolidate all results into the final structure
    final_output_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "models_tested": list(all_benchmark_results.keys()),
        "results_by_model": all_benchmark_results
        # Individual benchmark types are now nested under each model
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(RESULTS_DIR, f"benchmark_results_{timestamp}.json")
    try:
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump(final_output_results, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Benchmark run complete. Results saved to:\n{results_filename}")
    except Exception as e:
        print(f"ERROR: Could not save results to JSON file: {e}")
        print("Intermediate results (if any):")
        print(json.dumps(final_output_results, indent=4, ensure_ascii=False))

    print("\n--- API Call Summary ---")
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
    print(f"API Calls Pending Implementation: {api_calls_pending_implementation}")
    print("-------------------------")
