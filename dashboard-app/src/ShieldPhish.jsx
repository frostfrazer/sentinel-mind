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

export default function ShieldPhish() {
  const [tab, setTab] = useState('url')
  const [apiKey, setApiKey] = useState('')
  const [url, setUrl] = useState('')
  const [email, setEmail] = useState({ subject: '', sender: '', body: '' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    if (!apiKey) { setError('Enter your API key'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const res = tab === 'url'
        ? await scans.url(apiKey, url)
        : await scans.email(apiKey, email)
      setResult(res)
    } catch(e) { setError(e.message) }
    setLoading(false)
  }

  const ATTACK_COLORS = { 'Phishing': '#E24B4A', 'BEC': '#BA7517', 'Spear phishing': '#D85A30', 'Malware': '#A32D2D' }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 4 }}>Shield Phish</h1>
        <p style={{ fontSize: 13, color: '#888' }}>Detect phishing emails, malicious URLs, and social engineering attacks</p>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>API Key</div>
        <input placeholder="sm_live_..." value={apiKey} onChange={e => setApiKey(e.target.value)} style={{ width: '100%', fontFamily: 'monospace', fontSize: 12 }} />
      </Card>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {['url','email'].map(t => (
          <button key={t} onClick={() => { setTab(t); setResult(null) }} style={{ padding: '7px 16px', borderRadius: 8, fontSize: 13, fontWeight: tab===t?500:400, background: tab===t?'#1D9E75':'transparent', color: tab===t?'#fff':'#666', border: `0.5px solid ${tab===t?'#1D9E75':'#e0ded8'}`, cursor: 'pointer' }}>
            {t === 'url' ? '🔗 URL scan' : '✉ Email scan'}
          </button>
        ))}
      </div>

      <Card style={{ marginBottom: 16 }}>
        {tab === 'url' ? (
          <>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Enter URL to scan</div>
            <input placeholder="https://suspicious-link.xyz/verify" value={url} onChange={e => setUrl(e.target.value)} style={{ width: '100%' }} onKeyDown={e => e.key==='Enter' && run()} />
            <div style={{ fontSize: 11, color: '#aaa', marginTop: 6 }}>Try: http://paypa1-secure-login.xyz/verify</div>
          </>
        ) : (
          <>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Paste email details</div>
            <input placeholder="Sender email" value={email.sender} onChange={e => setEmail(x=>({...x,sender:e.target.value}))} style={{ width: '100%', marginBottom: 8 }} />
            <input placeholder="Subject line" value={email.subject} onChange={e => setEmail(x=>({...x,subject:e.target.value}))} style={{ width: '100%', marginBottom: 8 }} />
            <textarea placeholder="Email body..." value={email.body} onChange={e => setEmail(x=>({...x,body:e.target.value}))} rows={5} style={{ width: '100%', resize: 'vertical', padding: 8, border: '0.5px solid #e0ded8', borderRadius: 8, fontSize: 13, fontFamily: 'inherit' }} />
          </>
        )}

        {error && <div style={{ background: '#FCEBEB', color: '#791F1F', fontSize: 12, padding: '8px 12px', borderRadius: 8, marginTop: 10 }}>{error}</div>}

        <button onClick={run} disabled={loading || (tab==='url'?!url:!email.body)} style={{ marginTop: 14, padding: '9px 20px', background: '#1D9E75', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer', opacity: loading?0.7:1 }}>
          {loading ? 'Scanning...' : 'Run scan'}
        </button>
      </Card>

      {result && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Scan result</div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              {result.attack_type && <span style={{ fontSize: 11, fontWeight: 500, padding: '3px 9px', borderRadius: 20, background: '#FAEEDA', color: '#633806' }}>{result.attack_type}</span>}
              <Pill level={result.threat_level} />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 14 }}>
            {[
              ['Phishing', result.is_phishing ? '⚠ Detected' : '✓ Clean'],
              ['Confidence', `${Math.round((result.confidence||0)*100)}%`],
              ['Attack type', result.attack_type || 'None'],
              ['Scan ID', result.scan_id?.slice(0,8)+'...'],
            ].map(([k,v]) => (
              <div key={k} style={{ background: '#f9f8f5', borderRadius: 8, padding: '10px 12px' }}>
                <div style={{ fontSize: 11, color: '#aaa', marginBottom: 3 }}>{k}</div>
                <div style={{ fontSize: 13, fontWeight: 500, color: k==='Phishing'&&result.is_phishing?'#A32D2D':undefined }}>{v}</div>
              </div>
            ))}
          </div>
          {result.signals?.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 500, marginBottom: 6 }}>Signals detected</div>
              {result.signals.map((s,i) => (
                <div key={i} style={{ fontSize: 12, color: '#555', padding: '4px 0', borderBottom: '0.5px solid #f0eee8', display: 'flex', gap: 8 }}>
                  <span style={{ color: '#E24B4A' }}>→</span>{s}
                </div>
              ))}
            </div>
          )}
          <div style={{ fontSize: 12, background: '#f9f8f5', padding: '10px 12px', borderRadius: 8 }}>
            <strong>Recommendation:</strong> {result.recommendation}
          </div>
        </Card>
      )}
    </div>
  )
}
