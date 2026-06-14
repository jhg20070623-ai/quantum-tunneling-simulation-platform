import { calculateExperiment, percent, type ExperimentParams } from './physics';

export function generateMarkdownReport(params: ExperimentParams): string {
  const result = calculateExperiment(params);
  const classical =
    result.classicalTransmission === 0
      ? '经典力学预测：粒子能量低于势垒高度，不能越过势垒，透射率为 0。'
      : '经典力学预测：粒子能量高于势垒高度，应完全透射。';

  return `# 量子隧穿虚拟仿真实验报告

## 一、实验目的

通过一维方势垒模型观察量子隧穿现象，理解粒子能量、势垒高度、势垒宽度和粒子质量对透射率的影响。

## 二、实验原理

实验基于一维定态薛定谔方程。波函数及其一阶导数在势垒边界连续，因此即使 E < V0，势垒右侧仍可能出现非零透射概率。

## 三、实验参数

| 参数 | 数值 |
| --- | ---: |
| 粒子能量 E | ${params.energy.toFixed(2)} |
| 势垒高度 V0 | ${params.barrierHeight.toFixed(2)} |
| 势垒宽度 a | ${params.barrierWidth.toFixed(2)} |
| 粒子质量 m | ${params.mass.toFixed(2)} |

## 四、计算结果

| 项目 | 数值 |
| --- | ---: |
| 物理区域 | ${result.region} |
| 透射率 T | ${percent(result.transmission)} |
| 反射率 R | ${percent(result.reflection)} |
| 概率守恒误差 | ${result.conservationError.toExponential(2)} |

## 五、经典/量子对比

${classical}

量子力学预测：透射率 T = ${percent(result.transmission)}，反射率 R = ${percent(result.reflection)}。

## 六、结果分析

当 E < V0 时，波函数在势垒内指数衰减但不立即为零，因此透射率不为零；当 E > V0 时，边界处波矢失配会导致量子反射。调大势垒宽度、势垒高度或粒子质量通常会降低隧穿概率。

## 七、结论

本次虚拟实验说明，量子隧穿不是经典“穿墙”图像，而是波函数边界连续和概率诠释共同导致的非经典现象。`;
}
