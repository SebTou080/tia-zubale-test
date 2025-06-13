'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';
import ChatInterface from '@/components/chat/ChatInterface';
import ProductForm from '@/components/forms/ProductForm';
import { MessageCircle, Package } from 'lucide-react';

const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'products'>('chat');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <div className="container mx-auto px-4 py-6">
        <motion.header 
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-center mb-4">
            <Image
              src="/logo-entero.png"
              alt="Logo"
              width={180}
              height={60}
              className="h-auto"
              priority
            />
          </div>
          <motion.h1 
            className="text-4xl font-bold text-slate-800 mb-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            Asistente de Productos
          </motion.h1>
          <motion.p 
            className="text-lg text-slate-600 max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Pregúntame sobre cualquier producto
          </motion.p>
        </motion.header>

        <motion.div 
          className="max-w-6xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="border-b border-slate-200">
              <nav className="flex">
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`flex-1 px-6 py-4 text-sm font-medium flex items-center justify-center space-x-2 transition-all duration-200 ${
                    activeTab === 'chat'
                      ? 'text-primary bg-primary/5 border-b-2 border-primary'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                  }`}
                >
                  <MessageCircle size={18} />
                  <span>Chat con IA</span>
                </button>
                <button
                  onClick={() => setActiveTab('products')}
                  className={`flex-1 px-6 py-4 text-sm font-medium flex items-center justify-center space-x-2 transition-all duration-200 ${
                    activeTab === 'products'
                      ? 'text-primary bg-primary/5 border-b-2 border-primary'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                  }`}
                >
                  <Package size={18} />
                  <span>Agregar Producto</span>
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'chat' ? (
                <motion.div
                  key="chat"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChatInterface />
                </motion.div>
              ) : (
                <motion.div
                  key="products"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ProductForm onSuccess={() => setActiveTab('chat')} />
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default HomePage;