# Prompting guide

> System design principles for production-grade conversational AI

## Introduction

Effective prompting transforms [ElevenLabs Agents](/docs/agents-platform/overview) from robotic to lifelike.

<Frame background="subtle">
  ![ElevenLabs Agents prompting guide](file:f7cee6a4-43ff-4b1d-a4e3-f8a810d3429b)
</Frame>

A system prompt is the personality and policy blueprint of your AI agent. In enterprise use, it tends to be elaborateâ€”defining the agent's role, goals, allowable tools, step-by-step instructions for certain tasks, and guardrails describing what the agent should not do. The way you structure this prompt directly impacts reliability.

<Note>
  The system prompt controls conversational behavior and response style, but does not control
  conversation flow mechanics like turn-taking, or agent settings like which languages an agent can
  speak. These aspects are handled at the platform level.
</Note>

<Frame background="subtle">
  ![Enterprise agent reliability
  framework](file:186dace5-66e9-4604-b586-5c16402ea3f8)
</Frame>

## Prompt engineering fundamentals

A system prompt is the personality and policy blueprint of your AI agent. In enterprise use, it tends to be elaborateâ€”defining the agent's role, goals, allowable tools, step-by-step instructions for certain tasks, and guardrails describing what the agent should not do. The way you structure this prompt directly impacts reliability.

The following principles form the foundation of production-grade prompt engineering:

### Separate instructions into clean sections

Separating instructions into dedicated sections with markdown headings helps the model prioritize and interpret them correctly. Use whitespace and line breaks to separate instructions.

**Why this matters for reliability:** Models are tuned to pay extra attention to certain headings (especially `# Guardrails`), and clear section boundaries prevent instruction bleed where rules from one context affect another.

<CodeBlocks>
  ```mdx title="Less effective approach"
  You are a customer service agent. Be polite and helpful. Never share sensitive data. You can look up orders and process refunds. Always verify identity first. Keep responses under 3 sentences unless the user asks for details.
  ```

```mdx title="Recommended approach"
# Personality

You are a customer service agent for Acme Corp. You are polite, efficient, and solution-oriented.

# Goal

Help customers resolve issues quickly by looking up orders and processing refunds when appropriate.

# Guardrails

Never share sensitive customer data across conversations.
Always verify customer identity before accessing account information.

# Tone

Keep responses concise (under 3 sentences) unless the user requests detailed explanations.
```

</CodeBlocks>

### Be as concise as possible

Keep every instruction short, clear, and action-based. Remove filler words and restate only what is essential for the model to act correctly.

**Why this matters for reliability:** Concise instructions reduce ambiguity and token usage. Every unnecessary word is a potential source of misinterpretation.

<CodeBlocks>
  ```mdx title="Less effective approach"
  # Tone

When you're talking to customers, you should try to be really friendly and approachable, making sure that you're speaking in a way that feels natural and conversational, kind of like how you'd talk to a friend, but still maintaining a professional demeanor that represents the company well.

````

```mdx title="Recommended approach"
# Tone

Speak in a friendly, conversational manner while maintaining professionalism.
````

</CodeBlocks>

<Note>
  If you need the agent to maintain a specific tone, define it explicitly and concisely in the `#
    Personality` or `# Tone` section. Avoid repeating tone guidance throughout the prompt.
</Note>

### Emphasize critical instructions

Highlight critical steps by adding "This step is important" at the end of the line. Repeating the most important 1-2 instructions twice in the prompt can help reinforce them.

**Why this matters for reliability:** In complex prompts, models may prioritize recent context over earlier instructions. Emphasis and repetition ensure critical rules aren't overlooked.

<CodeBlocks>
  ```mdx title="Less effective approach"
  # Goal

Verify customer identity before accessing their account.
Look up order details and provide status updates.
Process refund requests when eligible.

````

```mdx title="Recommended approach"
# Goal

Verify customer identity before accessing their account. This step is important.
Look up order details and provide status updates.
Process refund requests when eligible.

# Guardrails

Never access account information without verifying customer identity first. This step is important.
````

</CodeBlocks>

### Normalize inputs and outputs

Voice agents often misinterpret or misformat structured information such as emails, IDs, or record locators. To ensure accuracy, separate (or "normalize") how data is spoken to the user from how it is written when used in tools or APIs.

