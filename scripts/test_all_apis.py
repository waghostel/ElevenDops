"""
ElevenDops API Test Script - Page-by-Page Testing
Tests all backend API endpoints used by each Streamlit page.
"""
import requests
import json
import time
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8000"
RESULTS = []

def log(msg: str, status: str = "INFO"):
    """Log a message and store result."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] [{status}] {msg}"
    print(line)
    RESULTS.append(line)

def test_endpoint(method: str, path: str, description: str, json_data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
    """Test a single endpoint and return result."""
    url = f"{BASE_URL}{path}"
    log(f"Testing: {method} {path} - {description}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return {"error": f"Unknown method: {method}"}
        
        result = {
            "endpoint": f"{method} {path}",
            "description": description,
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300 or response.status_code == 204,
            "response": None
        }
        
        try:
            result["response"] = response.json() if response.text else None
        except:
            result["response"] = response.text[:200] if response.text else None
            
        status = "✅ PASS" if result["success"] else f"❌ FAIL ({response.status_code})"
        log(f"  {status}", "PASS" if result["success"] else "FAIL")
        
        return result
        
    except requests.exceptions.ConnectionError:
        log(f"  ❌ CONNECTION ERROR - Server not reachable", "ERROR")
        return {"endpoint": f"{method} {path}", "description": description, "status_code": 0, "success": False, "error": "Connection refused"}
    except Exception as e:
        log(f"  ❌ ERROR: {str(e)}", "ERROR")
        return {"endpoint": f"{method} {path}", "description": description, "status_code": 0, "success": False, "error": str(e)}

def main():
    log("=" * 60)
    log("ElevenDops API Test Report")
    log(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Base URL: {BASE_URL}")
    log("=" * 60)
    
    all_results = []
    
    # ========================
    # Page 1: Doctor Dashboard
    # ========================
    log("\n" + "=" * 40)
    log("PAGE 1: Doctor Dashboard")
    log("=" * 40)
    
    all_results.append(test_endpoint("GET", "/api/health", "Health Check"))
    all_results.append(test_endpoint("GET", "/api/dashboard/stats", "Dashboard Statistics"))
    
    # ========================
    # Page 2: Upload Knowledge
    # ========================
    log("\n" + "=" * 40)
    log("PAGE 2: Upload Knowledge")
    log("=" * 40)
    
    # List existing documents
    list_result = test_endpoint("GET", "/api/knowledge", "List Knowledge Documents")
    all_results.append(list_result)
    
    # Create a test document
    create_payload = {
        "disease_name": "API Test Disease",
        "document_type": "faq",
        "raw_content": "# FAQ\n\nQ: What is this?\nA: A test document for API verification."
    }
    create_result = test_endpoint("POST", "/api/knowledge", "Create Knowledge Document", json_data=create_payload)
    all_results.append(create_result)
    
    # If creation succeeded, test get and delete
    created_id = None
    if create_result.get("success") and create_result.get("response"):
        created_id = create_result["response"].get("knowledge_id")
        
        if created_id:
            # Wait for sync
            log("  Waiting for sync (2 seconds)...")
            time.sleep(2)
            
            # Get single document
            all_results.append(test_endpoint("GET", f"/api/knowledge/{created_id}", "Get Single Document"))
            
            # Retry sync (if failed)
            all_results.append(test_endpoint("POST", f"/api/knowledge/{created_id}/retry-sync", "Retry Sync"))
            
            # Delete document
            all_results.append(test_endpoint("DELETE", f"/api/knowledge/{created_id}", "Delete Document"))
    
    # ========================
    # Page 3: Education Audio
    # ========================
    log("\n" + "=" * 40)
    log("PAGE 3: Education Audio")
    log("=" * 40)
    
    # Get voices
    voices_result = test_endpoint("GET", "/api/audio/voices/list", "Get Available Voices")
    all_results.append(voices_result)
    
    # Need a knowledge document for audio tests - create one
    audio_test_payload = {
        "disease_name": "Audio Test Disease",
        "document_type": "faq",
        "raw_content": "# Patient Education\n\nThis is educational content about diabetes management."
    }
    audio_doc_result = test_endpoint("POST", "/api/knowledge", "Create Doc for Audio Test", json_data=audio_test_payload)
    all_results.append(audio_doc_result)
    
    audio_knowledge_id = None
    if audio_doc_result.get("success") and audio_doc_result.get("response"):
        audio_knowledge_id = audio_doc_result["response"].get("knowledge_id")
        time.sleep(2)
        
        # Generate script
        script_result = test_endpoint("POST", "/api/audio/generate-script", "Generate Script", 
                                       json_data={"knowledge_id": audio_knowledge_id})
        all_results.append(script_result)
        
        # Get audio files (may be empty)
        all_results.append(test_endpoint("GET", f"/api/audio/{audio_knowledge_id}", "Get Audio Files"))
        
        # Generate audio (need voice_id)
        voice_id = None
        if voices_result.get("success") and voices_result.get("response"):
            voices = voices_result["response"]
            if voices:
                voice_id = voices[0].get("voice_id")
        
        if voice_id and script_result.get("success"):
            script_text = script_result.get("response", {}).get("script", "Hello, this is a test.")
            audio_gen_result = test_endpoint("POST", "/api/audio/generate", "Generate Audio",
                                              json_data={"knowledge_id": audio_knowledge_id, "script": script_text[:100], "voice_id": voice_id})
            all_results.append(audio_gen_result)
        
        # Cleanup
        test_endpoint("DELETE", f"/api/knowledge/{audio_knowledge_id}", "Cleanup Audio Test Doc")
    
    # ========================
    # Page 4: Agent Setup
    # ========================
    log("\n" + "=" * 40)
    log("PAGE 4: Agent Setup")
    log("=" * 40)
    
    # List agents
    agents_result = test_endpoint("GET", "/api/agent", "List Agents")
    all_results.append(agents_result)
    
    # Get voice for agent creation
    voice_id = None
    if voices_result.get("success") and voices_result.get("response"):
        voices = voices_result["response"]
        if voices:
            voice_id = voices[0].get("voice_id")
    
    if voice_id:
        # Create agent
        agent_payload = {
            "name": "API Test Agent",
            "knowledge_ids": [],
            "voice_id": voice_id,
            "answer_style": "professional",
            "doctor_id": "test_doctor"
        }
        agent_create_result = test_endpoint("POST", "/api/agent", "Create Agent", json_data=agent_payload)
        all_results.append(agent_create_result)
        
        agent_id = None
        if agent_create_result.get("success") and agent_create_result.get("response"):
            agent_id = agent_create_result["response"].get("agent_id")
            
            # Delete agent
            all_results.append(test_endpoint("DELETE", f"/api/agent/{agent_id}", "Delete Agent"))
    
    # ========================
    # Page 5: Patient Test
    # ========================
    log("\n" + "=" * 40)
    log("PAGE 5: Patient Test")
    log("=" * 40)
    
    # Need an agent for patient session - create one
    if voice_id:
        patient_agent_payload = {
            "name": "Patient Test Agent",
            "knowledge_ids": [],
            "voice_id": voice_id,
            "answer_style": "friendly",
            "doctor_id": "test_doctor"
        }
        patient_agent_result = test_endpoint("POST", "/api/agent", "Create Agent for Patient Test", json_data=patient_agent_payload)
        all_results.append(patient_agent_result)
        
        patient_agent_id = None
        if patient_agent_result.get("success") and patient_agent_result.get("response"):
            patient_agent_id = patient_agent_result["response"].get("agent_id")
            
            # Create session
            session_payload = {"patient_id": "test_patient_123", "agent_id": patient_agent_id}
            session_result = test_endpoint("POST", "/api/patient/session", "Create Patient Session", json_data=session_payload)
            all_results.append(session_result)
            
            session_id = None
            if session_result.get("success") and session_result.get("response"):
                session_id = session_result["response"].get("session_id")
                
                # Send message
                msg_result = test_endpoint("POST", f"/api/patient/session/{session_id}/message", "Send Message",
                                            json_data={"message": "Hello, I have a question about my medication."})
                all_results.append(msg_result)
                
                # End session
                all_results.append(test_endpoint("POST", f"/api/patient/session/{session_id}/end", "End Session"))
            
            # Cleanup agent
            test_endpoint("DELETE", f"/api/agent/{patient_agent_id}", "Cleanup Patient Test Agent")
    
    # ========================
    # Page 6: Conversation Logs
    # ========================
    log("\n" + "=" * 40)
    log("PAGE 6: Conversation Logs")
    log("=" * 40)
    
    all_results.append(test_endpoint("GET", "/api/conversations", "List Conversations"))
    all_results.append(test_endpoint("GET", "/api/conversations/statistics", "Get Statistics"))
    
    # ========================
    # Summary
    # ========================
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    
    passed = sum(1 for r in all_results if r.get("success"))
    failed = sum(1 for r in all_results if not r.get("success"))
    total = len(all_results)
    
    log(f"Total Tests: {total}")
    log(f"Passed: {passed}")
    log(f"Failed: {failed}")
    log(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
    
    log("\n" + "-" * 40)
    log("Failed Endpoints:")
    log("-" * 40)
    for r in all_results:
        if not r.get("success"):
            log(f"  ❌ {r.get('endpoint')} - {r.get('description')}")
            if r.get("error"):
                log(f"     Error: {r.get('error')}")
    
    log("\n" + "-" * 40)
    log("Passed Endpoints:")
    log("-" * 40)
    for r in all_results:
        if r.get("success"):
            log(f"  ✅ {r.get('endpoint')} - {r.get('description')}")
    
    # Write results to file
    report_path = "api_test_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(RESULTS))
    
    # Write JSON results
    json_path = "api_test_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "summary": {"total": total, "passed": passed, "failed": failed},
            "results": all_results
        }, f, indent=2, default=str)
    
    log(f"\n📄 Report saved to: {report_path}")
    log(f"📄 JSON results saved to: {json_path}")
    
    return all_results

if __name__ == "__main__":
    main()
