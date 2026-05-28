import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DailyPoint } from "../api/client";

type Props = {
  points: DailyPoint[];
};

export function DailyChart({ points }: Props) {
  if (points.length === 0) {
    return <p className="empty">No data for this day.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={points} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="minute" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
        <YAxis tick={{ fontSize: 11 }} unit=" Mbps" />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="download_mbps" name="Download" stroke="#2563eb" dot={false} />
        <Line type="monotone" dataKey="upload_mbps" name="Upload" stroke="#16a34a" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
