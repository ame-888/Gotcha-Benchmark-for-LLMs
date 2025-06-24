# automation/config.py

# --- General Configuration ---
SECONDS_BETWEEN_API_CALLS = 1 # Time in seconds to wait between API calls

# --- Provider Selection ---
# Choose your preferred API providers for text and image generation.
# Supported text providers: "gemini", "openai" (once implemented)
# Supported image providers: "dalle", "google_imagen" (once implemented), or None
TEXT_API_PROVIDER = "gemini"
IMAGE_API_PROVIDER = None # Or "dalle", "google_imagen" once you have keys and they are implemented

# --- API Credentials & Model Preferences ---
# IMPORTANT:
# 1. Fill in your API keys and any model preferences below.
# 2. DO NOT commit this file with real keys to a public repository.
#    If using git, ensure "automation/config.py" is in your .gitignore file.

API_CREDENTIALS = {
    "gemini": {
        "api_key": "YOUR_GEMINI_API_KEY_HERE"
        # No specific model name needed here yet, as run_benchmark.py uses a default
        # or could be enhanced to pick a model from here if specified.
    },
    "openai": {
        "api_key": "YOUR_OPENAI_API_KEY_HERE",
        "default_text_model": "gpt-4o", # Example: "gpt-4", "gpt-3.5-turbo"
        "default_image_model": "dall-e-3" # Example: "dall-e-2"
    },
    "google_imagen": { # For Google Cloud Vertex AI Imagen
        "project_id": "YOUR_GOOGLE_CLOUD_PROJECT_ID",
        "location": "us-central1", # e.g., "us-central1"
        "model_id": "imagegeneration@006", # Example: "imagegeneration@005", "imagegeneration@006"
        # Authentication for Vertex AI is typically handled via GOOGLE_APPLICATION_CREDENTIALS
        # environment variable pointing to a service account JSON key file, or by running
        # `gcloud auth application-default login`. No explicit API key in the code is usually needed here.
    }
    # Add other providers here in the future, e.g.:
    # "anthropic": {
    #     "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
    #     "default_text_model": "claude-3-opus-20240229"
    # },
    # "stabilityai": {
    #     "api_key": "YOUR_STABILITY_AI_KEY_HERE",
    #     "engine_id": "stable-diffusion-xl-1024-v1-0" # Example engine
    # }
}

# --- (Optional) Model specific configurations ---
# You could also define more detailed model configurations if needed,
# for example, to pass specific parameters like temperature, max_tokens, etc.
# MODEL_CONFIGS = {
#     "gemini_specific_settings": {
#         "temperature": 0.7
#     },
#     "openai_gpt4_settings": {
#         "temperature": 0.5,
#         "max_tokens": 1500
#     }
# }
# These would then be retrieved and passed to the API calling functions in run_benchmark.py
