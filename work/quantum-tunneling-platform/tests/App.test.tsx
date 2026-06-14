import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from '../src/App';

describe('App', () => {
  it('renders the virtual lab shell and core controls', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /量子隧穿虚拟仿真实验平台/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '虚拟实验' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '参数扫描' })).toBeInTheDocument();
    expect(screen.getByLabelText('粒子能量 E')).toBeInTheDocument();
    expect(screen.getByText(/概率守恒校验/)).toBeInTheDocument();
  });
});
