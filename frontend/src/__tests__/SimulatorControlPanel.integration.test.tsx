import { render, screen } from '@testing-library/react';
import SimulatorControlPanel from '../pages/SimulatorControlPanel';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('http://localhost:8000/api/sim/scenarios', (req, res, ctx) => {
    return res(ctx.json({ scenarios: [{ name: 'fixed_latency', description: 'Injects latency', parameter_schema: {}, safety_limits: {}, targets: ['http'] }] }));
  }),
  rest.get('http://localhost:8000/api/sim/status', (req, res, ctx) => {
    return res(ctx.json({ active: [] }));
  })
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
