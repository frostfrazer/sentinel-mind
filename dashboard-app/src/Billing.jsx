import { useEffect, useState } from 'react'
import { billing } from './api'

const PLANS = [
  { key: 'free', name: 'Free', price: 'KES 0', sub: 'forever', color: '#888', features: ['50 scans/day', 'Face deepfake detection', 'URL scanning', 'Code vulnerability scan', '2 API keys', '7-day history'] },
  { key: 'starter', name: 'Starter', price: 'KES 6,500', sub: '/month', color: '#0F6E56', features: ['500 scans/day', 'Email & URL phishing', 'Document forgery detection', 'Log analysis', '10 API keys', '3 team members', '30-day history', 'Email support'] },
  { key: 'pro', name: 'Pro', price: 'KES 26,000', sub: '/month', color: '#534AB7', popular: true, features: ['5,000 scans/day', 'All 4 pillars', 'Voice clone detection', 'CI/CD integration', 'Real-time alerts', 'Auto-remediation', '50 API keys', '15 members', '1-year history', 'Priority support'] },
  { key: 'enterprise', name: 'Enterprise', price: 'Custom', sub: 'annual', color: '#854F0B', features: ['Unlimited scans', 'Everything in Pro', 'SIEM/SOAR integration', 'SSO / SAML', 'Custom data region', 'Dedicated CSM', '99.99% SLA'] },
]

export default function Billing() {
  const [current, setCurrent] = useState(null)
  const [loading, setLoading] = useState(null)

  useEffect(() => { billing.status().then(setCurrent) }, [])

  const upgrade = async (plan) => {
    if (plan === 'enterprise') {
      window.open('mailto:sales@sentinelmind.com?subject=Enterprise inquiry', '_blank')
      return
    }
    setLoading(plan)
    const res = await billing.checkout(plan, window.location.href)
    setLoading(null)
    if (res.checkout_url) window.location.href = res.checkout_url
    else alert(res.detail || 'Checkout failed — add your Paystack key to .env')
  }

  return (
    <div>
      <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 8 }}>Billing & plans</h1>
      {current && <p style={{ fontSize: 13, color: '#888', marginBottom: 24 }}>Current plan: <strong>{current.plan}</strong> · {current.daily_limit === -1 ? 'Unlimited' : current.daily_limit} scans/day</p>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
        {PLANS.map(p => (
          <div key={p.key} style={{ background: '#fff', border: p.popular ? `2px solid #534AB7` : '0.5px solid #e0ded8', borderRadius: 12, padding: 16, position: 'relative', display: 'flex', flexDirection: 'column' }}>
            {p.popular && <div style={{ position: 'absolute', top: -1, left: 16, fontSize: 10, fontWeight: 500, background: '#EEEDFE', color: '#3C3489', padding: '3px 10px', borderRadius: '0 0 8px 8px' }}>Most popular</div>}
            <div style={{ marginTop: p.popular ? 12 : 0 }}>
              <div style={{ fontSize: 15, fontWeight: 500, marginBottom: 4 }}>{p.name}</div>
              <div style={{ fontSize: 22, fontWeight: 500, color: p.color }}>{p.price}</div>
              <div style={{ fontSize: 11, color: '#aaa', marginBottom: 16 }}>{p.sub}</div>
              <div style={{ flex: 1 }}>
                {p.features.map(f => (
                  <div key={f} style={{ display: 'flex', gap: 6, fontSize: 12, color: '#555', marginBottom: 6 }}>
                    <span style={{ color: '#0F6E56', flexShrink: 0 }}>✓</span>{f}
                  </div>
                ))}
              </div>
            </div>
            <button
              onClick={() => upgrade(p.key)}
              disabled={current?.plan === p.key || loading === p.key}
              style={{ marginTop: 16, width: '100%', padding: '9px', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: current?.plan === p.key ? 'default' : 'pointer', background: current?.plan === p.key ? '#f1efe8' : p.popular ? '#534AB7' : 'transparent', color: current?.plan === p.key ? '#aaa' : p.popular ? '#fff' : p.color, border: `0.5px solid ${current?.plan === p.key ? '#e0ded8' : p.color}` }}
            >
              {loading === p.key ? 'Loading...' : current?.plan === p.key ? 'Current plan' : p.key === 'enterprise' ? 'Contact sales' : 'Upgrade'}
            </button>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 24, background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 12, padding: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 8 }}>Payment powered by Paystack</div>
        <p style={{ fontSize: 12, color: '#888' }}>Payments via card, M-Pesa, mobile money, and bank transfer. Billed in KES. Cancel anytime from your Paystack account.</p>
      </div>
    </div>
  )
}
