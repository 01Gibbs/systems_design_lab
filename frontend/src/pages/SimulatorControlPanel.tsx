import { useEffect, useState } from 'react';
import { simApi, type Scenario, type ActiveScenario } from '@/api/client';
import ScenarioCard from '@/components/ScenarioCard';
import ActiveScenarios from '@/components/ActiveScenarios';

interface SimulatorControlPanelProps {
  onStatusChange: (count: number) => void;
}

export default function SimulatorControlPanel({ onStatusChange }: SimulatorControlPanelProps) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeScenarios, setActiveScenarios] = useState<ActiveScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    const [scenariosRes, statusRes] = await Promise.all([simApi.scenarios(), simApi.status()]);

    if (!scenariosRes.ok) {
      setError('Failed to load scenarios');
      setLoading(false);
      return;
    }

    if (!statusRes.ok) {
      setError('Failed to load status');
      setLoading(false);
      return;
    }

    setScenarios(scenariosRes.data.scenarios);
    setActiveScenarios(statusRes.data.active);
    onStatusChange(statusRes.data.active.length);
    setLoading(false);
  };

  useEffect(() => {
    let cancelled = false;
    async function poll() {
      const statusRes = await simApi.status();
      if (!cancelled && statusRes.ok) {
        setActiveScenarios(statusRes.data.active);
        onStatusChange(statusRes.data.active.length);
      }
    }
    loadData();
    const interval = setInterval(() => {
      void poll();
    }, 2000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleResetAll = async () => {
    const res = await simApi.reset();
    if (res.ok) {
      await loadData();
    }
  };

  const handleDisable = async (scenarioName: string) => {
    const res = await simApi.disable(scenarioName);
    if (res.ok) {
      await loadData();
    }
  };

  const handleEnable = async () => {
    await loadData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-xl text-gray-600 dark:text-gray-400">Loading scenarios...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">⚠️ Error</h3>
          <p className="text-red-700 dark:text-red-300">{error}</p>
          <button
            onClick={loadData}
            className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="max-w-7xl mx-auto p-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
          Systems Design Lab
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">Simulator Control Panel</p>
      </header>

      <ActiveScenarios
        scenarios={activeScenarios}
        onDisable={handleDisable}
        onResetAll={handleResetAll}
      />

      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">
          Available Scenarios ({scenarios.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {scenarios.map((scenario) => (
            <ScenarioCard key={scenario.name} scenario={scenario} onEnable={handleEnable} />
          ))}
        </div>
      </div>
    </main>
  );
}
