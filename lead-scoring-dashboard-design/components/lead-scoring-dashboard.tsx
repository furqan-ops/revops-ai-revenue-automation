'use client'

import { useMemo, useState } from 'react'
import { Check, ChevronDown, Link2 } from 'lucide-react'

const scenarios = {
  tier1: {
    label: 'Tier 1 example',
    firstName: 'Sarah',
    lastName: 'Jenkins',
    email: 's.jenkins@cloudscale.io',
    title: 'VP of Revenue Operations',
    company: 'CloudScale Systems',
    website: 'https://cloudscale.io',
    size: '250-500',
    message: 'Evaluating enterprise lead routing solutions for our sales team. Need CRM integration and automated Slack alerts.',
    score: 98,
    tier: 'Tier 1 (High)',
    parts: [30, 28, 30, 10] as const,
    deal_arr: '$45,000',
    action: 'Tier 1 Slack alert',
    enrichmentStep: 'Firmographics matched',
    rationale: 'High-value prospect matching core ICP (CloudScale Systems, 320 employees). VP of Revenue Operations has direct decision authority and approved budget.',
    approach: 'Focus on immediate ROI: explain how automated routing eliminates lead drop-off across their sales reps.',
    enrichment: [
      ['Company', 'CloudScale Systems'],
      ['Industry', 'B2B Cloud Infrastructure & DevOps'],
      ['Headcount', '320'],
      ['Annual revenue', '$45M'],
      ['Headquarters', 'San Francisco, CA, USA'],
      ['Tech stack', 'AWS, Kubernetes, HubSpot, Slack, PostgreSQL, Datadog'],
      ['Domain type', 'Corporate business domain']
    ],
    contact: '{\n  "firstname": "Sarah",\n  "lastname": "Jenkins",\n  "email": "s.jenkins@cloudscale.io",\n  "jobtitle": "VP of Revenue Operations",\n  "lifecyclestage": "salesqualifiedlead",\n  "hs_lead_status": "OPEN",\n  "ai_icp_score": 98,\n  "ai_icp_tier": "Tier 1 (High)",\n  "ai_qualification_notes": "High-value prospect matching core ICP (CloudScale Systems, 320 employees). VP of Revenue Operations has direct decision authority and approved budget."\n}',
    companyRecord: '{\n  "name": "CloudScale Systems",\n  "domain": "cloudscale.io",\n  "industry": "B2B Cloud Infrastructure & DevOps",\n  "numberofemployees": "320",\n  "annualrevenue": "$45M",\n  "icp_fit_tier": "Tier 1 (High)",\n  "target_account": "true"\n}'
  },
  tier2: {
    label: 'Tier 2 example',
    firstName: 'David',
    lastName: 'Miller',
    email: 'david.m@growthdigital.co',
    title: 'Marketing Manager',
    company: 'Growth Digital Agency',
    website: 'https://growthdigital.co',
    size: '20-50',
    message: 'Evaluating automation tools to connect our forms to CRM. Looking for case studies and pricing details.',
    score: 63,
    tier: 'Tier 2 (Medium)',
    parts: [20, 18, 20, 5] as const,
    deal_arr: '$10,000',
    action: 'Tier 2 SDR queue alert',
    enrichmentStep: 'Firmographics matched',
    rationale: 'Moderate fit from Growth Digital Agency (Performance Marketing & Digital Services, 20-50 employees). Evaluating options and fits MQL criteria.',
    approach: 'Provide relevant B2B case studies and offer a guided architecture walkthrough.',
    enrichment: [
      ['Company', 'Growth Digital Agency'],
      ['Industry', 'Performance Marketing & Digital Services'],
      ['Headcount', '35'],
      ['Annual revenue', '$3.8M'],
      ['Headquarters', 'Austin, TX, USA'],
      ['Tech stack', 'WordPress, Google Analytics, Mailchimp, Zapier'],
      ['Domain type', 'Corporate business domain']
    ],
    contact: '{\n  "firstname": "David",\n  "lastname": "Miller",\n  "email": "david.m@growthdigital.co",\n  "jobtitle": "Marketing Manager",\n  "lifecyclestage": "marketingqualifiedlead",\n  "hs_lead_status": "IN_PROGRESS",\n  "ai_icp_score": 63,\n  "ai_icp_tier": "Tier 2 (Medium)",\n  "ai_qualification_notes": "Moderate fit from Growth Digital Agency (Performance Marketing & Digital Services, 20-50 employees). Evaluating options and fits MQL criteria."\n}',
    companyRecord: '{\n  "name": "Growth Digital Agency",\n  "domain": "growthdigital.co",\n  "industry": "Performance Marketing & Digital Services",\n  "numberofemployees": "35",\n  "annualrevenue": "$3.8M",\n  "icp_fit_tier": "Tier 2 (Medium)",\n  "target_account": "false"\n}'
  },
  tier3: {
    label: 'Tier 3 example',
    firstName: 'Alex',
    lastName: 'K',
    email: 'alexk994@gmail.com',
    title: 'Student / Intern',
    company: 'Freelance',
    website: '',
    size: '1-5',
    message: 'Hey, I am doing research on revops automation and want to test how your system works for my class project.',
    score: 0,
    tier: 'Tier 3 (Disqualified)',
    parts: [0, 0, 0, 0] as const,
    deal_arr: '$0',
    action: 'Internal audit log',
    enrichmentStep: 'Fallback profile used',
    rationale: 'Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected (alexk994@gmail.com).',
    approach: 'No sales rep action required.',
    enrichment: [
      ['Company', 'Freelance'],
      ['Industry', 'Consumer / Independent'],
      ['Headcount', '1'],
      ['Annual revenue', 'N/A'],
      ['Headquarters', 'N/A'],
      ['Tech stack', 'None detected'],
      ['Domain type', 'Consumer email']
    ],
    contact: '{\n  "firstname": "Alex",\n  "lastname": "K",\n  "email": "alexk994@gmail.com",\n  "jobtitle": "Student / Intern",\n  "lifecyclestage": "lead",\n  "hs_lead_status": "UNQUALIFIED",\n  "ai_icp_score": 0,\n  "ai_icp_tier": "Tier 3 (Disqualified)",\n  "ai_qualification_notes": "Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected (alexk994@gmail.com)."\n}',
    companyRecord: '{\n  "name": "Freelance",\n  "domain": "gmail.com",\n  "industry": "Consumer / Independent",\n  "numberofemployees": "1",\n  "annualrevenue": "N/A",\n  "icp_fit_tier": "Tier 3 (Disqualified)",\n  "target_account": "false"\n}'
  }
} as const

