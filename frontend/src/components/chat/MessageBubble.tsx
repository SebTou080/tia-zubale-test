'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { User, AlertCircle } from 'lucide-react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage } from '@/stores/chatStore';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = false; // No error handling in ChatMessage

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex items-start space-x-3 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 260, damping: 20 }}
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-gradient-to-br from-primary to-primary-dark text-white' 
              : isError
                ? 'bg-gradient-to-br from-red-500 to-red-600 text-white'
                : 'bg-gradient-to-br from-slate-100 to-slate-200 border border-slate-300'
          }`}
        >
          {isUser ? (
            <User size={20} />
          ) : isError ? (
            <AlertCircle size={20} />
          ) : (
            <Image
              src="/logo.png"
              alt="AI Assistant"
              width={24}
              height={24}
              className="rounded-full"
            />
          )}
        </motion.div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <motion.div
            initial={{ opacity: 0, x: isUser ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.3 }}
            className={`relative px-6 py-4 rounded-2xl shadow-sm ${
              isUser
                ? 'bg-gradient-to-br from-primary to-primary-dark text-white rounded-br-md'
                : isError
                  ? 'bg-gradient-to-br from-red-50 to-red-100 border border-red-200 text-red-800 rounded-bl-md'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-bl-md shadow-md'
            }`}
          >
            {/* Message Text */}
            <div className={`prose max-w-none text-sm leading-relaxed ${
              isUser ? 'prose-invert' : isError ? 'prose-red' : 'prose-slate'
            }`}>
              {isError && (
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle size={16} className="text-red-600" />
                  <span className="text-sm font-medium text-red-600">Error</span>
                </div>
              )}
              {!isUser ? (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Custom styling for markdown elements
                    h1: ({ children }) => <h1 className="text-lg font-bold mb-2 text-slate-800">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-base font-bold mb-2 text-slate-800">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-sm font-bold mb-1 text-slate-800">{children}</h3>,
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    strong: ({ children }) => <strong className="font-bold text-slate-900">{children}</strong>,
                    em: ({ children }) => <em className="italic">{children}</em>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="text-sm">{children}</li>,
                    code: ({ children, className }) => {
                      const isInline = !className;
                      return isInline ? (
                        <code className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ) : (
                        <code className="block bg-slate-100 text-slate-800 p-3 rounded-lg text-xs font-mono overflow-x-auto">
                          {children}
                        </code>
                      );
                    },
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-primary/30 pl-4 italic text-slate-600 my-2">
                        {children}
                      </blockquote>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              ) : (
                <p className="mb-0 whitespace-pre-wrap">
                  {message.content}
                </p>
              )}
            </div>

            {/* Gradient overlay for user messages */}
            {isUser && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/10 rounded-2xl pointer-events-none" />
            )}
          </motion.div>

          {/* Timestamp */}
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.3 }}
            className={`text-xs text-slate-500 mt-2 px-2 ${
              isUser ? 'text-right' : 'text-left'
            }`}
          >
            {format(new Date(), 'HH:mm', { locale: es })}
          </motion.span>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;