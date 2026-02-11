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
});
