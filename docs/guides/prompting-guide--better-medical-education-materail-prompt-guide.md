Here is the rewritten, well-organized prompting guide based on your request. You can copy this directly into your documentation or personal notes.

---

# Guide: Prompting Strategies for Long-Form Medical Scripts

**Goal:** Force the LLM to generate deep, detailed content (10–30 minutes) instead of short summaries.

## 1. The "Micro-Step" Instruction (Force Granularity)

**Why:** Models naturally summarize to save tokens. You must force them to "zoom in" on every action.
**Instruction:** Explicitly command the model to describe the _process_ of an action, not just the _result_.

- **Prompt Example:**

  > "Do not summarize instructions. Break every procedure down into micro-steps. If the topic is 'Fasting,' do not just say 'Don't eat.' Discuss clear liquids, chewing gum, brushing teeth, and the exact time to stop."

- **❌ Don't Do:**

  > **Doctor:** [professional] You need to fast starting at midnight. No food or water.
  > **Patient:** [reassuring] Okay, I understand.
  > _(Result: Covers the topic in 5 seconds)_

- **✅ Do:**
  > **Doctor:** [professional] Let's talk about fasting. It is critical that you stop eating solid foods after midnight.
  > **Patient:** [curious] When you say solid foods, does that include yogurt or soup?
  > **Doctor:** [thoughtful] Good question. No, yogurt and soup count as food. [pause] However, you can have clear liquids up to 2 hours before arrival.
  > **Patient:** [confused] I'm not sure I know the difference. Is coffee a clear liquid?
  > **Doctor:** [gentle] Only if it's black coffee without milk or creamer. Apple juice is okay, but orange juice with pulp is not.

---

## 2. The "Skeptical Patient" Persona (Force Defense)

**Why:** A compliant patient kills the conversation. A skeptical patient forces the doctor to explain concepts twice or in greater depth (defending the medical advice).
**Instruction:** Program the patient to be anxious, confused, or influenced by internet myths.

- **Prompt Example:**

  > "The Patient should not accept information immediately. They should ask 'Why?', 'What if?', or 'How?'. They should express confusion or mention a myth they heard online. The Doctor must then correct them patiently."

- **❌ Don't Do:**

  > **Doctor:** [serious] You might feel some pressure during the procedure.
  > **Patient:** [calm] That sounds fine.
  > _(Result: Conversation ends immediately)_

- **✅ Do:**
  > **Doctor:** [serious] You might feel some pressure during the procedure, but no sharp pain.
  > **Patient:** [worried] I've heard horror stories online about people feeling everything. Are you sure the anesthesia works?
  > **Doctor:** [reassuring] That is a very common fear. [pause] Let me explain exactly how we monitor your comfort levels so that doesn't happen to you.

---

## 3. The "Analogy" Requirement (Force Visualization)

**Why:** Analogies slow down the pace and increase retention. They take up "air time" while adding value.
**Instruction:** Mandate a non-medical comparison for every technical term.

- **Prompt Example:**

  > "For every complex medical concept, the Doctor MUST use a real-world analogy (e.g., plumbing, traffic, gardening) to explain it before giving the technical definition."

- **❌ Don't Do:**

  > **Doctor:** [professional] The statins will lower your LDL cholesterol levels preventing plaque buildup.
  > _(Result: Too technical, too fast)_

- **✅ Do:**
  > **Doctor:** [thoughtful] Think of your blood vessels like the pipes in your kitchen sink. [pause] Over time, grease can build up and slow the water down.
  > **Patient:** [thoughtful] And that's the cholesterol?
  > **Doctor:** [affirming] Exactly. The medication works like a pipe cleaner. It prevents that 'grease' from sticking to the walls, keeping the water flowing freely to your heart.

---

## 4. Explicit "Pacing" Constraints (Force Exchange Count)

**Why:** LLMs don't understand "10 minutes," but they understand "turns."
**Instruction:** Set a hard floor for the number of interactions per topic.

- **Prompt Example:**

  > "Format this as a slow-paced conversation. For the current topic, you must generate a minimum of **6 back-and-forth exchanges**. Do not move to the next topic until you have explored this one fully."

- **❌ Don't Do:**

  > _(Allowing the model to cover "Symptoms" in one paragraph)._

- **✅ Do:**
  > _(The model forces the patient to ask about Symptom A, then Symptom B, then Symptom C, extending the dialogue significantly)._

---

## 5. Context Control (For "Divide and Conquer")

**Why:** When generating scripts longer than 10 minutes, you must split them into parts. If you don't control context, every part will sound like a new conversation (repeating "Hello").
**Instruction:** Tell the model exactly where it is in the timeline.

- **Prompt Example (Customize per section):**
- **Part 1 (Intro):** "Start with a greeting. Introduce the characters."
- **Part 2-4 (Middle):** "IMMEDIATELY dive into the topic. Do NOT write a greeting. Do NOT write a conclusion. Assume the conversation is already in progress."
- **Part 5 (End):** "Wrap up the conversation and say goodbye."

- **❌ Don't Do (In the middle of a script):**

  > **Doctor:** [professional] Hello, nice to see you today. Let's talk about your medication.
  > _(Result: Ruins the flow when stitched to previous audio)._

- **✅ Do (In the middle of a script):**
  > **Doctor:** [serious] Moving on to the next important point... [pause] we need to discuss your medication schedule.

---

### **Ready-to-Use Prompt Block**

_Copy and paste this section directly into your "Goal" or "Content Structure" block._

```markdown
# Content Expansion Rules (CRITICAL FOR LENGTH)

1. **Granularity:** Do not summarize. Break every instruction into micro-steps (e.g., "how to open the bottle," "what time of day," "with or without food").
2. **The "Why" Rule:** The Patient must ask "Why?" or express confusion at least 3 times per section, forcing the Doctor to elaborate.
3. **Analogy Requirement:** Use a real-world analogy (non-medical) to explain the core concept of this section.
4. **Exchange Minimum:** This specific section must contain at least 8 back-and-forth speaker exchanges.
5. **No Early Conclusions:** Do not wrap up the topic or say goodbye until the exchange minimum is met.
```