**Why this matters for reliability:** Text-to-speech models sometimes mispronounce symbols like "@" or "." naturally, for example when an agent speaks "[john@company.com](mailto:john@company.com)" directly. Normalizing to spoken format ("john at company dot com") creates natural, understandable speech while maintaining correct written format for tools.

<CodeBlocks>
  ```mdx title="Less effective approach"
  When collecting the customer's email, repeat it back to them exactly as they said it, then use it in the `lookupAccount` tool.
  ```

```mdx title="Recommended approach"
# Character normalization

When collecting structured data (emails, phone numbers, confirmation codes):

**Spoken format** (to/from user):

- Email: "john dot smith at company dot com"
- Phone: "five five five... one two three... four five six seven"
- Code: "A B C one two three"

**Written format** (for tools/APIs):

- Email: "john.smith@company.com"
- Phone: "5551234567"
- Code: "ABC123"

Always collect data in spoken format, then convert to written format before passing to tools.

## Example normalization rules

- "@" symbol â†’ spoken as "at", written as "@"
- "." symbol â†’ spoken as "dot", written as "."
- Numbers â†’ spoken individually ("one two three"), written as digits ("123")
- Spaces in codes â†’ spoken with pauses ("A B C"), written without spaces ("ABC")
```

</CodeBlocks>

<Tip>
  Add character normalization rules to your system prompt when agents collect emails, phone numbers,
  confirmation codes, or other structured identifiers that will be passed to tools.
</Tip>

### Provide clear examples

Include examples in the prompt to illustrate how agents should behave, use tools, or format data. Large language models follow instructions more reliably when they have concrete examples to reference.

**Why this matters for reliability:** Examples reduce ambiguity and provide a reference pattern. They're especially valuable for complex formatting, multi-step processes, and edge cases.

<CodeBlocks>
  ```mdx title="Less effective approach"
  When a customer provides a confirmation code, make sure to format it correctly before looking it up.
  ```

```mdx title="Recommended approach"
When a customer provides a confirmation code:

1. Listen for the spoken format (e.g., "A B C one two three")
2. Convert to written format (e.g., "ABC123")
3. Pass to `lookupReservation` tool

## Examples

User says: "My code is A... B... C... one... two... three"
You format: "ABC123"

User says: "X Y Z four five six seven eight"
You format: "XYZ45678"
```

</CodeBlocks>

### Dedicate a guardrails section

List all non-negotiable rules the model must always follow in a dedicated `# Guardrails` section. Models are tuned to pay extra attention to this heading.

**Why this matters for reliability:** Guardrails prevent inappropriate responses and ensure compliance with policies. Centralizing them in a dedicated section makes them easier to audit and update.

<CodeBlocks>
  ```mdx title="Recommended approach"
  # Guardrails

Never share customer data across conversations or reveal sensitive account information without proper verification.
Never process refunds over $500 without supervisor approval.
Never make promises about delivery dates that aren't confirmed in the order system.
Acknowledge when you don't know an answer instead of guessing.
If a customer becomes abusive, politely end the conversation and offer to escalate to a supervisor.

````
</CodeBlocks>

To learn more about designing effective guardrails, see our guide on [safety and moderation](/docs/agents-platform/customization/privacy).

## Tool configuration for reliability

Agents capable of handling transactional workflows can be highly effective. To enable this, they must be equipped with tools that let them perform actions in other systems or fetch live data from them.

Equally important as prompt structure is how you describe the tools available to your agent. Clear, action-oriented tool definitions help the model invoke them correctly and recover gracefully from errors.

### Describe tools precisely with detailed parameters

When creating a tool, add descriptions to all parameters. This helps the LLM construct tool calls accurately.

**Tool description:** "Looks up customer order status by order ID and returns current status, estimated delivery date, and tracking number."

**Parameter descriptions:**

* `order_id` (required): "The unique order identifier, formatted as written characters (e.g., 'ORD123456')"
* `include_history` (optional): "If true, returns full order history including status changes"

**Why this matters for reliability:** Parameter descriptions act as inline documentation for the model. They clarify format expectations, required vs. optional fields, and acceptable values.

### Explain when and how to use each tool in the system prompt

Clearly define in your system prompt when and how each tool should be used. Don't rely solely on tool descriptionsâ€”provide usage context and sequencing logic.

<CodeBlocks>
```mdx title="Recommended approach"
# Tools

