import { describe, expect, it } from 'vitest';
import { generateMarkdownReport } from '../src/report';

describe('experiment report generation', () => {
  it('renders a reusable Markdown experiment report from current parameters', () => {
    const markdown = generateMarkdownReport({
      energy: 0.5,
      barrierHeight: 1,
      barrierWidth: 1,
      mass: 1,
    });

    expect(markdown).toContain('# 量子隧穿虚拟仿真实验报告');
    expect(markdown).toContain('## 三、实验参数');
    expect(markdown).toContain('透射率 T');
    expect(markdown).toContain('经典力学预测');
    expect(markdown).not.toContain('沈阳大学');
  });
});
