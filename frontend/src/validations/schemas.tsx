/**
 * Zod Validation Schemas
 * Centralized validation for forms and data
 */
import { z } from 'zod';

// Password validation
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(72, 'Password must be less than 72 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/\d/, 'Password must contain at least one number')
  .regex(/[!@#$%^&*()_+\-=\[\]{};:,.<>?]/, 
    'Password must contain at least one special character'
  );

// Username validation
export const usernameSchema = z
  .string()
  .min(3, 'Username must be at least 3 characters')
  .max(50, 'Username must be less than 50 characters')
  .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores');

// Email validation
export const emailSchema = z
  .string()
  .email('Invalid email address')
  .min(5, 'Email must be at least 5 characters')
  .max(100, 'Email must be less than 100 characters');

// User schemas
export const loginSchema = z.object({
  username: usernameSchema,
  password: z.string().min(1, 'Password is required')
});

export const registerSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: passwordSchema,
  fullName: z.string().optional(),
  role: z.enum(['admin', 'investigator', 'analyst', 'viewer', 'auditor']).optional()
});

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: passwordSchema,
  confirmPassword: z.string().min(1, 'Please confirm your password')
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
});

// Case schemas
export const createCaseSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(200, 'Title must be less than 200 characters'),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical']).default('medium'),
  category: z.string().optional(),
  assignedTo: z.string().optional()
});

// Evidence schemas
export const createEvidenceSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(200, 'Title must be less than 200 characters'),
  description: z.string().optional(),
  type: z.enum(['document', 'image', 'video', 'audio', 'data', 'other']),
  source: z.string().min(1, 'Source is required'),
  trustScore: z.number().min(0).max(100).optional(),
  tags: z.array(z.string()).optional(),
  caseId: z.string().uuid('Invalid case ID')
});

// Graph schemas
export const graphQuerySchema = z.object({
  caseId: z.string().uuid('Invalid case ID'),
  depth: z.number().int().min(1).max(10).default(3),
  entityTypes: z.array(z.string()).optional(),
  relationshipTypes: z.array(z.string()).optional()
});

// Export types
export type LoginData = z.infer<typeof loginSchema>;
export type RegisterData = z.infer<typeof registerSchema>;
export type ChangePasswordData = z.infer<typeof changePasswordSchema>;
export type CreateCaseData = z.infer<typeof createCaseSchema>;
export type CreateEvidenceData = z.infer<typeof createEvidenceSchema>;
export type GraphQueryData = z.infer<typeof graphQuerySchema>;