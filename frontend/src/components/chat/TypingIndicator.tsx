'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';

const TypingIndicator: React.FC = () => {
  const dotVariants = {
    start: { y: "0%", opacity: 0.4 },
    end: { y: "-20%", opacity: 1 }
  };

  const dotTransition = {
    duration: 0.6,
    repeat: Infinity,
    repeatType: "reverse" as const,
    ease: "easeInOut"
  };

  return (
    <div className="flex items-start space-x-3 mb-4">
      <motion.div 
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
        className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 border border-slate-300 flex items-center justify-center"
      >
        <Image
          src="/logo.png"
          alt="AI Assistant"
          width={24}
          height={24}
          className="rounded-full"
        />
      </motion.div>
      
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="bg-white border border-slate-200 rounded-2xl rounded-bl-md px-6 py-4 shadow-sm"
      >
        <div className="flex items-center space-x-1">
          <span className="text-sm text-slate-600 mr-2">Escribiendo</span>
          <div className="flex space-x-1">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                className="w-2 h-2 bg-primary rounded-full"
                variants={dotVariants}
                initial="start"
                animate="end"
                transition={{
                  ...dotTransition,
                  delay: index * 0.2
                }}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default TypingIndicator;