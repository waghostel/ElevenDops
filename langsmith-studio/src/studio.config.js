/**
 * LangSmith Studio Configuration
 *
 * Configuration for connecting to local ElevenDops backend
 * and LangSmith cloud for trace visualization.
 */

export const studioConfig = {
  // Backend API configuration
  backend: {
    url: process.env.BACKEND_URL || "http://localhost:8000",
    debugEndpoint: "/api/debug",
    healthEndpoint: "/api/debug/health",
    timeout: 30000,
  },

  // LangSmith configuration
  langsmith: {
    apiKey: process.env.LANGCHAIN_API_KEY,
    project: process.env.LANGCHAIN_PROJECT || "elevendops-langgraph-debug",
    baseUrl: "https://smith.langchain.com",
  },

  // UI configuration
  ui: {
    port: parseInt(process.env.STUDIO_PORT) || 3001,
    autoRefresh: true,
    refreshInterval: 5000,
  },

  // Debugging options
  debug: {
    traceLevel: process.env.LANGSMITH_TRACE_LEVEL || "info",
    logRequests: process.env.DEBUG === "true",
  },
};

export default studioConfig;
