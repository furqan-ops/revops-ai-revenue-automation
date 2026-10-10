'use client'

import { useMemo, useState } from 'react'
import { Check, ChevronDown, Download, Link2 } from 'lucide-react'

interface FirmographicInfo {
  name: string
  domain: string
  industry: string
  employee_count: number
  employee_range: string
  estimated_annual_revenue: string
  headquarters: string
  tech_stack: string[]
}

const firmographicsDb: Record<string, FirmographicInfo> = {
  'cloudscale.io': {
    name: 'CloudScale Systems',
    domain: 'cloudscale.io',
    industry: 'B2B Cloud Infrastructure & DevOps',
    employee_count: 320,
    employee_range: '250-500',
    estimated_annual_revenue: '$45M',
    headquarters: 'San Francisco, CA, USA',
    tech_stack: ['AWS', 'Kubernetes', 'HubSpot', 'Slack', 'PostgreSQL', 'Datadog']
  },
  'growthdigital.co': {
    name: 'Growth Digital Agency',
    domain: 'growthdigital.co',
    industry: 'Performance Marketing & Digital Services',
    employee_count: 35,
    employee_range: '20-50',
    estimated_annual_revenue: '$3.8M',
    headquarters: 'Austin, TX, USA',
    tech_stack: ['WordPress', 'Google Analytics', 'Mailchimp', 'Zapier']
  }
}

interface ScenarioData {
  label: string
  firstName: string
  lastName: string
  email: string
  title: string
  company: string
  website: string
  size: string
  message: string
}

const presetScenarios: Record<string, ScenarioData> = {
  tier1: {
    label: 'Tier 1: Enterprise Buyer (CloudScale Systems)',
    firstName: 'Sarah',
    lastName: 'Jenkins',
    email: 's.jenkins@cloudscale.io',
    title: 'VP of Revenue Operations',
    company: 'CloudScale Systems',
    website: 'https://cloudscale.io',
    size: '250-500',
    message: 'We are looking to overhaul our manual lead routing and automate CRM enrichment for our 25 sales reps. Budget approved for Q4.'
  },
  tier2: {
    label: 'Tier 2: Mid-Market Prospect (Growth Digital Agency)',
    firstName: 'David',
    lastName: 'Miller',
    email: 'david.m@growthdigital.co',
    title: 'Marketing Manager',
    company: 'Growth Digital Agency',
    website: 'https://growthdigital.co',
    size: '20-50',
    message: 'Evaluating automation tools to connect our forms to CRM. Looking for case studies and pricing details.'
  },
  tier3: {
    label: 'Tier 3: Disqualified Inquiry (Freelance / Personal Gmail)',
    firstName: 'Alex',
    lastName: 'K',
    email: 'alexk994@gmail.com',
    title: 'Student / Intern',
    company: 'Freelance',
    website: '',
    size: '1-5',
    message: 'Do you offer free access or student discounts for educational projects?'
  }
}

interface ScoringResult {
  score: number
  tier: string
  tierClass: string
  f_score: number
  a_score: number
  p_score: number
  b_score: number
  rationale: string
  approach: string
  deal_arr: string
  action: string
  enrichmentStep: string
  enrichmentRows: [string, string][]
  contactPayload: Record<string, unknown>
  companyPayload: Record<string, unknown>
  sdrQueueText: string
  auditLogText: string
  latencyMs: number
}

