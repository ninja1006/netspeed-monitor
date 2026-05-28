import { memo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { WeekDay } from "../api/client";

const DayChart = memo(function DayChart({ day }: { day: WeekDay }) {
  return (
    <div className="week-day-chart">
      <h3>{day.date}</h3>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={day.points} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="minute" hide />
          <YAxis tick={{ fontSize: 10 }} domain={[0, "auto"]} width={40} />
          <Tooltip />
          <Line type="monotone" dataKey="download_mbps" stroke="#2563eb" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});

type Props = {
  days: WeekDay[];
};

export function WeekStack({ days }: Props) {
  return (
    <div className="week-stack">
      {days.map((day) => (
        <DayChart key={day.date} day={day} />
      ))}
    </div>
  );
}
