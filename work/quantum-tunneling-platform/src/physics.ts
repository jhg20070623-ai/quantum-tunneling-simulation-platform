export type ExperimentParams = {
  energy: number;
  barrierHeight: number;
  barrierWidth: number;
  mass: number;
};

export type Region = '深隧穿区' | '隧穿区' | '近垒顶区' | '越垒区';

export type ExperimentResult = ExperimentParams & {
  transmission: number;
  reflection: number;
  classicalTransmission: number;
  classicalReflection: number;
  region: Region;
  kappa?: number;
  k2?: number;
  conservationError: number;
};

export type WavePoint = {
  x: number;
  potential: number;
  energy: number;
  probabilityDensity: number;
  barrierTop?: number;
};

export type ScanMode = 'energy' | 'width' | 'height';

export type ScanPoint = {
  parameter: number;
  transmission: number;
  reflection: number;
  region: Region;
};

const HBAR = 1;
const EPSILON = 1e-8;

const clamp01 = (value: number) => Math.min(1, Math.max(0, value));

export function nearBarrierLimitTransmission(params: ExperimentParams): number {
  const { barrierHeight, barrierWidth, mass } = params;
  return 1 / (1 + (mass * barrierHeight * barrierWidth ** 2) / (2 * HBAR ** 2));
}

export function calculateExperiment(params: ExperimentParams): ExperimentResult {
  const energy = Math.max(params.energy, EPSILON);
  const barrierHeight = Math.max(params.barrierHeight, EPSILON);
  const barrierWidth = Math.max(params.barrierWidth, EPSILON);
  const mass = Math.max(params.mass, EPSILON);
  const normalized = { energy, barrierHeight, barrierWidth, mass };
  const delta = energy - barrierHeight;
  let transmission: number;
  let kappa: number | undefined;
  let k2: number | undefined;

  if (Math.abs(delta) < 1e-6) {
    transmission = nearBarrierLimitTransmission(normalized);
  } else if (energy < barrierHeight) {
    kappa = Math.sqrt((2 * mass * (barrierHeight - energy)) / HBAR ** 2);
    const denominator =
      1 +
      (barrierHeight ** 2 * Math.sinh(kappa * barrierWidth) ** 2) /
        (4 * energy * (barrierHeight - energy));
    transmission = 1 / denominator;
  } else {
    k2 = Math.sqrt((2 * mass * (energy - barrierHeight)) / HBAR ** 2);
    const denominator =
      1 +
      (barrierHeight ** 2 * Math.sin(k2 * barrierWidth) ** 2) /
        (4 * energy * (energy - barrierHeight));
    transmission = 1 / denominator;
  }

  transmission = clamp01(transmission);
  const reflection = clamp01(1 - transmission);
  return {
    ...normalized,
    transmission,
    reflection,
    classicalTransmission: energy >= barrierHeight ? 1 : 0,
    classicalReflection: energy >= barrierHeight ? 0 : 1,
    region: classifyRegion(normalized),
    kappa,
    k2,
    conservationError: Math.abs(transmission + reflection - 1),
  };
}

export function classifyRegion(params: ExperimentParams): Region {
  const ratio = params.energy / params.barrierHeight;
  if (Math.abs(ratio - 1) <= 0.06) return '近垒顶区';
  if (ratio > 1) return '越垒区';
  if (ratio < 0.45 || params.barrierWidth >= 3) return '深隧穿区';
  return '隧穿区';
}

export function generateWaveData(params: ExperimentParams, points = 181): WavePoint[] {
  const result = calculateExperiment(params);
  const left = -3;
  const right = Math.max(5, result.barrierWidth + 3);
  const span = right - left;
  const incomingK = Math.sqrt(2 * result.mass * result.energy) / HBAR;
  const decay = result.kappa ?? Math.sqrt(Math.max(0.001, 2 * result.mass * Math.abs(result.barrierHeight - result.energy)));
  const output: WavePoint[] = [];

  for (let i = 0; i < points; i += 1) {
    const x = left + (span * i) / (points - 1);
    const inBarrier = x >= 0 && x <= result.barrierWidth;
    const potential = inBarrier ? result.barrierHeight : 0;
    let probabilityDensity: number;

    if (x < 0) {
      const standing = 1 + Math.sqrt(result.reflection) * Math.cos(2 * incomingK * x);
      probabilityDensity = Math.max(0.02, standing ** 2 / 2.8);
    } else if (inBarrier && result.energy < result.barrierHeight) {
      probabilityDensity = Math.max(result.transmission, Math.exp(-2 * decay * x));
    } else if (inBarrier) {
      probabilityDensity = Math.max(
        result.transmission,
        0.45 + 0.25 * Math.cos((2 * Math.PI * x) / Math.max(result.barrierWidth, 0.2)),
      );
    } else {
      probabilityDensity = Math.max(0.01, result.transmission);
    }

    output.push({
      x: Number(x.toFixed(3)),
      potential,
      energy: result.energy,
      probabilityDensity: Number(probabilityDensity.toFixed(6)),
      barrierTop: result.barrierHeight,
    });
  }

  return output;
}

export function generateScan(mode: ScanMode, base: ExperimentParams, count = 100): ScanPoint[] {
  const ranges: Record<ScanMode, [number, number]> = {
    energy: [0.1, 3],
    width: [0.1, 6],
    height: [0.1, 3],
  };
  const [min, max] = ranges[mode];
  return Array.from({ length: count }, (_, index) => {
    const parameter = count === 1 ? min : min + ((max - min) * index) / (count - 1);
    const params = { ...base };
    if (mode === 'energy') params.energy = parameter;
    if (mode === 'width') params.barrierWidth = parameter;
    if (mode === 'height') params.barrierHeight = parameter;
    const result = calculateExperiment(params);
    return {
      parameter: Number(parameter.toFixed(4)),
      transmission: result.transmission,
      reflection: result.reflection,
      region: result.region,
    };
  });
}

export function exportScanCsv(points: ScanPoint[]): string {
  const rows = points.map((point) =>
    [
      point.parameter.toFixed(4),
      point.transmission.toFixed(6),
      point.reflection.toFixed(6),
      point.region,
    ].join(','),
  );
  return ['参数值,透射率T,反射率R,物理区域', ...rows].join('\n');
}

export const percent = (value: number) => `${(value * 100).toFixed(value < 0.01 ? 3 : 2)}%`;

export function downloadText(filename: string, text: string, mime = 'text/plain;charset=utf-8') {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
