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
            base_path = self.PROMPTS_DIR / "base_system_promptV2.txt"
            self._template_cache[cache_key] = self._load_template_file(base_path)
        return self._template_cache[cache_key]
    
    def get_speaker_format(self, is_multi_speaker: bool = True) -> str:
        """Load the appropriate speaker format prompt.
        
        Args:
            is_multi_speaker: If True, load multi-speaker (Doctor-Patient) format.
                              If False, load single-speaker (Solo Doctor) format.
        
        Returns:
            Speaker format prompt content.
        """
        cache_key = "__speaker_multi__" if is_multi_speaker else "__speaker_single__"
        if cache_key not in self._template_cache:
            filename = "speaker_format_multi.txt" if is_multi_speaker else "speaker_format_single.txt"
            format_path = self.PROMPTS_DIR / filename
            self._template_cache[cache_key] = self._load_template_file(format_path)
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
    
    # Duration to word count mapping (based on ~150 words per minute speaking rate)
    DURATION_WORD_ESTIMATES = {
        3: (400, 500),
        5: (650, 850),
        10: (1300, 1700),
        15: (2000, 2500),
    }
    
    async def build_prompt(
        self,
        template_ids: List[str],
        quick_instructions: Optional[str] = None,
        system_prompt_override: Optional[str] = None,
        preferred_languages: Optional[List[str]] = None,
        speaker1_languages: Optional[List[str]] = None,
        speaker2_languages: Optional[List[str]] = None,
        target_duration_minutes: Optional[int] = None,
        is_multi_speaker: bool = True,
    ) -> str:
        """Build final prompt by combining templates.
        
        Args:
            template_ids: List of template IDs in desired order.
            quick_instructions: Optional additional instructions to append.
            system_prompt_override: Optional custom base system prompt.
            preferred_languages: Optional list of preferred output language codes.
            speaker1_languages: Languages for Speaker 1 (Doctor/Educator role).
            speaker2_languages: Languages for Speaker 2 (Patient/Learner role).
            target_duration_minutes: Target speech duration in minutes (3, 5, 10, or 15).
            is_multi_speaker: Whether to use multi-speaker (Doctor-Patient) or single-speaker format.
            
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
        
        # 2. Speaker format (multi-speaker or single-speaker)
        try:
            speaker_format = self.get_speaker_format(is_multi_speaker)
            sections.append("\n---\n")
            sections.append(speaker_format)
        except FileNotFoundError:
            logger.warning(f"Speaker format file not found for is_multi_speaker={is_multi_speaker}")
        
        
        # 2. Script length requirement (if duration specified)
        if target_duration_minutes and target_duration_minutes in self.DURATION_WORD_ESTIMATES:
            min_words, max_words = self.DURATION_WORD_ESTIMATES[target_duration_minutes]
            sections.append(f"""

## Script Length Requirement

Generate a script approximately **{target_duration_minutes} minutes long** when spoken aloud.
Target word count: **{min_words:,}–{max_words:,} words**.

