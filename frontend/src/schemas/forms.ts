/**
 * Zod schemas for CLIENT-SIDE form validation ONLY
 *
 * These validate user input before calling the typed API client.
 * DO NOT duplicate backend request/response shapes here.
 * Use the typed client from src/api/client.ts for all API calls.
 */

import { z } from 'zod';

// Dynamic schema builder from backend parameter_schema
export function buildParameterSchema(paramSchema: Record<string, unknown>) {
  const shape: Record<string, z.ZodTypeAny> = {};
  const props = (paramSchema.properties as Record<string, unknown>) || {};
  const required = (paramSchema.required as string[]) || [];

  for (const [key, prop] of Object.entries(props)) {
    const p = prop as { type: string; minimum?: number; maximum?: number };
    let schema: z.ZodTypeAny;

    if (p.type === 'integer' || p.type === 'number') {
      schema = z.coerce.number();
      if (typeof p.minimum === 'number') schema = (schema as z.ZodNumber).min(p.minimum);
      if (typeof p.maximum === 'number') schema = (schema as z.ZodNumber).max(p.maximum);
    } else if (p.type === 'boolean') {
      schema = z.boolean();
    } else {
      schema = z.string().min(1);
    }

    if (required.includes(key)) {
      shape[key] = schema;
    } else {
      shape[key] = schema.optional();
    }
  }

  return z.object(shape);
}
