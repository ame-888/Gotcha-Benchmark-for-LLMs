# automation/config.py

# IMPORTANT:
# 1. Paste your API key here.
# 2. DO NOT commit this file with the real key to a public repository.
#    If using git, you should add "automation/config.py" to your .gitignore file.

API_KEY = "YOUR_GEMINI_API_KEY_HERE" # For Gemini text and vision models
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE" # For OpenAI text models (e.g., GPT-4) and DALL-E

# Potentially other distinct API keys if needed, e.g., if Imagen has a separate key
IMAGEN_API_KEY = "YOUR_IMAGEN_API_KEY_HERE" # Placeholder for Imagen, if it uses a separate key from Gemini/OpenAI

SECONDS_BETWEEN_API_CALLS = 5
