# Prompting Guide - ElevenLabs Agents Platform

System design principles for production-grade conversational AI

## Introduction

Effective prompting transforms ElevenLabs Agents from robotic to lifelike.

A system prompt is the personality and policy blueprint of your AI agent. In enterprise use, it tends to be elaborate—defining the agent's role, goals, allowable tools, step-by-step instructions for certain tasks, and guardrails describing what the agent should not do. The way you structure this prompt directly impacts reliability.

The system prompt controls conversational behavior and response style, but does not control conversation flow mechanics like turn-taking, or agent settings like which languages an agent can speak. These aspects are handled at the platform level.

## Prompt Engineering Fundamentals

A system prompt is the personality and policy blueprint of your AI agent. In enterprise use, it tends to be elaborate—defining the agent's role, goals, allowable tools, step-by-step instructions for certain tasks, and guardrails describing what the agent should not do. The way you structure this prompt directly impacts reliability.

The following principles form the foundation of production-grade prompt engineering:

### Separate Instructions into Clean Sections

Separating instructions into dedicated sections with markdown headings helps the model prioritize and interpret them correctly. Use whitespace and line breaks to separate instructions.

**Why this matters for reliability:** Models are tuned to pay extra attention to certain headings (especially `# Guardrails`), and clear section boundaries prevent instruction bleed where rules from one context affect another.

### Be as Concise as Possible

Keep every instruction short, clear, and action-based. Remove filler words and restate only what is essential for the model to act correctly.

**Why this matters for reliability:** Concise instructions reduce ambiguity and token usage. Every unnecessary word is a potential source of misinterpretation.

### Emphasize Critical Instructions

Highlight critical steps by adding "This step is important" at the end of the line. Repeating the most important 1-2 instructions twice in the prompt can help reinforce them.

**Why this matters for reliability:** In complex prompts, models may prioritize recent context over earlier instructions. Emphasis and repetition ensure critical rules aren't overlooked.

### Normalize Inputs and Outputs

Voice agents often misinterpret or misformat structured information such as emails, IDs, or record locators. To ensure accuracy, separate (or "normalize") how data is spoken to the user from how it is written when used in tools or APIs.

**Why this matters for reliability:** Text-to-speech models sometimes mispronounce symbols like "@" or "." naturally. Normalizing to spoken format ("john at company dot com") creates natural, understandable speech while maintaining correct written format for tools.

### Provide Clear Examples

Include examples in the prompt to illustrate how agents should behave, use tools, or format data. Large language models follow instructions more reliably when they have concrete examples to reference.

**Why this matters for reliability:** Examples reduce ambiguity and provide a reference pattern. They're especially valuable for complex formatting, multi-step processes, and edge cases.

### Dedicate a Guardrails Section

List all non-negotiable rules the model must always follow in a dedicated `# Guardrails` section. Models are tuned to pay extra attention to this heading.

**Why this matters for reliability:** Guardrails prevent inappropriate responses and ensure compliance with policies. Centralizing them in a dedicated section makes them easier to audit and update.

Example guardrails section:

```
# Guardrails

Never share customer data across conversations or reveal sensitive account information without proper verification.
Never process refunds over $500 without supervisor approval.
Never make promises about delivery dates that aren't confirmed in the order system.
Acknowledge when you don't know an answer instead of guessing.
If a customer becomes abusive, politely end the conversation and offer to escalate to a supervisor.
```

## Tool Configuration for Reliability

Agents capable of handling transactional workflows can be highly effective. To enable this, they must be equipped with tools that let them perform actions in other systems or fetch live data from them.

Equally important as prompt structure is how you describe the tools available to your agent. Clear, action-oriented tool definitions help the model invoke them correctly and recover gracefully from errors.

### Describe Tools Precisely with Detailed Parameters

When creating a tool, add descriptions to all parameters. This helps the LLM construct tool calls accurately.

**Tool description:** "Looks up customer order status by order ID and returns current status, estimated delivery date, and tracking number."

**Parameter descriptions:**

- `order_id` (required): "The unique order identifier, formatted as written characters (e.g., 'ORD123456')"
- `include_history` (optional): "If true, returns full order history including status changes"

**Why this matters for reliability:** Parameter descriptions act as inline documentation for the model. They clarify format expectations, required vs. optional fields, and acceptable values.

### Explain When and How to Use Each Tool in the System Prompt

Clearly define in your system prompt when and how each tool should be used. Don't rely solely on tool descriptions—provide usage context and sequencing logic.

Example:

