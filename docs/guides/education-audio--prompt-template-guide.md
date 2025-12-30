# Education Audio - Prompt Template System Guide

This document describes how the prompt template system works in the Education Audio page for generating patient education scripts.

---

## Overview

The Script Editor uses a layered prompt architecture to generate high-quality patient education audio scripts. Instead of writing prompts from scratch, doctors can:

- **Select** pre-built content templates
- **Combine** multiple templates in any order
- **Customize** with quick instructions
- **Create** their own reusable templates

---

## How It Works

### Prompt Structure

When you generate a script, the system builds a prompt in this order:

```
┌─────────────────────────────────────┐
│  1. Base System Prompt              │  ← Always included (voice optimization rules)
├─────────────────────────────────────┤
│  2. Selected Content Templates      │  ← Your chosen modules (in order)
├─────────────────────────────────────┤
│  3. Quick Instructions (Optional)   │  ← Your additional guidance
├─────────────────────────────────────┤
│  4. Knowledge Document              │  ← The source medical content
└─────────────────────────────────────┘
```

### Using Templates

1. **Select a Knowledge Document** - Choose the source material for your script.

2. **Choose Content Modules** - Use the multi-select to pick templates:

   - Pre-Surgery Education
   - Post-Surgery Education
   - Complete Surgical Education
   - Disease FAQ
   - Medication Instructions
   - Lifestyle Guidance

3. **Reorder (Optional)** - Drag and drop to change the order of selected templates.

4. **Add Quick Instructions (Optional)** - Type any additional guidance without modifying templates:

   > "Focus on elderly patients" or "Use simple language for pediatric content"

5. **Preview Prompt** - Click "👁️ Preview Combined Prompt" to see the exact text before generation.

6. **Generate** - Click "✨ Generate Script" to create your audio script.

---

## Custom Templates

### Creating a Custom Template

1. Click **🛠️ Manage Templates** in the Script Editor sidebar.
2. Expand **➕ Create New Template**.
3. Fill in:
   - **Template Name**: A descriptive title (e.g., "Pediatric Intro")
   - **Description**: Brief explanation of when to use it
   - **Content**: The actual prompt instructions
4. Click **Create Template**.

Your custom template will appear in the Content Modules selector alongside built-in templates.

### Deleting a Custom Template

1. Open **🛠️ Manage Templates**.
2. Find your template under "Your Custom Templates".
3. Click **Delete**.

---

## Template Mode vs Custom Prompt Mode

| Feature                | Template Mode (Default) | Custom Prompt Mode |
| ---------------------- | ----------------------- | ------------------ |
| Multi-select templates | ✅                      | ❌                 |
| Quick instructions     | ✅                      | ❌                 |
| Drag-and-drop reorder  | ✅                      | ❌                 |
| Full prompt control    | ❌                      | ✅                 |

Toggle between modes using the **Use Template Mode** switch.

---

## Technical Details

- **Backend Service**: `PromptTemplateService` handles template loading and combination.
- **Storage**: Built-in templates are stored as `.txt` files; custom templates are stored in Firestore.
- **API Endpoints**:
  - `GET /api/templates` - List all templates
  - `POST /api/templates/preview` - Preview combined prompt
  - `POST /api/templates/` - Create custom template
  - `DELETE /api/templates/{id}` - Delete custom template

---

## Best Practices

1. **Start with built-in templates** before creating custom ones.
2. **Use quick instructions** for one-off modifications instead of creating new templates.
3. **Preview before generating** to ensure the prompt looks correct.
4. **Order matters** - templates are combined in the order you arrange them.