Ensure the content is comprehensive enough to fill the target duration while remaining engaging and well-paced.
""")
        
        # 3. Multi-speaker dialogue format (if both speaker languages specified)
        if speaker1_languages and speaker2_languages:
            speaker1_langs = [lang_map.get(code, code) for code in speaker1_languages]
            speaker2_langs = [lang_map.get(code, code) for code in speaker2_languages]
            
            # Check if either speaker uses multiple languages (sentence-by-sentence multilingual)
            speaker1_multilingual = len(speaker1_languages) > 1
            speaker2_multilingual = len(speaker2_languages) > 1
            
            # Build per-speaker language instructions
            if speaker1_multilingual:
                speaker1_instruction = f"Speaks in {', '.join(speaker1_langs)} using **sentence-by-sentence multilingual format** (each sentence in first language, then same sentence in second language)"
            else:
                speaker1_instruction = f"Speaks ONLY in {speaker1_langs[0]}"
            
            if speaker2_multilingual:
                speaker2_instruction = f"Speaks in {', '.join(speaker2_langs)} using **sentence-by-sentence multilingual format** (each sentence in first language, then same sentence in second language)"
            else:
                speaker2_instruction = f"Speaks ONLY in {speaker2_langs[0]}"
            
            # Language-specific example phrases for dynamic example generation
            lang_examples = {
                "English": {"greeting": "Good morning.", "intro": "I'm here to explain your procedure.", "prep": "First, let me walk you through the preparation.", "thanks": "Thank you, Doctor.", "question": "What should I expect?"},
                "繁體中文 (Traditional Chinese)": {"greeting": "早安。", "intro": "我會解釋您的手術流程。", "prep": "首先，讓我說明準備步驟。", "thanks": "謝謝醫生。", "question": "我應該期待什麼？"},
                "簡體中文 (Simplified Chinese)": {"greeting": "早上好。", "intro": "我会解释您的手术流程。", "prep": "首先，让我说明准备步骤。", "thanks": "谢谢医生。", "question": "我应该期待什么？"},
                "日本語 (Japanese)": {"greeting": "おはようございます。", "intro": "手術について説明します。", "prep": "まず、準備の手順を説明しましょう。", "thanks": "ありがとうございます。", "question": "何を期待すればいいですか？"},
                "한국어 (Korean)": {"greeting": "안녕하세요.", "intro": "수술에 대해 설명드리겠습니다.", "prep": "먼저 준비 과정을 설명하겠습니다.", "thanks": "감사합니다.", "question": "무엇을 기대해야 하나요?"},
                "Español (Spanish)": {"greeting": "Buenos días.", "intro": "Voy a explicar su procedimiento.", "prep": "Primero, permítame explicar la preparación.", "thanks": "Gracias, Doctor.", "question": "¿Qué debo esperar?"},
                "Français (French)": {"greeting": "Bonjour.", "intro": "Je vais vous expliquer la procédure.", "prep": "D'abord, laissez-moi vous expliquer la préparation.", "thanks": "Merci, Docteur.", "question": "À quoi dois-je m'attendre?"},
                "Deutsch (German)": {"greeting": "Guten Morgen.", "intro": "Ich erkläre Ihnen den Eingriff.", "prep": "Zuerst erkläre ich die Vorbereitung.", "thanks": "Danke, Herr Doktor.", "question": "Was soll ich erwarten?"},
            }
            
            def get_phrase(lang, key, fallback_key):
                """Get phrase for language, with fallback to placeholder."""
                if lang in lang_examples:
                    return lang_examples[lang].get(key, f"[{lang} {fallback_key}]")
                return f"[{lang} {fallback_key}]"
            
            # Build example based on speaker configurations
            if speaker1_multilingual and speaker2_multilingual:
                # Both multilingual - use first two langs of each speaker
                s1_l1, s1_l2 = speaker1_langs[0], speaker1_langs[1] if len(speaker1_langs) > 1 else speaker1_langs[0]
                s2_l1, s2_l2 = speaker2_langs[0], speaker2_langs[1] if len(speaker2_langs) > 1 else speaker2_langs[0]
                example_text = f"""
### Example Format (Both speakers multilingual):
```
Speaker 1: [reassuring] {get_phrase(s1_l1, "greeting", "greeting")} {get_phrase(s1_l2, "greeting", "greeting")} {get_phrase(s1_l1, "intro", "intro")} {get_phrase(s1_l2, "intro", "intro")}

Speaker 2: [curious] {get_phrase(s2_l1, "thanks", "thanks")} {get_phrase(s2_l2, "thanks", "thanks")} {get_phrase(s2_l1, "question", "question")} {get_phrase(s2_l2, "question", "question")}

Speaker 1: [professional] {get_phrase(s1_l1, "prep", "prep")} {get_phrase(s1_l2, "prep", "prep")}
```
"""
            elif speaker1_multilingual:
                # Speaker 1 multilingual, Speaker 2 single language
                s1_l1, s1_l2 = speaker1_langs[0], speaker1_langs[1] if len(speaker1_langs) > 1 else speaker1_langs[0]
                s2_l1 = speaker2_langs[0]
                example_text = f"""
