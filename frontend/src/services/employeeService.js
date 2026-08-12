import axiosClient from "../api/axiosClient";

/**
 * Employee service — wraps every call to /api/employees*.
 * `params` is passed straight through to Axios as query params, so
 * callers can pass { search, department, status, page, page_size,
 * sort_by, sort_order } directly without this file needing to know
 * about each one individually.
 */

export async function listEmployees(params) {
  const response = await axiosClient.get("/api/employees", { params });
  return response.data; // { data, total, page, page_size }
}

export async function getEmployee(id) {
  const response = await axiosClient.get(`/api/employees/${id}`);
  return response.data;
}

export async function createEmployee(payload) {
  const response = await axiosClient.post("/api/employees", payload);
  return response.data;
}

export async function updateEmployee(id, payload) {
  const response = await axiosClient.put(`/api/employees/${id}`, payload);
  return response.data;
}

export async function deleteEmployee(id) {
  // "Delete" is a soft delete on the backend (sets status -> INACTIVE).
  const response = await axiosClient.delete(`/api/employees/${id}`);
  return response.data;
}
