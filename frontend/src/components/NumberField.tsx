"use client";

type Props = {
  label: string;
  value: number;
  onChange: (value: number) => void;
  suffix?: string;
  step?: number;
  min?: number;
};

// Champ numérique avec son libellé et son unité (€, %, mois).
export function NumberField({ label, value, onChange, suffix, step = 100, min = 0 }: Props) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm text-pierre">{label}</span>
      <span className="flex items-center rounded-md border border-ligne bg-papier focus-within:border-bleu focus-within:ring-2 focus-within:ring-bleu/20">
        <input
          type="number"
          inputMode="decimal"
          className="chiffres w-full bg-transparent px-3 py-2 text-base outline-none"
          value={Number.isFinite(value) ? value : ""}
          step={step}
          min={min}
          onChange={(event) => onChange(event.target.valueAsNumber)}
        />
        {suffix && <span className="pr-3 text-sm text-pierre">{suffix}</span>}
      </span>
    </label>
  );
}