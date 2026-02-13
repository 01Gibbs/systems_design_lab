import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SimulatorControlPanel from '../../pages/SimulatorControlPanel';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('http://localhost:8000/api/sim/scenarios', () =>
    HttpResponse.json({
      scenarios: [
        {
          name: 'test',
          description: 'Test',
          parameter_schema: {},
          safety_limits: {},
          targets: ['http'],
        },
      ],
    })
  ),
  http.get('http://localhost:8000/api/sim/status', () => HttpResponse.json({ active: [] }))
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
        HttpResponse.json({ error: 'Failed' }, { status: 500 })
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
        HttpResponse.json({
          active: [
            { name: 'scenario1', enabled: true, probability: 1.0, until: Date.now() + 100000 },
          ],
        })
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

  it('handles status API failure during initial load', async () => {
    server.use(
      http.get('http://localhost:8000/api/sim/status', () =>
        HttpResponse.json({ error: 'Status failed' }, { status: 500 })
      )
    );

    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText(/failed to load status/i)).toBeInTheDocument();
    });
  });

  it('calls handleResetAll and reloads data', async () => {
    const onStatusChange = vi.fn();
    let resetCalled = false;

    server.use(
      http.post('http://localhost:8000/api/sim/reset', () => {
        resetCalled = true;
        return HttpResponse.json({ success: true });
      })
    );

    render(<SimulatorControlPanel onStatusChange={onStatusChange} />);

    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });

    // Find and click reset all button via ActiveScenarios component
    const resetButton = screen.getByText('Reset All');
    fireEvent.click(resetButton);

    await waitFor(() => {
      expect(resetCalled).toBe(true);
    });
  });

  it('calls handleDisable and reloads data', async () => {
    const onStatusChange = vi.fn();
    let disableCalled = false;
    let disabledScenario = '';

    server.use(
      http.get('http://localhost:8000/api/sim/status', () =>
        HttpResponse.json({
          active: [
            {
              name: 'test_scenario',
              enabled_at: new Date().toISOString(),
              expires_at: null,
              parameters: {},
            },
          ],
        })
      ),
      http.post('http://localhost:8000/api/sim/disable', async ({ request }) => {
        disableCalled = true;
        const body = (await request.json()) as { name: string };
        disabledScenario = body.name;
        return HttpResponse.json({ success: true });
      })
    );

    render(<SimulatorControlPanel onStatusChange={onStatusChange} />);

    await waitFor(() => {
      expect(screen.getByText('🔴 Active Scenarios (1)')).toBeInTheDocument();
    });

    const disableButton = screen.getByLabelText('Disable test_scenario');
    fireEvent.click(disableButton);

    await waitFor(() => {
      expect(disableCalled).toBe(true);
      expect(disabledScenario).toBe('test_scenario');
    });
  });

  it('calls handleEnable when scenario is enabled', async () => {
    const onStatusChange = vi.fn();
    let enableCalled = false;

    server.use(
      http.post('http://localhost:8000/api/sim/enable', () => {
        enableCalled = true;
        return HttpResponse.json({ success: true });
      })
    );

    render(<SimulatorControlPanel onStatusChange={onStatusChange} />);

    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });

    const enableButton = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableButton);

    await waitFor(() => {
      expect(enableCalled).toBe(true);
    });
  });

  it('handles API failures in reset gracefully', async () => {
    server.use(
      http.post('http://localhost:8000/api/sim/reset', () =>
        HttpResponse.json({ error: 'Reset failed' }, { status: 500 })
      )
    );

    render(<SimulatorControlPanel onStatusChange={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });

    const resetButton = screen.getByText('Reset All');
    fireEvent.click(resetButton);

    // Should not crash or throw error
    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });
  });

  it('handles API failures in disable gracefully', async () => {
    server.use(
      http.get('http://localhost:8000/api/sim/status', () =>
        HttpResponse.json({
          active: [
            {
              name: 'test_scenario',
              enabled_at: new Date().toISOString(),
              expires_at: null,
              parameters: {},
            },
          ],
        })
      ),
      http.post('http://localhost:8000/api/sim/disable', () =>
        HttpResponse.json({ error: 'Disable failed' }, { status: 500 })
      )
    );

    render(<SimulatorControlPanel onStatusChange={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('🔴 Active Scenarios (1)')).toBeInTheDocument();
    });

    const disableButton = screen.getByLabelText('Disable test_scenario');
    fireEvent.click(disableButton);

    // Should not crash or throw error - just not reload data
    await waitFor(() => {
      expect(screen.getByText('🔴 Active Scenarios (1)')).toBeInTheDocument();
    });
  });

  it('tests handleEnable function directly via scenario card enable', async () => {
    const onStatusChange = vi.fn();
    server.use(
      http.post('http://localhost:8000/api/sim/enable', () => HttpResponse.json({ success: true }))
    );

    render(<SimulatorControlPanel onStatusChange={onStatusChange} />);

    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });

    const enableButton = screen.getByRole('button', { name: /enable/i });
    fireEvent.click(enableButton);

    // handleEnable should be called after successful enable
    await waitFor(() => {
      expect(onStatusChange).toHaveBeenCalled();
    });
  });

  it('handles status polling failures gracefully', async () => {
    vi.useFakeTimers();
    const onStatusChange = vi.fn();
    let pollCount = 0;

    server.use(
      http.get('http://localhost:8000/api/sim/status', () => {
        pollCount++;
        if (pollCount > 2) {
          return HttpResponse.json({ error: 'Poll failed' }, { status: 500 });
        }
        return HttpResponse.json({ active: [] });
      })
    );

    render(<SimulatorControlPanel onStatusChange={onStatusChange} />);

    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument();
    });

    // Fast forward to trigger polling
    vi.advanceTimersByTime(4000);

    // Should continue to work despite polling failures
    expect(onStatusChange).toHaveBeenCalled();

    vi.useRealTimers();
  });

  it('cleans up interval on unmount', () => {
    vi.useFakeTimers();
    const clearIntervalSpy = vi.spyOn(global, 'clearInterval');

    const { unmount } = render(<SimulatorControlPanel onStatusChange={() => {}} />);

    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();

    vi.useRealTimers();
    clearIntervalSpy.mockRestore();
  });
});
