import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as employeeService from "../../services/employeeService";
import * as attendanceService from "../../services/attendanceService";
import { ErrorMessage, SuccessMessage, Loader } from "../../components/Common";

const TODAY = new Date().toISOString().slice(0, 10);

// Single source of truth for which statuses need a check-in time and
// which statuses must NOT have any time recorded at all. Mirrored on
// the backend (see AttendanceCreate.validate_check_in_out_against_status
// in app/schemas/attendance.py) — this is a UX convenience, the real
// enforcement happens server-side.
const STATUSES_REQUIRING_CHECK_IN = ["PRESENT", "HALF_DAY"];
const STATUSES_FORBIDDING_TIMES = ["ABSENT", "ON_LEAVE"];

export default function MarkAttendance() {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState([]);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    employee_id: "",
    attendance_date: TODAY,
    status: "PRESENT",
    check_in: "",
    check_out: "",
  });

  const checkInRequired = STATUSES_REQUIRING_CHECK_IN.includes(form.status);
  const timesDisabled = STATUSES_FORBIDDING_TIMES.includes(form.status);

  useEffect(() => {
    // Only ACTIVE employees can have attendance marked — matches the
    // backend rule (see attendance_service.mark_attendance), so we
    // filter here too rather than letting the user pick someone the
    // API will reject anyway.
    employeeService
      .listEmployees({ status: "ACTIVE", page: 1, page_size: 100 })
      .then((data) => setEmployees(data.data))
      .catch(() => setError("Failed to load employees."))
      .finally(() => setLoadingEmployees(false));
  }, []);

  function handleChange(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  function handleStatusChange(e) {
    const newStatus = e.target.value;
    const willForbidTimes = STATUSES_FORBIDDING_TIMES.includes(newStatus);

    setForm((prev) => ({
      ...prev,
      status: newStatus,
      // Clear any previously entered times when switching to a status
      // that shouldn't carry them (ABSENT / ON_LEAVE) — otherwise a
      // stale check-in from a prior PRESENT selection could linger in
      // the form state and get submitted even though the field is
      // now disabled/hidden from the user's perspective.
      check_in: willForbidTimes ? "" : prev.check_in,
      check_out: willForbidTimes ? "" : prev.check_out,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      const payload = {
        employee_id: Number(form.employee_id),
        attendance_date: form.attendance_date,
        status: form.status,
        check_in: form.check_in || null,
        check_out: form.check_out || null,
      };
      await attendanceService.markAttendance(payload);
      setSuccess("Attendance marked successfully.");
      setForm((prev) => ({ ...prev, employee_id: "", check_in: "", check_out: "" }));
    } catch (err) {
      // FastAPI/Pydantic validation errors (422) come back as a LIST
      // of { msg, loc, ... } objects, not a single string — unlike our
      // own domain exceptions (404/409/422 raised in services), which
      // return a plain string in `detail`. Handle both shapes.
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg).join(", "));
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Failed to mark attendance.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (loadingEmployees) return <Loader />;

  return (
    <div>
      <h1>Mark Attendance</h1>

      <form className="card form-card" onSubmit={handleSubmit}>
        <ErrorMessage message={error} />
        <SuccessMessage message={success} />

        <label className="form-label">
          Employee
          <select
            className="form-input"
            value={form.employee_id}
            onChange={handleChange("employee_id")}
            required
          >
            <option value="" disabled>
              Select an employee
            </option>
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.employee_code} — {emp.name}
              </option>
            ))}
          </select>
        </label>

        <label className="form-label">
          Attendance Date
          <input
            type="date"
            className="form-input"
            value={form.attendance_date}
            onChange={handleChange("attendance_date")}
            required
          />
        </label>

        <label className="form-label">
          Status
          <select className="form-input" value={form.status} onChange={handleStatusChange}>
            <option value="PRESENT">Present</option>
            <option value="ABSENT">Absent</option>
            <option value="HALF_DAY">Half Day</option>
            <option value="ON_LEAVE">On Leave</option>
          </select>
        </label>

        <label className="form-label">
          Check-In Time {checkInRequired ? "(required)" : timesDisabled ? "" : "(optional)"}
          <input
            type="time"
            className="form-input"
            value={form.check_in}
            onChange={handleChange("check_in")}
            required={checkInRequired}
            disabled={timesDisabled}
          />
          {timesDisabled && (
            <span className="field-hint">Not applicable for {form.status.replace("_", " ")}.</span>
          )}
        </label>

        <label className="form-label">
          Check-Out Time {timesDisabled ? "" : "(optional — record when the employee leaves)"}
          <input
            type="time"
            className="form-input"
            value={form.check_out}
            onChange={handleChange("check_out")}
            disabled={timesDisabled}
          />
        </label>

        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Mark Attendance"}
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => navigate("/attendance")}>
            View Attendance
          </button>
        </div>
      </form>
    </div>
  );
}