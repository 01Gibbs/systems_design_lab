import { useState } from 'react';
import type { Scenario } from '@/api/client';
import { buildParameterSchema } from '@/schemas/forms';

interface ScenarioCardProps {
  scenario: Scenario;
  onEnable: () => void;
}

export default function ScenarioCard({ scenario, onEnable }: ScenarioCardProps) {
  const [parameters, setParameters] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const { meta } = scenario;
  const paramSchema = meta.parameter_schema as {
    properties?: Record<string, { type: string; minimum?: number; maximum?: number }>;
    required?: string[];
  };

  const handleEnable = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    // Validate with Zod (client-side form validation only)
    try {
      const zodSchema = buildParameterSchema(paramSchema);
      zodSchema.parse(parameters);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Validation failed');
      setLoading(false);
      return;
    }

    // Call typed API client
    const { simApi } = await import('@/api/client');
    const res = await simApi.enable(meta.name, parameters);

    setLoading(false);

    if (res.ok) {
      setSuccess(true);
      setParameters({});
      onEnable();
      setTimeout(() => setSuccess(false), 3000);
    } else {
      setError('Failed to enable scenario');
    }
  };

  const handleParamChange = (key: string, value: string) => {
    const paramType = paramSchema.properties?.[key]?.type;
    let parsedValue: unknown = value;

    if (paramType === 'number' || paramType === 'integer') {
      parsedValue = value === '' ? undefined : parseFloat(value);
    } else if (paramType === 'boolean') {
      parsedValue = value === 'true';
    }

    setParameters((prev) => ({
      ...prev,
      [key]: parsedValue,
    }));
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 bg-white dark:bg-gray-800 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400">{meta.name}</h3>
        <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
          {meta.targets.join(', ')}
        </span>
      </div>

      <p className="text-gray-700 dark:text-gray-300 mb-4">{meta.description}</p>

      {paramSchema.properties && Object.keys(paramSchema.properties).length > 0 && (
        <div className="space-y-3 mb-4">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase">
            Parameters
          </h4>
          {Object.entries(paramSchema.properties).map(([key, propSchema]) => {
            const isRequired = paramSchema.required?.includes(key);
            return (
              <div key={key}>
                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                  {key}
                  {isRequired && <span className="text-red-500 ml-1">*</span>}
                  <span className="text-xs text-gray-500 ml-2">({propSchema.type})</span>
                </label>
                <input
                  type={
                    propSchema.type === 'number' || propSchema.type === 'integer'
                      ? 'number'
                      : propSchema.type === 'boolean'
                        ? 'checkbox'
                        : 'text'
                  }
                  value={String(parameters[key] ?? '')}
                  onChange={(e) => handleParamChange(key, e.target.value)}
                  min={propSchema.minimum}
                  max={propSchema.maximum}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            );
          })}
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-sm text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md text-sm text-green-700 dark:text-green-300">
          ✓ Scenario enabled successfully
        </div>
      )}

      <button
        onClick={handleEnable}
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
      >
        {loading ? 'Enabling...' : 'Enable Scenario'}
      </button>
    </div>
  );
}
