import { useEffect, useMemo, useState } from "react";

const API =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
const reasonLabels = {
  all: "All reasons",
  missing_in_b: "Missing in B",
  orphan_in_b: "Orphan in B",
  duplicate_in_b: "Duplicate in B",
  value_mismatch: "Value mismatch",
};

const reasonMeta = {
  missing_in_b: {
    label: "Missing in B",
    icon: "↓",
    tone: "blue",
  },
  orphan_in_b: {
    label: "Orphan in B",
    icon: "↗",
    tone: "purple",
  },
  duplicate_in_b: {
    label: "Duplicate in B",
    icon: "≋",
    tone: "amber",
  },
  value_mismatch: {
    label: "Value mismatch",
    icon: "≠",
    tone: "red",
  },
};

function formatValue(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return value;
  }

  return number.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function ReasonBadge({ reason, label }) {
  const meta = reasonMeta[reason] || {
    label: label || reason,
    icon: "•",
    tone: "gray",
  };

  return (
    <span className={`reason-badge ${meta.tone}`}>
      <span className="reason-icon">{meta.icon}</span>
      {meta.label}
    </span>
  );
}

function StatCard({ title, value, tone, icon }) {
  return (
    <div className={`stat-card ${tone}`}>
      <div className="stat-icon">{icon}</div>

      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-title">{title}</div>
      </div>
    </div>
  );
}

