'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Star, DollarSign, Package, Tag, TrendingUp } from 'lucide-react';
import Card from '@/components/ui/Card';
import type { DocumentReference } from '@/types';

interface ProductCardProps {
  product: DocumentReference;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const formatScore = (score: number) => {
    return Math.round(score * 100);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 0.6) return 'text-blue-600 bg-blue-50 border-blue-200';
    return 'text-slate-600 bg-slate-50 border-slate-200';
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      <Card hover className="p-5 bg-gradient-to-br from-white to-slate-50 border border-slate-200 hover:border-primary/30 hover:shadow-lg transition-all duration-300">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              <h3 className="font-semibold text-slate-900 truncate">
                {product.product_name}
              </h3>
            </div>
            
            <p className="text-sm text-slate-600 line-clamp-2 leading-relaxed">
              {product.content_snippet}
            </p>
          </div>

          <div className={`flex items-center space-x-1 px-3 py-1 rounded-full border text-xs font-medium ml-3 ${getScoreColor(product.relevance_score)}`}>
            <TrendingUp size={12} />
            <span>{formatScore(product.relevance_score)}%</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1 text-slate-500">
              <Package size={14} />
              <span className="text-xs font-medium">
                ID: {product.product_id}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-1 text-primary bg-primary/10 px-2 py-1 rounded-md">
            <Star size={12} />
            <span className="text-xs font-medium">Relevante</span>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

export default ProductCard;