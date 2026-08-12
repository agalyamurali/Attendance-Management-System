import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as employeeService from "../../services/employeeService";
import { Loader, EmptyState, ErrorMessage, StatusBadge, Pagination } from "../../components/Common";

const PAGE_SIZE = 10;

export default function EmployeeList() {
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filter/search/sort state — each change resets to page 1, since
  // the previous page number may no longer be valid for a new filter.
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [status, setStatus] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    employeeService
      .listEmployees({
        search: search || undefined,
        department: department || undefined,
        status: status || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        page_size: PAGE_SIZE,
      })
      .then((data) => {
        if (!isMounted) return;
        setEmployees(data.data);
        setTotal(data.total);
        setError("");
      })
      .catch(() => {
        if (isMounted) setError("Failed to load employees.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [search, department, status, sortBy, sortOrder, page]);

  function handleFilterChange(setter) {
    return (e) => {
      setter(e.target.value);
      setPage(1);
    };
  }

  async function handleDelete(id, name) {
    if (!window.confirm(`Deactivate ${name}? Their attendance history will be preserved.`)) {
      return;
    }
    try {
      await employeeService.deleteEmployee(id);
      // Refresh current page after the change
      setPage((p) => p);
      setEmployees((prev) =>
        prev.map((emp) => (emp.id === id ? { ...emp, status: "INACTIVE" } : emp))
      );
    } catch {
      setError("Failed to deactivate employee.");
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Employees</h1>
        <Link className="btn btn-primary" to="/employees/new">
          + Add Employee
        </Link>
      </div>

      <div className="filters-bar">
        <input
          className="form-input"
          placeholder="Search name, email, or code..."
          value={search}
          onChange={handleFilterChange(setSearch)}
        />
        <input
          className="form-input"
          placeholder="Department"
          value={department}
          onChange={handleFilterChange(setDepartment)}
        />
        <select className="form-input" value={status} onChange={handleFilterChange(setStatus)}>
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
        <select
          className="form-input"
          value={`${sortBy}:${sortOrder}`}
          onChange={(e) => {
            const [by, order] = e.target.value.split(":");
            setSortBy(by);
            setSortOrder(order);
            setPage(1);
          }}
        >
          <option value="created_at:desc">Newest First</option>
          <option value="name:asc">Name (A–Z)</option>
          <option value="name:desc">Name (Z–A)</option>
          <option value="department:asc">Department (A–Z)</option>
        </select>
      </div>

      <ErrorMessage message={error} />

      {loading ? (
        <Loader />
      ) : employees.length === 0 ? (
        <EmptyState message="No employees match your filters." />
      ) : (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Designation</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.id}>
                  <td>{emp.employee_code}</td>
                  <td>{emp.name}</td>
                  <td>{emp.email}</td>
                  <td>{emp.department}</td>
                  <td>{emp.designation}</td>
                  <td>
                    <StatusBadge status={emp.status} />
                  </td>
                  <td className="table-actions">
                    <Link to={`/employees/${emp.id}`}>View</Link>
                    <Link to={`/employees/${emp.id}/edit`}>Edit</Link>
                    {emp.status === "ACTIVE" && (
                      <button
                        className="link-button"
                        onClick={() => handleDelete(emp.id, emp.name)}
                      >
                        Deactivate
                      </button>
                    )}
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
