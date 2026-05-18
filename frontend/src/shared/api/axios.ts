/**
 * Axios instance with JWT interceptor for generated API client.
 */
import axios from "axios";

export const axiosInstance = axios.create({
  baseURL: "http://localhost:8023",
  withCredentials: false,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
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

export async function request<T>(url: string, config?: any): Promise<any> {
  const { data } = await axiosInstance.request<T>({
    url,
    method: config?.method || "GET",
    headers: config?.headers,
    data: config?.body,
  });
  return data;
}
