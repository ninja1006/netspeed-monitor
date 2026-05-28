import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export type DailyPoint = {
  minute: string;
  download_mbps: number;
  upload_mbps: number;
  latency_ms: number;
  sample_count?: number;
};

export type DailyResponse = {
  date: string;
  timezone: string;
  points: DailyPoint[];
  summary: {
    avg_download_mbps: number;
    min_download_mbps: number;
    max_download_mbps: number;
  };
};

export type WeekDay = {
  date: string;
  points: DailyPoint[];
};

export type WeekResponse = {
  end: string;
  days: WeekDay[];
};

export type WorstWindow = {
  start: string;
  end: string;
  avg_download_mbps: number;
  avg_upload_mbps: number;
  avg_latency_ms: number;
  sample_count: number;
};

export async function getHealth() {
  const { data } = await api.get("/health");
  return data;
}

export async function getDaily(date: string) {
  const { data } = await api.get<DailyResponse>("/daily", { params: { date } });
  return data;
}

export async function getWeek(end: string) {
  const { data } = await api.get<WeekResponse>("/week", { params: { end } });
  return data;
}

export async function getWorstTimes(period: "day" | "week", date: string, end?: string) {
  const { data } = await api.get<{ period: string; windows: WorstWindow[] }>("/worst-times", {
    params: period === "day" ? { period, date } : { period, end: end ?? date },
  });
  return data;
}
