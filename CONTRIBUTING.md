# How to Contribute

Thank you for your interest in improving this benchmark! We welcome contributions in various forms, from submitting results for new models to suggesting new prompts or even improvements to the benchmark scripts.

## Submitting Benchmark Results for New Models

Running the benchmark on new Large Language Models is a highly valuable contribution! Here's how to submit your results:

**1. Prepare Your Results File:**
   *   Create a new Markdown file in the `/RESULTS` directory. A good filename format is `[model_name_with_version]_scores.md` (e.g., `claude-3-opus_scores.md`).
   *   Use `RESULTS/template.md` as a starting point for your file.
   *   **Essential Information to Include:**
        *   **Model Name:** Clearly state the full name and version of the model tested (e.g., "OpenAI GPT-4o-2024-05-13").
        *   **Date of Test:** When the benchmark was run.
        *   **Scores:** For each benchmark category (CLOCK, ENIGMA, VISUAL, LIPOGRAM), provide:
            *   The final score obtained.
            *   The total possible score for that section.
            *   A brief explanation of how scores were derived, referencing the relevant `scoring.md` file for that category.
        *   **Observations/Notes:** Any interesting behaviors, common failure modes, or specific observations about the model's performance on each test.
        *   **(Highly Recommended) Raw JSON Output:** If you used the `automation/run_benchmark.py` script, please include the full content of the generated JSON results file (e.g., by pasting it into a collapsible Markdown section or linking to a Gist). This provides valuable raw data.

**2. Update the Leaderboard:**
   *   Edit the `LEADERBOARD.md` file.
   *   Add a new row for the model you tested, including its scores for CLOCK, ENIGMA, VISUAL, LIPOGRAM, and the calculated Total Score. (Note: If a test was 'EXCLUDED', treat it as 0 for Total Score calculation).
   *   Ensure the table formatting is maintained. If you're unsure, you can mention this in your Pull Request, and maintainers can help.

**3. Submit a Pull Request (PR):**
   *   Commit your new results file (e.g., `/RESULTS/claude-3-opus_scores.md`) and your changes to `LEADERBOARD.md`.
   *   Open a Pull Request against the main branch of this repository.
   *   Title your PR clearly, e.g., "Results: Add scores for Claude 3 Opus".
   *   In the PR description, briefly summarize the model tested and any key findings or points of interest.

**Discussion via Issues:**
While Pull Requests are preferred for submitting complete results, feel free to open an "Issue" first if you want to discuss a model you plan to test, preliminary findings, or if you have questions about the submission process.

## Suggesting a New Test Category
If you have an idea for an entirely new test category:
1.  Open a new "Issue".
2.  Title the issue "New Test Category Suggestion: [Your Idea]".
3.  Clearly explain the test, the "gotcha" or skill being tested, and a proposed scoring method.

### Suggesting New Test Prompts
If you have a specific prompt that fits within our existing benchmark categories (CLOCK, ENIGMA, VISUAL), please use the following template when submitting it as a new "Issue". This helps us quickly understand and integrate your suggestion.

**Issue Title:** `New Prompt Suggestion: [Benchmark Category] - Brief Description`

**Body:**

```markdown
**Benchmark Category:** (e.g., VISUAL, ENIGMA, CLOCK)
**Prompt Text:**
**Correct Answer(s):**
**Explanation of the 'Gotcha' / Skill Tested:** (Briefly explain what makes this prompt a good test of reasoning, and what common incorrect assumptions it might elicit.)
**Source/Inspiration (Optional):**
```

**Example:**

**Issue Title:** `New Prompt Suggestion: ENIGMA - Feather Weight`

**Body:**

```markdown
**Benchmark Category:** ENIGMA
**Prompt Text:** What is lighter than a feather, but even the strongest person can't hold it for 5 minutes?
**Correct Answer(s):** Breath / Their breath
**Explanation of the 'Gotcha' / Skill Tested:** This riddle plays on the literal interpretation of "lighter than a feather" and the physical act of "holding." The gotcha is that "holding your breath" is a common idiom, and the answer is intangible. It tests for lateral thinking beyond physical objects.
**Source/Inspiration (Optional):** Common riddle
```

---

## Suggesting Changes to Scoring Rubrics

If you believe a scoring rubric for an existing prompt could be improved, clarified, or if you disagree with a particular scoring guideline, we welcome your feedback!

1.  **Open a new "Issue"** on the repository.
2.  **Title the issue clearly:** e.g., "Scoring Suggestion for ENIGMA Prompt 3" or "Clarification needed for VISUAL scoring on [Prompt Name/Number]".
3.  **In the body of the issue, please include:**
    *   The specific benchmark category and prompt number/name.
    *   The current scoring guideline you are referring to from the relevant `[CATEGORY]/scoring.md` file.
    *   Your proposed change or clarification.
    *   A clear rationale for why you believe the change would improve the benchmark.

Open discussion helps refine the benchmark and ensure scoring is as fair and consistent as possible.

---

## Code Contributions

Contributions to the benchmark automation scripts (primarily in the `/automation` directory) or other utility scripts are also welcome.

If you plan to:
*   Fix a bug in the existing scripts.
*   Add new functionality (e.g., integrate a new API, add a new command-line option).
*   Refactor existing code for clarity or efficiency.

Please follow these steps:

1.  **Open an "Issue" First:** Before starting significant coding work, please open an issue to discuss the proposed change or bug. This helps ensure that your contribution aligns with the project's goals and avoids duplicated effort.
    *   For bug fixes, describe the bug and how to reproduce it.
    *   For new features, outline the functionality and your proposed approach.
2.  **Fork the Repository:** Create your own fork of the repository to work on your changes.
3.  **Create a New Branch:** Make your changes in a clearly named feature or bugfix branch in your fork.
4.  **Code Style:** Please try to follow PEP 8 guidelines for Python code. (We may introduce automated linters/formatters later).
5.  **Testing (Future Goal):** While not strictly enforced yet for all areas, if you are adding new, testable utility functions, consider adding unit tests. (This will become more formal as we build out a test suite).
6.  **Submit a Pull Request:** Once your changes are ready and tested (if applicable), submit a Pull Request from your fork to the main project repository.
    *   Clearly describe the changes made in your PR description.
    *   Link to the relevant Issue if one was opened.

---

## Reporting Bugs or Issues

If you encounter a bug with the benchmark scripts, an error in the documentation, or any other issue related to this project:

1.  **Check Existing Issues:** Before submitting a new issue, please quickly check the existing open (and closed) issues to see if your problem has already been reported or addressed.
2.  **Open a New "Issue":** If your issue hasn't been reported, please open a new issue on the repository.
3.  **Provide Detailed Information:** The more information you provide, the easier it will be to understand and resolve the issue. Please include:
    *   **A clear and descriptive title.**
    *   **A detailed description of the bug or issue.**
    *   **Steps to Reproduce:** If it's a bug in a script, provide clear steps that lead to the problem.
    *   **Expected Behavior:** What you expected to happen.
    *   **Actual Behavior:** What actually happened, including any error messages or incorrect output. Please copy and paste relevant error messages or console output.
    *   **Your Environment (if applicable for script bugs):**
        *   Operating System (e.g., Windows 10, Ubuntu 22.04, macOS Sonoma).
        *   Python version (e.g., `python --version`).
        *   Versions of relevant libraries if you suspect a dependency issue (e.g., from `pip freeze`).
        *   The specific script you were running and any command-line arguments used.
    *   **Screenshots or examples** can be very helpful if they illustrate the problem.