You have access to the following tools:

## `getOrderStatus`

Use this tool when a customer asks about their order. Always call this tool before providing order informationâ€”never rely on memory or assumptions.

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
````

</CodeBlocks>

### Use character normalization for tool inputs

When tools require structured identifiers (emails, phone numbers, codes), ensure the prompt clarifies when to use written vs. spoken formats.

<CodeBlocks>
  ```mdx title="Recommended approach"
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

- "at" â†’ "@"
- "dot" â†’ "."
- Remove spaces between words

````
</CodeBlocks>

### Handle tool call failures gracefully

Tools can sometimes fail due to network issues, missing data, or other errors. Include clear instructions in your system prompt for recovery.

**Why this matters for reliability:** Tool failures are inevitable in production. Without explicit handling instructions, agents may hallucinate responses or provide incorrect information.

<CodeBlocks>
```mdx title="Recommended approach"
# Tool error handling

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
````

</CodeBlocks>

For detailed guidance on building reliable tool integrations, see our documentation on [Client tools](/docs/agents-platform/customization/tools/client-tools), [Server tools](/docs/agents-platform/customization/tools/server-tools), and [MCP tools](/docs/agents-platform/customization/tools/mcp).

## Architecture patterns for enterprise agents

While strong prompts and tools form the foundation of agent reliability, production systems require thoughtful architectural design. Enterprise agents handle complex workflows that often exceed the scope of a single, monolithic prompt.

### Keep agents specialized

Overly broad instructions or large context windows increase latency and reduce accuracy. Each agent should have a narrow, clearly defined knowledge base and set of responsibilities.

**Why this matters for reliability:** Specialized agents have fewer edge cases to handle, clearer success criteria, and faster response times. They're easier to test, debug, and improve.

<Note>
  A general-purpose "do everything" agent is harder to maintain and more likely to fail in
  production than a network of specialized agents with clear handoffs.
</Note>

### Use orchestrator and specialist patterns

For complex tasks, design multi-agent workflows that hand off tasks between specialized agentsâ€”and to human operators when needed.

**Architecture pattern:**

1. **Orchestrator agent:** Routes incoming requests to appropriate specialist agents based on intent classification
2. **Specialist agents:** Handle domain-specific tasks (billing, scheduling, technical support, etc.)
3. **Human escalation:** Defined handoff criteria for complex or sensitive cases

**Benefits of this pattern:**

- Each specialist has a focused prompt and reduced context
- Easier to update individual specialists without affecting the system
- Clear metrics per domain (billing resolution rate, scheduling success rate, etc.)
- Reduced latency per interaction (smaller prompts, faster inference)

### Define clear handoff criteria

When designing multi-agent workflows, specify exactly when and how control should transfer between agents or to human operators.

<CodeBlocks>
  ```mdx title="Orchestrator agent example"
  # Goal

Route customer requests to the appropriate specialist agent based on intent.

## Routing logic

**Billing specialist:** Customer mentions payment, invoice, refund, charge, subscription, or account balance
**Technical support specialist:** Customer reports error, bug, issue, not working, broken
**Scheduling specialist:** Customer wants to book, reschedule, cancel, or check appointment
**Human escalation:** Customer is angry, requests supervisor, or issue is unresolved after 2 specialist attempts

## Handoff process

1. Classify customer intent based on first message
2. Provide brief acknowledgment: "I'll connect you with our [billing/technical/scheduling] team."
3. Transfer conversation with context summary:
   - Customer name
   - Primary issue
   - Any account identifiers already collected
4. Do not repeat information collection that already occurred

````
</CodeBlocks>

<CodeBlocks>
```mdx title="Specialist agent example"
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
````

</CodeBlocks>

For detailed guidance on building multi-agent workflows, see our documentation on [Workflows](/docs/agents-platform/customization/agent-workflows).

## Model selection for enterprise reliability

Selecting the right model depends on your performance requirementsâ€”particularly latency, accuracy, and tool-calling reliability. Different models offer different tradeoffs between speed, reasoning capability, and cost.

### Understand the tradeoffs

