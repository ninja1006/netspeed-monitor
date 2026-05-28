import { format } from "date-fns";
import { useCallback, useEffect, useState } from "react";
import {
  getDaily,
  getHealth,
  getWeek,
  getWorstTimes,
  type DailyResponse,
  type WeekResponse,
  type WorstWindow,
} from "./api/client";
import { DailyChart } from "./components/DailyChart";
import { WeekStack } from "./components/WeekStack";
import { WorstTimesTable } from "./components/WorstTimesTable";
import "./App.css";

function todayIso() {
  return format(new Date(), "yyyy-MM-dd");
}

export default function App() {
  const [date, setDate] = useState(todayIso);
  const [daily, setDaily] = useState<DailyResponse | null>(null);
  const [week, setWeek] = useState<WeekResponse | null>(null);
  const [worst, setWorst] = useState<WorstWindow[]>([]);
  const [health, setHealth] = useState<string>("loading");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, d, w, wt] = await Promise.all([
        getHealth(),
        getDaily(date),
        getWeek(date),
        getWorstTimes("day", date),
      ]);
      setHealth(h.status ?? "ok");
      setDaily(d);
      setWeek(w);
      setWorst(wt.windows);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load API data");
    } finally {
      setLoading(false);
    }
  }, [date]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const id = setInterval(load, 60_000);
    return () => clearInterval(id);
  }, [load]);

  return (
    <div className="app">
      <header>
        <h1>Network Speed Monitor</h1>
        <p className="tagline">Know your true speed, not your tunnel speed.</p>
        <span className={`badge ${health === "ok" ? "ok" : ""}`}>API: {health}</span>
      </header>

      <section className="controls">
        <label>
          Date{" "}
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <button type="button" onClick={load} disabled={loading}>
          Refresh
        </button>
      </section>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Loading…</div>}

      {!loading && !error && daily && (
        <section>
          <h2>Daily — {daily.date}</h2>
          <p className="summary">
            Avg {daily.summary.avg_download_mbps} Mbps · Min {daily.summary.min_download_mbps} · Max{" "}
            {daily.summary.max_download_mbps}
          </p>
          <DailyChart points={daily.points} />
        </section>
      )}

      {!loading && !error && week && (
        <section>
          <h2>Week (7 days ending {week.end})</h2>
          <WeekStack days={week.days} />
        </section>
      )}

      {!loading && !error && (
        <section>
          <h2>Slowest 15-minute windows</h2>
          <WorstTimesTable windows={worst} />
        </section>
      )}
    </div>
  );
}
