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

const SAMPLE_CODE = `import sqlite3

password = "admin123"
API_KEY = "sk-prod-xK9pMt2rQw8nLv4j"

def get_user(user_input):
    conn = sqlite3.connect("db.sqlite")
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return conn.execute(query).fetchall()
`

const SEVERITY_COLORS = { critical: '#501313', high: '#791F1F', medium: '#854F0B', low: '#633806' }
const SEVERITY_BG = { critical: '#FCEBEB', high: '#FCEBEB', medium: '#FAEEDA', low: '#FAEEDA' }

export default function ShieldDev() {
  const [apiKey, setApiKey] = useState('')
  const [code, setCode] = useState(SAMPLE_CODE)
  const [language, setLanguage] = useState('python')
  const [filename, setFilename] = useState('auth.py')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    if (!apiKey) { setError('Enter your API key'); return }
    if (!code.trim()) { setError('Enter some code to scan'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await scans.code(apiKey, { code, language, filename })
      setResult(res)
    } catch(e) { setError(e.message) }
    setLoading(false)
  }

  const riskColor = (score) => {
    if (score >= 8) return '#E24B4A'
    if (score >= 6) return '#D85A30'
    if (score >= 4) return '#BA7517'
    return '#1D9E75'
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 4 }}>Shield Dev</h1>
        <p style={{ fontSize: 13, color: '#888' }}>Scan code for vulnerabilities, hardcoded secrets, and security issues</p>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>API Key</div>
        <input placeholder="sm_live_..." value={apiKey} onChange={e => setApiKey(e.target.value)} style={{ width: '100%', fontFamily: 'monospace', fontSize: 12 }} />
      </Card>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Language</div>
            <select value={language} onChange={e => setLanguage(e.target.value)} style={{ width: '100%' }}>
              {['python','javascript','typescript','java','go','php','ruby','rust','c','cpp'].map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
          <div style={{ flex: 2 }}>
            <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Filename (optional)</div>
            <input placeholder="auth.py" value={filename} onChange={e => setFilename(e.target.value)} />
          </div>
        </div>
        <div style={{ fontSize: 12, color: '#888', marginBottom: 6 }}>Code to scan</div>
        <textarea value={code} onChange={e => setCode(e.target.value)} rows={12} style={{ width: '100%', fontFamily: 'monospace', fontSize: 12, resize: 'vertical', padding: 10, border: '0.5px solid #e0ded8', borderRadius: 8, background: '#faf9f6', lineHeight: 1.6 }} />

        {error && <div style={{ background: '#FCEBEB', color: '#791F1F', fontSize: 12, padding: '8px 12px', borderRadius: 8, marginTop: 10 }}>{error}</div>}

        <button onClick={run} disabled={loading} style={{ marginTop: 12, padding: '9px 20px', background: '#BA7517', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer', opacity: loading?0.7:1 }}>
          {loading ? 'Scanning...' : 'Scan code'}
        </button>
      </Card>

      {result && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 16 }}>
            <div style={{ background: '#f9f8f5', borderRadius: 10, padding: '14px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 500, color: riskColor(result.risk_score) }}>{result.risk_score?.toFixed(1)}</div>
              <div style={{ fontSize: 11, color: '#aaa' }}>Risk score / 10</div>
            </div>
            <div style={{ background: '#f9f8f5', borderRadius: 10, padding: '14px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 500, color: result.vulnerabilities?.length>0?'#E24B4A':'#1D9E75' }}>{result.vulnerabilities?.length || 0}</div>
              <div style={{ fontSize: 11, color: '#aaa' }}>Vulnerabilities</div>
            </div>
            <div style={{ background: '#f9f8f5', borderRadius: 10, padding: '14px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 500, color: result.secrets_found?.length>0?'#D85A30':'#1D9E75' }}>{result.secrets_found?.length || 0}</div>
              <div style={{ fontSize: 11, color: '#aaa' }}>Secrets found</div>
            </div>
          </div>

          {result.vulnerabilities?.length > 0 && (
            <Card style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Vulnerabilities</div>
              {result.vulnerabilities.map((v, i) => (
                <div key={i} style={{ padding: '10px 0', borderBottom: i<result.vulnerabilities.length-1?'0.5px solid #f0eee8':'none' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{ fontSize: 11, fontWeight: 500, padding: '2px 8px', borderRadius: 20, background: SEVERITY_BG[v.severity?.toLowerCase()]||'#FAEEDA', color: SEVERITY_COLORS[v.severity?.toLowerCase()]||'#633806' }}>{v.severity}</span>
                    <span style={{ fontSize: 13, fontWeight: 500 }}>{v.type}</span>
                    {v.line && <span style={{ fontSize: 11, color: '#aaa' }}>line {v.line}</span>}
                  </div>
                  <div style={{ fontSize: 12, color: '#555', marginBottom: 4 }}>{v.description}</div>
                  {v.fix && <div style={{ fontSize: 12, color: '#0F6E56', background: '#E1F5EE', padding: '6px 10px', borderRadius: 6 }}>Fix: {v.fix}</div>}
                </div>
              ))}
            </Card>
          )}

          {result.secrets_found?.length > 0 && (
            <Card style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Secrets detected</div>
              {result.secrets_found.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderBottom: i<result.secrets_found.length-1?'0.5px solid #f0eee8':'none' }}>
                  <span style={{ fontSize: 11, fontWeight: 500, padding: '2px 8px', borderRadius: 20, background: '#FAECE7', color: '#993C1D' }}>{s.type}</span>
                  <code style={{ fontSize: 11, color: '#666', flex: 1 }}>{s.masked_value}</code>
                  {s.line && <span style={{ fontSize: 11, color: '#aaa' }}>line {s.line}</span>}
                </div>
              ))}
            </Card>
          )}

          {result.fix_suggestions?.length > 0 && (
            <Card>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Recommended fixes</div>
              {result.fix_suggestions.map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, fontSize: 12, color: '#444', padding: '5px 0', borderBottom: i<result.fix_suggestions.length-1?'0.5px solid #f0eee8':'none' }}>
                  <span style={{ color: '#534AB7', fontWeight: 500, flexShrink: 0 }}>{i+1}.</span>{f}
                </div>
              ))}
            </Card>
          )}
        </>
      )}
    </div>
  )
}
