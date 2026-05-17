/**
 * Axios instance with JWT interceptor for generated API client.
 *
 * Orval calls request(url, config). We translate that to an AxiosRequestConfig
 * so that method, body, headers and AbortSignal are forwarded correctly.
 */
import axios, { AxiosRequestConfig } from "axios";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  withCredentials: false,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

function normalizeHeaders(init?: HeadersInit): Record<string, string> | undefined {
  if (!init) return undefined;
  if (Array.isArray(init)) return Object.fromEntries(init);
  if (typeof init === "object" && !(init instanceof Headers)) {
    return init as Record<string, string>;
  }
  const h = new Headers(init);
  const result: Record<string, string> = {};
  h.forEach((v, k) => {
    result[k] = v;
  });
  return result;
}

export async function request<T>(
  url: string,
  config?: RequestInit,
): Promise<T> {
  const axiosConfig: AxiosRequestConfig = {
    url,
    method: (config?.method || "GET").toLowerCase() as AxiosRequestConfig["method"],
    headers: normalizeHeaders(config?.headers),
    data: config?.body,
    signal: config?.signal as any,
  };
  const { data } = await axiosInstance.request<T>(axiosConfig);
  return data;
}
