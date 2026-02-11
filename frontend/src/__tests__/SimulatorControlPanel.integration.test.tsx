import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SimulatorControlPanel from '../pages/SimulatorControlPanel';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get(
    'http://localhost:8000/api/sim/scenarios',
    () =>
      HttpResponse.json({
        scenarios: [
          {
            name: 'fixed_latency',
            description: 'Injects latency',
            parameter_schema: {},
            safety_limits: {},
            targets: ['http'] as ('http' | 'db' | 'cpu' | 'algorithm')[],
          },
        ],
      })
  ),
  http.get(
    'http://localhost:8000/api/sim/status',
    () => HttpResponse.json({ active: [] })
  )
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('SimulatorControlPanel integration', () => {
  it('renders scenario from mocked API', async () => {
    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    expect(await screen.findByText('fixed_latency')).toBeInTheDocument();
  });
});
