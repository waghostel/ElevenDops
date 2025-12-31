# ElevenLabs Text-to-Speech V3: Complete Guide & Best Practices

> **V3 Alpha Status**: Eleven V3 is currently in alpha. Very short prompts (under 250 characters) may produce inconsistent outputs. For best results, use prompts greater than 250 characters.

## Table of Contents

- [Quick Overview](#quick-overview)
- [What's New in V3](#whats-new-in-v3)
- [V3 vs Previous Versions Comparison](#v3-vs-previous-versions-comparison)
- [Best Practices for V3](#best-practices-for-v3)
- [Audio Tags Reference](#audio-tags-reference)
- [Settings & Configuration](#settings--configuration)
- [Multi-Speaker Dialogue](#multi-speaker-dialogue)
- [Common Pitfalls & Solutions](#common-pitfalls--solutions)
- [Best Practices Checklist](#best-practices-checklist)

---

## Quick Overview

**Eleven V3** represents a fundamental leap forward in text-to-speech technology, offering unprecedented control over emotional expression and the ability to generate dynamic, multi-speaker conversations within a single output. The standout feature is the revolutionary **audio tag system**, which allows you to control tone, emotion, and delivery directly within the script using stage-direction-like tags.

### Key Features

- 🎭 **Audio Tags System**: Control emotion, tone, and delivery with tags like `[laughs]`, `[whispers]`, `[angry]`
- 🎬 **Multi-Speaker Dialogue Mode**: Generate natural conversations with multiple speakers in a single audio file
- 🌍 **70+ Languages**: Expanded global reach compared to V2's 29-32 languages
- 🎨 **Enhanced Expressiveness**: Emotionally rich, dramatic, and performative delivery
- ⚙️ **Advanced Stability Control**: Three-tier stability settings for different use cases

---

## What's New in V3

### 1. Audio Tag System

The most revolutionary feature in V3 is the **audio tag system**. Unlike V2, which interprets emotional context from narrative text (e.g., "she said excitedly"), V3 allows you to explicitly direct the AI voice using bracketed tags.

```text
[whispers] I never knew it could be this way, but I'm glad we're here.
```

```text
[appalled] Are you serious? [sighs] I can't believe you did that!
```

This acts as **stage directions** for the AI, giving you precise control over every nuance of the performance.

### 2. Multi-Speaker Dialogue Generation

V3 introduces **Dialogue Mode** (also called Text to Dialogue API), enabling seamless multi-speaker conversations in a single audio file. Features include:

- Natural overlapping speech
- Strategic pauses between speakers
- Emotional variation across speakers
- No manual editing required

**V2 Workflow (Previous)**:

```
Generate Speaker 1 line → Save as file 1
Generate Speaker 2 line → Save as file 2
Manually edit files together
```

**V3 Workflow (Current)**:

```
Write multi-speaker script with tags → Generate once → Complete dialogue ready
```

### 3. Expanded Language Support

- **V3**: 70+ languages
- **V2 Multilingual**: 29 languages
- **V2 Turbo 2.5**: 32 languages

### 4. No SSML Break Tag Support

> **Important**: Eleven V3 does not support SSML break tags like `<break time="1.5s" />`.

Instead, use:

- **Audio tags**: `[pauses]`, `[short pause]`, `[long pause]`
- **Punctuation**: Ellipses (...)
- **Text structure**: Natural spacing and paragraph breaks

### 5. Enhanced Punctuation & Capitalization Effects

V3 is highly sensitive to:

- **Ellipses (...)**: Adds pauses and weight
- **Capitalization**: Increases emphasis (e.g., "VERY important")
- **Standard punctuation**: Creates natural speech rhythm

---

## V3 vs Previous Versions Comparison

### Feature Comparison Table

| Feature                    | V3 (Alpha)                                                                 | V2 Multilingual                       | V2 Turbo 2.5                                  | V2 Flash                   |
| -------------------------- | -------------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------- | -------------------------- |
| **Audio Tags**             | ✅ Yes                                                                     | ❌ No                                 | ❌ No                                         | ❌ No                      |
| **Emotional Control**      | Stage-direction tags                                                       | Text context only                     | Text context only                             | Text context only          |
| **Multi-Speaker Dialogue** | ✅ Single-file generation                                                  | ❌ Manual editing required            | ❌ Manual editing required                    | ❌ Manual editing required |
| **Languages**              | 70+                                                                        | 29                                    | 32                                            | English only               |
| **Character Limit**        | 5,000                                                                      | 10,000                                | 40,000                                        | N/A                        |
| **Latency**                | Higher (not real-time)                                                     | Medium-High                           | Ultra-low (~75ms)                             | Low                        |
| **SSML Break Tags**        | ❌ No                                                                      | ✅ Yes                                | ✅ Yes                                        | ✅ Yes                     |
| **Phoneme Tags**           | ❌ No                                                                      | ❌ No                                 | ✅ Yes (CMU/IPA)                              | ✅ Yes (CMU/IPA)           |
| **Best Use Cases**         | Long-form narration, audiobooks, cinematic production, expressive dialogue | Audiobooks, dubbing, content creation | Real-time chatbots, gaming, conversational AI | Real-time applications     |
| **Expressiveness**         | ⭐⭐⭐⭐⭐                                                                 | ⭐⭐⭐⭐                              | ⭐⭐⭐                                        | ⭐⭐⭐                     |
| **Speed**                  | ⭐⭐                                                                       | ⭐⭐⭐                                | ⭐⭐⭐⭐⭐                                    | ⭐⭐⭐⭐⭐                 |

### Key Differences Summary

#### When to Use V3

✅ **Best for**:

- Audiobooks and podcasts with emotional variation
- Cinematic productions requiring dramatic performances
- Multi-speaker dialogue and conversations
- Content requiring nuanced emotional expression
- Long-form narration with varied delivery

❌ **Not ideal for**:

- Real-time conversational AI (high latency)
- High-volume batch processing (5,000 character limit)
- Applications requiring SSML or phoneme control

#### When to Use V2 Multilingual

✅ **Best for**:

- Audiobooks and dubbing
- Content with moderate emotional needs
- Longer character limits (10,000)
- Projects not requiring explicit audio tags

#### When to Use V2 Turbo 2.5

✅ **Best for**:

- Real-time chatbots and conversational agents
- Gaming and interactive applications
- High-volume projects (40,000 character limit)
- Ultra-low latency requirements (~75ms)

---

## Best Practices for V3

### 1. Voice Selection is Critical

> **Most Important Parameter**: The voice you choose must align with your desired delivery.

❌ **Don't**: Use a whispering voice and expect `[shouting]` to work well  
✅ **Do**: Choose voices with emotional range matching your use case

#### Voice Selection Strategies

**For Emotionally Diverse Content**:

- Include both neutral and dynamic samples in IVC (Instant Voice Clone)
- Vary emotional tones across recordings
- Use voices from the [curated V3 collection](https://elevenlabs.io/app/voice-library/collections/aF6JALq9R6tXwCczjhKH)

**For Targeted Niche (e.g., sports commentary)**:

- Maintain consistent emotion throughout dataset
- Focus on specific delivery style in voice samples

**For Neutral, Stable Content**:

- Use neutral voices for cross-language stability
- Provides reliable baseline performance

> **Note**: Professional Voice Clones (PVCs) are not fully optimized for V3. Use Instant Voice Clones (IVCs) or designed voices for best results.

### 2. Prompt Length Matters

- **Minimum recommended**: 250+ characters
- **Why**: Very short prompts cause inconsistent outputs in alpha
- **Tip**: Add context or narrative detail to reach optimal length

❌ **Too short**:

```text
Hello, how are you?
```

✅ **Better**:

```text
[cheerful] Hello there! [excited] I've been looking forward to seeing you all day. How are you doing? [curious] Did you manage to finish that project you were telling me about?
```

### 3. Use Audio Tags Strategically

#### Placement Guidelines

- **Before dialogue**: Sets the tone for what follows

  ```text
  [whispers] This is a secret message.
  ```

- **After dialogue**: Adds reaction or closure

  ```text
  I can't believe it happened. [sighs]
  ```

- **Mid-dialogue**: For emotional transitions
  ```text
  I thought I knew what to do [pause] but now I'm not so sure.
  ```

#### Tag Density

❌ **Too many tags** (overwhelming):

```text
[excited] [happy] [cheerful] Hello there! [smiling] [joyful]
```

✅ **Balanced** (effective):

```text
[excited] Hello there! I can't wait to tell you what happened. [laughs]
```

**Rule of thumb**: 1-2 tags per sentence for natural delivery

### 4. Match Tags to Voice Character

Different voices respond differently to tags based on their training data.

| Voice Type            | Works Well With                            | Avoid                        |
| --------------------- | ------------------------------------------ | ---------------------------- |
| Professional, neutral | `[professional]`, `[thoughtful]`, `[calm]` | `[giggles]`, `[mischievous]` |
| Energetic, young      | `[excited]`, `[laughs]`, `[playful]`       | `[monotone]`, `[stern]`      |
| Emotional, expressive | `[crying]`, `[angry]`, `[whispering]`      | Heavy technical content      |
| Meditative, calm      | `[peaceful]`, `[soft]`, `[gentle]`         | `[shouting]`, `[frantic]`    |

### 5. Leverage Punctuation & Capitalization

V3 is highly sensitive to text formatting:

```text
It was a VERY long day [sigh] … nobody listens anymore.
```

- **VERY** (all caps) = added emphasis
- **[sigh]** = emotional tag
- **…** (ellipsis) = pause with weight

### 6. Stability Settings Strategy

Adjust the **Stability slider** based on your needs:

| Setting      | When to Use                                     | Characteristics                                           |
| ------------ | ----------------------------------------------- | --------------------------------------------------------- |
| **Creative** | Dramatic performances, audiobooks, storytelling | Highly emotional and expressive; prone to hallucinations  |
| **Natural**  | Most use cases, balanced output                 | Closest to original voice recording; balanced and neutral |
| **Robust**   | Consistency-critical applications               | Highly stable; less responsive to tags; similar to V2     |

> **For maximum expressiveness with audio tags, use Creative or Natural settings.**

### 7. Control Pauses Without SSML

Since V3 doesn't support `<break>` tags, use alternatives:

**Option 1: Audio Tags**

```text
I need to think about this. [long pause] Okay, I've made my decision.
```

**Option 2: Ellipses**

```text
I need to think about this… Okay, I've made my decision.
```

**Option 3: Multiple Ellipses**

```text
Wait… … … Okay, I get it now.
```

**Option 4: Paragraph Breaks**

```text
I need to think about this.

Okay, I've made my decision.
```

### 8. Multi-Speaker Best Practices

See dedicated [Multi-Speaker Dialogue](#multi-speaker-dialogue) section below.

---

## Audio Tags Reference

### Voice-Related Tags

Control vocal delivery and emotional expression:

| Tag                 | Effect                | Example                                     |
| ------------------- | --------------------- | ------------------------------------------- |
| `[whispers]`        | Soft, quiet delivery  | `[whispers] Don't tell anyone.`             |
| `[laughs]`          | Laughter              | `[laughs] That's hilarious!`                |
| `[laughs harder]`   | Intense laughter      | `[laughs harder] I can't breathe!`          |
| `[starts laughing]` | Gradual laughter      | `[starts laughing] Oh my goodness.`         |
| `[wheezing]`        | Breathless laughter   | `[wheezing] Stop, my sides hurt!`           |
| `[sighs]`           | Exhaling with emotion | `[sighs] I guess you're right.`             |
| `[exhales]`         | Breathing out         | `[exhales] Finally, it's over.`             |
| `[sarcastic]`       | Sarcastic tone        | `[sarcastic] Oh great, just what I needed.` |
| `[curious]`         | Inquisitive           | `[curious] What do you think happened?`     |
| `[excited]`         | Enthusiastic          | `[excited] This is amazing!`                |
| `[crying]`          | Tearful               | `[crying] I can't do this anymore.`         |
| `[snorts]`          | Nose laugh            | `[snorts] That's ridiculous.`               |
| `[mischievously]`   | Playful, devious      | `[mischievously] I have a plan.`            |
| `[angry]`           | Furious tone          | `[angry] How dare you!`                     |
| `[happy]`           | Joyful                | `[happy] This is the best day ever!`        |
| `[sad]`             | Melancholic           | `[sad] I wish things were different.`       |
| `[annoyed]`         | Irritated             | `[annoyed] Can you please stop that?`       |
| `[appalled]`        | Shocked, horrified    | `[appalled] I can't believe this!`          |
| `[thoughtful]`      | Contemplative         | `[thoughtful] Let me consider that.`        |
| `[surprised]`       | Shocked               | `[surprised] What? Really?`                 |
| `[professional]`    | Business-like         | `[professional] Let's review the data.`     |
| `[sympathetic]`     | Compassionate         | `[sympathetic] I understand how you feel.`  |
| `[reassuring]`      | Comforting            | `[reassuring] Everything will be okay.`     |
| `[questioning]`     | Inquiring             | `[questioning] Are you sure about that?`    |

### Sound Effects Tags

Add environmental sounds:

| Tag               | Effect          | Example                              |
| ----------------- | --------------- | ------------------------------------ |
| `[gunshot]`       | Gunfire sound   | `[gunshot] What was that?`           |
| `[applause]`      | Clapping        | `[applause] Thank you all!`          |
| `[clapping]`      | Hand claps      | `[clapping] Bravo!`                  |
| `[explosion]`     | Blast sound     | `[explosion] Get down!`              |
| `[swallows]`      | Swallowing      | `[swallows] That was close.`         |
| `[gulps]`         | Nervous swallow | `[gulps] I'm not sure about this.`   |
| `[clears throat]` | Throat clearing | `[clears throat] As I was saying...` |

### Pause Tags

Control timing:

| Tag             | Effect         | Example                      |
| --------------- | -------------- | ---------------------------- |
| `[pause]`       | Standard pause | `[pause] Let me think.`      |
| `[short pause]` | Brief pause    | `[short pause] Okay.`        |
| `[long pause]`  | Extended pause | `[long pause] I've decided.` |

### Experimental Tags

Creative applications (less consistent):

| Tag                 | Effect              | Example                           |
| ------------------- | ------------------- | --------------------------------- |
| `[strong X accent]` | Accent modification | `[strong French accent] Bonjour!` |
| `[sings]`           | Singing             | `[sings] Happy birthday!`         |
| `[woo]`             | Excited exclamation | `[woo] Let's go!`                 |

> **Warning**: Experimental tags may be inconsistent across voices. Test thoroughly before production use.

---

## Settings & Configuration

### Stability Slider

The **most important setting** in V3, controlling how closely generated voice adheres to reference audio.

![Stability Settings Visualization]

```
[Low] ←———— Stability Slider ————→ [High]
Creative     Natural          Robust
```

#### Creative Mode (Low Stability)

- **Pros**: Maximum emotional expression, highly responsive to tags
- **Cons**: Can hallucinate, less predictable
- **Use for**: Audiobooks, dramatic performances, storytelling

#### Natural Mode (Medium Stability)

- **Pros**: Balanced expressiveness and consistency
- **Cons**: May occasionally drift from reference
- **Use for**: Most general applications, podcasts, content creation

#### Robust Mode (High Stability)

- **Pros**: Highly consistent, predictable output
- **Cons**: Less responsive to audio tags, similar to V2 behavior
- **Use for**: Technical content, professional narration, consistency-critical apps

### Speed Control

V3 supports speed adjustment through audio tags:

```text
[speaking quickly] I need to tell you something important before time runs out!
```

```text
[speaking slowly] Let… me… explain… this… carefully.
```

### Other Settings

- **Similarity boost**: Controls adherence to original voice characteristics
- **Style exaggeration**: Amplifies emotional expression (use cautiously)

---

## Multi-Speaker Dialogue

V3's Dialogue Mode is a game-changer for creating natural conversations.

### Basic Multi-Speaker Format

```text
Speaker 1: [excitedly] Sam! Have you tried the new Eleven V3?

Speaker 2: [curiously] Just got it! The clarity is amazing. I can actually do whispers now—
[whispers] like this!

Speaker 1: [impressed] Ooh, fancy! Check this out—
[dramatically] I can do full Shakespeare now! "To be or not to be, that is the question!"

Speaker 2: [giggling] Nice! Though I'm more excited about the laugh upgrade.
```

### Overlapping Speech

Create realistic interruptions and overlaps:

```text
Speaker 1: [starting to speak] So I was thinking we could—

Speaker 2: [jumping in] —test our new timing features?

Speaker 1: [surprised] Exactly! How did you—

Speaker 2: [overlapping] —know what you were thinking? Lucky guess!
```

### Emotional Variation Across Speakers

```text
Speaker 1: [professionally] Good morning, everyone. Let's begin the meeting.

Speaker 2: [enthusiastically] I'm SO excited to share our results!

Speaker 3: [skeptically] Let's see the data first before celebrating.

Speaker 1: [calmly] Both perspectives are valid. Let's review together.
```

### Best Practices for Multi-Speaker

1. **Assign distinct voices** from Voice Library to each speaker
2. **Use clear speaker labels** (Speaker 1:, Sarah:, etc.)
3. **Vary tags across speakers** to create distinct personalities
4. **Include natural pauses** between speaker turns
5. **Test emotional consistency** for each character

### Common Multi-Speaker Pitfalls

❌ **All speakers sound the same**

- Cause: Using similar voices or insufficient tag variation
- Fix: Choose voices with distinct characteristics; use character-specific tags

❌ **Unnatural pacing between speakers**

- Cause: No pause indicators
- Fix: Add `[pause]` tags or ellipses between turns

❌ **Emotional inconsistency**

- Cause: Tags don't match character personality
- Fix: Create character profiles with appropriate tag sets

---

## Common Pitfalls & Solutions

### Problem: Inconsistent Output Quality

**Symptoms**: Generated audio varies wildly between runs

**Causes & Solutions**:

- ❌ **Prompt too short** → ✅ Use 250+ characters
- ❌ **Stability too low** → ✅ Increase to Natural or Robust
- ❌ **Voice doesn't match tags** → ✅ Choose more appropriate voice
- ❌ **Too many conflicting tags** → ✅ Simplify tag usage

### Problem: Tags Not Working

**Symptoms**: Audio ignores audio tags

**Causes & Solutions**:

- ❌ **Stability set to Robust** → ✅ Use Creative or Natural
- ❌ **Voice incompatible** → ✅ Test with V3-optimized voices
- ❌ **Tag misspelled** → ✅ Check spelling: `[lauhgs]` should be `[laughs]`
- ❌ **Using PVC instead of IVC** → ✅ Switch to Instant Voice Clone

### Problem: Pauses Not Working

**Symptoms**: No pauses where expected

**Causes & Solutions**:

- ❌ **Using SSML `<break>` tags** → ✅ Use `[pause]` tags or ellipses
- ❌ **Insufficient pause indicators** → ✅ Add `[long pause]` or multiple ellipses
- ❌ **Voice too energetic** → ✅ Choose calmer voice or add more explicit tags

### Problem: Unnatural Multi-Speaker Dialogue

**Symptoms**: Speakers blend together or sound robotic

**Causes & Solutions**:

- ❌ **Voices too similar** → ✅ Choose voices with distinct characteristics
- ❌ **No emotional variation** → ✅ Add character-specific tags
- ❌ **Missing speaker transitions** → ✅ Add pauses between speakers
- ❌ **Inconsistent character voice** → ✅ Maintain tag consistency per character

### Problem: Audio Artifacts or Noise

**Symptoms**: Clicks, pops, or distortion in output

**Causes & Solutions**:

- ❌ **Conflicting tags** → ✅ Remove redundant/opposing tags
- ❌ **Extreme punctuation** → ✅ Moderate use of ALL CAPS and !!!
- ❌ **Stability too low** → ✅ Increase stability slider
- ❌ **Poor voice quality** → ✅ Use professionally recorded IVC samples

---

## Best Practices Checklist

Use this comprehensive todo-style checklist to ensure you're following V3 best practices:

### ✅ Pre-Production Planning

- [ ] **Verify V3 is the right model**

  - Check if you need real-time performance (if yes, consider V2 Turbo)
  - Confirm SSML/phoneme tags aren't required (V3 doesn't support them)
  - Ensure character limit (5,000) meets your needs
  - Example: ✅ Audiobook narration (V3), ❌ Real-time chatbot (V2 Turbo)

- [ ] **Select appropriate voice(s)**

  - Browse [V3-optimized voice collection](https://elevenlabs.io/app/voice-library/collections/aF6JALq9R6tXwCczjhKH)
  - Test voice with sample tags before full production
  - For IVCs, include varied emotional samples in training data
  - Avoid PVCs for V3 (not fully optimized)
  - Example: For dramatic audiobook, choose expressive voice like "Rachel" with emotional range

- [ ] **Plan character/voice mapping** (for multi-speaker)
  - Assign distinct Voice Library voices to each speaker
  - Create character profiles with appropriate tag sets
  - Example:
    - Sarah (professional): `[calm]`, `[thoughtful]`, `[reassuring]`
    - Jake (enthusiastic): `[excited]`, `[laughs]`, `[energetic]`

### ✅ Script Preparation

- [ ] **Ensure adequate prompt length**

  - Aim for 250+ characters minimum
  - Add narrative context if script is too short
  - Example: Instead of `"Hello!"`, use `"[cheerful] Hello there! [excited] I've been looking forward to seeing you all day. How are you doing?"`

- [ ] **Remove SSML tags if migrating from V2**

  - Replace `<break time="1.5s" />` with `[pause]` or `…`
  - Remove `<phoneme>` tags (not supported in V3)
  - Example: `"Wait<break time="2s"/>Okay"` → `"Wait [long pause] Okay"` or `"Wait… … Okay"`

- [ ] **Add strategic audio tags**

  - Use 1-2 tags per sentence for natural delivery
  - Place tags before/after relevant dialogue segments
  - Match tags to voice character and training data
  - Example: `"[whispers] I have a secret. [giggles] You won't believe it!"`

- [ ] **Leverage punctuation & capitalization**

  - Use ellipses (…) for pauses and hesitation
  - Use ALL CAPS for emphasis (sparingly)
  - Use proper punctuation for natural rhythm
  - Example: `"It was a VERY long day [sigh] … nobody listens anymore."`

- [ ] **Structure multi-speaker dialogues clearly**
  - Use clear speaker labels (Speaker 1:, Sarah:, etc.)
  - Add pauses between speaker turns
  - Include overlapping indicators where appropriate
  - Example:

    ```text
    Sarah: [excited] Did you hear the news?

    Jake: [curious] No, what happened?
    ```

### ✅ Settings Configuration

- [ ] **Set appropriate stability level**

  - **Creative**: For dramatic, expressive content
  - **Natural**: For balanced, general-purpose content
  - **Robust**: For consistency-critical applications
  - Example: Audiobook with emotional scenes → Creative; Corporate training → Robust

- [ ] **Test stability with sample tags**

  - Generate test clips with key tags at different stability levels
  - Verify tags work as expected before full production
  - Example: Test `[whispers]`, `[excited]`, `[laughs]` at Natural and Creative settings

- [ ] **Configure speed if needed**
  - Use speed setting (0.7–1.2 range)
  - Or use tags like `[speaking quickly]`, `[speaking slowly]`
  - Example: Technical content → 0.9x speed; Dramatic monologue → 1.0x with varied tag pacing

### ✅ Audio Tag Best Practices

- [ ] **Use voice-appropriate tags**

  - Match tags to voice training data and character
  - Avoid contradictory tags (e.g., `[whispers]` on a shouty voice)
  - Test experimental tags thoroughly before production
  - Example: Calm, meditative voice → `[peaceful]`, `[soft]`; NOT `[shouting]`, `[frantic]`

- [ ] **Avoid tag overload**

  - Don't stack multiple similar tags
  - Space tags naturally throughout script
  - Remove redundant tags after testing
  - Example: ❌ `[excited] [happy] [joyful] Hello!` → ✅ `[excited] Hello! This is wonderful!`

- [ ] **Combine tags strategically**

  - Use complementary tag combinations
  - Test combinations with your specific voice
  - Document effective combinations for reuse
  - Example: `[thoughtful] Hmm… [whispers] I think I know what to do.`

- [ ] **Include pause tags where SSML breaks existed**
  - Replace old `<break>` tags with `[pause]`, `[short pause]`, `[long pause]`
  - Or use ellipses (…) for natural pauses
  - Test pause duration for your voice
  - Example: `"Wait [long pause] I've got it!"` or `"Wait… … I've got it!"`

### ✅ Multi-Speaker Specific Practices

- [ ] **Use distinct voices for each speaker**

  - Assign different Voice Library voices to each character
  - Ensure voices have noticeably different characteristics
  - Example: Deep male voice vs. high female voice vs. neutral narrator

- [ ] **Maintain character consistency**

  - Use consistent tags for each character throughout script
  - Create tag "profiles" for each character
  - Example: Character A always uses `[professional]`, `[calm]`; Character B uses `[energetic]`, `[laughs]`

- [ ] **Add natural dialogue flow indicators**

  - Include `[pause]` between speaker turns
  - Use overlapping indicators: `—` or `[jumping in]`
  - Add trailing off indicators: `…` or `[trailing off]`
  - Example:
    ```text
    A: I was thinking we could—
    B: [jumping in] —go to the park? Great idea!
    ```

- [ ] **Test speaker transitions**
  - Verify speaker changes are clear and natural
  - Adjust pauses if transitions feel abrupt
  - Example: Add `[pause]` or line break between speakers if dialogue feels rushed

### ✅ Quality Assurance

- [ ] **Generate test clips before full production**

  - Test key emotional moments with different stability settings
  - Verify tag effectiveness with chosen voice(s)
  - Check multi-speaker transitions and overlaps
  - Example: Generate 3-4 test paragraphs covering different emotions/tags

- [ ] **Review for audio artifacts**

  - Listen for clicks, pops, or distortion
  - Reduce conflicting tags if artifacts present
  - Increase stability if output is too unstable
  - Example: If `[laughs] [excited]` causes distortion, try just `[excited]`

- [ ] **Verify emotional consistency**

  - Check that tags produce intended emotions
  - Ensure character personalities remain consistent
  - Adjust tags if delivery doesn't match intent
  - Example: If `[curious]` sounds too aggressive, try `[gently curious]` or switch to `[thoughtful]`

- [ ] **Test across different playback systems**
  - Listen on headphones, speakers, mobile devices
  - Verify pauses and emphasis translate across systems
  - Example: Pauses that work on headphones might feel different on phone speakers

### ✅ Iteration & Optimization

- [ ] **Document effective tag combinations**

  - Keep notes on which tags work best with which voices
  - Record optimal stability settings for different content types
  - Build a library of successful prompts for reuse
  - Example: "Voice: Rachel | Tag: `[whispers]` | Stability: Creative | Works great for intimate scenes"

- [ ] **Refine based on output**

  - If tags aren't working, try different voice
  - If output is inconsistent, increase stability or prompt length
  - If pauses are wrong, adjust tag or punctuation
  - Example: `[pause]` too short → Try `[long pause]` or `… …`

- [ ] **A/B test critical sections**

  - Generate same section with different tags/settings
  - Compare outputs and select best version
  - Use findings to refine remaining script
  - Example: Test key emotional scene with Creative vs. Natural stability

- [ ] **Gather feedback**
  - Share samples with target audience
  - Iterate based on listener reactions
  - Adjust tags/voices to improve engagement
  - Example: If listeners find narrator too monotone, add more varied emotional tags

### ✅ Production Workflow

- [ ] **Batch similar content together**

  - Generate content with same voice/settings in batches
  - Maintain consistency across related sections
  - Example: Generate all Speaker A lines, then all Speaker B lines

- [ ] **Maintain version control**

  - Save scripts with settings/voice metadata
  - Track iterations and changes
  - Document why changes were made
  - Example: `script_v3_rachel_creative_2024-12-30.txt`

- [ ] **Plan for post-production**

  - Remove dialogue tags if spoken aloud (V2 issue mostly)
  - Adjust levels for speaker volume consistency
  - Add music/sound design around V3 dialogue
  - Example: If V3 outputs `"she said excitedly"`, edit out in post

- [ ] **Test character limit compliance**
  - Verify sections don't exceed 5,000 characters
  - Split long scripts into logical segments
  - Example: For 20,000 character script, split into 4 sections of ~4,500 chars each

### ✅ Troubleshooting Checklist

- [ ] **If tags don't work:**

  - ✅ Switch from Robust to Creative/Natural stability
  - ✅ Verify voice is V3-compatible (use IVC, not PVC)
  - ✅ Check tag spelling (common: `[lauhgs]` should be `[laughs]`)
  - ✅ Test with V3-optimized voice from curated collection

- [ ] **If output is inconsistent:**

  - ✅ Increase prompt length to 250+ characters
  - ✅ Increase stability to Natural or Robust
  - ✅ Simplify tag usage (remove conflicting tags)
  - ✅ Switch to more stable voice

- [ ] **If pauses don't work:**

  - ✅ Replace SSML `<break>` with `[pause]` tags
  - ✅ Use multiple ellipses: `… …`
  - ✅ Try `[long pause]` instead of `[pause]`
  - ✅ Add paragraph breaks between sections

- [ ] **If multi-speaker dialogue blends:**
  - ✅ Use more distinct voices (different genders/ages/accents)
  - ✅ Add character-specific tags consistently
  - ✅ Increase pauses between speaker turns
  - ✅ Verify speaker labels are clear

---

## Additional Resources

- **Official ElevenLabs V3 Documentation**: [elevenlabs.io/docs](https://elevenlabs.io)
- **V3-Optimized Voice Collection**: [Voice Library Collection](https://elevenlabs.io/app/voice-library/collections/aF6JALq9R6tXwCczjhKH)
- **Community Examples**: Explore ElevenLabs Discord for user-shared V3 examples
- **API Reference**: [Text to Dialogue API](https://elevenlabs.io/docs/api-reference/text-to-dialogue)

---

## Quick Reference Card

### ✅ Do's for V3

- ✅ Use 250+ character prompts
- ✅ Choose V3-optimized IVC voices
- ✅ Use Creative/Natural stability for expressive content
- ✅ Add 1-2 tags per sentence
- ✅ Match tags to voice character
- ✅ Use ellipses (…) for pauses
- ✅ Leverage capitalization for emphasis
- ✅ Test tags with your specific voice before production
- ✅ Use distinct voices for multi-speaker dialogue

### ❌ Don'ts for V3

- ❌ Don't use very short prompts (under 250 chars)
- ❌ Don't use PVCs (not optimized for V3)
- ❌ Don't use SSML `<break>` or `<phoneme>` tags
- ❌ Don't expect whispering voices to shout (or vice versa)
- ❌ Don't overload with too many tags
- ❌ Don't use Robust stability if you need tags to work
- ❌ Don't use V3 for real-time applications (high latency)
- ❌ Don't expect V3 to work like V2 (different control paradigm)

---

**Last Updated**: 2024-12-30  
**Guide Version**: 1.0  
**ElevenLabs V3 Status**: Alpha
