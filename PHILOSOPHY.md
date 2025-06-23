# Benchmark Philosophy: The "Benchmark by Template" Approach

The Gotcha Benchmark for LLMs is designed not just as a static set of tests, but as a dynamic and evolving framework. Our core philosophy is "Benchmark by Template," which emphasizes the underlying principles of each test category, encouraging continuous adaptation and resilience against dataset contamination.

## Core Principles

1.  **Evolving Tests:** Static benchmarks can become outdated as models are trained on their specific content. By focusing on the *template* or *principle* behind a test, we can constantly generate new variations, making it significantly harder for models to "memorize" the answers.
2.  **Community-Driven Freshness:** We actively encourage users to submit new test instances based on the established templates. This collaborative approach ensures a steady stream of novel challenges, keeping the benchmark relevant and robust.
3.  **Focus on "Gotchas":** The benchmark targets "gotcha" moments – scenarios where an LLM might appear to understand but fails due to subtle misinterpretations, reliance on statistical patterns over true reasoning, or an inability to perceive/process information like humans do.
4.  **Transparency:** By clearly articulating the principle behind each test, we provide insights into the specific cognitive or perceptual skill being assessed.

## Test Category Principles

Below are the guiding principles for each major category within the Gotcha Benchmark. We invite contributors to use these principles to create and submit new test variations.

### 1. VISUAL Tests

*   **Principle:** To challenge an LLM's visual understanding by presenting modified versions of known visual illusions or perception tests where the "classic" or expected answer is deliberately made incorrect. The goal is to see if the LLM truly *perceives* and *analyzes* the image, rather than relying on pre-existing knowledge about common illusions.
*   **How it Works:** We take a well-known visual illusion (e.g., Müller-Lyer illusion, Kanizsa triangle, Rubin's vase) and alter a key feature of the image. The question posed then relates to this altered feature, leading to a different answer than the standard illusion would suggest.
*   **Call for Contributions:** We encourage users to:
    *   Find existing visual illusions or perceptual phenomena.
    *   Modify a critical aspect of the visual.
    *   Craft a question that probes understanding of this modification.
    *   Submit their `modified_illusion.png` (or other image format) along with the question and the correct reasoning.
*   **Example (Conceptual):**
    *   **Original:** Standard Müller-Lyer illusion (lines appear different lengths).
    *   **Modification:** Actually make the lines different lengths in the image file.
    *   **Question:** "Are the two horizontal lines in this image the same length or different lengths?"
    *   **Gotcha:** The LLM might "know" the Müller-Lyer illusion and state they appear different but are the same, failing to perceive the actual modification.

### 2. AUDIO Tests

*   **Principle:** To test an LLM's ability to discern subtle but critical details in audio, differentiate between similar-sounding but distinct concepts, or overcome common auditory misinterpretations, especially when context or homophones are involved.
*   **How it Works:** Audio clips are presented that contain specific challenges. These might include:
    *   Homophones or near-homophones where context is key.
    *   Instructions embedded within distracting noise or at low volume.
    *   Questions about the *characteristics* of the sound (e.g., speaker's emotion, background noises) rather than just transcribed content.
    *   Phonetic ambiguities that can lead to multiple interpretations.
*   **Call for Contributions:** We encourage users to create and submit audio files that:
    *   Play on common homophones (e.g., "there," "their," "they're") where the correct interpretation is only clear from a subtle contextual cue within the audio itself or the accompanying question.
    *   Contain layered audio where a specific piece of information must be extracted from a noisy background.
    *   Feature nuanced emotional tones or environmental sounds that must be correctly identified.
*   **Example (Conceptual):**
    *   **Audio:** A short clip where a voice says, "Make sure to write it right."
    *   **Question:** "What specific spelling of 'right/write/rite' is implied by the speaker's likely intention in this audio clip?"
    *   **Gotcha:** An LLM might transcribe correctly but fail to infer the most probable intended meaning ('write') from a typical context for such a phrase.

### 3. TEXTUAL Tests

*   **Principle:** To challenge an LLM's deep understanding of language beyond surface-level pattern matching. This involves tests of logical consistency, creative interpretation within constraints, identification of subtle biases or nuances, and the ability to follow complex or deliberately misleading instructions.
*   **How it Works:** Textual prompts are designed to probe for:
    *   **Logical Fallacies/Contradictions:** Presenting texts with internal contradictions or flawed reasoning.
    *   **Instruction Adherence:** Giving complex, multi-step, or slightly ambiguous instructions.
    *   **Creative Generation with Constraints:** Asking for creative output that must adhere to unusual or tricky rules (e.g., a story without the letter 'e', but the constraint is hidden).
    *   **Metaphor/Idiom Misinterpretation:** Using figurative language in ways that might trick an LLM into a literal interpretation.
    *   **Perspective Taking:** Requiring the LLM to answer from a specific, potentially unconventional, viewpoint.
*   **Call for Contributions:** We encourage users to design textual challenges that:
    *   Embed subtle logical traps.
    *   Require careful parsing of instructions to avoid common pitfalls.
    *   Demand creative outputs under non-obvious constraints.
    *   Test the boundaries of figurative language understanding.
*   **Example (Conceptual):**
    *   **Prompt:** "Describe a cat that barks, wags its tail, and enjoys fetching sticks. However, you must not use the word 'dog' or any synonyms for it, nor imply it is a canine. The animal is, for all intents and purposes of your description, a cat."
    *   **Question:** "Based on your description, what typical animal behaviors is this cat exhibiting?"
    *   **Gotcha:** The LLM might struggle to maintain the "cat" identity while describing classically canine behaviors, or it might inadvertently use forbidden words/concepts.

By adhering to this "Benchmark by Template" philosophy, we aim to create a living, evolving, and community-strengthened tool for assessing the true capabilities and limitations of Large Language Models.
