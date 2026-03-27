import type { Locale } from "../../types";

const SOURCE_TYPE_LABELS: Record<string, { en: string; zh: string }> = {
  benchmark: { en: "Benchmark / Evaluation", zh: "基准 / 评测" },
  paper: { en: "Research Paper", zh: "研究论文" },
  survey: { en: "Survey", zh: "综述" },
  dataset: { en: "Dataset", zh: "数据集" },
  code: { en: "Code / Repo", zh: "代码 / 仓库" },
};

const POSITIONING_LABELS: Record<string, { en: string; zh: string }> = {
  "gap-driven": { en: "Gap-Driven", zh: "问题缺口型" },
  "benchmark-gap": { en: "Benchmark Gap", zh: "基准缺口型" },
  "applied-transfer": { en: "Applied Transfer", zh: "应用迁移型" },
  systems: { en: "Systems", zh: "系统支持型" },
  "systems-priority": { en: "Systems Priority", zh: "系统优先型" },
  transfer: { en: "Transfer", zh: "迁移型" },
};

const DIMENSION_LABELS: Record<string, { en: string; zh: string }> = {
  novelty: { en: "Novelty", zh: "新颖性" },
  feasibility: { en: "Feasibility", zh: "可行性" },
  evidence_strength: { en: "Evidence Strength", zh: "证据强度" },
  data_availability: { en: "Data Availability", zh: "数据可得性" },
  implementation_cost: { en: "Implementation Cost", zh: "实现成本" },
  risk: { en: "Risk", zh: "风险" },
};

const CONSTRAINT_KEY_LABELS: Record<string, { en: string; zh: string }> = {
  time_budget_months: { en: "Time Budget", zh: "时间预算" },
  resource_level: { en: "Resource Level", zh: "资源水平" },
  preferred_style: { en: "Preferred Style", zh: "偏好风格" },
  notes: { en: "Notes", zh: "备注" },
};

const LEVEL_LABELS: Record<string, { en: string; zh: string }> = {
  low: { en: "low", zh: "低" },
  low_medium: { en: "low-medium", zh: "较低" },
  medium: { en: "medium", zh: "中" },
  medium_high: { en: "medium-high", zh: "中高" },
  high: { en: "high", zh: "高" },
  unknown: { en: "unknown", zh: "未知" },
};

export function getTopicAgentSourceTypeLabel(sourceType: string, locale: Locale) {
  return SOURCE_TYPE_LABELS[sourceType]?.[locale] ?? sourceType;
}

export function getTopicAgentPositioningLabel(positioning: string, locale: Locale) {
  return POSITIONING_LABELS[positioning]?.[locale] ?? positioning;
}

export function getTopicAgentDimensionLabel(dimension: string, locale: Locale) {
  return DIMENSION_LABELS[dimension]?.[locale] ?? dimension;
}

export function getTopicAgentConstraintLabel(key: string, locale: Locale) {
  return CONSTRAINT_KEY_LABELS[key]?.[locale] ?? key;
}

export function getTopicAgentLevelLabel(level: string, locale: Locale) {
  return LEVEL_LABELS[level]?.[locale] ?? level;
}