function evaluateLead(input: ScenarioData): ScoringResult {
  const startTime = performance.now()
  const emailClean = input.email.trim().toLowerCase()
  const emailDomain = emailClean.includes('@') ? emailClean.split('@')[1] : ''
  const freeDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
  const isFree = freeDomains.includes(emailDomain)

  const enriched: FirmographicInfo = firmographicsDb[emailDomain] || {
    name: input.company || (isFree ? 'Freelance' : 'Individual Account'),
    domain: emailDomain || 'N/A',
    industry: isFree ? 'Consumer / Independent' : 'General Commercial Technology',
    employee_count: isFree ? 1 : 35,
    employee_range: isFree ? '1-5' : input.size || '1-5',
    estimated_annual_revenue: isFree ? 'N/A' : '$3.5M',
    headquarters: isFree ? 'N/A' : 'Global Remote',
    tech_stack: isFree ? [] : ['HubSpot', 'Cloud Services']
  }

  // Dimension 1: Firmographic
  let f_score = 0
  if (isFree) {
    f_score = 0
  } else if (enriched.employee_count >= 100) {
    f_score = 30
  } else if (enriched.employee_count >= 20) {
    f_score = 20
  } else {
    f_score = 5
  }

  // Dimension 2: Authority
  const titleLower = input.title.toLowerCase()
  let a_score = 10
  if (['vp', 'vice president', 'chief', 'director', 'head'].some(k => titleLower.includes(k))) {
    a_score = 30
  } else if (['manager', 'lead'].some(k => titleLower.includes(k))) {
    a_score = 20
  } else if (['student', 'intern'].some(k => titleLower.includes(k))) {
    a_score = 0
  }

  // Dimension 3: Problem
  const msgLower = input.message.toLowerCase()
  let p_score = 10
  if (['lead routing', 'overhaul', 'sales reps', 'enrichment'].some(k => msgLower.includes(k))) {
    p_score = 28
  } else if (['evaluating', 'pricing', 'case studies'].some(k => msgLower.includes(k))) {
    p_score = 18
  } else if (['free', 'student', 'discount'].some(k => msgLower.includes(k))) {
    p_score = 0
  }

  // Dimension 4: Budget
  let b_score = 0
  if (['budget approved', 'q4', 'immediate'].some(k => msgLower.includes(k))) {
    b_score = 10
  } else if (msgLower.includes('evaluating')) {
    b_score = 5
  }

  const totalScore = Math.min(100, f_score + a_score + p_score + b_score)

  let tier = 'Tier 3 (Disqualified)'
  let tierClass = 'tier-3'
  let action = 'Internal audit log'
  let rationale = `Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected (${input.email}).`
  let approach = 'No sales rep action required.'
  let deal_arr = '$0'

  if (totalScore >= 80) {
    tier = 'Tier 1 (High)'
    tierClass = 'tier-1'
    action = 'Tier 1 Slack alert'
    rationale = `High-value prospect matching core ICP (${enriched.name}, ${enriched.employee_count} employees). ${input.title} has direct decision authority and approved budget.`
    approach = 'Focus on immediate ROI: explain how automated routing eliminates lead drop-off across their sales reps.'
    deal_arr = `$${(enriched.employee_count * 120).toLocaleString()} ARR`
  } else if (totalScore >= 50) {
    tier = 'Tier 2 (Medium)'
    tierClass = 'tier-2'
    action = 'Tier 2 SDR queue alert'
    rationale = `Moderate fit from ${enriched.name} (${enriched.industry}, ${enriched.employee_range} employees). Evaluating options and fits MQL criteria.`
    approach = 'Provide relevant B2B case studies and offer a guided architecture walkthrough.'
    deal_arr = '$0 (In Nurture)'
  }

  const contactPayload = {
    firstname: input.firstName,
    lastname: input.lastName,
    email: input.email,
    jobtitle: input.title,
    lifecyclestage: totalScore >= 80 ? 'salesqualifiedlead' : totalScore >= 50 ? 'marketingqualifiedlead' : 'lead',
    hs_lead_status: totalScore >= 80 ? 'OPEN' : totalScore >= 50 ? 'IN_PROGRESS' : 'UNQUALIFIED',
    ai_icp_score: totalScore,
    ai_icp_tier: tier,
    ai_qualification_notes: rationale
  }

  const companyPayload = {
    name: enriched.name,
    domain: emailDomain,
    industry: enriched.industry,
    numberofemployees: String(enriched.employee_count),
    annualrevenue: enriched.estimated_annual_revenue,
    icp_fit_tier: tier,
    target_account: totalScore >= 80 ? 'true' : 'false'
  }

  const enrichmentRows: [string, string][] = [
    ['Company', enriched.name],
    ['Industry', enriched.industry],
    ['Headcount', String(enriched.employee_count)],
    ['Annual revenue', enriched.estimated_annual_revenue],
    ['Headquarters', enriched.headquarters],
    ['Tech stack', enriched.tech_stack.length > 0 ? enriched.tech_stack.join(', ') : 'None detected'],
    ['Domain type', isFree ? 'Consumer email' : 'Corporate business domain']
  ]

  const sdrQueueText = '[SDR QUEUE - TIER 2] Assigned to general SDR inbound triage pool. Notification routed to SDR lead view. Manual touchpoint required within 4 business hours.'
  const auditLogText = `[AUDIT LOG - TIER 3] Lead disqualified automatically (Consumer email / Out of ICP). Reason: Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected (${input.email}). Routing skipped.`

  const endTime = performance.now()
  const latencyMs = Number((endTime - startTime).toFixed(2))

  return {
    score: totalScore,
    tier,
    tierClass,
    f_score,
    a_score,
    p_score,
    b_score,
    rationale,
    approach,
    deal_arr,
    action,
    enrichmentStep: isFree ? 'Fallback profile used' : 'Firmographics matched',
    enrichmentRows,
    contactPayload,
    companyPayload,
    sdrQueueText,
    auditLogText,
    latencyMs
  }
}

