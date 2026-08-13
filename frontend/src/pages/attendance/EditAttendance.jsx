import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import * as attendanceService from "../../services/attendanceService";
import { ErrorMessage, SuccessMessage, Loader } from "../../components/Common";

// Same status rules as MarkAttendance.jsx — mirrored here rather than
// imported since the two pages are small enough that a shared file
// would add more indirection than it saves; the backend
// (AttendanceUpdate.validate_check_in_out_against_status) is the real
// source of truth either way.
const STATUSES_REQUIRING_CHECK_IN = ["PRESENT", "HALF_DAY"];
const STATUSES_FORBIDDING_TIMES = ["ABSENT", "ON_LEAVE"];

/**
 * Edits an existing attendance record — most commonly used to add a
 * check_out time later in the day after the employee was marked
 * PRESENT with only a check_in that morning. employee_id and
 * attendance_date are fixed (shown, not editable) since changing
 * either would mean this is really a different record, not an edit
 * of this one — see AttendanceUpdate on the backend for the same
 * reasoning.
 */
export default function EditAttendance() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [form, setForm] = useState({ status: "PRESENT", check_in: "", check_out: "" });

  const checkInRequired = STATUSES_REQUIRING_CHECK_IN.includes(form.status);
  const timesDisabled = STATUSES_FORBIDDING_TIMES.includes(form.status);

  useEffect(() => {
    attendanceService
      .getAttendance(id)
      .then((data) => {
        setRecord(data);
        setForm({
          status: data.status,
          check_in: data.check_in || "",
          check_out: data.check_out || "",
        });
      })
      .catch(() => setError("Failed to load attendance record."))
      .finally(() => setLoading(false));
  }, [id]);

  function handleStatusChange(e) {
    const newStatus = e.target.value;
    const willForbidTimes = STATUSES_FORBIDDING_TIMES.includes(newStatus);
    setForm((prev) => ({
      ...prev,
      status: newStatus,
      check_in: willForbidTimes ? "" : prev.check_in,
      check_out: willForbidTimes ? "" : prev.check_out,
    }));
  }

  function handleChange(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      await attendanceService.updateAttendance(id, {
        status: form.status,
        check_in: form.check_in || null,
        check_out: form.check_out || null,
      });
      setSuccess("Attendance record updated.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg).join(", "));
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Failed to update attendance record.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Loader />;
  if (error && !record) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1>Edit Attendance</h1>
      <p className="subtitle">
        {record.employee_code} — {record.employee_name} · {record.attendance_date}
      </p>

      <form className="card form-card" onSubmit={handleSubmit}>
        <ErrorMessage message={error} />
        <SuccessMessage message={success} />

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
        </label>

        <label className="form-label">
          Check-Out Time
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
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => navigate("/attendance")}>
            Back to Attendance
          </button>
        </div>
      </form>
    </div>
  );
}