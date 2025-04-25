import React, { useState, useRef } from 'react';

const loadingMessages = [
  'Submitting claim…',
  'Gathering sources…',
  'Analyzing data…',
  'Finalizing verdict…',
];

const styles = {
  container: {
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
    maxWidth: 600,
    margin: '80px auto',
    padding: '0 20px',
    color: '#222',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 600,
    textAlign: 'center',
    marginBottom: '40px',
  },
  input: {
    width: '100%',
    padding: '14px 16px',
    fontSize: '1rem',
    borderRadius: 8,
    border: '1px solid #ddd',
    marginBottom: 12,
    boxSizing: 'border-box',
    outline: 'none',
  },
  inputFocus: {
    borderColor: '#0070f3',
    boxShadow: '0 0 0 2px rgba(0, 112, 243, 0.2)',
  },
  button: {
    width: '100%',
    padding: '14px',
    fontSize: '1rem',
    borderRadius: 8,
    border: 'none',
    backgroundColor: '#0070f3',
    color: '#fff',
    cursor: 'pointer',
  },
  buttonDisabled: {
    backgroundColor: '#a0c4ff',
    cursor: 'not-allowed',
  },
  status: {
    fontStyle: 'italic',
    color: '#555',
    marginTop: 12,
    textAlign: 'center',
  },
  card: {
    background: '#fafafa',
    marginTop: '32px',
    padding: '24px',
    borderRadius: 8,
    boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
    lineHeight: 1.6,
  },
  verdict: {
    display: 'inline-block',
    marginLeft: 8,
    padding: '4px 12px',
    borderRadius: 4,
    color: '#fff',
    backgroundColor: '#28a745',
  },
  verdictFalse: {
    backgroundColor: '#dc3545',
  },
  link: {
    color: '#0070f3',
    textDecoration: 'none',
  },
};

function App() {
  const [claim, setClaim] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusIndex, setStatusIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const intervalRef = useRef(null);

  const checkClaim = async () => {
    if (!claim.trim()) return;

    // start loading states
    setResult(null);
    setError('');
    setLoading(true);
    setStatusIndex(0);
    intervalRef.current = setInterval(() => {
      setStatusIndex(i => (i + 1) % loadingMessages.length);
    }, 2000);

    try {
      const res = await fetch('/fact-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claim }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Unknown error');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      clearInterval(intervalRef.current);
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>veritas.ai</h1>

      <input
        style={{
          ...styles.input,
          ...(loading ? { opacity: 0.6 } : {}),
        }}
        type="text"
        value={claim}
        placeholder="Enter a claim to check…"
        onChange={e => setClaim(e.target.value)}
        disabled={loading}
        onFocus={e => Object.assign(e.target.style, styles.inputFocus)}
        onBlur={e => {
          e.target.style.borderColor = styles.input.border.split(' ')[2];
          e.target.style.boxShadow = 'none';
        }}
      />

      <button
        style={{
          ...styles.button,
          ...(!claim.trim() || loading ? styles.buttonDisabled : {}),
        }}
        onClick={checkClaim}
        disabled={!claim.trim() || loading}
      >
        {loading ? 'Checking…' : 'Check Claim'}
      </button>

      {loading && (
        <div style={styles.status}>
          {loadingMessages[statusIndex]}
        </div>
      )}

      {(error || result) && (
        <div style={styles.card}>
          {error && <p style={{ color: '#dc3545' }}>❌ {error}</p>}

          {result && (
            <>
              <h3>
                ✅ Verdict:
                <span
                  style={{
                    ...styles.verdict,
                    ...(result.verdict !== 'True' && styles.verdictFalse),
                  }}
                >
                  {result.verdict}
                </span>
              </h3>

              <p>
                <strong>Justification:</strong> {result.justification}
              </p>

              <h4>📚 Sources:</h4>
              <ul>
                {result.evidence_used.map((url, i) => (
                  <li key={i}>
                    <a
                      href={url}
                      target="_blank"
                      rel="noreferrer"
                      style={styles.link}
                    >
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;