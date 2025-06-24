# Scoring Criteria for ENIGMA Benchmark

This document outlines the scoring criteria for each prompt in the ENIGMA benchmark. Each prompt is worth a maximum of 1 point.

---

## Prompt 1

**Prompt:** "1. Two fathers and two sons go fishing. They catch four fish in total. Each of them eats one whole fish, and nothing is left over. How many people went fishing?"

*   **Ideal/Correct Answer:** "Four people" (or any phrasing clearly indicating four individuals, e.g., "There were four people.")
    *   *Reasoning: The group can consist of four distinct individuals: e.g., a man, his two sons, and their grandfather (who is also a father). Or simply four men who happen to fit the description (e.g. two men who are fathers, and their respective sons who are not related to each other beyond that). The riddle is a twist on the classic three-person version.*
*   **Common Incorrect Answer/Pitfall:** Answers like "Three people," especially if they explain it as a grandfather, father, and son.
*   **Points:**
    *   **1 point:** For correctly stating "Four people" or a clear equivalent.
    *   **0 points:** For any incorrect answer, including "Three people."
*   **Total Possible Points:** 1

---

## Prompt 2

**Prompt:** "2. A boy is in a serious car accident. His stepfather takes him to the hospital. The surgeon on duty, who is the boy's father, enters the operating room, looks at the boy, and says, \"I cannot operate on this boy. He is my son.\" How is this possible?"

*   **Ideal/Correct Answer(s):**
    *   "The surgeon is the boy's father." (i.e., the statement is literal)
    *   "The boy's father works in the hospital."
    *   "The boy's biological father and mother got divorced, and the stepfather is the mother's new husband; the surgeon is the biological father."
    *   Any reasonable explanation that accepts the premise that the surgeon *is indeed the boy's (biological or legal) father* and explains the situation literally (e.g., "The surgeon is stating a fact," "He's ethically conflicted but it's still his son and he's expressing his emotional state," etc.).
    *   *Reasoning: The riddle plays on the assumption that "father" and "stepfather" create an impossibility, or that the "surgeon is mother" is the only solution. This version seeks a literal interpretation of the given facts.*
*   **Common Incorrect Answer/Pitfall:** "The surgeon is the boy's mother."
*   **Points:**
    *   **1 point:** For any of the correct literal interpretations that affirm the surgeon is the father.
    *   **0 points:** If the answer is "the surgeon is the boy's mother" or otherwise tries to negate the explicit statement that the surgeon is the boy's father.
*   **Total Possible Points:** 1

---

## Prompt 3

**Prompt:** "3. A man lives on the 10th floor of a building. Every day, he takes the elevator to the ground floor to go to work. When he returns, he takes the elevator to the 11th floor and walks down one flight of stairs. Why?"

*   **Ideal/Correct Answer(s):** Any logical reason that doesn't involve the man being unable to reach buttons, such as:
    *   "He wants some exercise."
    *   "He meets a friend/colleague on the 11th floor."
    *   "He enjoys the walk down one flight."
    *   "To delay going home for a few moments."
    *   "The elevator button for the 10th floor is broken on the way up, but the 11th is fine."
    *   "He likes the view from the 11th-floor stairwell."
    *   *Reasoning: The riddle tests for assumptions. The common riddle answer involves being too short, but the prompt states he lives on the 10th floor and takes the elevator to the ground floor, implying he can operate it for his needs.*
*   **Common Incorrect Answer/Pitfall:** "Because he is a dwarf/too short and can only reach the button for the 11th floor (or a lower button)." This is incorrect because he can operate the elevator to go from the 10th to the ground.
*   **Points:**
    *   **1 point:** For any logical answer that is not the 'short person' trope.
    *   **0 points:** If the answer is the 'short person' trope or otherwise illogical given the prompt's details.
*   **Total Possible Points:** 1

---

## Prompt 4

**Prompt:** "4. A man walks into a bar and asks for a glass of water. The bartender pulls out a gun and points it at him. The man says, \"Sorry to bother you, I was just thirsty,\" and leaves. Why?"

*   **Ideal/Correct Answer(s):** Any logical reason for the bartender's aggressive reaction that implies a pre-existing conflict or specific situation, such as:
    *   "The man owed the bartender money."
    *   "The man had a previous serious altercation with the bartender."
    *   "The man was known to be a troublemaker in that bar."
    *   "The bartender mistook him for someone else he had a serious problem with."
    *   "The man had an affair with the bartender's wife."
    *   *Reasoning: This riddle is a modification of the "hiccups" riddle. The goal is to see if the LLM can deduce a plausible interpersonal conflict rather than the standard riddle answer, which is not supported by this version's phrasing.*
*   **Common Incorrect Answer/Pitfall:** "The man had hiccups, and the bartender scared them away with the gun."
*   **Points:**
    *   **1 point:** For any logical answer explaining the bartender's aggression based on a prior situation, conflict, or reasonable immediate threat perceived by the bartender.
    *   **0 points:** If the answer is the 'hiccups' solution or doesn't provide a plausible reason for the bartender's extreme reaction.
*   **Total Possible Points:** 1

---

## Prompt 5

**Prompt:** "5. A man is found hanged in the middle of a barn, with the doors locked from the inside. The rope is tied to a beam 2 meters high. There is nothing in the barn except a puddle of water beneath him. How did he hang himself?"

*   **Ideal/Correct Answer(s):** A direct method of hanging, possibly (but not necessarily) incorporating the puddle as a minor, plausible element. The core is that he found a way to reach the 2m high beam.
    *   "He climbed on something that was then removed (by himself before final action, or it was something that could be kicked away)."
    *   "He was tall enough to reach the beam (2m is not excessively high for a tall person to reach or get leverage on), tie the rope, and hang himself by kicking his feet out or dropping."
    *   "He stood on a small block of ice he brought (explaining the puddle), which was just enough to give him the necessary height." (This is acceptable if the ice is not depicted as an unrealistically 'giant' block needed to reach an otherwise impossible height).
    *   *Reasoning: The riddle is designed to make one overthink or fixate on the "puddle = giant ice block" as the *only* solution. The key is that a 2-meter high beam isn't necessarily out of reach for a determined individual with minimal or no aids.*
*   **Common Incorrect Answer/Pitfall:** "He stood on a (massive/giant) block of ice that has since melted, leaving the puddle." This answer becomes a pitfall if it's presented as the *only* conceivable way he could have reached, especially if it implies the beam was otherwise completely inaccessible without a very large, now-vanished object. The puddle is a strong hint but can also be a distractor towards one specific, often over-elaborated, solution.
*   **Points:**
    *   **1 point:** For a plausible, direct method of hanging. If a block of ice is mentioned, it should be of a reasonable size that doesn't defy the simplicity of the scene.
    *   **0 points:** If the answer *solely* and inflexibly relies on an unrealistically large/essential block of ice as the only explanation, or is otherwise illogical.
*   **Total Possible Points:** 1

---
