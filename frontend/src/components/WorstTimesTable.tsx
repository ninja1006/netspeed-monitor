import type { WorstWindow } from "../api/client";

type Props = {
  windows: WorstWindow[];
};

export function WorstTimesTable({ windows }: Props) {
  if (windows.length === 0) {
    return <p className="empty">No slow windows found.</p>;
  }

  return (
    <table className="worst-table">
      <thead>
        <tr>
          <th>Start</th>
          <th>End</th>
          <th>Avg download (Mbps)</th>
          <th>Avg upload (Mbps)</th>
          <th>Avg latency (ms)</th>
        </tr>
      </thead>
      <tbody>
        {windows.map((w) => (
          <tr key={w.start}>
            <td>{w.start}</td>
            <td>{w.end}</td>
            <td>{w.avg_download_mbps}</td>
            <td>{w.avg_upload_mbps}</td>
            <td>{w.avg_latency_ms}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