```
# Tools

You have access to the following tools:

## `getOrderStatus`

Use this tool when a customer asks about their order. Always call this tool before providing order information—never rely on memory or assumptions.

**When to use:**

- Customer asks "Where is my order?"
- Customer provides an order number
- Customer asks about delivery estimates

**How to use:**

1. Collect the order ID from the customer in spoken format
2. Convert to written format using character normalization rules
3. Call `getOrderStatus` with the formatted order ID
4. Present the results to the customer in natural language

**Error handling:**
If the tool returns "Order not found", ask the customer to verify the order number and try again.

## `processRefund`

Use this tool only after verifying:

1. Customer identity has been confirmed
2. Order is eligible for refund (within 30 days, not already refunded)
3. Refund amount is under $500 (escalate to supervisor if over $500)

**Required before calling:**

- Order ID (from `getOrderStatus`)
- Refund reason code
- Customer confirmation

This step is important: Always confirm refund details with the customer before calling this tool.
```

### Use Character Normalization for Tool Inputs

When tools require structured identifiers (emails, phone numbers, codes), ensure the prompt clarifies when to use written vs. spoken formats.

Example:

```
# Tools

## `lookupAccount`

**Parameters:**

- `email` (required): Customer email address in written format (e.g., "john.smith@company.com")

**Usage:**

1. Ask customer for their email in spoken format: "Can you provide your email address?"
2. Listen for spoken format: "john dot smith at company dot com"
3. Convert to written format: "john.smith@company.com"
4. Pass written format to this tool

**Character normalization for email:**

- "at" → "@"
- "dot" → "."
- Remove spaces between words
```

### Handle Tool Call Failures Gracefully

Tools can sometimes fail due to network issues, missing data, or other errors. Include clear instructions in your system prompt for recovery.

**Why this matters for reliability:** Tool failures are inevitable in production. Without explicit handling instructions, agents may hallucinate responses or provide incorrect information.

Example:

```
# Tool Error Handling

If any tool call fails or returns an error:

1. Acknowledge the issue to the customer: "I'm having trouble accessing that information right now."
2. Do not guess or make up information
3. Offer alternatives:
   - Try the tool again if it might be a temporary issue
   - Offer to escalate to a human agent
   - Provide a callback option
4. If the error persists after 2 attempts, escalate to a supervisor

**Example responses:**

- "I'm having trouble looking up that order right now. Let me try again... [retry]"
- "I'm unable to access the order system at the moment. I can transfer you to a specialist who can help, or we can schedule a callback. Which would you prefer?"
```

## Architecture Patterns for Enterprise Agents

While strong prompts and tools form the foundation of agent reliability, production systems require thoughtful architectural design. Enterprise agents handle complex workflows that often exceed the scope of a single, monolithic prompt.

### Keep Agents Specialized

Overly broad instructions or large context windows increase latency and reduce accuracy. Each agent should have a narrow, clearly defined knowledge base and set of responsibilities.

**Why this matters for reliability:** Specialized agents have fewer edge cases to handle, clearer success criteria, and faster response times. They're easier to test, debug, and improve.

A general-purpose "do everything" agent is harder to maintain and more likely to fail in production than a network of specialized agents with clear handoffs.

### Use Orchestrator and Specialist Patterns

For complex tasks, design multi-agent workflows that hand off tasks between specialized agents—and to human operators when needed.

**Architecture pattern:**

1. **Orchestrator agent:** Routes incoming requests to appropriate specialist agents based on intent classification
2. **Specialist agents:** Handle domain-specific tasks (billing, scheduling, technical support, etc.)
3. **Human escalation:** Defined handoff criteria for complex or sensitive cases

**Benefits of this pattern:**

- Each specialist has a focused prompt and reduced context
- Easier to update individual specialists without affecting the system
- Clear metrics per domain (billing resolution rate, scheduling success rate, etc.)
- Reduced latency per interaction (smaller prompts, faster inference)

### Define Clear Handoff Criteria

When designing multi-agent workflows, specify exactly when and how control should transfer between agents or to human operators.

**Orchestrator agent example:**

```
# Goal

Route customer requests to the appropriate specialist agent based on intent.

## Routing Logic

**Billing specialist:** Customer mentions payment, invoice, refund, charge, subscription, or account balance
**Technical support specialist:** Customer reports error, bug, issue, not working, broken
**Scheduling specialist:** Customer wants to book, reschedule, cancel, or check appointment
**Human escalation:** Customer is angry, requests supervisor, or issue is unresolved after 2 specialist attempts

## Handoff Process

1. Classify customer intent based on first message
2. Provide brief acknowledgment: "I'll connect you with our [billing/technical/scheduling] team."
3. Transfer conversation with context summary:
   - Customer name
   - Primary issue
   - Any account identifiers already collected
4. Do not repeat information collection that already occurred
```

**Specialist agent example:**

