import { useState } from "react";
import * as attendanceService from "../services/attendanceService";

/**
 * Small dropdown-free export control: two buttons, CSV and Excel,
 * both calling the same export endpoint with a different `format`.
 * Used on both the Attendance List page (general export, no
 * employeeId) and the Employee Attendance History page (per-employee
 * export, employeeId set) — the extra filters just get merged into
 * whatever params the parent page already has.
 */
export default function ExportButton({ filters = {} }) {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");

  async function handleExport(format) {
    setError("");
    setExporting(true);
    try {
      await attendanceService.exportAttendance({ ...filters, format });
    } catch {
      setError("Export failed. Please try again.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="export-controls">
      <button
        className="btn btn-secondary"
        type="button"
        disabled={exporting}
        onClick={() => handleExport("csv")}
      >
        Export CSV
      </button>
      <button
        className="btn btn-secondary"
        type="button"
        disabled={exporting}
        onClick={() => handleExport("xlsx")}
      >
        Export Excel
      </button>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
}