**Latency:** Smaller models (fewer parameters) generally respond faster, making them suitable for high-frequency, low-complexity interactions.

**Accuracy:** Larger models provide stronger reasoning capabilities and better handle complex, multi-step tasks, but with higher latency and cost.

**Tool-calling reliability:** Not all models handle tool/function calling with equal precision. Some excel at structured output, while others may require more explicit prompting.

### Model recommendations by use case

Based on deployments across millions of agent interactions, the following patterns emerge:

- **GPT-4o or GLM 4.5 Air (recommended starting point):** Best for general-purpose enterprise agents where latency, accuracy, and cost must all be balanced. Offers low-to-moderate latency with strong tool-calling performance and reasonable cost per interaction. Ideal for customer support, scheduling, order management, and general inquiry handling.

- **Gemini 2.5 Flash Lite (ultra-low latency):** Best for high-frequency, simple interactions where speed is critical. Provides the lowest latency with broad general knowledge, though with lower performance on complex tool-calling. Cost-effective at scale for initial routing/triage, simple FAQs, appointment confirmations, and basic data collection.

- **Claude Sonnet 4 or 4.5 (complex reasoning):** Best for multi-step problem-solving, nuanced judgment, and complex tool orchestration. Offers the highest accuracy and reasoning capability with excellent tool-calling reliability, though with higher latency and cost. Ideal for tasks where mistakes are costly, such as technical troubleshooting, financial advisory, compliance-sensitive workflows, and complex refund/escalation decisions.

### Benchmark with your actual prompts

Model performance varies significantly based on prompt structure and task complexity. Before committing to a model:

1. Test 2-3 candidate models with your actual system prompt
2. Evaluate on real user queries or synthetic test cases
3. Measure latency, accuracy, and tool-calling success rate
4. Optimize for the best tradeoff given your specific requirements

For detailed model configuration options, see our [Models documentation](/docs/agents-platform/customization/llm).

## Iteration and testing

Reliability in production comes from continuous iteration. Even well-constructed prompts can fail in real use. What matters is learning from those failures and improving through disciplined testing.

### Configure evaluation criteria

Attach concrete evaluation criteria to each agent to monitor success over time and check for regressions.

**Key metrics to track:**

- **Task completion rate:** Percentage of user intents successfully addressed
- **Escalation rate:** Percentage of conversations requiring human intervention

For detailed guidance on configuring evaluation criteria in ElevenLabs, see [Success Evaluation](/docs/agents-platform/customization/agent-analysis/success-evaluation).

### Analyze failure patterns

When agents underperform, identify patterns in problematic interactions:

- **Where does the agent provide incorrect information?** â†’ Strengthen instructions in specific sections
- **When does it fail to understand user intent?** â†’ Add examples or simplify language
- **Which user inputs cause it to break character?** â†’ Add guardrails for edge cases
- **Which tools fail most often?** â†’ Improve error handling or parameter descriptions

Review conversation transcripts where user satisfaction was low or tasks weren't completed.

### Make targeted refinements

Update specific sections of your prompt to address identified issues:

1. **Isolate the problem:** Identify which prompt section or tool definition is causing failures
2. **Test changes on specific examples:** Use conversations that previously failed as test cases
3. **Make one change at a time:** Isolate improvements to understand what works
4. **Re-evaluate with same test cases:** Verify the change fixed the issue without creating new problems

<Warning>
  Avoid making multiple prompt changes simultaneously. This makes it impossible to attribute
  improvements or regressions to specific edits.
</Warning>

### Configure data collection

Configure your agent to summarize data from each conversation. This allows you to analyze interaction patterns, identify common user requests, and continuously improve your prompt based on real-world usage.

For detailed guidance on configuring data collection in ElevenLabs, see [Data Collection](/docs/agents-platform/customization/agent-analysis/data-collection).

### Use simulation for regression testing

Before deploying prompt changes to production, test against a set of known scenarios to catch regressions.

For guidance on testing agents programmatically, see [Simulate Conversations](/docs/agents-platform/guides/simulate-conversations).

## Production considerations

Enterprise agents require additional safeguards beyond prompt quality. Production deployments must account for error handling, compliance, and graceful degradation.

### Handle errors across all tool integrations

Every external tool call is a potential failure point. Ensure your prompt includes explicit error handling for:

