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
    from config import (
        SECONDS_BETWEEN_API_CALLS,
        TEXT_API_PROVIDER,
        IMAGE_API_PROVIDER,
        API_CREDENTIALS
    )
except ImportError:
    print("ERROR: config.py not found or key configuration variables are missing.")
    print("Please ensure automation/config.py exists and contains: ")
    print("SECONDS_BETWEEN_API_CALLS, TEXT_API_PROVIDER, IMAGE_API_PROVIDER, API_CREDENTIALS")
    exit()

# Note: Global API configuration (like genai.configure) will now be handled
# within specific API calling functions or when clients are initialized.

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

# --- INTERNAL API CALLING FUNCTIONS ---
def _call_text_api(prompt_content, provider_name: str, provider_config: dict) -> str:
    """
    Calls the appropriate text generation API based on the provider.
    `prompt_content` can be a string or a list (for multimodal, e.g., text + image).
    Returns the text response or an error message string.
    """
    global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
    api_calls_total += 1

    if provider_name == "gemini":
        try:
            api_key = provider_config.get("api_key")
            if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
                return "ERROR: Gemini API key not configured in config.py."

            # Configure Gemini API specifically for this call if not already globally done
            # For simplicity, we assume genai is imported. If we support multiple versions
            # or need to avoid global config, this part might need more care.
            # genai.configure(api_key=api_key) # This might reconfigure globally.
            # A better approach for multiple providers would be to use client instances.
            # For now, let's assume the key is primary.

            # Determine model for Gemini - using a default for now
            # This could be enhanced to pull from provider_config if specified there
            gemini_model_name = provider_config.get("default_text_model", "gemini-1.5-flash-latest")
            model = genai.GenerativeModel(gemini_model_name)

            # Ensure genai.configure has been called with the key for this session
            # This is tricky if multiple Gemini keys were supported.
            # For now, we rely on the first valid key setting it.
            # A robust multi-key or multi-instance approach is more complex.
            # The simplest for now is that config.py's Gemini key is used for genai.configure once.
            # Let's refine this: we should configure per call or use distinct clients if possible.
            # The current genai SDK seems to favor a global configuration.
            # For this refactor, let's assume the initial genai.configure (if any) is sufficient
            # OR that we reconfigure if needed.
            # Reconfiguring globally per call is not ideal.
            # Let's assume the key from provider_config should be used.
            # The genai SDK doesn't easily support per-call API keys with a shared client.
            # For now, we'll rely on a single Gemini configuration done at startup using the selected key.
            # This part will need refinement if we want to support multiple Gemini accounts simultaneously.

            # The `genai.configure` should ideally be done once at startup based on the *selected* Gemini key.
            # For now, the benchmark functions will pass the model object.
            # This function should expect an initialized model object for Gemini.
            # Let's change the paradigm: this function receives an initialized client/model.
            # So, the calling code (in main) should initialize the client.
            # This function will be simplified if it receives the client.
            # --- REVISED APPROACH: This function will receive an initialized client ---
            # This will be handled when benchmark functions are updated.
            # For now, let's stick to the original plan of this function handling the call.

            # Assuming genai is configured with the key from provider_config.
            # This is a simplification for this step.
            configured_gemini_key = genai.API_KEY
            if not configured_gemini_key or configured_gemini_key != provider_config.get("api_key"):
                 # This indicates a mismatch or that genai hasn't been configured with THIS key.
                 # This part is tricky with the current genai SDK global config.
                 # For this step, we'll proceed assuming it's configured.
                 # A proper solution would involve instance-based clients if SDK supports,
                 # or careful management of global state.
                 # print("Warning: Gemini API key in provider_config may not match active genai configuration.")
                 # For now, we'll just use the globally configured genai.
                 pass


            model_to_use = genai.GenerativeModel(gemini_model_name) # Use default or configured model
            response = model_to_use.generate_content(prompt_content)
            api_calls_successful += 1
            return response.text
        except google_exceptions.ResourceExhausted as e:
            api_calls_failed_quota += 1
            return f"API Error: Quota Exceeded (429) for Gemini - {e.message}"
        except google_exceptions.GoogleAPIError as e:
            api_calls_failed_other += 1
            return f"API Error: Gemini ({type(e).__name__}) - {e.message}"
        except Exception as e:
            api_calls_failed_other += 1
            return f"Non-API Error (Gemini): {type(e).__name__} - {str(e)}"

    elif provider_name == "openai":
        # Placeholder for OpenAI text API call
        api_calls_failed_other +=1 # Count as other failure for now
        return f"ERROR: OpenAI text API not yet implemented. Prompt: {str(prompt_content)[:100]}"
    else:
        api_calls_failed_other += 1
        return f"ERROR: Unsupported text API provider: {provider_name}"

