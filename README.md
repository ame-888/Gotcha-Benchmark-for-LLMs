# LLM Cognitive & Reasoning Benchmark

This is an open-source benchmark designed to evaluate Large Language Models beyond simple knowledge recall. It tests for nuanced capabilities in **spatial reasoning**, **lateral thinking**, and **critical visual analysis**.

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

*This benchmark was created by [Your Name/Handle Here].*