### Example Format (Speaker 1 multilingual, Speaker 2 single language):
```
Speaker 1: [reassuring] {get_phrase(s1_l1, "greeting", "greeting")} {get_phrase(s1_l2, "greeting", "greeting")} {get_phrase(s1_l1, "intro", "intro")} {get_phrase(s1_l2, "intro", "intro")}

Speaker 2: [curious] {get_phrase(s2_l1, "thanks", "thanks")} {get_phrase(s2_l1, "question", "question")}

Speaker 1: [professional] {get_phrase(s1_l1, "prep", "prep")} {get_phrase(s1_l2, "prep", "prep")}
```
"""
            elif speaker2_multilingual:
                # Speaker 1 single language, Speaker 2 multilingual
                s1_l1 = speaker1_langs[0]
                s2_l1, s2_l2 = speaker2_langs[0], speaker2_langs[1] if len(speaker2_langs) > 1 else speaker2_langs[0]
                example_text = f"""
### Example Format (Speaker 1 single language, Speaker 2 multilingual):
```
Speaker 1: [reassuring] {get_phrase(s1_l1, "greeting", "greeting")} {get_phrase(s1_l1, "intro", "intro")}

Speaker 2: [curious] {get_phrase(s2_l1, "thanks", "thanks")} {get_phrase(s2_l2, "thanks", "thanks")} {get_phrase(s2_l1, "question", "question")} {get_phrase(s2_l2, "question", "question")}

Speaker 1: [professional] {get_phrase(s1_l1, "prep", "prep")}
```
"""
            else:
                # Both speakers single language
                s1_l1 = speaker1_langs[0]
                s2_l1 = speaker2_langs[0]
                example_text = f"""
### Example Format:
```
Speaker 1: [reassuring] {get_phrase(s1_l1, "greeting", "greeting")} {get_phrase(s1_l1, "intro", "intro")}

Speaker 2: [curious] {get_phrase(s2_l1, "thanks", "thanks")} {get_phrase(s2_l1, "question", "question")}

Speaker 1: [professional] {get_phrase(s1_l1, "prep", "prep")}
```
"""
            
            multi_speaker_instruction = f"""

## Multi-Speaker Dialogue Format

Generate the script as a dialogue between two speakers using ElevenLabs V3 format:

- **Speaker 1** (Doctor/Educator/Guider): {speaker1_instruction}
- **Speaker 2** (Patient/Learner): {speaker2_instruction}

**CRITICAL**: Each speaker must ONLY use their assigned language(s). Do NOT add any other languages (especially English if not selected for that speaker).

