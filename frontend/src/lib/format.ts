// Mise en forme française : espaces entre milliers, virgule décimale.

const tnd = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const percent = new Intl.NumberFormat("fr-FR", { style: "percent", maximumFractionDigits: 0 });

export function formatTND(value: number): string {
  return `${tnd.format(value)} TND`;
}

export function formatNumber(value: number, decimals = 0): string {
  return value.toLocaleString("fr-FR", { maximumFractionDigits: decimals });
}

export function formatPercent(ratio: number): string {
  return percent.format(ratio);
}