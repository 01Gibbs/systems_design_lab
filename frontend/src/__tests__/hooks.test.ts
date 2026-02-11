import { renderHook, act } from '@testing-library/react-hooks';
import { useState } from 'react';

describe('custom hook: useState', () => {
  it('increments value', () => {
    const { result } = renderHook(() => useState(0));
    act(() => {
      result.current[1](1);
    });
    expect(result.current[0]).toBe(1);
  });
});
