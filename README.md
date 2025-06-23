# Gotcha-Benchmark-for-LLMs
A benchmark for testing LLM reasoning in image generation (CLOCK), lateral thinking (ENIGMA), and visual analysis (VISUAL)

## Our Philosophy: Benchmark by Template

The Gotcha Benchmark is built on the idea of "Benchmark by Template." Instead of a static set of questions, we focus on the *underlying principles* that make a good "gotcha" test. This allows us, and the community, to continuously generate new test variations, making the benchmark more resilient to dataset contamination and ensuring it remains a challenging evaluation tool.

For a detailed explanation of this approach and the principles behind each test category, please see our [Benchmark Philosophy](./PHILOSOPHY.md).

## Test Categories

Currently, the benchmark focuses on the following (though we plan to expand!):

*   **VISUAL:** Tests involving image interpretation and analysis, often using modified illusions.
    *   Example: `VISUAL/modified_muller_lyer.png`
*   **AUDIO:** (Planned) Tests involving audio comprehension, focusing on nuances, homophones, and context.
*   **TEXTUAL:** (Planned) Tests involving deep text understanding, logical consistency, and creative interpretation under constraints.
    *   Example: `TEXTUAL/lateral_thinking_riddles.md` (Representing ENIGMA-style tests)
    *   Example: `CLOCK/clock_instructions.md` (Representing complex instruction following for generation)

*(Note: The initial project structure included placeholders like `AUDIO/placeholder.txt` and specific test files like `TEXTUAL/lateral_thinking_riddles.md` and `VISUAL/modified_muller_lyer.png`. The `CLOCK` test, while involving image generation, has its instructions in `CLOCK/clock_instructions.md`)*
