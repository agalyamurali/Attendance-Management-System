import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import * as attendanceService from "../../services/attendanceService";
import * as employeeService from "../../services/employeeService";
import { Loader, EmptyState, ErrorMessage, StatusBadge } from "../../components/Common";
import ExportButton from "../../components/export_button";

export default function EmployeeAttendanceHistory() {
  const { employeeId } = useParams();
  const [employee, setEmployee] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      employeeService.getEmployee(employeeId),
      attendanceService.getEmployeeAttendanceHistory(employeeId),
    ])
      .then(([emp, history]) => {
        setEmployee(emp);
        setRecords(history);
      })
      .catch(() => setError("Failed to load attendance history."))
      .finally(() => setLoading(false));
  }, [employeeId]);

  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} />;

  const presentCount = records.filter((r) => r.status === "PRESENT").length;
  const attendancePercentage =
    records.length > 0 ? Math.round((presentCount / records.length) * 100) : 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Attendance History — {employee.name}</h1>
          <p className="subtitle">
            {employee.employee_code} · {employee.department} · {presentCount}/{records.length} days
            present ({attendancePercentage}%)
          </p>
        </div>
        {/* Passing employee_id here is what makes this a per-employee
            export rather than the general one — same ExportButton
            component and same backend endpoint as the Attendance List
            page, just scoped by a different filter. */}
        <ExportButton filters={{ employee_id: employeeId }} />
      </div>

      {records.length === 0 ? (
        <EmptyState message="No attendance records for this employee yet." />
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Check-In</th>
              <th>Check-Out</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((rec) => (
              <tr key={rec.id}>
                <td>{rec.attendance_date}</td>
                <td>{rec.check_in || "—"}</td>
                <td>{rec.check_out || "—"}</td>
                <td>
                  <StatusBadge status={rec.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}