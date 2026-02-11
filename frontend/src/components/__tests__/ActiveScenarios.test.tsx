import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActiveScenarios from '../ActiveScenarios';

describe('ActiveScenarios', () => {
  const scenarios = [
    {
      name: 'fixed_latency',
      parameters: { delay_ms: 100 },
      enabled_at: new Date().toISOString(),
      expires_at: null,
    },
  ];

  it('renders active scenario names', () => {
    render(
      <ActiveScenarios
        scenarios={scenarios}
        onDisable={() => {}}
        onResetAll={() => {}}
      />
    );
    expect(screen.getByText('fixed_latency')).toBeInTheDocument();
  });
});
