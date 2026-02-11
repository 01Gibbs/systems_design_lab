import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SimulatorControlPanel from '../../pages/SimulatorControlPanel';

describe('SimulatorControlPanel', () => {
  it('renders loading state', () => {
    render(<SimulatorControlPanel onStatusChange={() => {}} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
