/**
 * LangSmith Studio - Main Entry Point
 * 
 * Provides local utilities for debugging LangGraph workflows.
 */

import { studioConfig } from './studio.config.js';

/**
 * Check connection to backend debug API
 */
async function checkBackendConnection() {
  const url = `${studioConfig.backend.url}${studioConfig.backend.healthEndpoint}`;
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(studioConfig.backend.timeout),
    });
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    
    const data = await response.json();
    return {
      connected: true,
      data,
    };
  } catch (error) {
    return {
      connected: false,
      error: error.message,
    };
  }
}

/**
 * Execute a debug script generation
 */
async function runDebugExecution(options) {
  const url = `${studioConfig.backend.url}${studioConfig.backend.debugEndpoint}/script-generation`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      knowledge_content: options.knowledgeContent,
      prompt: options.prompt,
      model_name: options.modelName || 'gemini-2.0-flash',
      debug_level: options.debugLevel || studioConfig.debug.traceLevel,
      session_name: options.sessionName,
    }),
    signal: AbortSignal.timeout(studioConfig.backend.timeout),
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Debug execution failed: ${error}`);
  }
  
  return await response.json();
}

/**
 * Get LangSmith URL for a trace
 */
function getLangSmithTraceUrl(traceId) {
  const project = studioConfig.langsmith.project;
  return `${studioConfig.langsmith.baseUrl}/o/default/projects/p/${project}`;
}

/**
 * Main studio display
 */
async function main() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('      ElevenDops LangSmith Studio - Debug Utilities');
  console.log('═══════════════════════════════════════════════════════════');
  console.log();
  
  // Check backend connection
  console.log('🔍 Checking backend connection...');
  const backend = await checkBackendConnection();
  
  if (backend.connected) {
    console.log('✅ Backend connected');
    console.log(`   URL: ${studioConfig.backend.url}`);
    console.log(`   LangSmith configured: ${backend.data.langsmith_configured}`);
    console.log(`   LangSmith available: ${backend.data.langsmith_available}`);
    console.log(`   Project: ${backend.data.project}`);
    console.log(`   Trace level: ${backend.data.trace_level}`);
  } else {
    console.log('❌ Backend not connected');
    console.log(`   Error: ${backend.error}`);
    console.log();
    console.log('Please start the backend server:');
    console.log('   cd .. && poetry run uvicorn backend.main:app --reload');
    process.exit(1);
  }
  
  console.log();
  console.log('🚀 Studio ready!');
  console.log();
  console.log('LangSmith Dashboard:');
  console.log(`   ${getLangSmithTraceUrl()}`);
  console.log();
  console.log('Debug API endpoints:');
  console.log(`   POST ${studioConfig.backend.url}/api/debug/script-generation`);
  console.log(`   GET  ${studioConfig.backend.url}/api/debug/sessions`);
  console.log(`   GET  ${studioConfig.backend.url}/api/debug/health`);
  console.log();
}

// Run main
main().catch(console.error);
