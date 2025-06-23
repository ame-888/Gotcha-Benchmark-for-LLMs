# automation/config.py

# IMPORTANT:
# 1. Paste your API key here.
# 2. DO NOT commit this file with the real key to a public repository.
#    If using git, you should add "automation/config.py" to your .gitignore file.

API_KEY = "YOUR_GEMINI_API_KEY_HERE"
IMAGE_API_KEY = "YOUR_IMAGE_API_KEY_HERE" # Placeholder for image generation model

# Delay in seconds between consecutive API calls to the Gemini API.
# Helps in managing rate limits. Set to 0 for no delay.
SECONDS_BETWEEN_API_CALLS = 1
