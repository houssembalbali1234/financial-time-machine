// Types de décisions proposés, avec des valeurs de départ réalistes (toutes modifiables).
import type { Decision } from "./api";

export type Horizon = 36 | 60 | 120;

export type Preset = {
  key: string;
  label: string;
  horizon: Horizon;          // durée d'observation adaptée à ce type d'achat
  decision: Decision;
};

export const PRESETS: Preset[] = [
  {
    key: "voiture",
    label: "Voiture",
    horizon: 36,
    decision: {
      name: "Voiture", price: 25000, down_payment: 5000, loan_annual_rate: 0.065,
      loan_months: 60, asset_annual_depreciation: 0.12, extra_monthly_cost: 200,
    },
  },
  {
    key: "logement",
    label: "Logement",
    horizon: 120,
    decision: {
      name: "Logement", price: 250000, down_payment: 50000, loan_annual_rate: 0.037,
      loan_months: 300, asset_annual_depreciation: -0.01, extra_monthly_cost: 300,
    },
  },
  {
    key: "travaux",
    label: "Travaux",
    horizon: 60,
    decision: {
      name: "Travaux", price: 30000, down_payment: 5000, loan_annual_rate: 0.055,
      loan_months: 120, asset_annual_depreciation: 0.03, extra_monthly_cost: 0,
    },
  },
  {
    key: "etudes",
    label: "Études",
    horizon: 60,
    decision: {
      name: "Études", price: 15000, down_payment: 2000, loan_annual_rate: 0.045,
      loan_months: 84, asset_annual_depreciation: 1, extra_monthly_cost: 0,
    },
  },
  {
    key: "mariage",
    label: "Mariage",
    horizon: 36,
    decision: {
      name: "Mariage", price: 12000, down_payment: 3000, loan_annual_rate: 0.07,
      loan_months: 36, asset_annual_depreciation: 1, extra_monthly_cost: 0,
    },
  },
];

export const HORIZONS: { value: Horizon; label: string }[] = [
  { value: 36, label: "3 ans" },
  { value: 60, label: "5 ans" },
  { value: 120, label: "10 ans" },
];