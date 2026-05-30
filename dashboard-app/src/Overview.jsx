import { useEffect, useState } from 'react'
import { users } from './api'

const PILL = { safe: ['#E1F5EE','#085041'], low: ['#FAEEDA','#633806'], medium: ['#FAEEDA','#854F0B'], high: ['#FCEBEB','#791F1F'], critical: ['#FCEBEB','#501313'] }

function Pill({ level }) {
  const [bg, col] = PILL[level] || PILL.safe
  return <span style={{ fontSize: 11, fontWeight: 500, padding: '3px 8px', borderRadius: 20, background: bg, color: col }}>{level}</span>
}

function Metric({ label, value, sub, subColor }) {
  return (
    <div style={{ background: '#f1efe8', borderRadius: 8, padding: '14px 16px' }}>
      <div style={{ fontSize: 11, color: '#888', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 500 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: subColor || '#888', marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

export default function Overview() {
  const [usage, setUsage] = useState(null)

  useEffect(() => { users.usage().then(setUsage) }, [])

  const total = usage?.total_scans || 0
  const byPillar = usage?.scans_by_pillar || []
  const limit = usage?.daily_limit || 50

  const PILLAR_COLORS = { shield_id: '#534AB7', shield_phish: '#1D9E75', shield_dev: '#BA7517', shield_soc: '#D85A30' }

  const recentScans = [
    { name: 'KYC image scan', pillar: 'Shield ID', time: '2 mins ago', level: 'high' },
    { name: 'Email analysis', pillar: 'Shield Phish', time: '18 mins ago', level: 'safe' },
    { name: 'auth.py code scan', pillar: 'Shield Dev', time: '1 hour ago', level: 'critical' },
    { name: 'URL scan', pillar: 'Shield Phish', time: '2 hours ago', level: 'medium' },
    { name: 'Log analysis', pillar: 'Shield SOC', time: '3 hours ago', level: 'safe' },
  ]

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <h1 style={{ fontSize: 18, fontWeight: 500 }}>Overview</h1>
        <div style={{ fontSize: 12, color: '#888' }}>Last 30 days</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 24 }}>
        <Metric label="Total scans" value={total.toLocaleString()} sub="All pillars" />
        <Metric label="Daily limit" value={`${Math.min(38, limit)} / ${limit}`} sub={limit > 0 ? `${Math.round((38/limit)*100)}% used` : 'Unlimited'} subColor={38/limit > 0.8 ? '#854F0B' : '#0F6E56'} />
        <Metric label="Pillars active" value={byPillar.length || 4} sub="of 4" />
        <Metric label="Threats found" value="47" sub="3 critical" subColor="#A32D2D" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 16 }}>
        <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Recent scans</div>
          {recentScans.map((s, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 0', borderBottom: i < recentScans.length - 1 ? '0.5px solid #f0eee8' : 'none' }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{s.name}</div>
                <div style={{ fontSize: 11, color: '#aaa' }}>{s.pillar} · {s.time}</div>
              </div>
              <Pill level={s.level} />
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Scans by pillar</div>
            {(byPillar.length ? byPillar : [
              { pillar: 'shield_id', count: 924 }, { pillar: 'shield_phish', count: 212 },
              { pillar: 'shield_dev', count: 98 }, { pillar: 'shield_soc', count: 50 }
            ]).map(p => {
              const max = 924
              return (
                <div key={p.pillar} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0' }}>
                  <div style={{ fontSize: 12, color: '#666', minWidth: 80 }}>{p.pillar.replace('_', ' ')}</div>
                  <div style={{ flex: 1, height: 5, background: '#f1efe8', borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${Math.round((p.count/max)*100)}%`, background: PILLAR_COLORS[p.pillar] || '#534AB7', borderRadius: 4 }} />
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 500, minWidth: 32 }}>{p.count}</div>
                </div>
              )
            })}
          </div>

          <div style={{ background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Alerts</div>
            {[
              { msg: 'SQL injection in auth.py', color: '#E24B4A', time: '1hr ago' },
              { msg: 'Deepfake KYC flagged', color: '#E24B4A', time: '2hr ago' },
              { msg: 'Phishing URL blocked', color: '#BA7517', time: '3hr ago' },
            ].map((a, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, padding: '6px 0', borderBottom: i < 2 ? '0.5px solid #f0eee8' : 'none' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: a.color, marginTop: 4, flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 500 }}>{a.msg}</div>
                  <div style={{ fontSize: 11, color: '#aaa' }}>{a.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
