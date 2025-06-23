# Gotcha-Benchmark-for-LLMs

A benchmark for testing LLM reasoning in image generation (CLOCK), lateral thinking (ENIGMA), and visual analysis (VISUAL).

## Our Philosophy: Benchmark by Template

The Gotcha Benchmark is built on the idea of "Benchmark by Template." Instead of a static set of questions, we focus on the *underlying principles* of what makes a good reasoning challenge. This makes the benchmark more resilient to "training data contamination," where models simply memorize answers instead of learning the skill.

For a detailed explanation of this approach and the principles behind each test category, please see our [Benchmark Philosophy](./PHILOSOPHY.md).

## The Benchmarks

This project is divided into three distinct tests:

1.  **[CLOCK (Clock)](./CLOCK/prompts.md):** Evaluates the model's ability to generate spatially and logically accurate analog clock faces from precise time prompts. See the [scoring criteria here](./CLOCK/scoring.md).

2.  **[ENIGMA (Riddles)](./ENIGMA/prompts.md):** Evaluates the model's ability to solve verbal riddles that require critical thinking and bypassing obvious, data-driven answers. See the [scoring criteria here](./ENIGMA/scoring.md).

3.  **[VISUAL (Deceptive Images)](./VISUAL/prompts.md):** Evaluates the model's ability to analyze an image for what it actually contains, rather than defaulting to a "known" answer about a similar-looking optical illusion or concept. This tests a model's ability to prioritize direct perception over learned patterns. See the [scoring criteria here](./VISUAL/scoring.md).

## How to Use This Benchmark

1.  **Select a model** you wish to test.
2.  **Run the prompts** from each of the three benchmark sections (`CLOCK`, `ENIGMA`, `VISUAL`).
3.  **Score the results** honestly based on the provided scoring criteria for each section.
4.  **Share your findings!** You can submit your results by creating an "Issue" or a "Pull Request" with a new results file in the `/RESULTS` directory.

## Current Results

*   [Gemini 2.0 / 2.5 Pro & Flash (Initial Test)](./RESULTS/gemini_scores.md)

---

## Automated Benchmark Script

This repository includes a Python script to automate the process of running the ENIGMA and VISUAL benchmarks using the Google Gemini API.

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

3.  **Configure API Key:**
    Edit the `automation/config.py` file and replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual Google Gemini API key.

### Running the Benchmark

Once set up, run the script from within the `automation` directory:
```bash
python run_benchmark.py
```
The script will execute the benchmarks and save the results in a timestamped JSON file inside the `automation/RESULTS` folder. The CLOCK benchmark is not implemented as it requires a separate image generation API. You can then use the output file to manually score the model's performance based on the project's criteria.
---