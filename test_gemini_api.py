"""Test script to verify Gemini API with updated model names."""
import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

async def test_gemini_api():
    """Test Google Gemini API with LangChain-compatible models."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Updated model list per LangChain docs
    models_to_test = [
        "gemini-2.5-flash",      # Per LangChain docs
        "gemini-1.5-flash",      # Fallback
        "gemini-2.5-pro",        # Pro version
    ]
    
    for model_name in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing model: {model_name}")
        print(f"{'='*60}")
        
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.7,
                timeout=30,
                max_retries=2
            )
            
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Say 'Hello, API test successful!' in under 10 words.")
            ]
            
            print(f"Sending request...")
            
            response = await asyncio.wait_for(
                llm.ainvoke(messages),
                timeout=35.0
            )
            
            print(f"✅ SUCCESS!")
            print(f"Response: {response.content}")
            return  # Exit on first success
            
        except asyncio.TimeoutError:
            print(f"❌ TIMEOUT after 35 seconds")
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"❌ ERROR: {error_type}")
            print(f"Message: {error_msg}")
    
    print("\n❌ ALL MODELS FAILED - Check API key permissions")

if __name__ == "__main__":
    print("Testing Gemini API with LangChain-compatible models...\n")
    asyncio.run(test_gemini_api())
