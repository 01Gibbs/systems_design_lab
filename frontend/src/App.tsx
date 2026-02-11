import { useState } from 'react';
import GlobalBanner from './components/GlobalBanner';
import SimulatorControlPanel from './pages/SimulatorControlPanel';

export default function App() {
  const [activeCount, setActiveCount] = useState(0);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <GlobalBanner activeCount={activeCount} />
      <SimulatorControlPanel onStatusChange={setActiveCount} />
    </div>
  );
}