```
# Personality

You are a billing specialist for Acme Corp. You handle payment issues, refunds, and subscription changes.

# Goal

Resolve billing inquiries by:

1. Verifying customer identity
2. Looking up account and billing history
3. Processing refunds (under $500) or escalating (over $500)
4. Updating subscription settings when requested

# Guardrails

Never access account information without identity verification.
Never process refunds over $500 without supervisor approval.
If the customer's issue is not billing-related, transfer back to the orchestrator agent.
```

## Model Selection for Enterprise Reliability

Selecting the right model depends on your performance requirements—particularly latency, accuracy, and tool-calling reliability. Different models offer different tradeoffs between speed, reasoning capability, and cost.

### Understand the Tradeoffs

**Latency:** Smaller models (fewer parameters) generally respond faster, making them suitable for high-frequency, low-complexity interactions.

**Accuracy:** Larger models provide stronger reasoning capabilities and better handle complex, multi-step tasks, but with higher latency and cost.

**Tool-calling reliability:** Not all models handle tool/function calling with equal precision. Some excel at structured output, while others may require more explicit prompting.

### Model Recommendations by Use Case

Based on deployments across millions of agent interactions, the following patterns emerge:

- **GPT-4o or GLM 4.5 Air (recommended starting point):** Best for general-purpose enterprise agents where latency, accuracy, and cost must all be balanced. Offers low-to-moderate latency with strong tool-calling performance and reasonable cost per interaction. Ideal for customer support, scheduling, order management, and general inquiry handling.

- **Gemini 2.5 Flash Lite (ultra-low latency):** Best for high-frequency, simple interactions where speed is critical. Provides the lowest latency with broad general knowledge, though with lower performance on complex tool-calling. Cost-effective at scale for initial routing/triage, simple FAQs, appointment confirmations, and basic data collection.

- **Claude Sonnet 4 or 4.5 (complex reasoning):** Best for multi-step problem-solving, nuanced judgment, and complex tool orchestration. Offers the highest accuracy and reasoning capability with excellent tool-calling reliability, though with higher latency and cost. Ideal for tasks where mistakes are costly, such as technical troubleshooting, financial advisory, compliance-sensitive workflows, and complex refund/escalation decisions.

### Benchmark with Your Actual Prompts

Model performance varies significantly based on prompt structure and task complexity. Before committing to a model:

1. Test 2-3 candidate models with your actual system prompt
2. Evaluate on real user queries or synthetic test cases
3. Measure latency, accuracy, and tool-calling success rate
4. Optimize for the best tradeoff given your specific requirements

## Iteration and Testing

Reliability in production comes from continuous iteration. Even well-constructed prompts can fail in real use. What matters is learning from those failures and improving through disciplined testing.

### Configure Evaluation Criteria

Attach concrete evaluation criteria to each agent to monitor success over time and check for regressions.

**Key metrics to track:**

- **Task completion rate:** Percentage of user intents successfully addressed
- **Escalation rate:** Percentage of conversations requiring human intervention

### Analyze Failure Patterns

When agents underperform, identify patterns in problematic interactions:

- **Where does the agent provide incorrect information?** → Strengthen instructions in specific sections
- **When does it fail to understand user intent?** → Add examples or simplify language
- **Which user inputs cause it to break character?** → Add guardrails for edge cases
- **Which tools fail most often?** → Improve error handling or parameter descriptions

Review conversation transcripts where user satisfaction was low or tasks weren't completed.

### Make Targeted Refinements

Update specific sections of your prompt to address identified issues:

1. **Isolate the problem:** Identify which prompt section or tool definition is causing failures
2. **Test changes on specific examples:** Use conversations that previously failed as test cases
3. **Make one change at a time:** Isolate improvements to understand what works
4. **Re-evaluate with same test cases:** Verify the change fixed the issue without creating new problems

Avoid making multiple prompt changes simultaneously. This makes it impossible to attribute improvements or regressions to specific edits.

### Configure Data Collection

Configure your agent to summarize data from each conversation. This allows you to analyze interaction patterns, identify common user requests, and continuously improve your prompt based on real-world usage.

## Production Considerations

### Handle Errors Across All Tool Integrations

Ensure your system prompt includes comprehensive error handling for all tools your agent uses. This prevents hallucination and maintains user trust when systems fail.

## Key Takeaways

1. **Structure matters:** Use clear sections, headings, and whitespace to help models prioritize instructions
2. **Conciseness is critical:** Every word should serve a purpose; remove filler
3. **Emphasize guardrails:** Use dedicated sections and repetition for non-negotiable rules
4. **Tool clarity:** Provide detailed parameter descriptions and usage context
5. **Specialize agents:** Narrow scope improves reliability and reduces latency
6. **Test continuously:** Use real conversation data to identify and fix failure patterns
7. **Choose the right model:** Balance latency, accuracy, and cost for your specific use case

---

**Source:** [ElevenLabs Prompting Guide](https://elevenlabs.io/docs/agents-platform/best-practices/prompting-guide)
