import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as attendanceService from "../../services/attendanceService";
import { Loader, EmptyState, ErrorMessage, StatusBadge, Pagination } from "../../components/Common";
import ExportButton from "../../components/export_button";

const PAGE_SIZE = 10;

export default function AttendanceList() {
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [date, setDate] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    attendanceService
      .listAttendance({
        attendance_date: date || undefined,
        status: status || undefined,
        page,
        page_size: PAGE_SIZE,
      })
      .then((data) => {
        if (!isMounted) return;
        setRecords(data.data);
        setTotal(data.total);
        setError("");
      })
      .catch(() => {
        if (isMounted) setError("Failed to load attendance records.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [date, status, page]);

  return (
    <div>
      <div className="page-header">
        <h1>Attendance</h1>
        <div className="header-actions">
          {/* Export respects whatever date/status filters are currently
              applied on screen — "export what I'm looking at," not a
              separate, disconnected export flow. Pagination itself is
              NOT passed through: the export always returns every
              matching row, not just the current page (see
              attendance_repository.list_for_export). */}
          <ExportButton filters={{ attendance_date: date || undefined, status: status || undefined }} />
          <Link className="btn btn-primary" to="/attendance/mark">
            + Mark Attendance
          </Link>
        </div>
      </div>

      <div className="filters-bar">
        <input
          type="date"
          className="form-input"
          value={date}
          onChange={(e) => {
            setDate(e.target.value);
            setPage(1);
          }}
        />
        <select
          className="form-input"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Statuses</option>
          <option value="PRESENT">Present</option>
          <option value="ABSENT">Absent</option>
          <option value="HALF_DAY">Half Day</option>
          <option value="ON_LEAVE">On Leave</option>
        </select>
      </div>

      <ErrorMessage message={error} />

      {loading ? (
        <Loader />
      ) : records.length === 0 ? (
        <EmptyState message="No attendance records match your filters." />
      ) : (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Employee</th>
                <th>Check-In</th>
                <th>Check-Out</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {records.map((rec) => (
                <tr key={rec.id}>
                  <td>{rec.attendance_date}</td>
                  <td>
                    <Link to={`/attendance/history/${rec.employee_id}`}>
                      {rec.employee_code} — {rec.employee_name}
                    </Link>
                  </td>
                  <td>{rec.check_in || "—"}</td>
                  <td>{rec.check_out || "—"}</td>
                  <td>
                    <StatusBadge status={rec.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
