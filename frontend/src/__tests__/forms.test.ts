import { buildParameterSchema } from '../schemas/forms';

describe('buildParameterSchema', () => {
  it('returns a Zod schema for number params', () => {
    const schema = buildParameterSchema({
      properties: { foo: { type: 'number', minimum: 1, maximum: 10 } },
      required: ['foo'],
    });
    expect(() => schema.parse({ foo: 5 })).not.toThrow();
    expect(() => schema.parse({ foo: 0 })).toThrow();
    expect(() => schema.parse({ foo: 11 })).toThrow();
  });

  it('handles integer type parameters', () => {
    const schema = buildParameterSchema({
      properties: { count: { type: 'integer', minimum: 0, maximum: 100 } },
      required: ['count'],
    });

    expect(() => schema.parse({ count: 50 })).not.toThrow();
    expect(() => schema.parse({ count: -1 })).toThrow();
    expect(() => schema.parse({ count: 101 })).toThrow();
    // Should coerce string numbers
    expect(() => schema.parse({ count: '42' })).not.toThrow();
  });

  it('handles boolean type parameters', () => {
    const schema = buildParameterSchema({
      properties: { enabled: { type: 'boolean' } },
      required: ['enabled'],
    });

    expect(() => schema.parse({ enabled: true })).not.toThrow();
    expect(() => schema.parse({ enabled: false })).not.toThrow();
    expect(() => schema.parse({ enabled: 'true' })).toThrow();
  });

  it('handles string type parameters', () => {
    const schema = buildParameterSchema({
      properties: { name: { type: 'string' } },
      required: ['name'],
    });

    expect(() => schema.parse({ name: 'test' })).not.toThrow();
    expect(() => schema.parse({ name: '' })).toThrow(); // min length 1
    expect(() => schema.parse({ name: 123 })).toThrow();
  });

  it('handles optional parameters', () => {
    const schema = buildParameterSchema({
      properties: {
        required_field: { type: 'string' },
        optional_field: { type: 'number' },
      },
      required: ['required_field'],
    });

    // Should pass with only required field
    expect(() => schema.parse({ required_field: 'test' })).not.toThrow();

    // Should pass with both fields
    expect(() =>
      schema.parse({
        required_field: 'test',
        optional_field: 42,
      })
    ).not.toThrow();

    // Should fail without required field
    expect(() => schema.parse({ optional_field: 42 })).toThrow();
  });

  it('handles number parameters without min/max constraints', () => {
    const schema = buildParameterSchema({
      properties: { value: { type: 'number' } },
      required: ['value'],
    });

    expect(() => schema.parse({ value: -999 })).not.toThrow();
    expect(() => schema.parse({ value: 999 })).not.toThrow();
    expect(() => schema.parse({ value: 0 })).not.toThrow();
  });

  it('handles empty properties object', () => {
    const schema = buildParameterSchema({
      properties: {},
      required: [],
    });

    expect(() => schema.parse({})).not.toThrow();
    const result = schema.parse({});
    expect(result).toEqual({});
  });

  it('handles missing properties field', () => {
    const schema = buildParameterSchema({
      required: ['foo'],
    });

    // Should create empty schema when no properties
    expect(() => schema.parse({})).not.toThrow();
  });

  it('handles missing required field', () => {
    const schema = buildParameterSchema({
      properties: {
        field1: { type: 'string' },
        field2: { type: 'number' },
      },
    });

    // All fields should be optional when no required array
    expect(() => schema.parse({})).not.toThrow();
    expect(() => schema.parse({ field1: 'test' })).not.toThrow();
    expect(() => schema.parse({ field2: 42 })).not.toThrow();
  });

  it('handles unknown parameter types', () => {
    const schema = buildParameterSchema({
      properties: {
        unknown_type: { type: 'unknown' },
        custom_type: { type: 'array' },
      },
      required: ['unknown_type', 'custom_type'],
    });

    // Unknown types should default to string validation
    expect(() =>
      schema.parse({
        unknown_type: 'test',
        custom_type: 'another_test',
      })
    ).not.toThrow();

    // Should fail with empty strings (min length 1)
    expect(() =>
      schema.parse({
        unknown_type: '',
        custom_type: 'test',
      })
    ).toThrow();
  });

  it('handles complex mixed schema', () => {
    const schema = buildParameterSchema({
      properties: {
        delay: { type: 'integer', minimum: 100, maximum: 5000 },
        probability: { type: 'number', minimum: 0, maximum: 1 },
        enabled: { type: 'boolean' },
        description: { type: 'string' },
        mode: { type: 'string' },
      },
      required: ['delay', 'enabled'],
    });

    const validData = {
      delay: 1000,
      enabled: true,
      probability: 0.5,
      description: 'Test scenario',
    };

    expect(() => schema.parse(validData)).not.toThrow();

    // Missing required field should fail
    expect(() => schema.parse({ enabled: true })).toThrow();

    // Invalid delay should fail
    expect(() =>
      schema.parse({
        delay: 50, // too low
        enabled: true,
      })
    ).toThrow();
  });
});
