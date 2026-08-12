import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import * as employeeService from "../../services/employeeService";
import { Loader, ErrorMessage, StatusBadge } from "../../components/Common";

export default function EmployeeDetails() {
  const { id } = useParams();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    employeeService
      .getEmployee(id)
      .then(setEmployee)
      .catch(() => setError("Employee not found."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <div className="page-header">
        <h1>{employee.name}</h1>
        <div className="table-actions">
          <Link className="btn btn-secondary" to={`/employees/${id}/edit`}>
            Edit
          </Link>
          <Link className="btn btn-secondary" to={`/attendance/history/${id}`}>
            View Attendance History
          </Link>
        </div>
      </div>

      <div className="card details-card">
        <DetailRow label="Employee Code" value={employee.employee_code} />
        <DetailRow label="Email" value={employee.email} />
        <DetailRow label="Mobile" value={employee.mobile} />
        <DetailRow label="Department" value={employee.department} />
        <DetailRow label="Designation" value={employee.designation} />
        <DetailRow label="Status" value={<StatusBadge status={employee.status} />} />
        <DetailRow label="Added On" value={new Date(employee.created_at).toLocaleDateString()} />
      </div>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value}</span>
    </div>
  );
}
