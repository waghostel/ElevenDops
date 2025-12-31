"""Prompt Template Service for managing and combining prompt templates.

This service handles loading, listing, and combining prompt templates
for script generation in the Education Audio feature.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel

from backend.services.data_service import get_data_service

logger = logging.getLogger(__name__)


class TemplateInfo(BaseModel):
    """Template metadata for API responses."""
    template_id: str
    display_name: str
    description: str
    category: str  # 'base' | 'content_type' | 'custom'
    preview: str = ""  # First 200 chars of template content


class PromptTemplateService:
    """Service for loading and combining prompt templates.
    
    This service manages the prompt template system that allows users to:
    - Select multiple content type templates
    - Specify template ordering
    - Add quick instructions without modifying templates
    - Load custom user-defined templates from database
    """
    
    PROMPTS_DIR = Path(__file__).parent.parent / "config" / "prompts"
    CONTENT_TYPES_DIR = PROMPTS_DIR / "content_types"
    
    # Template metadata registry
    TEMPLATE_METADATA: Dict[str, Dict[str, str]] = {
        "pre_surgery": {
            "display_name": "Pre-Surgery Education",
            "description": "Helps patients prepare for their upcoming procedure",
        },
        "post_surgery": {
            "display_name": "Post-Surgery Education",
            "description": "Guides patients through their recovery process",
        },
        "pre_post_surgery": {
            "display_name": "Complete Surgical Education",
            "description": "Combined pre-operative and post-operative care guide",
        },
        "faq": {
            "display_name": "Disease FAQ",
            "description": "Q&A format answering common patient questions",
        },
        "medication": {
            "display_name": "Medication Instructions",
            "description": "How to properly take prescribed medications",
        },
        "lifestyle": {
            "display_name": "Lifestyle Guidance",
            "description": "Daily habits and self-care practices",
        },
    }
    
    def __init__(self):
        """Initialize the template service."""
        self._template_cache: Dict[str, str] = {}
        self._db_service = get_data_service()
    
    def _load_template_file(self, filepath: Path) -> str:
        """Load template content from file."""
        if not filepath.exists():
            raise FileNotFoundError(f"Template file not found: {filepath}")
        
        return filepath.read_text(encoding="utf-8")
    
    def get_base_prompt(self) -> str:
        """Load the base system prompt."""
        cache_key = "__base__"
        if cache_key not in self._template_cache:
            base_path = self.PROMPTS_DIR / "base_system_prompt.txt"
            self._template_cache[cache_key] = self._load_template_file(base_path)
        return self._template_cache[cache_key]
    
    async def get_template(self, template_id: str) -> str:
        """Load a single template by ID.
        
        Checks file-based templates first, then falls back to custom templates.
        
        Args:
            template_id: Template identifier.
            
        Returns:
            Template content as string.
            
        Raises:
            ValueError: If template_id is not found.
        """
        # 1. Check file-based cache and metadata
        if template_id in self.TEMPLATE_METADATA:
            if template_id not in self._template_cache:
                template_path = self.CONTENT_TYPES_DIR / f"{template_id}.txt"
                self._template_cache[template_id] = self._load_template_file(template_path)
            return self._template_cache[template_id]
        
        # 2. Check custom templates (no caching for now to keep it fresh)
        custom_template = await self._db_service.get_custom_template(template_id)
        if custom_template:
            return custom_template.content
            
        raise ValueError(f"Unknown template ID: {template_id}")
    
    async def list_templates(self) -> List[TemplateInfo]:
        """List all available templates (file-based + custom).
        
        Returns:
            List of TemplateInfo objects.
        """
        templates = []
        
        # 1. File-based templates
        for template_id, metadata in self.TEMPLATE_METADATA.items():
            try:
                # We can use sync get_template logic here partly or just read files
                # Reuse async get_template is fine, but it might be slower if we iterate?
                # Actually, for list, we just want preview.
                # Let's peek cache or load if needed, but keeping it async consistent
                content = await self.get_template(template_id)
                preview = content[:200] + "..." if len(content) > 200 else content
            except FileNotFoundError:
                logger.warning(f"Template file missing for: {template_id}")
                preview = "[Template file not found]"
            
            templates.append(TemplateInfo(
                template_id=template_id,
                display_name=metadata["display_name"],
                description=metadata["description"],
                category="content_type",
                preview=preview,
            ))
            
        # 2. Custom templates
        custom_templates = await self._db_service.get_custom_templates()
        for ct in custom_templates:
            templates.append(TemplateInfo(
                template_id=ct.template_id,
                display_name=ct.display_name,
                description=ct.description,
                category="custom",
                preview=ct.preview,
            ))
        
        return templates
    
    async def build_prompt(
        self,
        template_ids: List[str],
        quick_instructions: Optional[str] = None,
        system_prompt_override: Optional[str] = None,
        preferred_languages: Optional[List[str]] = None,
        speaker1_languages: Optional[List[str]] = None,
        speaker2_languages: Optional[List[str]] = None,
    ) -> str:
        """Build final prompt by combining templates.
        
        Args:
            template_ids: List of template IDs in desired order.
            quick_instructions: Optional additional instructions to append.
            system_prompt_override: Optional custom base system prompt.
            preferred_languages: Optional list of preferred output language codes.
            speaker1_languages: Languages for Speaker 1 (Doctor/Educator role).
            speaker2_languages: Languages for Speaker 2 (Patient/Learner role).
            
        Returns:
            Combined prompt string ready for LLM.
        """
        sections = []
        
        # Language code to display name mapping (native script + English)
        # Regional variants for Chinese and Portuguese included for correct LLM output
        lang_map = {
            "ar": "العربية (Arabic)",
            "bg": "Български (Bulgarian)",
            "cs": "Čeština (Czech)",
            "da": "Dansk (Danish)",
            "de": "Deutsch (German)",
            "el": "Ελληνικά (Greek)",
            "en": "English",
            "es": "Español (Spanish)",
            "fi": "Suomi (Finnish)",
            "fil": "Filipino",
            "fr": "Français (French)",
            "hi": "हिन्दी (Hindi)",
            "hr": "Hrvatski (Croatian)",
            "hu": "Magyar (Hungarian)",
            "id": "Bahasa Indonesia (Indonesian)",
            "it": "Italiano (Italian)",
            "ja": "日本語 (Japanese)",
            "ko": "한국어 (Korean)",
            "ms": "Bahasa Melayu (Malay)",
            "nl": "Nederlands (Dutch)",
            "no": "Norsk (Norwegian)",
            "pl": "Polski (Polish)",
            "pt": "Português (Portuguese)",
            "pt-BR": "Português Brasileiro (Brazilian Portuguese)",
            "pt-PT": "Português Europeu (European Portuguese)",
            "ro": "Română (Romanian)",
            "ru": "Русский (Russian)",
            "sk": "Slovenčina (Slovak)",
            "sv": "Svenska (Swedish)",
            "ta": "தமிழ் (Tamil)",
            "tr": "Türkçe (Turkish)",
            "uk": "Українська (Ukrainian)",
            "zh": "中文 (Chinese)",
            "zh-TW": "繁體中文 (Traditional Chinese)",
            "zh-CN": "簡體中文 (Simplified Chinese)"
        }
        
        # 1. Base system prompt (use override if provided)
        if system_prompt_override:
            sections.append(system_prompt_override)
        else:
            try:
                base_prompt = self.get_base_prompt()
                sections.append(base_prompt)
            except FileNotFoundError:
                logger.error("Base system prompt not found!")
                sections.append("You are a medical education script writer.")
        
        # 2. Multi-speaker dialogue format (if both speaker languages specified)
        if speaker1_languages and speaker2_languages:
            speaker1_langs = [lang_map.get(code, code) for code in speaker1_languages]
            speaker2_langs = [lang_map.get(code, code) for code in speaker2_languages]
            
            multi_speaker_instruction = f"""

