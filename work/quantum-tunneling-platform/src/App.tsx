import { useMemo, useState } from 'react';
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  BookOpen,
  ClipboardList,
  Download,
  FileText,
  Gauge,
  PlayCircle,
  SlidersHorizontal,
} from 'lucide-react';
import {
  calculateExperiment,
  downloadText,
  exportScanCsv,
  generateScan,
  generateWaveData,
  percent,
  type ExperimentParams,
  type ScanMode,
} from './physics';
import { generateMarkdownReport } from './report';

type Tab = 'lab' | 'scan' | 'report' | 'guide';

const initialParams: ExperimentParams = {
  energy: 0.5,
  barrierHeight: 1,
  barrierWidth: 1,
  mass: 1,
};

const presets: Array<{ name: string; params: ExperimentParams; note: string }> = [
  { name: '明显隧穿', params: { energy: 0.5, barrierHeight: 1, barrierWidth: 1, mass: 1 }, note: 'E < V0，透射非零' },
  { name: '弱隧穿', params: { energy: 0.3, barrierHeight: 1.5, barrierWidth: 3, mass: 1 }, note: '厚势垒抑制透射' },
  { name: '近垒顶', params: { energy: 0.95, barrierHeight: 1, barrierWidth: 2, mass: 1 }, note: '参数变化敏感' },
  { name: '越垒传播', params: { energy: 1.5, barrierHeight: 1, barrierWidth: 2, mass: 1 }, note: '越垒仍有反射' },
  { name: '宽垒隧穿', params: { energy: 0.6, barrierHeight: 1.2, barrierWidth: 5, mass: 2 }, note: '趋近经典极限' },
  { name: '共振附近', params: { energy: 2.2, barrierHeight: 1, barrierWidth: 2.2, mass: 1 }, note: '观察透射峰' },
];

const scanLabels: Record<ScanMode, string> = {
  energy: 'T-E 扫描',
  width: 'T-a 扫描',
  height: 'T-V0 扫描',
};

const formatChartValue = (value: unknown) => (typeof value === 'number' ? value.toFixed(4) : String(value ?? ''));

function NumberControl({
  id,
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  id: keyof ExperimentParams;
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (key: keyof ExperimentParams, value: number) => void;
}) {
  return (
    <label className="control" htmlFor={id}>
      <span>
        {label}
        <strong>{value.toFixed(2)}</strong>
      </span>
      <input
        id={id}
        aria-label={label}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(id, Number(event.target.value))}
      />
      <input
        className="number-input"
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(id, Number(event.target.value))}
      />
    </label>
  );
}

