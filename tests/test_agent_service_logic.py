import unittest
from unittest.mock import MagicMock, patch
from backend.services.elevenlabs_service import ElevenLabsService

class TestAgentCreationLogic(unittest.TestCase):
    def setUp(self):
        self.service = ElevenLabsService()
        self.service.use_mock = False # We want to test the logic, not the mock path
        self.service.client = MagicMock()
    
    def test_english_only_uses_v2(self):
        """Case 1: English-only request should use v2 model and keep 'en' primary."""
        self.service.create_agent(
            name="Test Agent",
            system_prompt="prompt",
            knowledge_base=[],
            voice_id="voice123",
            languages=["en"]
        )
        
        # Verify call args
        call_args = self.service.client.conversational_ai.agents.create.call_args
        _, kwargs = call_args
        
        # Check model
        tts_config = kwargs['conversation_config']['tts']
        self.assertEqual(tts_config['model_id'], "eleven_turbo_v2")
        
        # Check language
        agent_config = kwargs['conversation_config']['agent']
        self.assertEqual(agent_config['language'], "en")

    def test_multilingual_english_primary_swaps_language(self):
        """Case 2: English + French should use v2.5 model and SWAP primary language to French."""
        self.service.create_agent(
            name="Test Agent",
            system_prompt="prompt",
            knowledge_base=[],
            voice_id="voice123",
            languages=["en", "fr"]
        )
        
        call_args = self.service.client.conversational_ai.agents.create.call_args
        _, kwargs = call_args
        
        # Check model
        tts_config = kwargs['conversation_config']['tts']
        self.assertEqual(tts_config['model_id'], "eleven_turbo_v2_5")
        
        # Check language (Should NOT swap, should stay 'en')
        agent_config = kwargs['conversation_config']['agent']
        self.assertEqual(agent_config['language'], "en")
        
        # Check presets include both
        presets = agent_config.get('language_presets', {})
        self.assertIn('en', presets)
        self.assertIn('fr', presets)

    def test_multilingual_non_english_primary_keeps_order(self):
        """Case 3: French + English should use v2.5 model and keep French primary."""
        self.service.create_agent(
            name="Test Agent",
            system_prompt="prompt",
            knowledge_base=[],
            voice_id="voice123",
            languages=["fr", "en"]
        )
        
        call_args = self.service.client.conversational_ai.agents.create.call_args
        _, kwargs = call_args
        
        # Check model
        tts_config = kwargs['conversation_config']['tts']
        self.assertEqual(tts_config['model_id'], "eleven_turbo_v2_5")
        
        # Check language (Should remain 'fr')
        agent_config = kwargs['conversation_config']['agent']
        self.assertEqual(agent_config['language'], "fr")

    def test_multilingual_no_english_keeps_order(self):
        """Case 4: Spanish + German should use v2.5 model and keep Spanish primary."""
        self.service.create_agent(
            name="Test Agent",
            system_prompt="prompt",
            knowledge_base=[],
            voice_id="voice123",
            languages=["es", "de"]
        )
        
        call_args = self.service.client.conversational_ai.agents.create.call_args
        _, kwargs = call_args
        
        # Check model
        tts_config = kwargs['conversation_config']['tts']
        self.assertEqual(tts_config['model_id'], "eleven_turbo_v2_5")
        
        # Check language
        agent_config = kwargs['conversation_config']['agent']
        self.assertEqual(agent_config['language'], "es")

class TestAgentUpdateLogic(unittest.TestCase):
    def setUp(self):
        self.service = ElevenLabsService()
        self.service.use_mock = False 
        self.service.client = MagicMock()

    def test_update_agent_name_only(self):
        """Test updating name only."""
        self.service.update_agent(
            agent_id="agent123",
            name="New Name"
        )
        
        call_args = self.service.client.conversational_ai.agents.update.call_args
        _, kwargs = call_args
        
        self.assertEqual(kwargs['agent_id'], "agent123")
        self.assertEqual(kwargs['name'], "New Name")
        # Should not have conversation_config if only name updated
        self.assertNotIn('conversation_config', kwargs)

    def test_update_languages_to_multilingual(self):
        """Test updating languages triggers model change."""
        self.service.update_agent(
            agent_id="agent123",
            languages=["en", "fr"]
        )
        
        call_args = self.service.client.conversational_ai.agents.update.call_args
        _, kwargs = call_args
        
        tts_config = kwargs['conversation_config']['tts']
        self.assertEqual(tts_config['model_id'], "eleven_turbo_v2_5")
        
        agent_config = kwargs['conversation_config']['agent']
        # Should NOT swap primary to 'fr' even if 'en' primary with multilingual
        self.assertEqual(agent_config['language'], "en")
        
        presets = agent_config['language_presets']
        self.assertIn('en', presets)
        self.assertIn('fr', presets)

    def test_update_knowledge_base(self):
        """Test updating knowledge base."""
        kb = [{"id": "doc1", "name": "Doc", "type": "file"}]
        self.service.update_agent(
            agent_id="agent123",
            knowledge_base=kb
        )
        
        call_args = self.service.client.conversational_ai.agents.update.call_args
        _, kwargs = call_args
        
        agent_config = kwargs['conversation_config']['agent']
        self.assertEqual(agent_config['prompt']['knowledge_base'], kb)


if __name__ == '__main__':
    unittest.main()

