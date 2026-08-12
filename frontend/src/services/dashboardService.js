import axiosClient from "../api/axiosClient";

export async function getDashboardStats() {
  const response = await axiosClient.get("/api/dashboard/stats");
  return response.data;
}
