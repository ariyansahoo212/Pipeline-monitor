import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [resultId, setResultId] = useState('');
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState('');
  const [dashboard, setDashboard] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [allResults, setAllResults] = useState(null);
  const [healthHistory, setHealthHistory] = useState([]);

  // Auto-poll dashboard every 10 seconds
  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const res = await axios.get('http://localhost:5003/dashboard');
        setDashboard(res.data);

        const problems = [];
        if (res.data.data_ingestion !== 'healthy') problems.push('❌ Data Ingestion is DOWN');
        if (res.data.processing_engine !== 'healthy') problems.push('❌ Processing Engine is DOWN');
        if (res.data.redis !== 'up') problems.push('❌ Redis is DOWN');

        setAlerts(problems);
      } catch (err) {
        setAlerts(['❌ Failed to reach dashboard API']);
      }
    }, 10000);

    return () => clearInterval(poll);
  }, []);

  const fetchResult = async () => {
    try {
      const res = await axios.get(`http://localhost:5002/results/${resultId}`);
      setResultData(res.data);
      setError('');
    } catch (err) {
      setResultData(null);
      setError('Result not found.');
    }
  };

  const loadAllResults = async () => {
    const res = await axios.get('http://localhost:5002/results');
    setAllResults(res.data);
  };

  const loadHealthLog = async () => {
    const res = await axios.get('http://localhost:5003/healthlog');
    setHealthHistory(res.data.reverse());
  };

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif' }}>
      <h1>📦 Pipeline Result Viewer</h1>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div style={{ backgroundColor: '#ffe6e6', padding: 10, color: '#b30000', marginBottom: 20 }}>
          <strong>⚠️ Alerts:</strong>
          <ul>
            {alerts.map((a, idx) => (
              <li key={idx}>{a}</li>
            ))}
          </ul>
        </div>
      )}

      <input
        type="text"
        placeholder="Enter Result ID"
        value={resultId}
        onChange={(e) => setResultId(e.target.value)}
        style={{ padding: 8, marginRight: 10 }}
      />
      <button onClick={fetchResult}>Fetch Result</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {resultData && (
        <pre style={{ background: '#eee', padding: 10 }}>
          {JSON.stringify(resultData, null, 2)}
        </pre>
      )}

      <hr />

      <h2>🧠 System Health</h2>
      {dashboard && (
        <pre style={{ background: '#f0f0f0', padding: 10 }}>
          {JSON.stringify(dashboard, null, 2)}
        </pre>
      )}

      <hr />

      <h2>📃 All Stored Results</h2>
      <button onClick={loadAllResults}>Show All</button>
      {allResults && (
        <pre style={{ background: '#f8f8f8', padding: 10, marginTop: 10 }}>
          {JSON.stringify(allResults, null, 2)}
        </pre>
      )}

      <hr />

      <h2>📊 Health Log History</h2>
      <button onClick={loadHealthLog}>Show Health Logs</button>
      {healthHistory.length > 0 && (
        <pre style={{ background: '#fdfdfd', padding: 10 }}>
          {JSON.stringify(healthHistory, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;
