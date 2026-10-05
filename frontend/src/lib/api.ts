// Client de l'API : les types reprennent exactement les schémas Pydantic du backend.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Profile = {
  monthly_income: number;
  monthly_expenses: number;
  cash: number;
  annual_inflation: number;
};

export type Decision = {
  name: string;
  price: number;
  down_payment: number;
  loan_annual_rate: number;
  loan_months: number;
  asset_annual_depreciation: number;
  extra_monthly_cost: number;
};

export type Month = {
  month: number;
  income: number;
  expenses: number;
  loan_payments: number;
  cash_flow: number;
  cash: number;
  debt_remaining: number;
  asset_value: number;
  net_worth: number;
  debt_ratio: number;
};

export type Summary = {
  final_cash: number;
  final_net_worth: number;
  final_debt: number;
  min_cash: number;
  months_negative: number;
  first_negative_month: number | null;
  max_debt_ratio: number;
  max_monthly_outflow: number;
};

export type InputWarning = {
  code: string;
  level: "danger" | "attention";
  values: Record<string, number>;
};

export type SimulationResult = { summary: Summary; months: Month[]; warnings: InputWarning[] };

export type HealthFactor = {
  key: string;
  label: string;
  value: number;
  score: number;
  weight: number;
  points: number;
  explanation: string;
};

export type HealthScore = { total: number; grade: string; factors: HealthFactor[] };

export type HealthScoreResult = {
  current: HealthScore;
  after_decision: HealthScore | null;
  impact: number | null;
};

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`L'API a répondu ${response.status} sur ${path}`);
  }
  return response.json() as Promise<T>;
}

export function simulate(profile: Profile, decision: Decision | null, horizon = 36) {
  return post<SimulationResult>("/simulations", {
    profile,
    decision,
    horizon_months: horizon,
  });
}

export function getHealthScore(profile: Profile, decision: Decision | null) {
  return post<HealthScoreResult>("/health-score", { profile, decision });
}