"use client";

import {
  CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

import type { Month } from "@/lib/api";
import { formatMoney, formatNumber } from "@/lib/format";

type Props = {
  withDecision: Month[];
  withoutDecision: Month[];
  decisionName: string;
  turningMonth: number | null;   // premier mois où l'on dépense plus qu'on ne gagne
};

// Les deux futurs possibles de l'épargne, mois par mois.
export function FutureChart({ withDecision, withoutDecision, decisionName, turningMonth }: Props) {
  const name = decisionName.toLowerCase();
  const data = withDecision.map((m, i) => ({
    month: m.month,
    avec: m.cash,
    sans: withoutDecision[i]?.cash ?? null,
  }));

  return (
    <figure className="flex flex-col gap-3">
      <figcaption className="flex flex-wrap gap-x-6 gap-y-1 text-sm">
        <span className="flex items-center gap-2">
          <span className="h-0.5 w-6 bg-bleu" aria-hidden="true" />
          Avec {name}
        </span>
        <span className="flex items-center gap-2 text-pierre">
          <span className="w-6 border-t-2 border-dashed border-pierre" aria-hidden="true" />
          Sans {name}
        </span>
      </figcaption>

      {turningMonth && (
        <p className="text-sm text-grenade">
          À partir du mois {turningMonth} (trait rouge), vous dépenseriez chaque mois plus que
          vous ne gagnez.
        </p>
      )}

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 16, right: 28, bottom: 8, left: 0 }}>
            <CartesianGrid stroke="var(--ligne)" vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              axisLine={{ stroke: "var(--ligne)" }}
              tick={{ fill: "var(--pierre)", fontSize: 12 }}
              tickFormatter={(m: number) => (m % 12 === 0 ? `${m} mois` : "")}
              interval={0}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              width={64}
              tick={{ fill: "var(--pierre)", fontSize: 12 }}
              tickFormatter={(v: number) => formatNumber(v)}
            />
            <ReferenceLine y={0} stroke="var(--grenade)" strokeDasharray="4 4" />
            {turningMonth && <ReferenceLine x={turningMonth} stroke="var(--grenade)" />}
            <Tooltip
              formatter={(value, series) => [
                formatMoney(Number(value)),
                series === "avec" ? `Avec ${name}` : `Sans ${name}`,
              ]}
              labelFormatter={(m) => `Mois ${m}`}
              contentStyle={{ borderRadius: 8, borderColor: "var(--ligne)" }}
            />
            <Line type="monotone" dataKey="sans" stroke="var(--pierre)" strokeWidth={2}
                  strokeDasharray="6 4" dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="avec" stroke="var(--bleu)" strokeWidth={3}
                  dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </figure>
  );
}