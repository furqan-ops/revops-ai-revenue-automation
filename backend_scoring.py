import json

def process_lead(lead_input: dict, firms_data: dict) -> dict:
    """
    Core backend RevOps pipeline evaluation engine.
    Called identically by both app.py and generate_strict_baseline.py.
    Returns only data and plain text (no HTML).
    """
    first_name = lead_input.get("first_name", "")
    last_name = lead_input.get("last_name", "")
    work_email = lead_input.get("work_email", "")
    job_title = lead_input.get("job_title", "")
    company_name = lead_input.get("company_name", "")
    company_website = lead_input.get("company_website", "")
    company_size = lead_input.get("company_size", "")
    message = lead_input.get("message", "")

    # Domain Sanitization
    email_clean = work_email.strip().lower()
    email_domain = email_clean.split("@")[1] if "@" in email_clean else ""
    free_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    is_free = email_domain in free_domains

    # Firmographic Enrichment Lookup
    enriched = firms_data.get(email_domain, {
        "name": company_name or "Individual Account",
        "industry": "Consumer / Independent" if is_free else "General Commercial Technology",
        "employee_count": 1 if is_free else 35,
        "employee_range": "1-5" if is_free else company_size,
        "estimated_annual_revenue": "N/A" if is_free else "$3.5M",
        "headquarters": "N/A" if is_free else "Global Remote",
        "tech_stack": [] if is_free else ["HubSpot", "Cloud Services"]
    })

    # Dimension 1: Firmographic
    f_match_cond = ""
    if is_free:
        f_score = 0
        f_status = "SHORT_CIRCUIT"
        f_match_cond = "if is_free: matched True -> sets f_score = 0 (short-circuits subsequent employee_count checks: '>= 100', '>= 20', 'else: 5' are skipped)"
    elif enriched.get("employee_count", 0) >= 100:
        f_score = 30
        f_status = "COMPUTED"
        f_match_cond = f"elif enriched.get('employee_count', 0) >= 100: matched True ({enriched.get('employee_count')} >= 100) -> sets f_score = 30"
    elif enriched.get("employee_count", 0) >= 20:
        f_score = 20
        f_status = "COMPUTED"
        f_match_cond = f"elif enriched.get('employee_count', 0) >= 20: matched True ({enriched.get('employee_count')} >= 20) -> sets f_score = 20"
    else:
        f_score = 5
        f_status = "COMPUTED"
        f_match_cond = f"else: matched True (employee_count is {enriched.get('employee_count')}) -> sets f_score = 5"

    # Dimension 2: Authority
    title_lower = job_title.lower()
    a_match_cond = ""
    a_status = "COMPUTED"
    if any(t in title_lower for t in ["vp", "vice president", "chief", "director", "head"]):
        a_score = 30
        first_kw = next(t for t in ["vp", "vice president", "chief", "director", "head"] if t in title_lower)
        a_match_cond = f"if any(t in title_lower for t in ['vp', 'vice president', 'chief', 'director', 'head']): matched True (first matched keyword: '{first_kw}') -> sets a_score = 30"
    elif any(t in title_lower for t in ["manager", "lead"]):
        a_score = 20
        first_kw = next(t for t in ["manager", "lead"] if t in title_lower)
        a_match_cond = f"elif any(t in title_lower for t in ['manager', 'lead']): matched True (first matched keyword: '{first_kw}') -> sets a_score = 20"
    elif any(t in title_lower for t in ["student", "intern"]):
        a_score = 0
        first_kw = next(t for t in ["student", "intern"] if t in title_lower)
        a_match_cond = f"elif any(t in title_lower for t in ['student', 'intern']): matched True (first matched keyword: '{first_kw}') -> sets a_score = 0"
    else:
        a_score = 10
        a_match_cond = "else: matched True -> sets a_score = 10"

    # Dimension 3: Problem
    msg_lower = message.lower()
    p_match_cond = ""
    p_status = "COMPUTED"
    if any(k in msg_lower for k in ["lead routing", "overhaul", "sales reps", "enrichment"]):
        p_score = 28
        first_kw = next(k for k in ["lead routing", "overhaul", "sales reps", "enrichment"] if k in msg_lower)
        p_match_cond = f"if any(k in msg_lower for k in ['lead routing', 'overhaul', 'sales reps', 'enrichment']): matched True (first matched keyword: '{first_kw}') -> sets p_score = 28"
    elif any(k in msg_lower for k in ["evaluating", "pricing", "case studies"]):
        p_score = 18
        first_kw = next(k for k in ["evaluating", "pricing", "case studies"] if k in msg_lower)
        p_match_cond = f"elif any(k in msg_lower for k in ['evaluating', 'pricing', 'case studies']): matched True (first matched keyword: '{first_kw}') -> sets p_score = 18"
    elif any(k in msg_lower for k in ["free", "student", "discount"]):
        p_score = 0
        first_kw = next(k for k in ["free", "student", "discount"] if k in msg_lower)
        p_match_cond = f"elif any(k in msg_lower for k in ['free', 'student', 'discount']): matched True (first matched keyword: '{first_kw}') -> sets p_score = 0"
    else:
        p_score = 10
        p_match_cond = "else: matched True -> sets p_score = 10"

    # Dimension 4: Budget
    b_match_cond = ""
    b_status = "COMPUTED"
    if any(b in msg_lower for b in ["budget approved", "q4", "immediate"]):
        b_score = 10
        first_kw = next(b for b in ["budget approved", "q4", "immediate"] if b in msg_lower)
        b_match_cond = f"if any(b in msg_lower for b in ['budget approved', 'q4', 'immediate']): matched True (first matched keyword: '{first_kw}') -> sets b_score = 10"
    elif "evaluating" in msg_lower:
        b_score = 5
        b_match_cond = "elif 'evaluating' in msg_lower: matched True (matched keyword: 'evaluating') -> sets b_score = 5"
    else:
        b_score = 0
        b_match_cond = "else: matched True -> sets b_score = 0"

    # Aggregate & Tier Assignment
    total_score = min(100, f_score + a_score + p_score + b_score)

    if total_score >= 80:
        tier = "Tier 1 (High)"
        tier_class = "tier-1"
        action = "ROUTE_TO_AE_IMMEDIATE"
        rationale = f"High-value prospect matching core ICP ({enriched['name']}, {enriched['employee_count']} employees). {job_title} has direct decision authority and approved budget."
        sales_hook = f"Focus on immediate ROI: explain how automated routing eliminates lead drop-off across their sales reps."
        deal_arr = f"${(enriched.get('employee_count', 100) * 120):,} ARR"
    elif total_score >= 50:
        tier = "Tier 2 (Medium)"
        tier_class = "tier-2"
        action = "ASSIGN_SDR_NURTURE"
        rationale = f"Moderate fit from {enriched['name']} ({enriched['industry']}, {enriched['employee_range']} employees). Evaluating options and fits MQL criteria."
        sales_hook = "Provide relevant B2B case studies and offer a guided architecture walkthrough."
        deal_arr = "$0 (In Nurture)"
    else:
        tier = "Tier 3 (Disqualified)"
        tier_class = "tier-3"
        action = "DISQUALIFY_AND_LOG"
        rationale = f"Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected ({work_email})."
        sales_hook = "No sales rep action required."
        deal_arr = "$0"

    # HubSpot CRM v3 Payloads
    contact_payload = {
        "firstname": first_name,
        "lastname": last_name,
        "email": work_email,
        "jobtitle": job_title,
        "lifecyclestage": "salesqualifiedlead" if total_score >= 80 else ("marketingqualifiedlead" if total_score >= 50 else "lead"),
        "hs_lead_status": "OPEN" if total_score >= 80 else ("IN_PROGRESS" if total_score >= 50 else "UNQUALIFIED"),
        "ai_icp_score": total_score,
        "ai_icp_tier": tier,
        "ai_qualification_notes": rationale
    }

    company_payload = {
        "name": enriched.get("name"),
        "domain": email_domain,
        "industry": enriched.get("industry"),
        "numberofemployees": str(enriched.get("employee_count", 1)),
        "annualrevenue": enriched.get("estimated_annual_revenue"),
        "icp_fit_tier": tier,
        "target_account": "true" if total_score >= 80 else "false"
    }

    # Rendered Plain Text Notifications (No HTML)
    if total_score >= 80:
        rendered_slack_text = (
            f"#sales-inbound-leads\n"
            f"Inbound Router Bot · just now\n"
            f"[ALERT] New {tier} lead: {first_name} {last_name} at {enriched.get('name')}\n"
            f"Score: {total_score}/100 · Role: {job_title}\n"
            f"Projected ARR: {deal_arr} · Assigned AE: Alex Vance (Round-Robin)\n"
            f'"{sales_hook}"\n'
            f"View deal in HubSpot CRM (#hs_deal_894129)"
        )
        sdr_queue_render = "None (Branch not taken; total_score >= 80 took the Tier 1 Slack alert branch)"
        audit_log_render = "None (Branch not taken; total_score >= 80 took the Tier 1 Slack alert branch)"
    elif total_score >= 50:
        rendered_slack_text = "None (Branch not taken; total_score >= 50 took the Tier 2 SDR Queue branch)"
        rendered_sdr_text = "[MQL Queue] Lead routed to SDR 24h follow-up queue. Contact enrolled in educational nurture sequence."
        sdr_queue_render = rendered_sdr_text
        audit_log_render = "None (Branch not taken; total_score >= 50 took the Tier 2 SDR Queue branch)"
    else:
        rendered_slack_text = "None (Branch not taken; total_score < 50 took the Tier 3 Audit Log branch)"
        sdr_queue_render = "None (Branch not taken; total_score < 50 took the Tier 3 Audit Log branch)"
        rendered_audit_text = "[Audit Log] No sales alert dispatched for this lead. Disqualification recorded in CRM audit trail."
        audit_log_render = rendered_audit_text

    return {
        "first_name": first_name,
        "last_name": last_name,
        "work_email": work_email,
        "job_title": job_title,
        "company_name": company_name,
        "company_size": company_size,
        "company_website": company_website,
        "message": message,
        "email_clean": email_clean,
        "email_domain": email_domain,
        "is_free": is_free,
        "enriched": enriched,
        "f_score": f_score,
        "a_score": a_score,
        "p_score": p_score,
        "b_score": b_score,
        "f_status": f_status,
        "a_status": a_status,
        "p_status": p_status,
        "b_status": b_status,
        "f_match_cond": f_match_cond,
        "a_match_cond": a_match_cond,
        "p_match_cond": p_match_cond,
        "b_match_cond": b_match_cond,
        "total_score": total_score,
        "tier": tier,
        "tier_class": tier_class,
        "action": action,
        "rationale": rationale,
        "sales_hook": sales_hook,
        "deal_arr": deal_arr,
        "contact_payload": contact_payload,
        "company_payload": company_payload,
        "slack_text": rendered_slack_text,
        "sdr_queue_text": sdr_queue_render,
        "audit_log_text": audit_log_render
    }
