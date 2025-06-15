import axios from 'axios';
import type { 
  ChatResponse, 
  Product, 
  ProductIngestResponse, 
  User, 
  Conversation,
  Message
} from '@/types';

// Use environment variable for API base URL or fallback to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased to 60 seconds for product ingestion with Azure OpenAI
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      url: error.config?.url,
    });
    return Promise.reject(error);
  }
);

// API Methods
export const chatApi = {
  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Start new chat
  async startChat(userId?: string): Promise<{ conversation_id: string; user_id: string; message: string; is_new_user: boolean }> {
    const response = await api.post('/chat/start', userId ? { user_id: userId } : {});
    return response.data;
  },

  // Send chat message
  async sendMessage(message: string, userId: string, conversationId?: string): Promise<ChatResponse> {
    const response = await api.post('/chat/message', {
      message,
      user_id: userId,
      conversation_id: conversationId,
    });
    return response.data;
  },

  // Get conversation history
  async getConversationHistory(conversationId: string): Promise<{
    conversation_id: string;
    messages: Message[];
    summary: string;
    total_messages: number;
  }> {
    const response = await api.get(`/chat/${conversationId}/history`);
    return response.data;
  },

  // Get user profile
  async getUserProfile(userId: string): Promise<User> {
    const response = await api.get(`/user/${userId}/profile`);
    return response.data;
  },
};

export const productApi = {
  // Ingest new product
  async ingestProduct(product: Product): Promise<ProductIngestResponse> {
    const response = await api.post('/ingest', product);
    return response.data;
  },

};

// Error handling helper
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default api;