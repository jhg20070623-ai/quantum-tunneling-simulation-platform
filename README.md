# Quantum Tunneling Simulation Platform

A web-based interactive simulation platform for exploring quantum tunneling behavior through configurable parameters and visual feedback.

## Overview

This project is educational simulation software with a React and TypeScript frontend. It provides an interactive way to vary a rectangular potential-barrier model, inspect calculated transmission and reflection values, and export an experiment report.

The implementation is intended for learning and software experimentation. It does not claim scientific research accuracy or replace a specialist physics package.

## Features

- Adjust particle energy, barrier height, barrier width, and mass.
- Compare the simplified classical and quantum transmission results.
- Visualize the potential barrier, energy level, and generated probability-density curve.
- Scan transmission/reflection behavior across energy, width, or height parameters.
- Export scan data as CSV.
- Generate a Markdown experiment report from the current parameters.
- Switch between the lab, scan, report, and teaching-guide views.

## Tech Stack

- React
- TypeScript
- Vite
- Vitest
- Recharts
- React Testing Library
- lucide-react

## Project Structure

```text
work/quantum-tunneling-platform/
├── src/
│   ├── App.tsx       # Application shell and interactive views
│   ├── physics.ts    # Barrier model, scans, CSV export, and helpers
│   ├── report.ts     # Markdown report generation
│   ├── main.tsx      # React entry point
│   └── styles.css    # UI styling
├── tests/
│   ├── App.test.tsx
│   ├── physics.test.ts
│   └── report.test.ts
├── package.json
├── vite.config.ts
└── vitest.config.ts
```

## Getting Started

```bash
cd work/quantum-tunneling-platform
npm install
npm run dev
```

The development server is configured to bind to `127.0.0.1`.

## Build and Testing

```bash
npm run build
npm test
```

The test suite covers the physics calculations, probability conservation for representative inputs, scan generation, CSV/report output, and the main application shell. Coverage percentages are intentionally not reported here.

## Engineering Notes

- TypeScript keeps the UI, model parameters, and calculated results explicit.
- The physics model is separated from React rendering in `src/physics.ts`.
- Report generation is separated from the UI in `src/report.ts`.
- Vitest and Testing Library provide repeatable local validation.
- The app uses a simplified one-dimensional rectangular-barrier model with normalized constants for interactive teaching.

## Limitations

- The visual wave-density curve is an explanatory visualization, not a high-fidelity numerical solver.
- The model uses normalized units and simplified assumptions.
- The current project is a local educational web app; it has no hosted deployment or backend service.
- UI copy in the application is still being refined separately from this English project documentation.

## Additional Materials

Legacy design reports, presentation assets, and other submission materials are kept under `docs/archive/`. They are not required to run the application; the source and tests under `work/quantum-tunneling-platform/` are the primary engineering artifacts.
