import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import * as employeeService from "../../services/employeeService";
import { ErrorMessage, Loader } from "../../components/Common";

const EMPTY_FORM = {
  employee_code: "",
  name: "",
  email: "",
  mobile: "",
  department: "",
  designation: "",
  status: "ACTIVE",
};

/**
 * Shared by both "Add Employee" and "Edit Employee" — same fields,
 * different submit behavior. isEdit is inferred from the presence of
 * an :id route param, not passed as a prop, so this component works
 * the same way whichever route rendered it.
 */
export default function EmployeeForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEdit) return;
    employeeService
      .getEmployee(id)
      .then((data) => setForm(data))
      .catch(() => setError("Failed to load employee."))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  function handleChange(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
  e.preventDefault();
  setError("");
  setSaving(true);

  try {
    if (isEdit) {
      await employeeService.updateEmployee(id, form);
    } else {
      await employeeService.createEmployee(form);
    }

    navigate("/employees");
  } catch (err) {
    const detail = err.response?.data?.detail;

    if (Array.isArray(detail)) {
      setError(detail.map((item) => item.msg).join(", "));
    } else if (typeof detail === "string") {
      setError(detail);
    } else {
      setError("Failed to save employee.");
    }
  } finally {
    setSaving(false);
  }
}

  if (loading) return <Loader />;

  return (
    <div>
      <h1>{isEdit ? "Edit Employee" : "Add Employee"}</h1>

      <form className="card form-card" onSubmit={handleSubmit}>
        <ErrorMessage message={error} />

        <label className="form-label">
  Employee Code
  <input
    className="form-input"
    value={form.employee_code}
    onChange={(e) => {
      const value = e.target.value
        .toUpperCase()
        .replace(/[^A-Z0-9]/g, "");

      setForm((prev) => ({
        ...prev,
        employee_code: value,
      }));
    }}
    placeholder="e.g. EMP001"
    maxLength={6}
    required
  />

  {form.employee_code.length > 0 &&
    !/^EMP\d{3}$/.test(form.employee_code) && (
      <span className="field-error">
        Employee code must be in the format EMP001.
      </span>
    )}
</label>

        <label className="form-label">
          Name
          <input className="form-input" value={form.name} onChange={handleChange("name")} required />
        </label>

        <label className="form-label">
          Email
          <input
            type="email"
            className="form-input"
            value={form.email}
            onChange={handleChange("email")}
            required
          />
        </label>

        <label className="form-label">
          Mobile
         <input
           type="tel"
           className="form-input"
           value={form.mobile}
           onChange={(e) => {
           const value = e.target.value.replace(/\D/g, "").slice(0, 10);
          setForm((prev) => ({ ...prev, mobile: value }));
    }}
          placeholder="Enter 10-digit mobile number"
          inputMode="numeric"
          maxLength={10}
          required
  />

  {form.mobile.length > 0 && form.mobile.length < 10 && (
    <span className="field-error">
      Mobile number must be exactly 10 digits.
    </span>
  )}
</label>

        <label className="form-label">
          Department
          <input
            className="form-input"
            value={form.department}
            onChange={handleChange("department")}
            required
          />
        </label>

        <label className="form-label">
          Designation
          <input
            className="form-input"
            value={form.designation}
            onChange={handleChange("designation")}
            required
          />
        </label>

        {isEdit && (
          <label className="form-label">
            Status
            <select className="form-input" value={form.status} onChange={handleChange("status")}>
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
          </label>
        )}

        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : isEdit ? "Save Changes" : "Add Employee"}
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => navigate(-1)}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
