import type { ActiveScenario } from '@/api/client';

interface ActiveScenariosProps {
  scenarios: ActiveScenario[];
  onDisable: (name: string) => void;
  onResetAll: () => void;
}

export default function ActiveScenarios({
  scenarios,
  onDisable,
  onResetAll,
}: ActiveScenariosProps) {
  if (scenarios.length === 0) return null;

  return (
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-red-800 dark:text-red-200">
          🔴 Active Scenarios ({scenarios.length})
        </h2>
        <button
          onClick={onResetAll}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
        >
          Reset All
        </button>
      </div>

      <div className="space-y-3">
        {scenarios.map((scenario) => (
          <div
            key={scenario.name}
            className="flex justify-between items-start bg-white dark:bg-gray-800 rounded-md p-4 border border-red-200 dark:border-red-700"
          >
            <div className="flex-1">
              <div className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                {scenario.name}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Enabled: {new Date(scenario.enabled_at).toLocaleString()}
                {scenario.expires_at && (
                  <> • Expires: {new Date(scenario.expires_at).toLocaleString()}</>
                )}
              </div>
              <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-900 rounded p-2 overflow-x-auto">
                {JSON.stringify(scenario.parameters, null, 2)}
              </pre>
            </div>
            <button
              onClick={() => onDisable(scenario.name)}
              className="ml-4 px-3 py-1 bg-red-100 hover:bg-red-200 dark:bg-red-800 dark:hover:bg-red-700 text-red-800 dark:text-red-100 rounded-md text-xl font-bold transition-colors"
              aria-label={`Disable ${scenario.name}`}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