- **Network failures:** "I'm having trouble connecting to our system. Let me try again."
- **Missing data:** "I don't see that information in our system. Can you verify the details?"
- **Timeout errors:** "This is taking longer than expected. I can escalate to a specialist or try again."
- **Permission errors:** "I don't have access to that information. Let me transfer you to someone who can help."

## Example prompts

The following examples demonstrate how to apply the principles outlined in this guide to real-world enterprise use cases. Each example includes annotations highlighting which reliability principles are in use.

### Example 1: Technical support agent

<CodeBlocks>
  ```mdx title="Technical support specialist" maxLines=60
  # Personality

You are a technical support specialist for CloudTech, a B2B SaaS platform.
You are patient, methodical, and focused on resolving issues efficiently.
You speak clearly and adapt technical language based on the user's familiarity.

# Environment

You are assisting customers via phone support.
Customers may be experiencing service disruptions and could be frustrated.
You have access to diagnostic tools and the customer account database.

# Tone

Keep responses clear and concise (2-3 sentences unless troubleshooting requires more detail).
Use a calm, professional tone with brief affirmations ("I understand," "Let me check that").
Adapt technical depth based on customer responses.
Check for understanding after complex steps: "Does that make sense?"

# Goal

Resolve technical issues through structured troubleshooting:

1. Verify customer identity using email and account ID
2. Identify affected service and severity level
3. Run diagnostics using `runSystemDiagnostic` tool
4. Provide step-by-step resolution or escalate if unresolved after 2 attempts

This step is important: Always run diagnostics before suggesting solutions.

# Guardrails

Never access customer accounts without identity verification. This step is important.
Never guess at solutionsâ€”always base recommendations on diagnostic results.
If an issue persists after 2 troubleshooting attempts, escalate to engineering team.
Acknowledge when you don't know the answer instead of speculating.

# Tools

## `verifyCustomerIdentity`

**When to use:** At the start of every conversation before accessing account data
**Parameters:**

- `email` (required): Customer email in written format (e.g., "user@company.com")
- `account_id` (optional): Account ID if customer provides it

**Usage:**

1. Ask customer for email in spoken format: "Can I get the email associated with your account?"
2. Convert to written format: "john dot smith at company dot com" â†’ "john.smith@company.com"
3. Call this tool with written email

**Error handling:**
If verification fails, ask customer to confirm email spelling and try again.

## `runSystemDiagnostic`

**When to use:** After verifying identity and understanding the reported issue
**Parameters:**

- `account_id` (required): From `verifyCustomerIdentity` response
- `service_name` (required): Name of affected service (e.g., "api", "dashboard", "storage")

**Usage:**

1. Confirm which service is affected
2. Run diagnostic with account ID and service name
3. Review results before providing solution

**Error handling:**
If diagnostic fails, acknowledge the issue: "I'm having trouble running that diagnostic. Let me escalate to our engineering team."

# Character normalization

When collecting email addresses:

- Spoken: "john dot smith at company dot com"
- Written: "john.smith@company.com"
- Convert "@" from "at", "." from "dot", remove spaces

# Error handling

If any tool call fails:

1. Acknowledge: "I'm having trouble accessing that information right now."
2. Do not guess or make up information
3. Offer to retry once, then escalate if failure persists

````
</CodeBlocks>

**Principles demonstrated:**

* âœ“ Clean section separation (`# Personality`, `# Goal`, `# Tools`, etc.)
* âœ“ One action per line (see `# Goal` numbered steps)
* âœ“ Concise instructions (tone section is brief and clear)
* âœ“ Emphasized critical steps ("This step is important")
* âœ“ Character normalization (email format conversion)
* âœ“ Clear examples (in character normalization section)
* âœ“ Dedicated guardrails section
* âœ“ Precise tool descriptions with when/how/error guidance
* âœ“ Explicit error handling instructions

### Example 2: Customer service refund agent

