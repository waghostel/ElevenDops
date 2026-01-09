"""Quick script to list ElevenLabs knowledge documents."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
docs = client.conversational_ai.knowledge_base.list()
doc_list = list(docs.documents) if hasattr(docs, 'documents') else list(docs)

print('ElevenLabs Knowledge Base Documents:')
if not doc_list:
    print('  (No documents)')
else:
    for doc in doc_list:
        doc_id = getattr(doc, 'id', None) or getattr(doc, 'document_id', 'unknown')
        doc_name = getattr(doc, 'name', 'Unnamed')
        print(f'  - ID: {doc_id}, Name: {doc_name[:50] if doc_name else "(no name)"}')
print(f'Total: {len(doc_list)} documents')
