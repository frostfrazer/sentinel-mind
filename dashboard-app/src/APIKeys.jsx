import { useEffect, useState } from 'react'
import { users } from './api'

export default function APIKeys() {
  const [keys, setKeys] = useState([])
  const [name, setName] = useState('')
  const [newKey, setNewKey] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => { users.apiKeys().then(setKeys) }, [])

  const create = async () => {
    if (!name.trim()) return
    setLoading(true)
    const res = await users.createKey(name)
    if (res.raw_key) {
      setNewKey(res.raw_key)
      setName('')
      users.apiKeys().then(setKeys)
    }
    setLoading(false)
  }

  const revoke = async (id) => {
    await users.revokeKey(id)
    setKeys(k => k.filter(x => x.id !== id))
  }

  const copy = () => {
    navigator.clipboard.writeText(newKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div>
      <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 24 }}>API keys</h1>

      {newKey && (
        <div style={{ background: '#E1F5EE', border: '0.5px solid #9FE1CB', borderRadius: 12, padding: 16, marginBottom: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 500, color: '#085041', marginBottom: 8 }}>⚠ Copy this key now — it will never be shown again</div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <code style={{ flex: 1, fontSize: 12, background: '#fff', padding: '8px 12px', borderRadius: 8, wordBreak: 'break-all' }}>{newKey}</code>
            <button onClick={copy} style={{ fontSize: 12, padding: '8px 12px', borderRadius: 8, border: '0.5px solid #9FE1CB', background: '#fff', cursor: 'pointer', color: '#085041', whiteSpace: 'nowrap' }}>
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </div>
          <button onClick={() => setNewKey(null)} style={{ fontSize: 11, color: '#0F6E56', background: 'none', border: 'none', cursor: 'pointer', marginTop: 8 }}>Dismiss</button>
        </div>
      )}

      <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16, marginBottom: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Create new key</div>
        <div style={{ display: 'flex', gap: 10 }}>
          <input placeholder="Key name (e.g. Production)" value={name} onChange={e => setName(e.target.value)} onKeyDown={e => e.key === 'Enter' && create()} style={{ flex: 1 }} />
          <button onClick={create} disabled={loading || !name.trim()} style={{ padding: '8px 16px', background: '#534AB7', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? '...' : 'Create'}
          </button>
        </div>
      </div>

      <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Active keys</div>
        {keys.length === 0 && <div style={{ fontSize: 13, color: '#aaa', textAlign: 'center', padding: 20 }}>No API keys yet — create one above</div>}
        {keys.map((k, i) => (
          <div key={k.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: i < keys.length - 1 ? '0.5px solid #f0eee8' : 'none' }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 500 }}>{k.name}</div>
              <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                <code>{k.key_prefix}</code> · {k.scans_total} scans · Created {new Date(k.created_at).toLocaleDateString()}
              </div>
            </div>
            <div style={{ display: 'flex', align: 'center', gap: 8 }}>
              <span style={{ fontSize: 11, color: k.is_active ? '#0F6E56' : '#aaa' }}>● {k.is_active ? 'Active' : 'Inactive'}</span>
              <button onClick={() => revoke(k.id)} style={{ fontSize: 11, color: '#A32D2D', background: 'none', border: '0.5px solid #f0e0e0', borderRadius: 6, padding: '4px 10px', cursor: 'pointer' }}>Revoke</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
