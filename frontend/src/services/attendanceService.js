import axiosClient from "../api/axiosClient";

export async function markAttendance(payload) {
  const response = await axiosClient.post("/api/attendance", payload);
  return response.data;
}

export async function listAttendance(params) {
  const response = await axiosClient.get("/api/attendance", { params });
  return response.data; // { data, total, page, page_size }
}

export async function getAttendanceSummary(params) {
  const response = await axiosClient.get("/api/attendance/summary", { params });
  return response.data;
}

export async function getEmployeeAttendanceHistory(employeeId) {
  const response = await axiosClient.get(`/api/attendance/employee/${employeeId}`);
  return response.data;
}

/**
 * Downloads an attendance export (CSV or XLSX) and triggers a browser
 * "Save As" for it.
 *
 * responseType: "blob" is essential here — without it, Axios tries to
 * parse the response as JSON/text and corrupts the binary .xlsx bytes.
 *
 * The filename is read from the backend's Content-Disposition header
 * when available (requires CORS expose_headers — see app/main.py), but
 * we ALSO build a correct fallback filename with the right extension
 * from the request params themselves, so the download never ends up
 * with a missing/wrong extension even if that header isn't readable.
 */
export async function exportAttendance(params) {
  const response = await axiosClient.get("/api/attendance/export", {
    params,
    responseType: "blob",
  });

  const format = params.format || "csv";
  const mimeType =
    format === "xlsx"
      ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      : "text/csv";

  const disposition = response.headers["content-disposition"] || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : `attendance_export.${format}`;

  // Explicitly set the Blob's MIME type rather than trusting whatever
  // Axios inferred — this is what makes Windows/macOS recognize the
  // downloaded file as a real CSV/Excel file instead of plain text.
  const blob = new Blob([response.data], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}