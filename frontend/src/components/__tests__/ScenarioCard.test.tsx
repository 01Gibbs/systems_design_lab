import { render, screen, fireEvent } from '@testing-library/react';
import ScenarioCard from '../ScenarioCard';

describe('ScenarioCard', () => {
  const scenario = {
    name: 'fixed_latency',
    description: 'Injects latency',
    parameter_schema: {},
    safety_limits: {},
    targets: ['http'],
  };

  it('renders scenario name and description', () => {
    render(<ScenarioCard scenario={scenario} onEnable={() => {}} />);
    expect(screen.getByText('fixed_latency')).toBeInTheDocument();
    expect(screen.getByText('Injects latency')).toBeInTheDocument();
  });

  it('calls onEnable when enable button is clicked', () => {
    const onEnable = jest.fn();
    render(<ScenarioCard scenario={scenario} onEnable={onEnable} />);
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);
    expect(onEnable).toHaveBeenCalled();
  });
});