export default function App() {
  const [tab, setTab] = useState<Tab>('lab');
  const [params, setParams] = useState<ExperimentParams>(initialParams);
  const [scanMode, setScanMode] = useState<ScanMode>('energy');

  const result = useMemo(() => calculateExperiment(params), [params]);
  const waveData = useMemo(() => generateWaveData(params), [params]);
  const scanData = useMemo(() => generateScan(scanMode, params, 100), [scanMode, params]);
  const markdown = useMemo(() => generateMarkdownReport(params), [params]);

  const updateParam = (key: keyof ExperimentParams, value: number) => {
    setParams((current) => ({ ...current, [key]: value }));
  };

  const tabs: Array<{ id: Tab; label: string; icon: React.ReactNode }> = [
    { id: 'lab', label: '虚拟实验', icon: <PlayCircle size={18} /> },
    { id: 'scan', label: '参数扫描', icon: <Gauge size={18} /> },
    { id: 'report', label: '实验报告', icon: <FileText size={18} /> },
    { id: 'guide', label: '教学说明', icon: <BookOpen size={18} /> },
  ];

  return (
    <main className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">QT</span>
          <div>
            <h1>量子隧穿虚拟仿真实验平台</h1>
            <p>自选题2 · 教学资源和虚仿</p>
          </div>
        </div>

        <nav className="tabs" aria-label="功能视图">
          {tabs.map((item) => (
            <button key={item.id} className={tab === item.id ? 'active' : ''} onClick={() => setTab(item.id)}>
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>

        <section className="panel controls">
          <h2>
            <SlidersHorizontal size={18} /> 参数控制
          </h2>
          <NumberControl id="energy" label="粒子能量 E" value={params.energy} min={0.1} max={3} step={0.01} onChange={updateParam} />
          <NumberControl id="barrierHeight" label="势垒高度 V0" value={params.barrierHeight} min={0.1} max={3} step={0.01} onChange={updateParam} />
          <NumberControl id="barrierWidth" label="势垒宽度 a" value={params.barrierWidth} min={0.1} max={6} step={0.01} onChange={updateParam} />
          <NumberControl id="mass" label="粒子质量 m" value={params.mass} min={0.2} max={5} step={0.01} onChange={updateParam} />
        </section>

        <section className="panel presets">
          <h2>
            <ClipboardList size={18} /> 预设场景
          </h2>
          {presets.map((preset) => (
            <button key={preset.name} onClick={() => setParams(preset.params)}>
              <span>{preset.name}</span>
              <small>{preset.note}</small>
            </button>
          ))}
        </section>
      </aside>

      <section className="workspace">
        <header className="summary-grid">
          <div className="metric">
            <span>物理区域</span>
            <strong>{result.region}</strong>
          </div>
          <div className="metric">
            <span>透射率 T</span>
            <strong>{percent(result.transmission)}</strong>
          </div>
          <div className="metric">
            <span>反射率 R</span>
            <strong>{percent(result.reflection)}</strong>
          </div>
          <div className="metric">
            <span>概率守恒校验</span>
            <strong>{result.conservationError < 1e-6 ? '通过' : '需检查'}</strong>
          </div>
        </header>

        {tab === 'lab' && (
          <div className="content-grid">
            <section className="panel chart-panel">
              <div className="section-title">
                <h2>势垒、能量线与相对概率密度</h2>
                <p>|psi(x)|^2 为入射振幅归一化后的相对概率密度。</p>
              </div>
              <ResponsiveContainer width="100%" height={390}>
                <ComposedChart data={waveData} margin={{ top: 20, right: 24, bottom: 12, left: 0 }}>
                  <CartesianGrid stroke="#dde5ea" strokeDasharray="4 4" />
                  <XAxis dataKey="x" label={{ value: 'x', position: 'insideBottomRight', offset: -4 }} />
                  <YAxis />
                  <Tooltip formatter={formatChartValue} />
                  <Legend />
                  <Area type="stepAfter" dataKey="potential" name="V(x)" stroke="#d04f4f" fill="#f3b6a6" fillOpacity={0.36} />
                  <Line type="monotone" dataKey="energy" name="E" stroke="#8067b7" strokeDasharray="8 6" dot={false} />
                  <Line type="monotone" dataKey="probabilityDensity" name="|psi(x)|²" stroke="#0e9f9a" strokeWidth={2.5} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </section>

            <section className="panel comparison">
              <h2>经典 / 量子对比</h2>
              <div className="compare-row">
                <div>
                  <span>经典力学</span>
                  <strong>T = {percent(result.classicalTransmission)}</strong>
                  <p>{result.classicalTransmission === 0 ? '能量不足，不能越过势垒。' : '能量足够，预测完全透射。'}</p>
                </div>
                <div>
                  <span>量子力学</span>
                  <strong>T = {percent(result.transmission)}</strong>
                  <p>{result.energy < result.barrierHeight ? '波函数指数衰减后仍有非零透射。' : '边界干涉导致越垒区仍可出现反射。'}</p>
                </div>
              </div>
              <table>
                <tbody>
                  <tr><th>E / V0</th><td>{(result.energy / result.barrierHeight).toFixed(3)}</td></tr>
                  <tr><th>kappa</th><td>{result.kappa ? result.kappa.toFixed(4) : '不适用'}</td></tr>
                  <tr><th>k2</th><td>{result.k2 ? result.k2.toFixed(4) : '不适用'}</td></tr>
                  <tr><th>|T + R - 1|</th><td>{result.conservationError.toExponential(2)}</td></tr>
                </tbody>
              </table>
            </section>
          </div>
        )}

        {tab === 'scan' && (
          <section className="panel chart-panel">
            <div className="section-title actions">
              <div>
                <h2>{scanLabels[scanMode]}</h2>
                <p>每次扫描默认 100 个数据点，可导出 CSV 用于实验报告。</p>
              </div>
              <div className="segmented">
                {(['energy', 'width', 'height'] as ScanMode[]).map((mode) => (
                  <button key={mode} className={scanMode === mode ? 'active' : ''} onClick={() => setScanMode(mode)}>
                    {scanLabels[mode]}
                  </button>
                ))}
              </div>
              <button className="primary" onClick={() => downloadText(`scan-${scanMode}.csv`, exportScanCsv(scanData), 'text/csv;charset=utf-8')}>
                <Download size={17} /> 导出 CSV
              </button>
            </div>
            <ResponsiveContainer width="100%" height={430}>
              <LineChart data={scanData} margin={{ top: 20, right: 24, bottom: 12, left: 0 }}>
                <CartesianGrid stroke="#dde5ea" strokeDasharray="4 4" />
                <XAxis dataKey="parameter" />
                <YAxis domain={[0, 1]} />
                <Tooltip formatter={(value: unknown) => (typeof value === 'number' ? percent(value) : String(value ?? ''))} />
                <Legend />
                <Line type="monotone" dataKey="transmission" name="透射率 T" stroke="#0e9f9a" strokeWidth={2.6} dot={false} />
                <Line type="monotone" dataKey="reflection" name="反射率 R" stroke="#d04f4f" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </section>
        )}

        {tab === 'report' && (
          <section className="panel report-panel">
            <div className="section-title actions">
              <div>
                <h2>实验报告自动生成</h2>
                <p>根据当前参数、计算结果和物理解释生成 Markdown 报告。</p>
              </div>
              <button className="primary" onClick={() => downloadText('量子隧穿虚拟实验报告.md', markdown)}>
                <Download size={17} /> 下载报告
              </button>
            </div>
            <pre>{markdown}</pre>
          </section>
        )}

        {tab === 'guide' && (
          <section className="panel guide">
            <h2>教学说明</h2>
            <ol>
              <li><strong>设置参数：</strong>先判断 E 与 V0 的大小关系，提出对透射率的预测。</li>
              <li><strong>观察图像：</strong>比较势垒区内 |psi(x)|² 的衰减或振荡行为。</li>
              <li><strong>扫描曲线：</strong>分别观察 T-E、T-a、T-V0 曲线，总结参数规律。</li>
              <li><strong>生成报告：</strong>记录当前参数、透射率、反射率和经典/量子对比。</li>
            </ol>
            <div className="note">
              教学重点：不是把隧穿理解成“粒子挖洞穿墙”，而是理解波函数边界连续、概率流守恒和经典禁戒区中的指数衰减。
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
