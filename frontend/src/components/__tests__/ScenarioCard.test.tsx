import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScenarioCard from '../ScenarioCard';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.post('http://localhost:8000/api/sim/enable', () => HttpResponse.json({ success: true }))
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ScenarioCard', () => {
  const basicScenario = {
    name: 'fixed_latency',
    description: 'Injects latency',
    parameter_schema: {},
    safety_limits: {},
    targets: ['http'] as ('http' | 'db' | 'cpu' | 'algorithm')[],
  };

  const scenarioWithParams = {
    name: 'error_burst',
    description: 'Random errors',
    parameter_schema: {
      properties: {
        probability: { type: 'number', minimum: 0, maximum: 1 },
        duration_ms: { type: 'integer', minimum: 100, maximum: 5000 },
        enabled: { type: 'boolean' },
      },
      required: ['probability'],
    },
    safety_limits: {},
    targets: ['http', 'db'] as ('http' | 'db' | 'cpu' | 'algorithm')[],
  };

  it('renders scenario name and description', () => {
    render(<ScenarioCard scenario={basicScenario} onEnable={() => {}} />);
    expect(screen.getByText('fixed_latency')).toBeInTheDocument();
    expect(screen.getByText('Injects latency')).toBeInTheDocument();
  });

  it('displays targets as comma-separated list', () => {
    render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);
    expect(screen.getByText('http, db')).toBeInTheDocument();
  });

  it('renders parameter inputs for scenario with parameters', () => {
    const { container } = render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);
    expect(screen.getByText('Parameters')).toBeInTheDocument();
    expect(screen.getByText('probability')).toBeInTheDocument();
    expect(screen.getByText('duration_ms')).toBeInTheDocument();
    // Verify inputs exist
    const inputs = container.querySelectorAll('input[type="number"]');
    expect(inputs.length).toBeGreaterThan(0);
  });

  it('marks required parameters with asterisk', () => {
    render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);
    // probability is required
    const labelText = screen.getByText('probability').parentElement?.textContent;
    expect(labelText).toContain('*');
  });

  it('shows parameter types', () => {
    render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);
    expect(screen.getByText(/(number)/i)).toBeInTheDocument();
    expect(screen.getByText(/(integer)/i)).toBeInTheDocument();
  });

  it('handles number input changes', () => {
    const { container } = render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);
    const inputs = container.querySelectorAll('input[type="number"]');
    const probabilityInput = inputs[0] as HTMLInputElement; // First number input is probability
    fireEvent.change(probabilityInput, { target: { value: '0.5' } });
    expect(probabilityInput.value).toBe('0.5');
  });

  it('handles integer input changes', () => {
    const { container } = render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);
    const inputs = container.querySelectorAll('input[type="number"]');
    const durationInput = inputs[1] as HTMLInputElement; // Second number input is duration_ms
    fireEvent.change(durationInput, { target: { value: '1000' } });
    expect(durationInput.value).toBe('1000');
  });

  it('calls onEnable when enable button is clicked successfully', async () => {
    const onEnable = vi.fn();
    render(<ScenarioCard scenario={basicScenario} onEnable={onEnable} />);
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);
    await waitFor(() => {
      expect(onEnable).toHaveBeenCalled();
    });
  });

  it('shows success message after successful enable', async () => {
    render(<ScenarioCard scenario={basicScenario} onEnable={() => {}} />);
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);
    await waitFor(() => {
      expect(screen.getByText(/Scenario enabled successfully/i)).toBeInTheDocument();
    });
  });

  it('shows error message on API failure', async () => {
    server.use(
      http.post('http://localhost:8000/api/sim/enable', () =>
        HttpResponse.json({ error: 'Failed' }, { status: 500 })
      )
    );

    render(<ScenarioCard scenario={basicScenario} onEnable={() => {}} />);
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);

    await waitFor(() => {
      expect(screen.getByText(/Failed to enable scenario/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid input', async () => {
    render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);

    // Leave required field empty and click enable
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);

    // Should show validation error (Zod error message for missing required field)
    await waitFor(() => {
      const errorDiv = screen.getByText(/required|invalid|expected/i);
      expect(errorDiv).toBeInTheDocument();
    });
  });

  it('disables button while loading', async () => {
    render(<ScenarioCard scenario={basicScenario} onEnable={() => {}} />);
    const enableBtn = screen.getByRole('button', { name: /enable/i });

    fireEvent.click(enableBtn);

    // Button should show "Enabling..." and be disabled
    await waitFor(() => {
      const loadingBtn = screen.getByRole('button', { name: /enabling/i });
      expect(loadingBtn).toBeDisabled();
    });
  });

  it('clears parameters after successful enable', async () => {
    const { container } = render(<ScenarioCard scenario={scenarioWithParams} onEnable={() => {}} />);

    // Fill in a parameter
    const inputs = container.querySelectorAll('input[type="number"]');
    const probabilityInput = inputs[0] as HTMLInputElement;
    fireEvent.change(probabilityInput, { target: { value: '0.8' } });
    expect(probabilityInput.value).toBe('0.8');

    // Enable scenario
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);

    // Parameters should be cleared
    await waitFor(() => {
      expect(probabilityInput.value).toBe('');
    });
  });

  it('renders correctly without parameters', () => {
    render(<ScenarioCard scenario={basicScenario} onEnable={() => {}} />);
    expect(screen.queryByText('Parameters')).not.toBeInTheDocument();
  });
});
