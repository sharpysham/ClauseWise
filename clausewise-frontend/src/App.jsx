import { useState } from "react";
import axios from "axios";

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState({});

  const getRiskColor = (level) => {
    if (level === "HIGH") return "#dc2626";
    if (level === "MEDIUM") return "#ca8a04";
    return "#16a34a";
  };

  const getScoreColor = (score) => {
    if (score >= 0.6) return "#dc2626";
    if (score >= 0.35) return "#ca8a04";
    return "#16a34a";
  };

  const resetApp = () => {
    setResult(null);
    setLoading(false);
    setError(null);
    setExpanded({});
  };

  const toggleExpand = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL}/analyze`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to connect to backend. Make sure it is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.bgBlob1}></div>
      <div style={styles.bgBlob2}></div>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.logoWrapper}>
          <div style={styles.paper}></div>
          <div style={styles.magnifier}></div>
        </div>
        <h1 style={styles.brand}>ClauseWise</h1>
        <p style={styles.tagline}>See contract risks before they cost you.</p>
      </div>

      <h1 style={styles.title}>Understand contract risks before you sign</h1>
      <p style={styles.subtitle}>
        Upload your contract. We explain hidden risks in plain English.
      </p>

      {/* Upload Box */}
      {!loading && !result && (
        <div
          style={styles.uploadBox}
          onClick={() => document.getElementById("fileInput").click()}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "#6366f1";
            e.currentTarget.style.transform = "translateY(-4px) scale(1.01)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "rgba(99,102,241,0.25)";
            e.currentTarget.style.transform = "translateY(0) scale(1)";
          }}
        >
          <input
            type="file"
            accept=".pdf"
            style={{ display: "none" }}
            id="fileInput"
            onChange={handleFileUpload}
          />
          <p style={{ fontSize: "40px", margin: 0 }}>📄</p>
          <p style={styles.uploadText}>Click to upload contract PDF</p>
          <p style={{ fontSize: "13px", color: "#94a3b8", marginTop: "8px" }}>
            Supports any legal PDF
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={styles.errorBox}>
          <p>❌ {error}</p>
          <button style={styles.resetBtn} onClick={resetApp}>Try Again</button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={styles.analyzingBox}>
          <p style={styles.loadingText}>🔍 Analyzing contract...</p>
          <p style={{ color: "#94a3b8", fontSize: "14px" }}>
            This may take 1–3 minutes depending on document size
          </p>
          <div style={styles.spinner}></div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={styles.dashboard}>

          {/* Summary Banner */}
          <div style={styles.summaryBanner}>
            <p style={styles.summaryText}>📋 {result.summary}</p>
          </div>

          {/* Stats Row */}
          <div style={styles.statsRow}>
            <div style={styles.statBox}>
              <p style={styles.statNumber}>
                {(result.overall_risk_score * 10).toFixed(1)}/10
              </p>
              <p style={styles.statLabel}>Overall Risk</p>
            </div>
            <div style={styles.statBox}>
              <p style={{ ...styles.statNumber, color: "#dc2626" }}>
                {result.total_contradictions}
              </p>
              <p style={styles.statLabel}>Contradictions</p>
            </div>
            <div style={styles.statBox}>
              <p style={{ ...styles.statNumber, color: "#dc2626" }}>
                {result.high_risk_count}
              </p>
              <p style={styles.statLabel}>High Risk</p>
            </div>
            <div style={styles.statBox}>
              <p style={{ ...styles.statNumber, color: "#ca8a04" }}>
                {result.medium_risk_count}
              </p>
              <p style={styles.statLabel}>Medium Risk</p>
            </div>
            <div style={styles.statBox}>
              <p style={{ ...styles.statNumber, color: "#16a34a" }}>
                {result.low_risk_count}
              </p>
              <p style={styles.statLabel}>Low Risk</p>
            </div>
          </div>

          {/* Clause Cards */}
          <h2 style={styles.sectionTitle}>Clause Analysis</h2>
          {result.clauses.map((clause) => (
            <div
              key={clause.clause_id}
              style={{
                ...styles.card,
                borderLeft: `5px solid ${getRiskColor(clause.risk_level)}`,
                background: clause.is_contradicting
                  ? "#fff5f5"
                  : "#ffffff",
              }}
            >
              {/* Card Header */}
              <div style={styles.cardHeader}>
                <div>
                  <span
                    style={{
                      ...styles.badge,
                      background: getRiskColor(clause.risk_level),
                    }}
                  >
                    {clause.risk_level}
                  </span>
                  {clause.is_contradicting && (
                    <span style={styles.contradictionBadge}>
                      ⚡ CONTRADICTION
                    </span>
                  )}
                  <span style={styles.categoryText}>{clause.category}</span>
                </div>
                <button
                  style={styles.expandBtn}
                  onClick={() => toggleExpand(clause.clause_id)}
                >
                  {expanded[clause.clause_id] ? "▲ Less" : "▼ More"}
                </button>
              </div>

              {/* Explanation */}
              <p style={styles.explanation}>{clause.explanation}</p>

              {/* Contradiction note */}
              {clause.is_contradicting && clause.contradiction_with && (
                <p style={styles.contradictionNote}>
                  ⚠️ Conflicts with Clause #{clause.contradiction_with}
                </p>
              )}

              {/* Expanded Details */}
              {expanded[clause.clause_id] && (
                <div style={styles.expandedSection}>
                  <p style={styles.clauseText}>
                    <strong>Original text:</strong> {clause.text}
                  </p>
                  {clause.entities?.durations?.length > 0 && (
                    <p style={styles.entityText}>
                      🕐 Durations: {clause.entities.durations.join(", ")}
                    </p>
                  )}
                  {clause.entities?.money?.length > 0 && (
                    <p style={styles.entityText}>
                      💰 Amounts: {clause.entities.money.join(", ")}
                    </p>
                  )}
                  {clause.entities?.percentages?.length > 0 && (
                    <p style={styles.entityText}>
                      📊 Percentages: {clause.entities.percentages.join(", ")}
                    </p>
                  )}
                  <p style={styles.scoreText}>
                    Risk Score: {(clause.risk_score * 10).toFixed(1)}/10 |
                    Confidence: {(clause.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              )}
            </div>
          ))}

          <button style={styles.resetBtn} onClick={resetApp}>
            Upload Another Contract
          </button>

          <p style={styles.disclaimer}>
            ⚖️ This tool provides AI-assisted risk insights and is not legal advice.
          </p>
        </div>
      )}

      <p style={styles.trust}>
        We don't store your contracts. Analysis happens in real time.
      </p>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f9fafb",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "40px 20px",
    textAlign: "center",
    position: "relative",
    overflow: "hidden",
    fontFamily: "'Segoe UI', sans-serif",
  },
  bgBlob1: {
    position: "fixed", width: "420px", height: "420px",
    background: "#c7d2fe", borderRadius: "50%",
    top: "-120px", left: "-120px", filter: "blur(120px)", zIndex: 0,
  },
  bgBlob2: {
    position: "fixed", width: "420px", height: "420px",
    background: "#e9d5ff", borderRadius: "50%",
    bottom: "-120px", right: "-120px", filter: "blur(120px)", zIndex: 0,
  },
  header: { marginBottom: "20px", zIndex: 1 },
  logoWrapper: {
    position: "relative", width: "64px", height: "64px",
    margin: "0 auto 16px auto",
  },
  paper: {
    width: "40px", height: "52px", background: "#ffffff",
    borderRadius: "6px", position: "absolute", top: "6px", left: "6px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.15)",
  },
  magnifier: {
    width: "26px", height: "26px", borderRadius: "50%",
    border: "4px solid #7c3aed", position: "absolute",
    bottom: "6px", right: "2px",
  },
  brand: { fontSize: "42px", fontWeight: "700", color: "#4f46e5", margin: 0 },
  tagline: { marginTop: "8px", fontSize: "18px", color: "#475569" },
  title: {
    fontSize: "32px", fontWeight: "700", color: "#0f172a",
    marginBottom: "12px", zIndex: 1, maxWidth: "700px",
  },
  subtitle: {
    fontSize: "18px", color: "#475569", maxWidth: "600px",
    marginBottom: "40px", zIndex: 1,
  },
  uploadBox: {
    background: "rgba(255,255,255,0.65)",
    backdropFilter: "blur(14px)",
    borderRadius: "18px", padding: "48px", width: "380px",
    cursor: "pointer", border: "1px solid rgba(99,102,241,0.25)",
    boxShadow: "0 20px 40px rgba(79,70,229,0.18)",
    transition: "all 0.35s ease", zIndex: 1,
  },
  uploadText: { marginTop: "12px", color: "#64748b", fontWeight: "500" },
  analyzingBox: {
    marginTop: "40px", textAlign: "center", zIndex: 1,
  },
  loadingText: {
    fontSize: "20px", fontWeight: "600", color: "#6366f1",
  },
  spinner: {
    margin: "20px auto",
    width: "40px", height: "40px",
    border: "4px solid #e0e7ff",
    borderTop: "4px solid #6366f1",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  },
  errorBox: {
    background: "#fee2e2", borderRadius: "12px",
    padding: "20px 30px", marginTop: "20px", zIndex: 1,
  },
  dashboard: {
    marginTop: "20px", maxWidth: "860px",
    width: "95%", zIndex: 1,
  },
  summaryBanner: {
    background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
    borderRadius: "14px", padding: "16px 24px",
    marginBottom: "24px",
    boxShadow: "0 8px 24px rgba(99,102,241,0.3)",
  },
  summaryText: {
    color: "#ffffff", fontWeight: "600",
    fontSize: "16px", margin: 0,
  },
  statsRow: {
    display: "flex", gap: "12px", justifyContent: "center",
    flexWrap: "wrap", marginBottom: "32px",
  },
  statBox: {
    background: "#ffffff", borderRadius: "12px",
    padding: "16px 24px", minWidth: "100px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
  },
  statNumber: {
    fontSize: "28px", fontWeight: "700",
    color: "#4f46e5", margin: 0,
  },
  statLabel: {
    fontSize: "13px", color: "#94a3b8",
    marginTop: "4px", margin: 0,
  },
  sectionTitle: {
    fontSize: "22px", fontWeight: "700",
    color: "#0f172a", marginBottom: "16px",
    textAlign: "left",
  },
  card: {
    background: "#ffffff", borderRadius: "12px",
    padding: "20px 24px", marginBottom: "16px",
    boxShadow: "0 4px 16px rgba(0,0,0,0.06)",
    textAlign: "left", transition: "all 0.2s ease",
  },
  cardHeader: {
    display: "flex", justifyContent: "space-between",
    alignItems: "center", marginBottom: "10px",
  },
  badge: {
    color: "#ffffff", fontSize: "11px",
    fontWeight: "700", padding: "3px 10px",
    borderRadius: "999px", marginRight: "8px",
  },
  contradictionBadge: {
    background: "#fef3c7", color: "#b45309",
    fontSize: "11px", fontWeight: "700",
    padding: "3px 10px", borderRadius: "999px",
    marginRight: "8px",
  },
  categoryText: {
    fontSize: "14px", color: "#64748b", fontWeight: "500",
  },
  expandBtn: {
    background: "none", border: "1px solid #e2e8f0",
    borderRadius: "8px", padding: "4px 12px",
    cursor: "pointer", fontSize: "13px", color: "#64748b",
  },
  explanation: {
    fontSize: "15px", color: "#334155",
    lineHeight: "1.6", margin: "8px 0",
  },
  contradictionNote: {
    fontSize: "13px", color: "#b45309",
    background: "#fef3c7", padding: "6px 12px",
    borderRadius: "8px", marginTop: "8px",
  },
  expandedSection: {
    marginTop: "12px", borderTop: "1px solid #f1f5f9",
    paddingTop: "12px",
  },
  clauseText: {
    fontSize: "13px", color: "#94a3b8",
    fontStyle: "italic", lineHeight: "1.5",
  },
  entityText: {
    fontSize: "13px", color: "#475569", marginTop: "6px",
  },
  scoreText: {
    fontSize: "12px", color: "#94a3b8", marginTop: "8px",
  },
  resetBtn: {
    marginTop: "30px", padding: "12px 28px",
    borderRadius: "10px", border: "none",
    background: "#6366f1", color: "#ffffff",
    fontSize: "15px", fontWeight: "600",
    cursor: "pointer",
  },
  disclaimer: {
    marginTop: "16px", fontSize: "13px",
    color: "#94a3b8", fontStyle: "italic",
  },
  trust: {
    marginTop: "24px", fontSize: "13px",
    color: "#94a3b8", zIndex: 1,
  },
};

export default App;