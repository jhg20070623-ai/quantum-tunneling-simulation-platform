import { describe, expect, it } from 'vitest';
import {
  calculateExperiment,
  exportScanCsv,
  generateScan,
  nearBarrierLimitTransmission,
  type ExperimentParams,
} from '../src/physics';

describe('quantum tunneling physics model', () => {
  it('calculates the reference tunneling case from the design report', () => {
    const result = calculateExperiment({ energy: 0.5, barrierHeight: 1, barrierWidth: 1, mass: 1 });

    expect(result.region).toBe('隧穿区');
    expect(result.transmission).toBeCloseTo(0.41997, 4);
    expect(result.reflection).toBeCloseTo(0.58003, 4);
    expect(result.classicalTransmission).toBe(0);
  });

  it('preserves probability for representative parameters', () => {
    const cases: ExperimentParams[] = [
      { energy: 0.3, barrierHeight: 1.5, barrierWidth: 3, mass: 1 },
      { energy: 0.95, barrierHeight: 1, barrierWidth: 2, mass: 1 },
      { energy: 1.5, barrierHeight: 1, barrierWidth: 2, mass: 1 },
    ];

    for (const params of cases) {
      const result = calculateExperiment(params);
      expect(result.transmission).toBeGreaterThanOrEqual(0);
      expect(result.transmission).toBeLessThanOrEqual(1);
      expect(result.transmission + result.reflection).toBeCloseTo(1, 8);
    }
  });

  it('uses the finite E=V0 limit at the barrier top', () => {
    const result = calculateExperiment({ energy: 1, barrierHeight: 1, barrierWidth: 2, mass: 1 });
    const expected = nearBarrierLimitTransmission({ energy: 1, barrierHeight: 1, barrierWidth: 2, mass: 1 });

    expect(result.region).toBe('近垒顶区');
    expect(result.transmission).toBeCloseTo(expected, 10);
    expect(result.transmission).toBeCloseTo(1 / 3, 10);
  });

  it('generates bounded scan data with the requested number of points', () => {
    const scan = generateScan('energy', { energy: 0.5, barrierHeight: 1, barrierWidth: 1, mass: 1 }, 12);

    expect(scan).toHaveLength(12);
    expect(scan[0].parameter).toBeGreaterThan(0);
    expect(scan.every((point) => point.transmission >= 0 && point.transmission <= 1)).toBe(true);
  });

  it('exports scan data as CSV with Chinese headers', () => {
    const csv = exportScanCsv([
      { parameter: 0.5, transmission: 0.4261, reflection: 0.5739, region: '隧穿区' },
    ]);

    expect(csv).toContain('参数值,透射率T,反射率R,物理区域');
    expect(csv).toContain('0.5000,0.426100,0.573900,隧穿区');
  });
});
