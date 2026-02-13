import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActiveScenarios from '../ActiveScenarios';

describe('ActiveScenarios', () => {
  const mockOnDisable = vi.fn();
  const mockOnResetAll = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const scenarios = [
    {
      name: 'fixed_latency',
      parameters: { delay_ms: 100 },
      enabled_at: new Date('2024-01-01T12:00:00Z').toISOString(),
      expires_at: null,
    },
  ];

  const scenariosWithExpiry = [
    {
      name: 'error_burst', 
      parameters: { probability: 0.5, duration: 30 },
      enabled_at: new Date('2024-01-01T12:00:00Z').toISOString(),
      expires_at: new Date('2024-01-01T13:00:00Z').toISOString(),
    },
  ];

  it('renders nothing when no scenarios', () => {
    const { container } = render(
      <ActiveScenarios scenarios={[]} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders active scenario names', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    expect(screen.getAllByText('fixed_latency')[0]).toBeInTheDocument();
  });

  it('displays scenario count in header', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    expect(screen.getByText('🔴 Active Scenarios (1)')).toBeInTheDocument();
  });

  it('renders Reset All button and calls onResetAll when clicked', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    const resetButton = screen.getByText('Reset All');
    expect(resetButton).toBeInTheDocument();
    
    fireEvent.click(resetButton);
    expect(mockOnResetAll).toHaveBeenCalledTimes(1);
  });

  it('renders disable button for each scenario and calls onDisable when clicked', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    const disableButton = screen.getByLabelText('Disable fixed_latency');
    expect(disableButton).toBeInTheDocument();
    
    fireEvent.click(disableButton);
    expect(mockOnDisable).toHaveBeenCalledWith('fixed_latency');
    expect(mockOnDisable).toHaveBeenCalledTimes(1);
  });

  it('displays enabled_at timestamp', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    // Should display formatted date (exact format depends on locale)
    expect(screen.getByText(text => text.includes('Enabled:'))).toBeInTheDocument();
  });

  it('displays expires_at timestamp when present', () => {
    render(<ActiveScenarios scenarios={scenariosWithExpiry} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    const timeInfo = screen.getByText(text => text.includes('Expires:'));
    expect(timeInfo).toBeInTheDocument();
  });

  it('calls toLocaleString function on expires_at dates properly', () => {
    const mockDateSpy = vi.spyOn(Date.prototype, 'toLocaleString');
    
    render(<ActiveScenarios scenarios={scenariosWithExpiry} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    // Should be called for both enabled_at and expires_at
    expect(mockDateSpy).toHaveBeenCalledTimes(2);
    
    mockDateSpy.mockRestore();
  });

  it('handles null expires_at without calling date functions', () => {
    const mockDateSpy = vi.spyOn(Date.prototype, 'toLocaleString');
    
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    // Should only be called once for enabled_at, not for expires_at since it's null
    expect(mockDateSpy).toHaveBeenCalledTimes(1);
    
    mockDateSpy.mockRestore();
  });

  it('properly renders JSX fragment for expires information', () => {
    // This specifically targets the JSX fragment function on line 43
    const { container } = render(
      <ActiveScenarios scenarios={scenariosWithExpiry} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />
    );
    
    // Check that the fragment content is rendered as expected
    const expiresText = container.querySelector('.text-sm');
    expect(expiresText?.textContent).toContain('Expires:');
    expect(expiresText?.textContent).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}.*Expires:.*\d{1,2}\/\d{1,2}\/\d{4}/);
  });

  it('does not display expires info when expires_at is null', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    expect(screen.queryByText(text => text.includes('Expires:'))).not.toBeInTheDocument();
  });

  it('displays parameters as formatted JSON', () => {
    render(<ActiveScenarios scenarios={scenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    // Should display formatted JSON parameters
    expect(screen.getByText(text => text.includes('"delay_ms": 100'))).toBeInTheDocument();
  });

  it('handles multiple scenarios correctly', () => {
    const multipleScenarios = [
      ...scenarios,
      {
        name: 'slow_db_query',
        parameters: { query_delay: 200 },
        enabled_at: new Date('2024-01-01T11:00:00Z').toISOString(),
        expires_at: new Date('2024-01-01T14:00:00Z').toISOString(),
      },
    ];
    
    render(<ActiveScenarios scenarios={multipleScenarios} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    expect(screen.getByText('🔴 Active Scenarios (2)')).toBeInTheDocument();
    expect(screen.getByText('fixed_latency')).toBeInTheDocument();
    expect(screen.getByText('slow_db_query')).toBeInTheDocument();
  });

  it('correctly handles complex parameter objects', () => {
    const complexScenario = [{
      name: 'complex_scenario',
      parameters: {
        nested: { value: 42 },
        array: [1, 2, 3],
        boolean: true,
      },
      enabled_at: new Date().toISOString(),
      expires_at: null,
    }];
    
    render(<ActiveScenarios scenarios={complexScenario} onDisable={mockOnDisable} onResetAll={mockOnResetAll} />);
    
    // Check that JSON.stringify with formatting is used
    const preElement = screen.getByText(text => 
      text.includes('"nested"') && 
      text.includes('"array"') &&
      text.includes('"boolean": true')
    );
    expect(preElement).toBeInTheDocument();
  });
});
