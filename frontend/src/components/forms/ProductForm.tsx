'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Package, Plus, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

import { productApi, handleApiError } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import type { Product } from '@/types';

// Validation schema
const productSchema = z.object({
  name: z.string().optional(),
  description: z.string().optional(),
  category: z.string().optional(),
  price: z.string().optional().transform((val) => val ? parseFloat(val) : undefined),
  stock_quantity: z.string().optional().transform((val) => val ? parseInt(val) : undefined),
  specs: z.string().optional(),
});

type ProductFormData = z.infer<typeof productSchema>;

interface ProductFormProps {
  onSuccess?: () => void;
}

const ProductForm: React.FC<ProductFormProps> = ({ onSuccess }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    mode: 'onChange',
  });

  const onSubmit = async (data: ProductFormData) => {
    try {
      setIsSubmitting(true);
      setSubmitStatus('idle');
      console.log("Form data received:", data);
      console.log("Name field value:", data.name);
      console.log("Name field type:", typeof data.name);

      // Validate that name is not empty
      if (!data.name || data.name.trim() === '') {
        toast.error('El nombre del producto es requerido');
        return;
      }

      // Parse specs JSON if provided
      let parsedSpecs = {};
      if (data.specs && data.specs.trim()) {
        try {
          parsedSpecs = JSON.parse(data.specs);
        } catch (e) {
          toast.error('Las especificaciones deben ser un JSON válido');
          return;
        }
      }

      // Prepare product data
      const productData: Product = {
        name: data.name.trim(),
      };

      // Add optional fields only if they have values
      if (data.description && data.description.trim()) {
        productData.description = data.description.trim();
      }
      if (data.category && data.category.trim()) {
        productData.category = data.category.trim();
      }
      if (data.price !== undefined && data.price > 0) {
        productData.price = data.price;
      }
      if (data.stock_quantity !== undefined && data.stock_quantity >= 0) {
        productData.stock_quantity = data.stock_quantity;
      }
      if (Object.keys(parsedSpecs).length > 0) {
        productData.specs = parsedSpecs;
      }

      console.log("Product data being sent to backend:", productData);

      // Submit to API
      const response = await productApi.ingestProduct(productData);

      setSubmitStatus('success');
      toast.success(`Producto "${data.name || 'Sin nombre'}" agregado exitosamente`, {
        icon: '🎉',
        duration: 4000,
      });

      // Reset form
      reset();
      
      // Call success callback
      onSuccess?.();

    } catch (error) {
      const errorMessage = handleApiError(error);
      setSubmitStatus('error');
      toast.error(`Error al agregar producto: ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    reset();
    setSubmitStatus('idle');
  };

  return (
    <Card className="p-6">
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary-dark rounded-full flex items-center justify-center">
            <Package className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Agregar Producto</h2>
            <p className="text-sm text-gray-600">Completa la información del nuevo producto</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <Input
              label="Nombre del Producto *"
              placeholder="Ej: MacBook Pro M3 14-inch"
              error={errors.name?.message}
              {...register('name')}
            />
          </div>

          <Input
            label="Categoría"
            placeholder="Ej: Tecnología, Hogar, Belleza"
            error={errors.category?.message}
            {...register('category')}
          />

          <Input
            label="Precio"
            type="number"
            step="0.01"
            placeholder="Ej: 1999.99"
            error={errors.price?.message}
            {...register('price')}
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción
          </label>
          <textarea
            className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-primary focus:border-primary bg-white shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 resize-vertical min-h-[100px]"
            placeholder="Describe las características principales del producto..."
            {...register('description')}
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>

        {/* Additional Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Cantidad en Stock"
            type="number"
            min="0"
            placeholder="Ej: 10"
            error={errors.stock_quantity?.message}
            {...register('stock_quantity')}
          />

          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Especificaciones (JSON)
            </label>
            <textarea
              className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-primary focus:border-primary bg-white shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 resize-vertical min-h-[80px]"
              placeholder='{"processor": "Apple M3", "memory": "16GB", "storage": "512GB SSD"}'
              {...register('specs')}
            />
            {errors.specs && (
              <p className="mt-1 text-sm text-red-600">{errors.specs.message}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Formato JSON. Ejemplo: {'{\"key\": \"value\", \"key2\": \"value2\"}'}
            </p>
          </div>
        </div>

        {/* Submit Status */}
        {submitStatus === 'success' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 text-green-600 bg-green-50 p-3 rounded-lg"
          >
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Producto agregado exitosamente</span>
          </motion.div>
        )}

        {submitStatus === 'error' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg"
          >
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Error al agregar el producto</span>
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-4 pt-4">
          <Button
            type="submit"
            size="lg"
            icon={Plus}
            loading={isSubmitting}
            disabled={isSubmitting}
            className="flex-1"
          >
            {isSubmitting ? 'Agregando...' : 'Agregar Producto'}
          </Button>

          <Button
            type="button"
            variant="secondary"
            size="lg"
            onClick={resetForm}
            disabled={isSubmitting}
          >
            Limpiar
          </Button>
        </div>
      </form>

      {/* Help Text */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-2">💡 Consejos:</h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Un nombre descriptivo mejora la búsqueda</li>
          <li>• La descripción ayuda al sistema a entender el producto</li>
          <li>• Las especificaciones permiten comparaciones más precisas</li>
          <li>• Los productos se indexan automáticamente para búsqueda</li>
        </ul>
      </div>
    </Card>
  );
};

export default ProductForm;