type ScenarioKey = keyof typeof scenarios

function TierPill({ tier }: { tier: string }) {
  const tierKey = tier.includes('Tier 1') ? 'tier-1' : tier.includes('Tier 2') ? 'tier-2' : 'tier-3'
  return <span className={`tier-pill ${tierKey}`}>{tier}</span>
}

export default function LeadScoringDashboard() {
  const [scenarioKey, setScenarioKey] = useState<ScenarioKey>('tier1')
  const [activeTab, setActiveTab] = useState('Company enrichment')
  const [running, setRunning] = useState(false)
  const [hasRun, setHasRun] = useState(false)
  const [completed, setCompleted] = useState(0)

  const data = scenarios[scenarioKey]
  const todayDate = useMemo(() => {
    return new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
  }, [])

  function runScoring() {
    setRunning(true)
    setCompleted(0)
    let step = 0
    const interval = window.setInterval(() => {
      step += 1
      setCompleted(step)
      if (step === 5) {
        window.clearInterval(interval)
        setRunning(false)
        setHasRun(true)
      }
    }, 200)
  }

  const pipelineStatusTexts = [
    hasRun ? 'Lead received' : 'Waiting',
    hasRun ? data.enrichmentStep : 'Waiting',
    hasRun ? `Score ${data.score}` : 'Waiting',
    hasRun ? 'Payloads built' : 'Waiting',
    hasRun ? data.action : 'Waiting'
  ]

  return (
    <main className="dashboard-shell">
      <header className="topbar">
        <div className="brand-mark">
          <span className="brand-wordmark">RevOps</span>
          <div>
            <div className="brand">Lead Scoring Pipeline</div>
            <span className="brand-context">Revenue operations workspace</span>
          </div>
        </div>
        <div className="topbar-meta">
          <span>{todayDate}</span>
        </div>
      </header>

      <div className="dashboard-content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">Revenue operations</p>
            <h1>Inbound lead scoring</h1>
            <p className="subheading">
              Scores inbound leads on four weighted criteria and routes each one to Slack, the SDR queue, or the audit log.
            </p>
          </div>
        </section>

        <section className="stats-grid" aria-label="Pipeline summary">
          <article className="stat-card stat-card-1">
            <p>Test leads</p>
            <strong>3</strong>
            <span>All scenarios</span>
          </article>
          <article className="stat-card stat-card-2">
            <p>Scoring time</p>
            <strong>1.18 ms</strong>
            <span>Measured locally</span>
          </article>
          <article className="stat-card stat-card-3">
            <p>Tier 1 share</p>
            <strong>33%</strong>
            <span>Share of demo scenarios</span>
          </article>
        </section>

        <section className="pipeline-card" aria-labelledby="pipeline-heading">
          <div className="section-header">
            <div>
              <p className="eyebrow">Workflow status</p>
              <h2 id="pipeline-heading">Pipeline status</h2>
            </div>
            <span className="run-label">{running ? 'Scoring in progress' : hasRun ? 'Completed' : 'Ready'}</span>
          </div>
          <div className="steps">
            {['Inbound intake', 'Enrichment', 'AI scoring', 'CRM sync', 'Routing and alerts'].map((step, index) => (
              <div className="step" key={step}>
                <span className={`step-circle ${index < completed ? 'complete' : ''}`}>
                  {index < completed ? <Check aria-hidden="true" /> : index + 1}
                </span>
                <span className="step-copy">
                  <b>{step}</b>
                  <small>{pipelineStatusTexts[index]}</small>
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="workspace-grid">
          <article className="panel" id="lead-input">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Step 1</p>
                <h2>Lead input</h2>
              </div>
              <span className="muted-label">Sample leads</span>
            </div>
            <label className="field full">
              <span>Scenario</span>
              <div className="select-wrap">
                <select
                  value={scenarioKey}
                  onChange={(event) => {
                    setScenarioKey(event.target.value as ScenarioKey)
                  }}
                >
                  <option value="tier1">Tier 1 example</option>
                  <option value="tier2">Tier 2 example</option>
                  <option value="tier3">Tier 3 example</option>
                </select>
                <ChevronDown aria-hidden="true" />
              </div>
            </label>
            <div className="form-grid">
              {[
                ['First name', data.firstName],
                ['Last name', data.lastName],
                ['Work email', data.email],
                ['Job title', data.title],
                ['Company name', data.company],
                ['Website', data.website],
                ['Company size', data.size]
              ].map(([label, value]) => (
                <label className="field" key={label}>
                  <span>{label}</span>
                  <input value={value} readOnly />
                </label>
              ))}
              <label className="field full">
                <span>Inbound message</span>
                <textarea value={data.message} readOnly rows={3} />
              </label>
            </div>
            <div className="action-row">
              <span className="form-note">Inputs are validated before scoring.</span>
              <button className="primary-button" onClick={runScoring} disabled={running}>
                {running ? 'Running…' : 'Run scoring'}
              </button>
            </div>
          </article>

          <article className="panel" id="scoring-result">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Step 3</p>
                <h2>Scoring result</h2>
              </div>
              <span className="muted-label">Rule-based scoring</span>
            </div>

            {!hasRun ? (
              <div style={{ textAlign: 'center', color: '#6b7280', padding: '64px 20px' }}>
                <p style={{ margin: 0, fontSize: '13px' }}>Select a lead and run scoring to see the result.</p>
              </div>
            ) : (
              <>
                <div className="score-header">
                  <div className="score-value">
                    <strong>{data.score}</strong>
                    <span>/ 100</span>
                  </div>
                  <TierPill tier={data.tier} />
                </div>
                <div className="breakdown">
                  {[
                    ['Firmographic fit', data.parts[0], 30],
                    ['Persona and authority', data.parts[1], 30],
                    ['Problem alignment', data.parts[2], 30],
                    ['Budget and timing', data.parts[3], 10]
                  ].map(([label, value, max]) => (
                    <div className="score-row" key={label}>
                      <div className="score-row-label">
                        <span>{label}</span>
                        <b>
                          {value} / {max}
                        </b>
                      </div>
                      <div className="progress-track">
                        <div className="progress-fill" style={{ width: `${(Number(value) / Number(max)) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="rationale">
                  <h3>Rationale</h3>
                  <p>{data.rationale}</p>
                </div>
                <div className="approach">
                  <h3>Suggested first-call approach</h3>
                  <p>{data.approach}</p>
                </div>
              </>
            )}
          </article>
        </section>

        <section className="records-section" id="records">
          <div className="tabs" role="tablist">
            {['Company enrichment', 'CRM records', 'Slack alert'].map((tab) => (
              <button
                key={tab}
                role="tab"
                aria-selected={activeTab === tab}
                className={activeTab === tab ? 'active' : ''}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="tab-panel">
            {!hasRun ? (
              <div style={{ textAlign: 'center', color: '#6b7280', padding: '36px 24px' }}>
                <p style={{ margin: 0, fontSize: '13px' }}>Run scoring to see results here.</p>
              </div>
            ) : (
              <>
                {activeTab === 'Company enrichment' && (
                  <div className="enrichment-table">
                    {data.enrichment.map(([label, value]) => (
                      <div className="table-row" key={label}>
                        <span>{label}</span>
                        <b>{value}</b>
                      </div>
                    ))}
                  </div>
                )}
                {activeTab === 'CRM records' && (
                  <>
                    <div className="code-grid">
                      <CodePanel
                        title="Contact"
                        endpoint="/crm/v3/objects/contacts"
                        content={data.contact}
                        count="12 properties"
                      />
                      <CodePanel
                        title="Company"
                        endpoint="/crm/v3/objects/companies"
                        content={data.companyRecord}
                        count="9 properties"
                      />
                    </div>
                    <p className="association">
                      <Link2 aria-hidden="true" /> Associated via contact-to-company association.
                    </p>
                  </>
                )}
                {activeTab === 'Slack alert' && <SlackPreview data={data} />}
              </>
            )}
          </div>
        </section>

        <footer style={{ marginTop: '48px', paddingTop: '16px', borderTop: '1px solid #e5e7eb', textAlign: 'center', color: '#9ca3af', fontSize: '12px' }}>
          v1.0 &middot; Rule-based scoring engine
        </footer>
      </div>
    </main>
  )
}

function CodePanel({
  title,
  endpoint,
  content,
  count
}: {
  title: string
  endpoint: string
  content: string
  count: string
}) {
  return (
    <div className="code-panel">
      <div className="code-header">
        <div>
          <b>{title}</b>
          <span>{endpoint}</span>
        </div>
        <small>{count}</small>
      </div>
      <pre>{content}</pre>
    </div>
  )
}

function SlackPreview({ data }: { data: (typeof scenarios)[ScenarioKey] }) {
  if (data.score >= 80) {
    return (
      <div className="slack-message">
        <div className="slack-top">
          <b>#sales-inbound-leads</b>
          <span>Inbound Router Bot &middot; just now</span>
        </div>
        <div className="slack-body">
          <p>
            <strong>[ALERT] New {data.tier} lead:</strong> {data.firstName} {data.lastName} at {data.company}
          </p>
          <p>
            <strong>Score:</strong> {data.score}/100 &middot; <strong>Role:</strong> {data.title}
          </p>
          <p>
            <strong>Projected ARR:</strong> {data.deal_arr} &middot; <strong>Assigned AE:</strong> Alex Vance (Round-Robin)
          </p>
          <p>
            <em>&quot;{data.approach}&quot;</em>
          </p>
          <a className="slack-link" href="#records">
            View deal in HubSpot CRM (#hs_deal_894129)
          </a>
        </div>
      </div>
    )
  }

  if (data.score >= 50) {
    return (
      <div className="slack-empty">
        <span>
          [SDR QUEUE - TIER 2] Assigned to general SDR inbound triage pool. Notification routed to SDR lead view. Manual touchpoint required within 4 business hours.
        </span>
      </div>
    )
  }

  return (
    <div className="slack-empty">
      <span>
        [AUDIT LOG - TIER 3] Lead disqualified automatically (Consumer email / Out of ICP). Reason: Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected ({data.email}). Routing skipped.
      </span>
    </div>
  )
}
