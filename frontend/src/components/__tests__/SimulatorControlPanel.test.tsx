import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SimulatorControlPanel from '../../pages/SimulatorControlPanel';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('http://localhost:8000/api/sim/scenarios', () => 
    HttpResponse.json({ scenarios: [{ name: 'test', description: 'Test', parameter_schema: {}, safety_limits: {}, targets: ['http'] }] })
  ),
  http.get('http://localhost:8000/api/sim/status', () => 
    HttpResponse.json({ active: [] })
  )
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('SimulatorControlPanel', () => {
  it('renders loading state initially', () => {
    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders scenarios after loading', async () => {
    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });
  });

  it('shows error state on API failure', async () => {
    server.use(
      http.get('http://localhost:8000/api/sim/scenarios', () => 
        HttpResponse.json({ error: 'Failed' }, {status: 500 })
      )
    );

    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('calls onStatusChange with active scenario count', async () => {
    const onStatusChange = vi.fn();
    
    server.use(
      http.get('http://localhost:8000/api/sim/status', () => 
        HttpResponse.json({ active: [{ name: 'scenario1', enabled: true, probability: 1.0, until: Date.now() + 100000 }] })
      )
    );

    render(<SimulatorControlPanel onStatusChange={onStatusChange} />);
    
    await waitFor(() => {
      expect(onStatusChange).toHaveBeenCalledWith(1);
    });
  });

  it('retry button reloads data on error', async () => {
    let attempts = 0;
    server.use(
      http.get('http://localhost:8000/api/sim/scenarios', () => {
        attempts++;
        if (attempts === 1) {
          return HttpResponse.json({ error: 'Failed' }, { status: 500 });
        }
        return HttpResponse.json({ scenarios: [] });
      })
    );

    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });

    const retryButton = screen.getByRole('button', { name: /retry/i });
    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });
  });
});
