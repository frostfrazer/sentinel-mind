import { useState } from 'react'
import { scans, users } from './api'

const PILL = { safe: ['#E1F5EE','#085041'], low: ['#FAEEDA','#633806'], medium: ['#FAEEDA','#854F0B'], high: ['#FCEBEB','#791F1F'], critical: ['#FCEBEB','#501313'] }

function Pill({ level }) {
  const [bg, col] = PILL[level?.toLowerCase()] || PILL.safe
  return <span style={{ fontSize: 11, fontWeight: 500, padding: '3px 9px', borderRadius: 20, background: bg, color: col }}>{level}</span>
}

function Card({ children, style }) {
  return <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16, ...style }}>{children}</div>
}

export default function ShieldID() {
  const [tab, setTab] = useState('image')
  const [apiKey, setApiKey] = useState('')
  const [imageB64, setImageB64] = useState('')
  const [docB64, setDocB64] = useState('')
  const [docType, setDocType] = useState('id_card')
  const [context, setContext] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toB64 = (file) => new Promise((res, rej) => {
    const r = new FileReader()
    r.onload = () => res(r.result.split(',')[1])
    r.onerror = rej
    r.readAsDataURL(file)
  })

  const handleFile = async (e, setter) => {
    const file = e.target.files[0]
    if (!file) return
    const b64 = await toB64(file)
    setter(b64)
  }

  const run = async () => {
    if (!apiKey) { setError('Enter your API key'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const res = tab === 'image'
        ? await scans.image(apiKey, { image_base64: imageB64, context })
        : await scans.image(apiKey, { image_base64: docB64, context: docType })
      setResult(res)
    } catch(e) { setError(e.message) }
    setLoading(false)
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 4 }}>Shield ID</h1>
        <p style={{ fontSize: 13, color: '#888' }}>Detect deepfake faces, cloned voices, and forged identity documents</p>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>API Key</div>
        <input placeholder="sm_live_..." value={apiKey} onChange={e => setApiKey(e.target.value)} style={{ width: '100%', fontFamily: 'monospace', fontSize: 12 }} />
      </Card>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {['image','document'].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ padding: '7px 16px', borderRadius: 8, fontSize: 13, fontWeight: tab===t?500:400, background: tab===t?'#534AB7':'transparent', color: tab===t?'#fff':'#666', border: `0.5px solid ${tab===t?'#534AB7':'#e0ded8'}`, cursor: 'pointer' }}>
            {t === 'image' ? '👁 Face / Image' : '🪪 Document'}
          </button>
        ))}
      </div>

      <Card style={{ marginBottom: 16 }}>
        {tab === 'image' ? (
          <>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Upload image to scan</div>
            <input type="file" accept="image/*" onChange={e => handleFile(e, setImageB64)} style={{ marginBottom: 10 }} />
            {imageB64 && <img src={`data:image/jpeg;base64,${imageB64}`} style={{ width: 120, height: 120, objectFit: 'cover', borderRadius: 8, marginBottom: 10, display: 'block' }} alt="preview" />}
            <input placeholder="Context (e.g. KYC verification)" value={context} onChange={e => setContext(e.target.value)} style={{ width: '100%' }} />
          </>
        ) : (
          <>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Upload identity document</div>
            <select value={docType} onChange={e => setDocType(e.target.value)} style={{ marginBottom: 10, width: '100%' }}>
              <option value="id_card">National ID</option>
              <option value="passport">Passport</option>
              <option value="drivers_license">Driver's License</option>
            </select>
            <input type="file" accept="image/*" onChange={e => handleFile(e, setDocB64)} />
          </>
        )}

        {error && <div style={{ background: '#FCEBEB', color: '#791F1F', fontSize: 12, padding: '8px 12px', borderRadius: 8, marginTop: 10 }}>{error}</div>}

        <button onClick={run} disabled={loading || (!imageB64 && !docB64)} style={{ marginTop: 14, padding: '9px 20px', background: '#534AB7', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer', opacity: loading?0.7:1 }}>
          {loading ? 'Scanning...' : 'Run scan'}
        </button>
      </Card>

      {result && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Scan result</div>
            <Pill level={result.threat_level} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 14 }}>
            {[
              ['Synthetic', result.is_synthetic ? '⚠ Yes' : '✓ No'],
              ['Confidence', `${Math.round((result.confidence||0)*100)}%`],
              ['Threat level', result.threat_level],
              ['Scan ID', result.scan_id?.slice(0,8)+'...'],
            ].map(([k,v]) => (
              <div key={k} style={{ background: '#f9f8f5', borderRadius: 8, padding: '10px 12px' }}>
                <div style={{ fontSize: 11, color: '#aaa', marginBottom: 3 }}>{k}</div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{v}</div>
              </div>
            ))}
          </div>
          {result.signals?.length > 0 && (
            <div>
              <div style={{ fontSize: 12, fontWeight: 500, marginBottom: 6 }}>Signals detected</div>
              {result.signals.map((s,i) => (
                <div key={i} style={{ fontSize: 12, color: '#555', padding: '4px 0', borderBottom: '0.5px solid #f0eee8', display: 'flex', gap: 8 }}>
                  <span style={{ color: '#E24B4A' }}>→</span>{s}
                </div>
              ))}
            </div>
          )}
          <div style={{ marginTop: 12, fontSize: 12, background: '#f9f8f5', padding: '10px 12px', borderRadius: 8 }}>
            <strong>Recommendation:</strong> {result.recommendation}
          </div>
        </Card>
      )}
    </div>
  )
}
