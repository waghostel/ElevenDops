"""Test script to verify Gemini credentials and model access."""
import asyncio
import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_credentials():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("❌ GOOGLE_API_KEY not found in environment")
        return

    logger.info(f"✅ Found API Key: {api_key[:10]}...{api_key[-4:]}")
    
    models_to_test = ["gemini-1.5-flash", "gemini-2.5-flash"]
    
    for model_name in models_to_test:
        logger.info(f"\nTesting model: {model_name}")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.7,
                timeout=30,
                max_retries=1
            )
            
            message = HumanMessage(content="Hello, are you working?")
            logger.info("Sending request...")
            
            response = await llm.ainvoke([message])
            logger.info(f"✅ Success with {model_name}: {response.content}")
            
        except Exception as e:
            logger.error(f"❌ Failed with {model_name}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_credentials())
