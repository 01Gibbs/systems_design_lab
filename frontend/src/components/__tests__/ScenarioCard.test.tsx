import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScenarioCard from '../ScenarioCard';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.post('http://localhost:8000/api/sim/enable', () =>
    HttpResponse.json({ success: true })
  )
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ScenarioCard', () => {
  const scenario = {
    name: 'fixed_latency',
    description: 'Injects latency',
    parameter_schema: {},
    safety_limits: {},
    targets: ['http'] as ('http' | 'db' | 'cpu' | 'algorithm')[],
  };

  it('renders scenario name and description', () => {
    render(<ScenarioCard scenario={scenario} onEnable={() => {}} />);
    expect(screen.getByText('fixed_latency')).toBeInTheDocument();
    expect(screen.getByText('Injects latency')).toBeInTheDocument();
  });

  it('calls onEnable when enable button is clicked', async () => {
    const onEnable = vi.fn();
    render(<ScenarioCard scenario={scenario} onEnable={onEnable} />);
    const enableBtn = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableBtn);
    await waitFor(() => {
      expect(onEnable).toHaveBeenCalled();
    });
  });
});
