import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
}) => {
  const baseClasses = 'rounded-lg bg-white border border-gray-200 shadow-soft transition-all duration-200';
  const hoverClasses = hover ? 'hover:shadow-elegant hover:scale-[1.02]' : '';
  const cardClasses = `${baseClasses} ${hoverClasses} ${className}`;

  const CardComponent = hover ? motion.div : 'div';
  const motionProps = hover ? {
    whileHover: { y: -2 },
    transition: { duration: 0.2 }
  } : {};

  return (
    <CardComponent
      className={cardClasses}
      {...motionProps}
    >
      {children}
    </CardComponent>
  );
};

export default Card;