<CodeBlocks>
```mdx title="Refund processing specialist" maxLines=50
# Personality

You are a refund specialist for RetailCo.
You are empathetic, solution-oriented, and efficient.
You balance customer satisfaction with company policy compliance.

# Goal

Process refund requests through this workflow:

1. Verify customer identity using order number and email
2. Look up order details with `getOrderDetails` tool
3. Confirm refund eligibility (within 30 days, not digital download, not already refunded)
4. For refunds under $100: Process immediately with `processRefund` tool
5. For refunds $100-$500: Apply secondary verification, then process
6. For refunds over $500: Escalate to supervisor with case summary

This step is important: Never process refunds without verifying eligibility first.

# Guardrails

Never process refunds outside the 30-day return window without supervisor approval.
Never process refunds over $500 without supervisor approval. This step is important.
Never access order information without verifying customer identity.
If a customer becomes aggressive, remain calm and offer supervisor escalation.

# Tools

## `verifyIdentity`

**When to use:** At the start of every conversation
**Parameters:**

- `order_id` (required): Order ID in written format (e.g., "ORD123456")
- `email` (required): Customer email in written format

**Usage:**

1. Collect order ID: "Can I get your order number?"
   - Spoken: "O R D one two three four five six"
   - Written: "ORD123456"
2. Collect email and convert to written format
3. Call this tool with both values

## `getOrderDetails`

**When to use:** After identity verification
**Returns:** Order date, items, total amount, refund eligibility status

**Error handling:**
If order not found, ask customer to verify order number and try again.

## `processRefund`

**When to use:** Only after confirming eligibility
**Required checks before calling:**

- Identity verified
- Order is within 30 days
- Order is eligible (not digital, not already refunded)
- Refund amount is under $500

**Parameters:**

- `order_id` (required): From previous verification
- `reason_code` (required): One of "defective", "wrong_item", "late_delivery", "changed_mind"

**Usage:**

1. Confirm refund details with customer: "I'll process a $[amount] refund to your original payment method. It will appear in 3-5 business days. Does that work for you?"
2. Wait for customer confirmation
3. Call this tool

**Error handling:**
If refund processing fails, apologize and escalate: "I'm unable to process that refund right now. Let me escalate to a supervisor who can help."

# Character normalization

Order IDs:

- Spoken: "O R D one two three four five six"
- Written: "ORD123456"
- No spaces, all uppercase

Email addresses:

- Spoken: "john dot smith at retailco dot com"
- Written: "john.smith@retailco.com"
````

</CodeBlocks>

**Principles demonstrated:**

- âœ“ Specialized agent scope (refunds only, not general support)
- âœ“ Clear workflow steps in `# Goal` section
- âœ“ Repeated emphasis on critical rules (refund limits, verification)
- âœ“ Detailed tool usage with "when to use" and "required checks"
- âœ“ Character normalization for structured IDs
- âœ“ Explicit error handling per tool
- âœ“ Escalation criteria clearly defined

## Formatting best practices

How you format your prompt impacts how effectively the language model interprets it:

- **Use markdown headings:** Structure sections with `#` for main sections, `##` for subsections
- **Prefer bulleted lists:** Break down instructions into digestible bullet points
- **Use whitespace:** Separate sections and instruction groups with blank lines
- **Keep headings in sentence case:** `# Goal` not `# GOAL`
- **Be consistent:** Use the same formatting pattern throughout the prompt

## Frequently asked questions