def _call_image_api(prompt_text: str, provider_name: str, provider_config: dict) -> dict:
    """
    Calls the appropriate image generation API based on the provider.
    Returns a dictionary: {"status": "SUCCESS/EXCLUDED/ERROR", "image_path": "path/to/img" or None, "message": "details"}
    """
    global api_calls_total, api_calls_successful, api_calls_failed_quota, api_calls_failed_other
    api_calls_total += 1 # All attempts are counted

    if not provider_name:
        api_calls_failed_other +=1 # Or a specific counter for config errors
        return {"status": "EXCLUDED", "image_path": None, "message": "No image provider configured."}

    if provider_name == "dalle": # Assuming "dalle" will be used for OpenAI DALL-E
        api_calls_failed_other +=1
        return {"status": "EXCLUDED", "image_path": None, "message": f"DALL-E (OpenAI) image API not yet implemented. Prompt: {prompt_text[:100]}"}
    elif provider_name == "google_imagen":
        api_calls_failed_other +=1
        return {"status": "EXCLUDED", "image_path": None, "message": f"Google Imagen image API not yet implemented. Prompt: {prompt_text[:100]}"}
    else:
        api_calls_failed_other +=1
        return {"status": "EXCLUDED", "image_path": None, "message": f"Unsupported or unknown image API provider: {provider_name}"}


# --- BENCHMARK EXECUTION FUNCTIONS ---
def run_enigma_benchmark(text_provider_name: str, text_provider_config: dict):
    benchmark_name = "ENIGMA"
    print(f"\n--- Running {benchmark_name} Benchmark using {text_provider_name} ---")
    prompts = parse_md_file(ENIGMA_PROMPTS_PATH)
    results = {}
    if not prompts:
        print(f"DEBUG run_enigma_benchmark: No prompts returned. Skipping {benchmark_name} benchmark.")
        return results

    quota_error_hit_for_benchmark = False
    for i, prompt_text in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)}: {prompt_text[:70]}...")

        response_text = _call_text_api(prompt_text, text_provider_name, text_provider_config)
        results[prompt_text] = response_text

        # Check if this specific call hit a quota error to stop this benchmark run
        # This relies on a specific string format from _call_text_api for quota errors
        if "API Error: Quota Exceeded" in response_text:
            quota_error_hit_for_benchmark = True
            print(f"INFO: API Quota Exceeded in {benchmark_name} with {text_provider_name}. Skipping remaining prompts for this benchmark.")
            break # Stop processing more prompts for THIS benchmark type

        if SECONDS_BETWEEN_API_CALLS > 0: # No sleep if we are breaking due to quota
            time.sleep(SECONDS_BETWEEN_API_CALLS)

    return results

