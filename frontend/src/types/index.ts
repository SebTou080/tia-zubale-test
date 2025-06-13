export interface User {
  user_id: string;
  created_at: string;
  last_activity: string;
  total_conversations: number;
  preferences: Record<string, any>;
  viewed_products: string[];
  favorite_categories: string[];
}

export interface Conversation {
  conversation_id: string;
  user_id: string;
  created_at: string;
  last_message_at: string;
  total_messages: number;
  status: 'active' | 'archived' | 'ended';
  summary: string;
  mentioned_products: string[];
}

export interface Message {
  message_id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  products_referenced?: string[];
  intent?: string;
  confidence_score?: number;
}

export interface DocumentReference {
  product_id: string;
  product_name: string;
  relevance_score: number;
  content_snippet: string;
}

export interface Product {
  product_id?: string;
  name: string;
  description?: string;
  category?: string;
  price?: number;
  stock_quantity?: number;
  specs?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface ProductIngestResponse {
  product_id: string;
  message: string;
  status: string;
}

export interface ChatState {
  user_id: string | null;
  conversation_id: string | null;
  messages: Message[];
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ProductSource {
  product_id: string;
  product_name: string;
  relevance_score: number;
  content_snippet: string;
}

export interface ChatResponse {
  message: string;
  sources: ProductSource[];
  confidence_score: number;
  conversation_history: ChatMessage[];
}

export interface ProductFormData {
  name: string;
  description: string;
  category: string;
  price: number;
  metadata?: Record<string, any>;
}