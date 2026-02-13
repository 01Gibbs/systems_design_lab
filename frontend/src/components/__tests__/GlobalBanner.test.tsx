import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import GlobalBanner from '../GlobalBanner';

describe('GlobalBanner', () => {
  it('renders nothing when activeCount is 0', () => {
    const { container } = render(<GlobalBanner activeCount={0} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders banner when activeCount is 1', () => {
    const { getByText } = render(<GlobalBanner activeCount={1} />);
    const banner = getByText(/1 Active Scenario Running/i);
    expect(banner).toBeInTheDocument();
  });

  it('uses singular form for activeCount = 1', () => {
    const { getByText } = render(<GlobalBanner activeCount={1} />);
    expect(getByText('🔴 1 Active Scenario Running')).toBeInTheDocument();
  });

  it('uses plural form for activeCount > 1', () => {
    const { getByText } = render(<GlobalBanner activeCount={3} />);
    expect(getByText('🔴 3 Active Scenarios Running')).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { getByText } = render(<GlobalBanner activeCount={1} />);
    const banner = getByText(/Active Scenario/);
    expect(banner).toHaveClass(
      'bg-red-500',
      'dark:bg-red-600',
      'text-white',
      'py-2',
      'px-4',
      'text-center',
      'font-medium'
    );
  });

  it('handles large activeCount numbers', () => {
    const { getByText } = render(<GlobalBanner activeCount={99} />);
    expect(getByText('🔴 99 Active Scenarios Running')).toBeInTheDocument();
  });
});