def run_visual_benchmark(text_provider_name: str, text_provider_config: dict): # Simplified for Phase 1
    benchmark_name = "VISUAL"
    print(f"\n--- Running {benchmark_name} Benchmark using {text_provider_name} for text component ---")
    # Note: Visual analysis (image understanding) is more complex with provider abstraction.
    # Current Gemini _call_text_api can handle multimodal if prompt_content is a list [text, Image].
    # If text_provider_name is not Gemini, this will need careful handling.

    prompts_data = parse_visual_prompts(VISUAL_PROMPTS_PATH)
    results = {}
    if not prompts_data:
        print(f"DEBUG run_visual_benchmark: No prompts data. Skipping {benchmark_name} benchmark.")
        return results

    quota_error_hit_for_benchmark = False
    for i, data in enumerate(prompts_data):
        prompt_text = data['prompt']
        image_path = data['image_path']
        prompt_key = f"{prompt_text} [{os.path.basename(image_path)}]"
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts_data)} ({os.path.basename(image_path)})...")

        response_text = "ERROR: Visual processing logic not fully updated for multi-API."

        if text_provider_name == "gemini":
            try:
                img = Image.open(image_path)
                # For Gemini, _call_text_api can handle a list [text, Image]
                response_text = _call_text_api([prompt_text, img], text_provider_name, text_provider_config)
            except FileNotFoundError:
                response_text = f"ERROR: Image file not found at {image_path}"
            except Exception as e:
                response_text = f"ERROR: Could not open or process image {image_path}: {str(e)}"
        else:
            # For other text providers, they might not support direct image input in the same way.
            # This benchmark fundamentally requires multimodal input for the selected text provider,
            # or a separate vision provider.
            # For Phase 1, if not Gemini, we mark as not supported by this benchmark's current logic for that provider.
            response_text = f"ERROR: Visual benchmark with provider '{text_provider_name}' needs specific multimodal handling or a dedicated vision provider. Not yet implemented."
            # We still increment a counter as an attempt was made by the script structure
            global api_calls_total, api_calls_failed_other
            api_calls_total +=1 # Count this as an attempt that results in an internal error/skip
            api_calls_failed_other +=1


        results[prompt_key] = response_text

        if "API Error: Quota Exceeded" in response_text:
            quota_error_hit_for_benchmark = True
            print(f"INFO: API Quota Exceeded in {benchmark_name} with {text_provider_name}. Skipping remaining prompts.")
            break

        if SECONDS_BETWEEN_API_CALLS > 0:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

    return results

def run_lipogram_benchmark(text_provider_name: str, text_provider_config: dict):
    benchmark_name = "LIPOGRAM"
    print(f"\n--- Running {benchmark_name} Benchmark using {text_provider_name} ---")
    prompts = parse_md_file(LIPOGRAM_PROMPTS_PATH)
    results = {}
    if not prompts:
        print(f"DEBUG run_lipogram_benchmark: No prompts. Skipping {benchmark_name} benchmark.")
        return results

    quota_error_hit_for_benchmark = False
    for i, prompt_text in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)}: {prompt_text[:70]}...")

        response_text = _call_text_api(prompt_text, text_provider_name, text_provider_config)
        results[prompt_text] = response_text

        if "API Error: Quota Exceeded" in response_text:
            quota_error_hit_for_benchmark = True
            print(f"INFO: API Quota Exceeded in {benchmark_name} with {text_provider_name}. Skipping remaining prompts.")
            break

        if SECONDS_BETWEEN_API_CALLS > 0:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

    return results

def run_relogio_benchmark(image_provider_name: str, image_provider_config: dict):
    benchmark_name = "CLOCK"
    print(f"\n--- Running {benchmark_name} Benchmark using {image_provider_name or 'No Provider'} ---")
    prompts = parse_md_file(CLOCK_PROMPTS_PATH)
    results = {}
    if not prompts:
        print(f"DEBUG run_relogio_benchmark: No prompts for CLOCK. Skipping.")
        return results

    # Quota error for image generation is handled per call by _call_image_api if it occurs
    # but let's add a flag if we want to stop early for this benchmark type too.
    quota_error_hit_for_benchmark = False
    for i, prompt_text in enumerate(prompts):
        print(f"  Processing {benchmark_name} prompt {i+1}/{len(prompts)}: {prompt_text[:70]}...")

        # _call_image_api expects provider_name and provider_config.
        # If image_provider_name is None, _call_image_api handles it.
        image_result_dict = _call_image_api(prompt_text, image_provider_name, image_provider_config)
        results[prompt_text] = image_result_dict # Store the whole dict {status, image_path, message}

        if image_result_dict.get("status") == "ERROR" and "Quota Exceeded" in image_result_dict.get("message", ""):
            # This check depends on how _call_image_api formats quota errors for specific image APIs
            quota_error_hit_for_benchmark = True
            print(f"INFO: API Quota Exceeded in {benchmark_name} with {image_provider_name}. Skipping remaining prompts.")
            break

        if SECONDS_BETWEEN_API_CALLS > 0:
            time.sleep(SECONDS_BETWEEN_API_CALLS)

    return results