function App() {
  const [organizations, setOrganizations] = useState([]);
  const [orgId, setOrgId] = useState("");

  const [reason, setReason] = useState("all");
  const [sort, setSort] = useState("value_desc");

  const [rows, setRows] = useState([]);

  const [loadingOrganizations, setLoadingOrganizations] = useState(true);
  const [loadingRows, setLoadingRows] = useState(false);

  const [error, setError] = useState("");

  // ---------------------------------------------------------
  // Load organizations
  // ---------------------------------------------------------

  async function loadOrganizations() {
    setLoadingOrganizations(true);
    setError("");

    try {
      const response = await fetch(`${API}/organizations/`);

      if (!response.ok) {
        throw new Error("Could not load organizations.");
      }

      const data = await response.json();

      const orgs = data.organizations || [];

      setOrganizations(orgs);

      if (orgs.length > 0 && !orgId) {
        setOrgId(orgs[0]);
      }
    } catch (err) {
      setError(err.message || "Could not load organizations.");
    } finally {
      setLoadingOrganizations(false);
    }
  }

  // ---------------------------------------------------------
  // Load filtered disagreements
  // ---------------------------------------------------------

  async function loadDisagreements() {
    if (!orgId) {
      return;
    }

    setLoadingRows(true);
    setError("");

    try {
      const params = new URLSearchParams({
        org_id: orgId,
        reason: reason,
        sort: sort,
      });

      const response = await fetch(
        `${API}/disagreements/?${params.toString()}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not load disagreement records."
        );
      }

      setRows(data.results || []);
    } catch (err) {
      setRows([]);
      setError(err.message || "Could not load disagreement records.");
    } finally {
      setLoadingRows(false);
    }
  }

  // ---------------------------------------------------------
  // Initial organization load
  // ---------------------------------------------------------

  useEffect(() => {
    loadOrganizations();
  }, []);

  // ---------------------------------------------------------
  // Reload records whenever filters/sorting change
  // ---------------------------------------------------------

  useEffect(() => {
    if (orgId) {
      loadDisagreements();
    }
  }, [orgId, reason, sort]);

  // ---------------------------------------------------------
  // Overview statistics
  //
  // IMPORTANT:
  // Stats are calculated from "rows", which are already filtered
  // by the selected organization + reason.
  //
  // Sorting does NOT affect the counts.
  // ---------------------------------------------------------

  const stats = useMemo(() => {
    const result = {
      value_mismatch: 0,
      missing_in_b: 0,
      duplicate_in_b: 0,
      orphan_in_b: 0,
    };

    rows.forEach((row) => {
      if (result[row.reason] !== undefined) {
        result[row.reason] += 1;
      }
    });

    return result;
  }, [rows]);

  // ---------------------------------------------------------
  // Page description based on selected filter
  // ---------------------------------------------------------

  const overviewDescription = useMemo(() => {
    if (!orgId) {
      return "Select an organization to begin";
    }

    if (reason === "all") {
      return `All disagreement types for ${orgId}`;
    }

    return `${reasonLabels[reason]} for ${orgId}`;
  }, [orgId, reason]);

  // ---------------------------------------------------------
  // Empty state message
  // ---------------------------------------------------------

  const emptyMessage = useMemo(() => {
    if (reason === "all") {
      return "No disagreements found for this organization.";
    }

    return `No ${reasonLabels[reason].toLowerCase()} records found.`;
  }, [reason]);

  return (
    <main className="page">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="hero">

        <div className="brand-row">

          <div className="brand-mark">
            ↔
          </div>

          <div>
            <div className="eyebrow">
              DATA QUALITY • RECONCILIATION
            </div>

            <h1>
              System Reconciliation
            </h1>
          </div>

        </div>

        <p className="subtitle">
          Identify and review records where System A and System B disagree.
        </p>

        <div className="status-pill">
          <span className="status-dot"></span>
          Reconciliation service connected
        </div>

      </header>


      {/* =====================================================
          FILTERS & SORTING
      ====================================================== */}

      <section className="filters-card">

        <div className="filters-title">

          <span className="filter-icon">
            ⚙
          </span>

          <div>
            <h2>
              Filters & sorting
            </h2>

            <p>
              Refine the records shown in the reconciliation table.
            </p>
          </div>

        </div>


        <div className="controls">

          {/* Organization */}

          <label>

            <span>
              Organization
            </span>

            <select
              value={orgId}
              onChange={(event) => setOrgId(event.target.value)}
              disabled={loadingOrganizations}
            >

              {organizations.map((org) => (
                <option
                  key={org}
                  value={org}
                >
                  {org}
                </option>
              ))}

            </select>

          </label>


          {/* Reason */}

          <label>

            <span>
              Reason
            </span>

            <select
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            >

              {Object.entries(reasonLabels).map(
                ([key, label]) => (
                  <option
                    key={key}
                    value={key}
                  >
                    {label}
                  </option>
                )
              )}

            </select>

          </label>


          {/* Sorting */}

          <label>

            <span>
              Sort by
            </span>

            <select
              value={sort}
              onChange={(event) => setSort(event.target.value)}
            >

              <option value="value_desc">
                Value: high to low
              </option>

              <option value="value_asc">
                Value: low to high
              </option>

              <option value="record">
                Record ID
              </option>

            </select>

          </label>

        </div>

      </section>


      {/* =====================================================
          ERROR
      ====================================================== */}

      {error && (
        <div className="error">
          ⚠ {error}
        </div>
      )}


      {/* =====================================================
          RECONCILIATION OVERVIEW
      ====================================================== */}

      <section className="dashboard-card">

        <div className="section-heading">

          <div>

            <h2>
              Reconciliation overview
            </h2>

            <p>
              {overviewDescription}
            </p>

          </div>


          <div className="result-count">

            <strong>
              {loadingRows ? "…" : rows.length}
            </strong>

            <span>
              shown
            </span>

          </div>

        </div>


        <div className="stats-grid">

          <StatCard
            title="Value mismatches"
            value={stats.value_mismatch}
            tone="red"
            icon="≠"
          />

          <StatCard
            title="Missing in B"
            value={stats.missing_in_b}
            tone="blue"
            icon="↓"
          />

          <StatCard
            title="Duplicates in B"
            value={stats.duplicate_in_b}
            tone="amber"
            icon="≋"
          />

          <StatCard
            title="Orphans in B"
            value={stats.orphan_in_b}
            tone="purple"
            icon="↗"
          />

        </div>

      </section>


      {/* =====================================================
          DISAGREEMENT RECORDS
      ====================================================== */}

      <section className="table-card">

        <div className="table-header">

          <div>

            <h2>
              Disagreement records
            </h2>

            <p>
              {loadingRows
                ? "Loading records…"
                : `${rows.length} record${
                    rows.length === 1 ? "" : "s"
                  } require review`}
            </p>

          </div>


          <div className="tenant-chip">

            <span>
              Tenant
            </span>

            <strong>
              {orgId || "—"}
            </strong>

          </div>

        </div>


        <div className="table-wrap">

          <table>

            <thead>

              <tr>

                <th>
                  Record
                </th>

                <th>
                  Reason
                </th>

                <th>
                  System A value
                </th>

                <th>
                  System B value
                </th>

                <th>
                  Location
                </th>

                <th>
                  B entry
                </th>

              </tr>

            </thead>


            <tbody>

              {/* Loading */}

              {loadingRows && (
                <tr>

                  <td colSpan="6">

                    <div className="loading-state">

                      <div className="loading-spinner"></div>

                      <strong>
                        Loading reconciliation records...
                      </strong>

                      <span>
                        Applying the selected filters.
                      </span>

                    </div>

                  </td>

                </tr>
              )}


              {/* Empty */}

              {!loadingRows && rows.length === 0 && (
                <tr>

                  <td colSpan="6">

                    <div className="empty-state">

                      <div className="empty-icon">
                        ✓
                      </div>

                      <strong>
                        No disagreements found
                      </strong>

                      <span>
                        {emptyMessage}
                      </span>

                    </div>

                  </td>

                </tr>
              )}


              {/* Records */}

              {!loadingRows &&
                rows.map((row, index) => (

                  <tr
                    key={`${row.reason}-${row.record_ref}-${row.system_b_entry_id || "none"}-${index}`}
                  >

                    <td>
                      <span className="record-id">
                        {row.record_ref}
                      </span>
                    </td>


                    <td>

                      <ReasonBadge
                        reason={row.reason}
                        label={row.reason_label}
                      />

                    </td>


                    <td>

                      <span className="value">
                        {formatValue(row.system_a_value)}
                      </span>

                    </td>


                    <td>

                      <span className="value">
                        {formatValue(row.system_b_value)}
                      </span>

                    </td>


                    <td>

                      <span className="location-chip">
                        {row.location_id}
                      </span>

                    </td>


                    <td>

                      <span className="entry-id">
                        {row.system_b_entry_id || "—"}
                      </span>

                    </td>

                  </tr>

                ))}

            </tbody>

          </table>

        </div>

      </section>


      {/* =====================================================
          FOOTER
      ====================================================== */}

      <footer>

        <span>
          System Reconciliation
        </span>

        <span>
          •
        </span>

        <span>
          Data quality review dashboard
        </span>

      </footer>

    </main>
  );
}

export default App;