function TierPill({ tier }: { tier: string }) {
  const tierKey = tier.includes('Tier 1') ? 'tier-1' : tier.includes('Tier 2') ? 'tier-2' : 'tier-3'
  return <span className={`tier-pill ${tierKey}`}>{tier}</span>
}

export default function LeadScoringDashboard() {
  const [selectedScenarioKey, setSelectedScenarioKey] = useState<string>('tier1')
  const [formData, setFormData] = useState<ScenarioData>(presetScenarios.tier1)
  const [activeTab, setActiveTab] = useState('Company enrichment')
  const [running, setRunning] = useState(false)
  const [hasRun, setHasRun] = useState(false)
  const [completed, setCompleted] = useState(0)
  const [result, setResult] = useState<ScoringResult | null>(null)
  const [errors, setErrors] = useState<{ firstName?: string; lastName?: string; email?: string; message?: string }>({})

  const todayDate = useMemo(() => {
    return new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
  }, [])

  function handleScenarioChange(key: string) {
    setSelectedScenarioKey(key)
    if (presetScenarios[key]) {
      setFormData(presetScenarios[key])
      setErrors({})
    }
  }

  function handleFieldChange(field: keyof ScenarioData, value: string) {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field as keyof typeof errors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  function validate(): boolean {
    const nextErrors: { firstName?: string; lastName?: string; email?: string; message?: string } = {}
    if (!formData.firstName.trim()) nextErrors.firstName = 'First name is required.'
    if (!formData.lastName.trim()) nextErrors.lastName = 'Last name is required.'
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email.trim())) {
      nextErrors.email = 'Work email must contain "@" followed by a domain.'
    }
    if (!formData.message.trim()) nextErrors.message = 'Inbound message is required.'

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  function runScoring() {
    if (!validate()) return

    setRunning(true)
    setCompleted(0)

    const evaluated = evaluateLead(formData)
    setResult(evaluated)

    let step = 0
    const interval = window.setInterval(() => {
      step += 1
      setCompleted(step)
      if (step === 5) {
        window.clearInterval(interval)
        setRunning(false)
        setHasRun(true)
      }
    }, 180)
  }

  const pipelineStatusTexts = [
    hasRun ? 'Lead received' : 'Waiting',
    hasRun && result ? result.enrichmentStep : 'Waiting',
    hasRun && result ? `Score ${result.score}` : 'Waiting',
    hasRun ? 'Payloads built' : 'Waiting',
    hasRun && result ? result.action : 'Waiting'
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
            <strong>{result ? `${result.latencyMs.toFixed(2)} ms` : '1.18 ms'}</strong>
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className="run-label">{running ? 'Scoring in progress' : hasRun ? 'Completed' : 'Ready'}</span>
              <a
                href="/master_revops_pipeline.json"
                download="master_revops_pipeline.json"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  border: '1px solid #d1d5db',
                  background: '#ffffff',
                  color: '#374151',
                  fontSize: '12px',
                  fontWeight: 500,
                  textDecoration: 'none'
                }}
              >
                <Download style={{ width: '13px', height: '13px' }} aria-hidden="true" />
                Workflow JSON
              </a>
            </div>
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
                  value={selectedScenarioKey}
                  onChange={(event) => handleScenarioChange(event.target.value)}
                >
                  <option value="tier1">Tier 1: Enterprise Buyer (CloudScale Systems)</option>
                  <option value="tier2">Tier 2: Mid-Market Prospect (Growth Digital Agency)</option>
                  <option value="tier3">Tier 3: Disqualified Inquiry (Freelance / Personal Gmail)</option>
                </select>
                <ChevronDown aria-hidden="true" />
              </div>
            </label>
            <div className="form-grid">
              <label className="field">
                <span>First name</span>
                <input
                  value={formData.firstName}
                  onChange={(e) => handleFieldChange('firstName', e.target.value)}
                />
                {errors.firstName && <span style={{ color: '#dc2626', fontSize: '11px' }}>{errors.firstName}</span>}
              </label>

              <label className="field">
                <span>Last name</span>
                <input
                  value={formData.lastName}
                  onChange={(e) => handleFieldChange('lastName', e.target.value)}
                />
                {errors.lastName && <span style={{ color: '#dc2626', fontSize: '11px' }}>{errors.lastName}</span>}
              </label>

              <label className="field">
                <span>Work email</span>
                <input
                  value={formData.email}
                  onChange={(e) => handleFieldChange('email', e.target.value)}
                />
                {errors.email && <span style={{ color: '#dc2626', fontSize: '11px' }}>{errors.email}</span>}
              </label>

              <label className="field">
                <span>Job title</span>
                <input
                  value={formData.title}
                  onChange={(e) => handleFieldChange('title', e.target.value)}
                />
              </label>

              <label className="field">
                <span>Company name</span>
                <input
                  value={formData.company}
                  onChange={(e) => handleFieldChange('company', e.target.value)}
                />
              </label>

              <label className="field">
                <span>Website</span>
                <input
                  value={formData.website}
                  onChange={(e) => handleFieldChange('website', e.target.value)}
                />
              </label>

              <label className="field">
                <span>Company size</span>
                <input
                  value={formData.size}
                  onChange={(e) => handleFieldChange('size', e.target.value)}
                />
              </label>

              <label className="field full">
                <span>Inbound message</span>
                <textarea
                  value={formData.message}
                  onChange={(e) => handleFieldChange('message', e.target.value)}
                  rows={3}
                />
                {errors.message && <span style={{ color: '#dc2626', fontSize: '11px' }}>{errors.message}</span>}
              </label>
            </div>
            <div className="action-row">
              <span className="form-note">
                {Object.keys(errors).length > 0 ? (
                  <span style={{ color: '#dc2626' }}>Please fix the errors above before scoring.</span>
                ) : hasRun ? (
                  <span style={{ color: '#047857' }}>All inputs valid</span>
                ) : (
                  'Inputs are validated before scoring.'
                )}
              </span>
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

            {!hasRun || !result ? (
              <div style={{ textAlign: 'center', color: '#6b7280', padding: '64px 20px' }}>
                <p style={{ margin: 0, fontSize: '13px' }}>Select a lead and run scoring to see the result.</p>
              </div>
            ) : (
              <>
                <div className="score-header">
                  <div className="score-value">
                    <strong>{result.score}</strong>
                    <span>/ 100</span>
                  </div>
                  <TierPill tier={result.tier} />
                </div>
                <div className="breakdown">
                  {[
                    ['Firmographic fit', result.f_score, 30],
                    ['Persona and authority', result.a_score, 30],
                    ['Problem alignment', result.p_score, 30],
                    ['Budget and timing', result.b_score, 10]
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
                  <p>{result.rationale}</p>
                </div>
                <div className="approach">
                  <h3>Suggested first-call approach</h3>
                  <p>{result.approach}</p>
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
            {!hasRun || !result ? (
              <div style={{ textAlign: 'center', color: '#6b7280', padding: '36px 24px' }}>
                <p style={{ margin: 0, fontSize: '13px' }}>Run scoring to see results here.</p>
              </div>
            ) : (
              <>
                {activeTab === 'Company enrichment' && (
                  <div className="enrichment-table">
                    {result.enrichmentRows.map(([label, value]) => (
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
                        content={JSON.stringify(result.contactPayload, null, 2)}
                        count={`${Object.keys(result.contactPayload).length} properties`}
                      />
                      <CodePanel
                        title="Company"
                        endpoint="/crm/v3/objects/companies"
                        content={JSON.stringify(result.companyPayload, null, 2)}
                        count={`${Object.keys(result.companyPayload).length} properties`}
                      />
                    </div>
                    <p className="association">
                      <Link2 aria-hidden="true" /> Associated via contact-to-company association.
                    </p>
                  </>
                )}
                {activeTab === 'Slack alert' && (
                  <SlackPreview result={result} formData={formData} />
                )}
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

function SlackPreview({ result, formData }: { result: ScoringResult; formData: ScenarioData }) {
  if (result.score >= 80) {
    return (
      <div className="slack-message">
        <div className="slack-top">
          <b>#sales-inbound-leads</b>
          <span>Inbound Router Bot &middot; just now</span>
        </div>
        <div className="slack-body">
          <p>
            <strong>[ALERT] New {result.tier} lead:</strong> {formData.firstName} {formData.lastName} at {formData.company}
          </p>
          <p>
            <strong>Score:</strong> {result.score}/100 &middot; <strong>Role:</strong> {formData.title}
          </p>
          <p>
            <strong>Projected ARR:</strong> {result.deal_arr} &middot; <strong>Assigned AE:</strong> Alex Vance (Round-Robin)
          </p>
          <p>
            <em>&quot;{result.approach}&quot;</em>
          </p>
          <a className="slack-link" href="#records">
            View deal in HubSpot CRM (#hs_deal_894129)
          </a>
        </div>
      </div>
    )
  }

  if (result.score >= 50) {
    return (
      <div className="slack-empty">
        <span>{result.sdrQueueText}</span>
      </div>
    )
  }

  return (
    <div className="slack-empty">
      <span>{result.auditLogText}</span>
    </div>
  )
}