if __name__ == "__main__":
    print("Initializing Benchmark Automation Script...")

    # --- Retrieve Provider Configurations ---
    selected_text_provider = TEXT_API_PROVIDER.lower()
    selected_image_provider = IMAGE_API_PROVIDER.lower() if IMAGE_API_PROVIDER else None

    text_provider_config = API_CREDENTIALS.get(selected_text_provider)
    image_provider_config = API_CREDENTIALS.get(selected_image_provider) if selected_image_provider else None

    if not text_provider_config:
        print(f"ERROR: Configuration for TEXT_API_PROVIDER '{TEXT_API_PROVIDER}' not found in API_CREDENTIALS.")
        exit()

    # --- Initialize Models/Clients (Example for Gemini, to be expanded) ---
    # This section will be replaced by calls to abstracted API functions later.
    # For now, we handle Gemini initialization here if selected.
    
    # text_model_client = None # This will hold the initialized client or model object
    # vision_model_client = None # For visual test, might be same as text or different
    # image_generation_client = None # For CLOCK test

    # TEMP: The old script used one model for text and vision (Gemini).
    # The new benchmark functions will take provider configs.
    # For now, we're just setting up to pass these configs.
    # Actual client initialization will move into _call_text_api / _call_image_api.

    print(f"Selected Text API Provider: {selected_text_provider}")
    if text_provider_config.get('default_text_model'):
        print(f"  Using Text Model (from config): {text_provider_config['default_text_model']}")
    elif selected_text_provider == "gemini":
         print(f"  Using Gemini (default model will be used by its SDK or in _call_text_api)")


    if selected_image_provider:
        print(f"Selected Image API Provider: {selected_image_provider}")
        if image_provider_config and image_provider_config.get('default_image_model'):
            print(f"  Using Image Model (from config): {image_provider_config['default_image_model']}")
        elif image_provider_config:
             print(f"  Using {selected_image_provider} (default model will be used by its SDK or in _call_image_api)")
    else:
        print("No Image API Provider selected. CLOCK test will be EXCLUDED.")

    # --- Run Benchmarks ---
    # These functions will be updated in next steps to accept and use provider configs

    # enigma_results = run_enigma_benchmark(text_model_for_script) # OLD
    # visual_results = run_visual_benchmark(vision_model_for_script) # OLD
    # lipogram_results = run_lipogram_benchmark(text_model_for_script) # OLD
    # relogio_results = run_relogio_benchmark() # OLD

    # --- Run Benchmarks ---
    # Pass the selected provider name and its specific configuration dictionary

    # Initialize Gemini API if it's the selected text provider
    # This is a temporary measure. Ideally, client initialization should be cleaner,
    # perhaps within the _call_text_api or managed by a central client factory.
    # For now, this ensures genai is configured if Gemini is used.
    if selected_text_provider == "gemini":
        gemini_api_key = text_provider_config.get("api_key")
        if gemini_api_key and gemini_api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=gemini_api_key)
                print(f"Configured Gemini API with key for {selected_text_provider}.")
            except Exception as e:
                print(f"ERROR: Failed to configure Gemini API with provided key: {e}")
                # Potentially exit or mark all Gemini calls as failed
        else:
            print("Warning: Gemini API key not found or is placeholder in config; Gemini calls may fail.")

    print("\nStarting benchmark runs...")
    enigma_results = run_enigma_benchmark(selected_text_provider, text_provider_config)
    visual_results = run_visual_benchmark(selected_text_provider, text_provider_config) # Still uses text_provider for vision if Gemini
    lipogram_results = run_lipogram_benchmark(selected_text_provider, text_provider_config)
    relogio_results = run_relogio_benchmark(selected_image_provider, image_provider_config)

    # --- Aggregate and Save Results ---
    # The "model_used" will need to be more dynamic based on providers
    # For now, let's use the text provider and its configured model as primary
    model_display_name = f"{selected_text_provider}"
    if text_provider_config.get('default_text_model'):
        model_display_name += f" ({text_provider_config['default_text_model']})"
    elif selected_text_provider == "gemini":
        model_display_name += " (gemini-1.5-flash-latest or SDK default)"


    all_results = {
        "benchmark_run_date": datetime.now().isoformat(),
        "text_api_provider": selected_text_provider,
        "image_api_provider": selected_image_provider if selected_image_provider else "None",
        "model_details_from_config": { # Storing a snapshot of what was configured
            "text": text_provider_config,
            "image": image_provider_config
        },
        "model_used_display": model_display_name, # A simplified display name
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
