import { useEffect, useState } from "react";
import * as dashboardService from "../services/dashboardService";
import { Loader, ErrorMessage } from "../components/Common";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;
    dashboardService
      .getDashboardStats()
      .then((data) => {
        if (isMounted) setStats(data);
      })
      .catch(() => {
        if (isMounted) setError("Failed to load dashboard stats.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <Loader label="Loading dashboard..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <StatCard label="Total Employees" value={stats.total_employees} />
        <StatCard label="Active Employees" value={stats.active_employees} />
        <StatCard label="Present Today" value={stats.present_today} accent="green" />
        <StatCard label="Absent Today" value={stats.absent_today} accent="red" />
      </div>

      <div className="card">
        <h2>Department-wise Employee Count</h2>
        {stats.department_wise_count.length === 0 ? (
          <p>No active employees yet.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Active Employees</th>
              </tr>
            </thead>
            <tbody>
              {stats.department_wise_count.map((row) => (
                <tr key={row.department}>
                  <td>{row.department}</td>
                  <td>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div className={`stat-card ${accent ? `stat-card-${accent}` : ""}`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
