# Gotcha-Benchmark-for-LLMs

## 🏆 Leaderboard 🏆

**For a comprehensive overview of model performances, please see the [Current Leaderboard](./LEADERBOARD.md).**

---

A benchmark for testing LLM reasoning in image generation (CLOCK), lateral thinking (ENIGMA), restricted text generation (LIPOGRAM) and visual analysis (VISUAL).

## Our Philosophy: Benchmark by Template

The Gotcha Benchmark is built on the idea of "Benchmark by Template." Instead of a static set of questions, we focus on the *underlying principles* of what makes a good reasoning challenge. This makes the benchmark more resilient to "training data contamination," where models simply memorize answers instead of learning the skill.

For a detailed explanation of this approach and the principles behind each test category, please see our [Benchmark Philosophy](./PHILOSOPHY.md).

## The Benchmarks

This project is divided into four distinct tests:

1.  **[CLOCK (Clock)](./CLOCK/prompts.md):** Evaluates the model's ability to generate spatially and logically accurate analog clock faces from precise time prompts. See the [scoring criteria here](./CLOCK/scoring.md).

2.  **[ENIGMA (Riddles)](./ENIGMA/prompts.md):** Evaluates the model's ability to solve verbal riddles that require critical thinking and bypassing obvious, data-driven answers. See the [scoring criteria here](./ENIGMA/scoring.md).

3.  **[VISUAL (Deceptive Images)](./VISUAL/prompts.md):** Evaluates the model's ability to analyze an image for what it actually contains, rather than defaulting to a "known" answer about a similar-looking optical illusion or concept. This tests a model's ability to prioritize direct perception over learned patterns. See the [scoring criteria here](./VISUAL/scoring.md).

4.  **[LIPOGRAM](./LIPOGRAM/prompts.md):** Evaluates the model's creative ability and cognitive control by challenging it to write a lengthy text without using a specific letter. See the [scoring criteria here](./LIPOGRAM/scoring.md).

## How to Use This Benchmark

1.  **Select a model** you wish to test.
2.  **Run the prompts** from each of the four benchmark sections (`CLOCK`, `ENIGMA`, `VISUAL`, `LIPOGRAM`).
3.  **Score the results** honestly based on the provided scoring criteria for each section.
2.  **Share your findings!** You can submit your results by creating an "Issue" or a "Pull Request" with a new results file in the `/RESULTS` directory. You can then update the main [Leaderboard](./LEADERBOARD.md).

---

## Automated Benchmark Script

This repository includes a Python script to automate the process of running three of the four benchmarks: ENIGMA, VISUAL, and CLOCK. The LIPOGRAM benchmark is currently performed manually.

*   For ENIGMA and VISUAL benchmarks, it uses the Google Gemini API.
*   For the CLOCK benchmark (image generation), it currently generates **placeholder images**. You will need to modify the script (`automation/run_benchmark.py`) to integrate a real image generation API (e.g., DALL-E, Imagen). Instructions and placeholders for API keys are in `automation/config.py` and comments within `automation/run_benchmark.py`.

### Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ame-888/Gotcha-Benchmark-for-LLMs.git
    cd Gotcha-Benchmark-for-LLMs
    ```

2.  **Install Dependencies:**
    Navigate to the `automation` directory and install the required Python libraries.
    ```bash
    cd automation
    pip install -r requirements.txt
    ```

3.  **Configure API Key(s):**
    *   Edit the `automation/config.py` file.
    *   Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual Google Gemini API key for the ENIGMA and VISUAL benchmarks.
    *   For the CLOCK benchmark, replace `"YOUR_IMAGE_API_KEY_HERE"` with your image generation model's API key if you intend to implement a live API call. If left as is, the script will generate placeholder images.

### Running the Benchmark

Once set up, run the script from within the `automation` directory:
```bash
python run_benchmark.py
```
The script will execute the automated benchmarks (ENIGMA, VISUAL, and CLOCK):
*   ENIGMA and VISUAL results (text-based) will be saved in a timestamped JSON file inside the `automation/RESULTS` folder.
*   CLOCK benchmark results (placeholder images) will be saved in the `automation/RESULTS/CLOCK_IMAGES/` directory. The JSON results file will contain paths to these images.

You can then use the output file and images to manually score the model's performance based on the project's criteria.
---