<AccordionGroup>
  <Accordion title="How do I maintain consistency across multiple agents?">
    Create shared prompt templates for common sections like character normalization, error handling,
    and guardrails. Store these in a central repository and reference them across specialist agents.
    Use the orchestrator pattern to ensure consistent routing logic and handoff procedures.
  </Accordion>

  <Accordion title="What's the minimum viable prompt for production?">
    At minimum, include: (1) Personality/role definition, (2) Primary goal, (3) Core guardrails, and
    (4) Tool descriptions if tools are used. Even simple agents benefit from explicit section
    structure and error handling instructions.
  </Accordion>

  <Accordion title="How do I handle tool deprecation without breaking agents?">
    When deprecating a tool, add a new tool first, then update the prompt to prefer the new tool while
    keeping the old one as a fallback. Monitor usage, then remove the old tool once usage drops to
    zero. Always include error handling so agents can recover if a deprecated tool is called.
  </Accordion>

  <Accordion title="Should I use different prompts for different LLMs?">
    Generally, prompts structured with the principles in this guide work across models. However,
    model-specific tuning can improve performanceâ€”particularly for tool-calling format and reasoning
    steps. Test your prompt with multiple models and adjust if needed.
  </Accordion>

  <Accordion title="How long should my system prompt be?">
    No universal limit exists, but prompts over 2000 tokens increase latency and cost. Focus on
    conciseness: every line should serve a clear purpose. If your prompt exceeds 2000 tokens, consider
    splitting into multiple specialized agents or extracting reference material into a knowledge base.
  </Accordion>

  <Accordion title="How do I balance consistency with adaptability?">
    Define core personality traits, goals, and guardrails firmly while allowing flexibility in tone
    and verbosity based on user communication style. Use conditional instructions: "If the user is
    frustrated, acknowledge their concerns before proceeding."
  </Accordion>

  <Accordion title="Can I update prompts after deployment?">
    Yes. System prompts can be modified at any time to adjust behavior. This is particularly useful
    for addressing emerging issues or refining capabilities as you learn from user interactions.
    Always test changes in a staging environment before deploying to production.
  </Accordion>

  <Accordion title="How do I prevent agents from hallucinating when tools fail?">
    Include explicit error handling instructions for every tool. Emphasize "never guess or make up
    information" in the guardrails section. Repeat this instruction in tool-specific error handling
    sections. Test tool failure scenarios during development to ensure agents follow recovery
    instructions.
  </Accordion>
</AccordionGroup>

## Prompting guide checklist

Use this checklist to verify your agent prompts follow the best practices outlined in this guide. Review each section to ensure your implementation is production-ready.

### Fundamental prompt structure

<AccordionGroup>
  <Accordion title="✓ Structure and organization">
    - [ ] Prompt is organized into clear sections with markdown headings (`# Personality`, `# Goal`, `# Guardrails`, etc.)
    - [ ] Sections are separated with whitespace and line breaks
    - [ ] Each section has a focused, single purpose
    - [ ] Instructions are written in sentence case, not all caps
    - [ ] Related instructions are grouped together logically
  </Accordion>

  <Accordion title="✓ Conciseness and clarity">
    - [ ] Every instruction is as concise as possible (no filler words)
    - [ ] Each line contains one clear action or rule
    - [ ] Instructions use direct, action-based language
    - [ ] Technical jargon is avoided unless necessary
    - [ ] Tone guidance appears once, not repeated throughout
  </Accordion>

  <Accordion title="✓ Critical instructions">
    - [ ] Most important 1-2 rules include "This step is important" emphasis
    - [ ] Critical verification steps are repeated in relevant sections
    - [ ] Security-critical rules are highlighted in `# Guardrails`
    - [ ] Workflow dependencies are clearly marked (e.g., "Always do X before Y")
  </Accordion>

  <Accordion title="✓ Character normalization">
    - [ ] Spoken format is defined for emails, phone numbers, and codes
    - [ ] Written format is defined for tool/API usage
    - [ ] Conversion rules are explicit (e.g., "at" → "@", "dot" → ".")
    - [ ] Examples show both formats for common data types
    - [ ] Tool sections reference normalization rules where applicable
  </Accordion>

  <Accordion title="✓ Examples and demonstrations">
    - [ ] Complex workflows include concrete examples
    - [ ] Character normalization includes before/after examples
    - [ ] Tool usage shows realistic input/output scenarios
    - [ ] Edge cases are illustrated with sample interactions
  </Accordion>

  <Accordion title="✓ Guardrails section">
    - [ ] All non-negotiable rules are in a dedicated `# Guardrails` section
    - [ ] Rules use "Never" or "Always" language for clarity
    - [ ] Escalation criteria are clearly defined
    - [ ] Privacy and security rules are prominently listed
    - [ ] Handling of sensitive data is explicitly addressed
  </Accordion>
</AccordionGroup>

### Tool configuration