## Multi-Speaker Dialogue Format

Generate the script as a dialogue between two speakers using ElevenLabs V3 format:

- **Speaker 1** (Doctor/Educator/Guider): Speaks in {', '.join(speaker1_langs)}
- **Speaker 2** (Patient/Learner): Speaks in {', '.join(speaker2_langs)}

### Format Rules:
1. Each speaker's line MUST start with `Speaker 1:` or `Speaker 2:` prefix
2. Use audio tags like `[cheerful]`, `[curious]`, `[reassuring]` for emotion
3. Alternate between speakers naturally for a conversational flow
4. Speaker 1 leads the conversation with educational content
5. Speaker 2 asks questions and responds to learn

### Example Format:
```
Speaker 1: [reassuring] Welcome! Today I'll explain the procedure you'll be having.

Speaker 2: [curious] Thank you, Doctor. What should I expect?

Speaker 1: [professional] First, let me walk you through the preparation steps...
```
"""
            sections.append(multi_speaker_instruction)
        
        # 3. Single/multi-language instruction (if preferred_languages specified, but not multi-speaker)
        elif preferred_languages:
            # Filter valid languages
            langs = [lang_map[code] for code in preferred_languages if code in lang_map]
            
            if len(langs) == 1:
                # Single language specific instructions
                code = preferred_languages[0]
                if code == "zh-TW":
                    sections.append("\n\n## Language Requirement\nGenerate the script in Traditional Chinese (繁體中文). Use culturally appropriate expressions for Taiwan.")
                elif code == "en":
                    sections.append("\n\n## Language Requirement\nGenerate the script in English. Use clear, accessible language suitable for patients.")
                elif code == "zh-CN":
                    sections.append("\n\n## Language Requirement\nGenerate the script in Simplified Chinese (简体中文).")
            elif len(langs) > 1:
                # Multi-language instructions
                lang_str = ", ".join(langs)
                sections.append(f"\n\n## Language Requirement\nGenerate the script in the following languages: {lang_str}. Provide the content in all requested languages, organizing it clearly (e.g., sequentially or side-by-side where appropriate).")
        
        # 4. Content type templates (in order)
        if template_ids:
            sections.append("\n---\n\n# Content Structure\n")
            for template_id in template_ids:
                try:
                    template_content = await self.get_template(template_id)
                    sections.append(template_content)
                    sections.append("\n---\n")
                except (ValueError, FileNotFoundError) as e:
                    logger.warning(f"Skipping template {template_id}: {e}")
        
        # 5. Quick instructions
        if quick_instructions and quick_instructions.strip():
            sections.append("\n# Additional Instructions\n")
            sections.append(quick_instructions.strip())
        
        return "\n".join(sections)
    
    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
        logger.info("Template cache cleared")


# Singleton instance for dependency injection
_service_instance: Optional[PromptTemplateService] = None


def get_prompt_template_service() -> PromptTemplateService:
    """Get or create the singleton PromptTemplateService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = PromptTemplateService()
    return _service_instance
