import axios, { isAxiosError } from "axios";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export type DailyPoint = {
  minute: string;
  download_mbps: number | null;
  upload_mbps: number | null;
  latency_ms: number | null;
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

export async function getDaily(date: string): Promise<DailyResponse | null> {
  try {
    const { data } = await api.get<DailyResponse>("/daily", { params: { date } });
    return data;
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function getWeek(end: string) {
  const { data } = await api.get<WeekResponse>("/week", { params: { end } });
  return data;
}

export async function getWorstTimes(
  period: "day" | "week",
  date: string,
  end?: string,
): Promise<{ period: string; windows: WorstWindow[] }> {
  try {
    const { data } = await api.get<{ period: string; windows: WorstWindow[] }>("/worst-times", {
      params: period === "day" ? { period, date } : { period, end: end ?? date },
    });
    return data;
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 404) {
      return { period, windows: [] };
    }
    throw error;
  }
}

export function formatApiError(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Failed to load API data";
}
