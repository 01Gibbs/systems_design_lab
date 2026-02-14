import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { act } from 'react';
import { vi } from 'vitest';
import App from '../App';

// Mock child components to isolate App.tsx testing
vi.mock('../components/GlobalBanner', () => ({
  default: ({ activeCount }: { activeCount: number }) => (
    <div data-testid="global-banner">Active: {activeCount}</div>
  ),
}));

vi.mock('../pages/SimulatorControlPanel', () => ({
  default: ({ onStatusChange }: { onStatusChange: (count: number) => void }) => (
    <div data-testid="simulator-panel">
      <button onClick={() => onStatusChange(3)}>Set Active</button>
    </div>
  ),
}));

describe('App', () => {
  it('renders without crashing', () => {
    const { getByTestId } = render(<App />);
    expect(getByTestId('global-banner')).toBeInTheDocument();
    expect(getByTestId('simulator-panel')).toBeInTheDocument();
  });

  it('passes activeCount state to GlobalBanner', () => {
    const { getByTestId } = render(<App />);
    const banner = getByTestId('global-banner');
    expect(banner).toHaveTextContent('Active: 0');
  });

  it('updates activeCount when SimulatorControlPanel changes status', () => {
    const { getByText, getByTestId } = render(<App />);
    const setActiveButton = getByText('Set Active');

    // Initially activeCount should be 0
    expect(getByTestId('global-banner')).toHaveTextContent('Active: 0');

    // Click button to trigger onStatusChange
    act(() => {
      setActiveButton.click();
    });

    // activeCount should now be 3
    expect(getByTestId('global-banner')).toHaveTextContent('Active: 3');
  });

  it('applies correct CSS classes for layout', () => {
    const { container } = render(<App />);
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv).toHaveClass('min-h-screen', 'bg-gray-50', 'dark:bg-gray-900');
  });
});
