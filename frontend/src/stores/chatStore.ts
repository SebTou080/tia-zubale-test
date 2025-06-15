import { create } from 'zustand';

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

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  sendMessage: async (message: string) => {
    const { messages } = get();
    
    // Add user message immediately
    const userMessage: ChatMessage = { role: 'user', content: message };
    set({ 
      messages: [...messages, userMessage], 
      isLoading: true, 
      error: null 
    });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      
      if (!apiUrl) {
        throw new Error('API URL not configured');
      }
      
      const response = await fetch(`${apiUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          conversation_history: messages
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Update with the complete conversation history from the response
      set({ 
        messages: data.conversation_history,
        isLoading: false 
      });

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.'
      };
      
      set({ 
        messages: [...get().messages, errorMessage],
        isLoading: false,
        error: error instanceof Error ? error.message : 'Error desconocido'
      });
    }
  },

  clearChat: () => {
    set({ 
      messages: [], 
      error: null 
    });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));