### Format Rules:
1. Each speaker's line MUST start with `Speaker 1:` or `Speaker 2:` prefix
2. Use audio tags like `[cheerful]`, `[curious]`, `[reassuring]` for emotion
3. If a speaker has multiple languages, write each complete sentence in their FIRST language, then IMMEDIATELY follow with the SAME sentence in their SECOND language
4. Alternate between speakers naturally for conversational flow
5. Speaker 1 leads the conversation with educational content
6. Speaker 2 asks questions and responds to learn
7. Do NOT include any language not explicitly assigned to that speaker
{example_text}"""
            sections.append(multi_speaker_instruction)
        
        # 4. Single/multi-language instruction (if preferred_languages specified, but not multi-speaker)
        elif preferred_languages:
            # Filter valid languages
            langs = [lang_map[code] for code in preferred_languages if code in lang_map]
            
            if len(langs) == 1:
                # Single language specific instructions
                code = preferred_languages[0]
                lang_name = langs[0]
                if code == "zh-TW":
                    sections.append("\n\n## Language Requirement\nGenerate the script in Traditional Chinese (繁體中文). Use culturally appropriate expressions for Taiwan.")
                elif code == "en":
                    sections.append("\n\n## Language Requirement\nGenerate the script in English. Use clear, accessible language suitable for patients.")
                elif code == "zh-CN":
                    sections.append("\n\n## Language Requirement\nGenerate the script in Simplified Chinese (简体中文).")
                else:
                    # Generic handler for all other languages (Japanese, Korean, French, etc.)
                    sections.append(f"\n\n## Language Requirement\nGenerate the script entirely in {lang_name}. Do NOT use English unless quoting technical medical terms that have no direct translation.")
            elif len(langs) > 1:
                # Multi-language sentence-by-sentence format
                lang_str = ", ".join(langs)
                first_lang = langs[0]
                second_lang = langs[1] if len(langs) > 1 else langs[0]
                
                # Build dynamic example based on selected languages
                # Use language-specific greeting examples where available
                lang_examples = {
                    "English": ("Good morning, I'm Dr. Smith.", "Today we'll discuss your procedure.", "First, let me explain what will happen."),
                    "繁體中文 (Traditional Chinese)": ("早安，我是史密斯醫生。", "今天我們來討論您的手術流程。", "首先，讓我解釋會發生什麼事。"),
                    "簡體中文 (Simplified Chinese)": ("早上好，我是史密斯医生。", "今天我们来讨论您的手术流程。", "首先，让我解释会发生什么事。"),
                    "日本語 (Japanese)": ("おはようございます、スミス医師です。", "今日は手術についてお話しします。", "まず、何が起こるか説明しましょう。"),
                    "한국어 (Korean)": ("안녕하세요, 스미스 의사입니다.", "오늘 수술에 대해 이야기하겠습니다.", "먼저 무슨 일이 일어날지 설명드리겠습니다."),
                    "Español (Spanish)": ("Buenos días, soy el Dr. Smith.", "Hoy hablaremos sobre su procedimiento.", "Primero, déjame explicar lo que sucederá."),
                    "Français (French)": ("Bonjour, je suis le Dr Smith.", "Aujourd'hui, nous allons discuter de votre procédure.", "D'abord, laissez-moi vous expliquer ce qui va se passer."),
                    "Deutsch (German)": ("Guten Morgen, ich bin Dr. Smith.", "Heute werden wir über Ihren Eingriff sprechen.", "Zuerst möchte ich erklären, was passieren wird."),
                }
                
                # Get examples for selected languages, fallback to placeholder
                first_examples = lang_examples.get(first_lang, (f"[{first_lang} greeting]", f"[{first_lang} introduction]", f"[{first_lang} explanation]"))
                second_examples = lang_examples.get(second_lang, (f"[{second_lang} greeting]", f"[{second_lang} introduction]", f"[{second_lang} explanation]"))
                
                # Build example with [pause] between language transitions
                example_lines = [
                    f"{first_examples[0]}",
                    f"{second_examples[0]}",
                    "",
                    "[pause]",
                    "",
                    f"{first_examples[1]}",
                    f"{second_examples[1]}",
                    "",
                    "[pause]",
                    "",
                    f"{first_examples[2]}",
                    f"{second_examples[2]}",
                ]
                example_output = "\n".join(example_lines)
                
                sections.append(f"""

## Language Requirement (Multilingual)

Generate the script using **sentence-by-sentence multilingual format** in ONLY these languages: {lang_str}.

**CRITICAL**: Use ONLY the specified languages. Do NOT add any other languages (especially English if not selected).

### Format Rules:
1. Write each complete thought/sentence FIRST in {first_lang}
2. IMMEDIATELY follow with the SAME sentence in {second_lang}
3. Add `[pause]` between major topic transitions for natural pacing
4. If more than two languages are selected, continue the pattern for each additional language
5. Keep all translations of the same sentence together on adjacent lines
6. Do NOT separate languages into different sections or paragraphs
7. Do NOT include any language that was not explicitly selected
8. Do NOT use speaker labels like "Doctor:" - just write the content directly

### Example Output (using {first_lang} + {second_lang}):
```
{example_output}
```

This sentence-by-sentence format with pauses helps listeners learn vocabulary in context while understanding the full educational content.
""")
        
        # 5. Content type templates (in order)
        if template_ids:
            sections.append("\n---\n\n# Content Structure\n")
            for template_id in template_ids:
                try:
                    template_content = await self.get_template(template_id)
                    sections.append(template_content)
                    sections.append("\n---\n")
                except (ValueError, FileNotFoundError) as e:
                    logger.warning(f"Skipping template {template_id}: {e}")
        
        # 6. Quick instructions
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
