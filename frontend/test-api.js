// Simple test script to verify API endpoints
// Run this in the browser console on your deployed site

const API_BASE = 'https://cirinew.onrender.com/api/v1';

// Test function to check API connectivity
async function testAPI() {
  console.log('Testing API connectivity...');
  
  try {
    // Test health endpoint
    const healthResponse = await fetch(`${API_BASE.replace('/v1', '')}/health`);
    console.log('Health check:', healthResponse.status, await healthResponse.text());
    
    // Test CORS preflight
    const corsResponse = await fetch(`${API_BASE}/auth/login`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'https://ciri.no',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization'
      }
    });
    console.log('CORS preflight:', corsResponse.status, corsResponse.headers);
    
  } catch (error) {
    console.error('API test failed:', error);
  }
}

// Test function to check environment variables
function testEnvVars() {
  console.log('Environment variables:');
  console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
  console.log('NEXT_PUBLIC_API_BASE_URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
  console.log('BASE_URL:', process.env.BASE_URL);
  console.log('DASHBOARD_BASE_URL:', process.env.DASHBOARD_BASE_URL);
}

// Run tests
testEnvVars();
testAPI(); 