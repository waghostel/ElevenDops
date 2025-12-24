/**
 * Test connection to backend debug API
 */

import { studioConfig } from './studio.config.js';

async function testConnection() {
  console.log('Testing connection to backend...');
  console.log(`URL: ${studioConfig.backend.url}${studioConfig.backend.healthEndpoint}`);
  console.log();
  
  try {
    const response = await fetch(
      `${studioConfig.backend.url}${studioConfig.backend.healthEndpoint}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000),
      }
    );
    
    if (!response.ok) {
      console.log(`❌ Backend returned status ${response.status}`);
      process.exit(1);
    }
    
    const data = await response.json();
    
    console.log('✅ Connection successful!');
    console.log();
    console.log('Response:');
    console.log(JSON.stringify(data, null, 2));
    
    // Verify expected fields
    const requiredFields = ['status', 'langsmith_configured', 'project', 'trace_level'];
    const missingFields = requiredFields.filter(f => !(f in data));
    
    if (missingFields.length > 0) {
      console.log();
      console.log(`⚠️  Missing expected fields: ${missingFields.join(', ')}`);
      process.exit(1);
    }
    
    console.log();
    console.log('✅ All expected fields present');
    process.exit(0);
    
  } catch (error) {
    console.log(`❌ Connection failed: ${error.message}`);
    console.log();
    console.log('Make sure the backend is running:');
    console.log('   cd .. && poetry run uvicorn backend.main:app --reload');
    process.exit(1);
  }
}

testConnection();