<AccordionGroup>
  <Accordion title="✓ Tool descriptions">
    - [ ] Each tool has a clear, action-oriented description
    - [ ] All parameters include detailed descriptions
    - [ ] Required vs. optional parameters are clearly marked
    - [ ] Expected formats are specified (e.g., "written format: user@company.com")
    - [ ] Return values and response structures are documented
  </Accordion>

  <Accordion title="✓ Tool usage instructions">
    - [ ] "When to use" criteria are explicitly defined for each tool
    - [ ] "How to use" includes step-by-step instructions
    - [ ] Prerequisites are listed (e.g., "After identity verification")
    - [ ] Multi-step tool workflows are numbered
    - [ ] Tool sequencing is clear (e.g., "Always call A before calling B")
  </Accordion>

  <Accordion title="✓ Character normalization for tools">
    - [ ] Tools requiring structured data reference normalization rules
    - [ ] Examples show spoken → written conversion before tool calls
    - [ ] Format conversion steps are numbered in tool usage
    - [ ] Edge cases (e.g., special characters) are addressed
  </Accordion>

  <Accordion title="✓ Error handling">
    - [ ] Each tool has explicit error handling instructions
    - [ ] Recovery steps are defined for common errors
    - [ ] Escalation criteria are clear (e.g., "After 2 failed attempts")
    - [ ] "Never guess or make up information" is emphasized
    - [ ] Alternative actions are provided when tools fail
  </Accordion>
</AccordionGroup>

### Architecture and design

<AccordionGroup>
  <Accordion title="✓ Agent specialization">
    - [ ] Agent has a narrow, clearly defined scope
    - [ ] Responsibilities are focused on a specific domain
    - [ ] Out-of-scope requests have clear handling instructions
    - [ ] Success criteria are measurable and specific
  </Accordion>

  <Accordion title="✓ Multi-agent workflows (if applicable)">
    - [ ] Orchestrator routing logic is clearly defined
    - [ ] Handoff criteria between specialists are explicit
    - [ ] Context passed during handoffs is specified
    - [ ] Human escalation conditions are documented
    - [ ] Specialist agents reference orchestrator handoff rules
  </Accordion>

  <Accordion title="✓ Model selection">
    - [ ] Model is appropriate for task complexity and latency requirements
    - [ ] Prompt has been tested with chosen model
    - [ ] Tool-calling reliability has been validated
    - [ ] Alternative models have been benchmarked if needed
  </Accordion>
</AccordionGroup>

### Production readiness

<AccordionGroup>
  <Accordion title="✓ Error handling and resilience">
    - [ ] Global error handling instructions are present
    - [ ] Network failures have defined responses
    - [ ] Missing data scenarios are addressed
    - [ ] Timeout handling is explicit
    - [ ] Permission errors include escalation paths
  </Accordion>

  <Accordion title="✓ Evaluation and testing">
    - [ ] Success metrics are configured (task completion rate, escalation rate)
    - [ ] Test cases cover common user intents
    - [ ] Edge cases and error scenarios are tested
    - [ ] Regression test suite exists for prompt changes
    - [ ] Conversation transcripts are reviewed for failure patterns
  </Accordion>

  <Accordion title="✓ Data collection and monitoring">
    - [ ] Data collection is configured to capture conversation insights
    - [ ] Key interaction patterns are tracked
    - [ ] Common user requests are identified
    - [ ] Failure patterns are monitored
    - [ ] Metrics are reviewed regularly for improvement opportunities
  </Accordion>

  <Accordion title="✓ Compliance and security">
    - [ ] PII handling is explicitly addressed
    - [ ] Data retention policies are documented
    - [ ] Identity verification steps are enforced
    - [ ] Sensitive operations require appropriate authorization
    - [ ] Privacy requirements are met per applicable regulations
  </Accordion>
</AccordionGroup>

## Next steps

This guide establishes the foundation for reliable agent behavior through prompt engineering, tool configuration, and architectural patterns. To build production-grade systems, continue with:

- **[Workflows](/docs/agents-platform/customization/agent-workflows):** Design multi-agent orchestration and specialist handoffs
- **[Success Evaluation](/docs/agents-platform/customization/agent-analysis/success-evaluation):** Configure metrics and evaluation criteria
- **[Data Collection](/docs/agents-platform/customization/agent-analysis/data-collection):** Capture structured insights from conversations
- **[Testing](/docs/agents-platform/customization/agent-testing):** Implement regression testing and simulation
- **[Security & Privacy](/docs/agents-platform/customization/privacy):** Ensure compliance and data protection
- **[Our Docs Agent](/docs/agents-platform/guides/elevenlabs-docs-agent):** See a complete case study of these principles in action

For enterprise deployment support, [contact our team](https://elevenlabs.io/contact-sales).
