// Mise en forme française des montants : « 45 000 € », « 9,8 ».
// La devise est définie à un seul endroit pour pouvoir la changer facilement.

export const CURRENCY = "EUR";

const money = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: CURRENCY,
  maximumFractionDigits: 0,
});

export function formatMoney(value: number): string {
  return money.format(value);
}

export function formatNumber(value: number, decimals = 0): string {
  return value.toLocaleString("fr-FR", { maximumFractionDigits: decimals });
}