from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .database import get_db
from .models import Scan, Finding, Report
from .schemas import (
    MessageScanRequest,
    UrlScanRequest,
    ProfileScanRequest,
    RecruiterScanRequest,
    CompanyScanRequest,
    ScanResponse,
    FindingResponse,
    ReportCreateRequest,
    ReportResponse,
    DashboardStatsResponse,
    DistributionItem
)
from .detection import (
    analyze_message_content,
    analyze_url_content,
    analyze_linkedin_profile,
    analyze_recruiter_and_job,
    analyze_company_content,
    analyze_document_content
)
from .document_parser import extract_text_from_file

router = APIRouter(prefix="/api/v1", tags=["scamlens"])


def _persist_scan_and_findings(db: Session, scan_type: str, analysis: dict) -> Scan:
    """Helper to commit scan result and child findings to MySQL database."""
    new_scan = Scan(
        scan_type=scan_type,
        input_summary=analysis.get("input_summary", "Scan target"),
        status="completed",
        risk_score=analysis.get("risk_score", 0),
        risk_label=analysis.get("risk_label", "Lower Observed Risk"),
        scoring_method="Deterministic Weighted Rule Engine v1.0",
        sources_checked=analysis.get("sources_checked", []),
        unavailable_checks=analysis.get("unavailable_checks", []),
        limitations=analysis.get("limitations", []),
        recommendations=analysis.get("recommendations", [])
    )
    db.add(new_scan)
    db.flush()

    for item in analysis.get("findings", []):
        finding = Finding(
            scan_id=new_scan.id,
            indicator=item["indicator"],
            severity=item["severity"],
            strength=item["strength"],
            evidence=item.get("evidence"),
            explanation=item["explanation"]
        )
        db.add(finding)

    db.commit()
    db.refresh(new_scan)
    return new_scan


# ==========================================
# 1. ANALYSIS ENDPOINTS
# ==========================================

@router.post("/analyze/message", response_model=ScanResponse)
def analyze_message(payload: MessageScanRequest, db: Session = Depends(get_db)):
    """Analyze suspicious email, SMS, or text messages."""
    result = analyze_message_content(
        message_text=payload.message_text,
        sender_details=payload.sender_details,
        related_url=payload.related_url
    )
    scan = _persist_scan_and_findings(db, "message", result)
    return scan


@router.post("/analyze/url", response_model=ScanResponse)
def analyze_url(payload: UrlScanRequest, db: Session = Depends(get_db)):
    """Scan URL with domain heuristics and SSRF protection."""
    result = analyze_url_content(
        raw_url=payload.url,
        context=payload.context
    )
    scan = _persist_scan_and_findings(db, "url", result)
    return scan


@router.post("/analyze/profile", response_model=ScanResponse)
def analyze_profile(payload: ProfileScanRequest, db: Session = Depends(get_db)):
    """Examine LinkedIn or recruiter social profiles."""
    result = analyze_linkedin_profile(
        profile_text=payload.profile_text,
        profile_url=payload.profile_url,
        name_employer=payload.name_employer,
        recruitment_message=payload.recruitment_message
    )
    scan = _persist_scan_and_findings(db, "profile", result)
    return scan


@router.post("/analyze/recruiter", response_model=ScanResponse)
def analyze_recruiter(payload: RecruiterScanRequest, db: Session = Depends(get_db)):
    """Evaluate job offers and recruiter communications for employment fraud."""
    result = analyze_recruiter_and_job(
        recruiter_name=payload.recruiter_name,
        recruiter_email=payload.recruiter_email,
        company_name=payload.company_name,
        company_website=payload.company_website,
        job_title=payload.job_title,
        job_description=payload.job_description,
        salary_details=payload.salary_details,
        recruitment_message=payload.recruitment_message,
        requested_fees=payload.requested_fees
    )
    scan = _persist_scan_and_findings(db, "recruiter", result)
    return scan


@router.post("/analyze/company", response_model=ScanResponse)
def analyze_company(payload: CompanyScanRequest, db: Session = Depends(get_db)):
    """Check corporate domains and business identity indicators."""
    result = analyze_company_content(
        company_name=payload.company_name,
        website=payload.website,
        email_domain=payload.email_domain,
        registration_id=payload.registration_id,
        additional_context=payload.additional_context
    )
    scan = _persist_scan_and_findings(db, "company", result)
    return scan


@router.post("/analyze/document", response_model=ScanResponse)
async def analyze_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and scan PDF, DOCX, TXT, or image documents in-memory."""
    contents = await file.read()
    success, extracted_text, err = extract_text_from_file(contents, file.filename or "uploaded_file")
    if not success:
        raise HTTPException(status_code=400, detail=err or "Failed to read document")

    result = analyze_document_content(
        extracted_text=extracted_text,
        filename=file.filename or "document"
    )
    scan = _persist_scan_and_findings(db, "document", result)
    return scan


# ==========================================
# 2. SCANS MANAGEMENT ENDPOINTS
# ==========================================

@router.get("/scans", response_model=List[ScanResponse])
def get_all_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    scan_type: Optional[str] = Query(None),
    risk_label: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve historical scans with optional filtering, search, and pagination."""
    query = db.query(Scan)

    if scan_type and scan_type.lower() != "all":
        query = query.filter(Scan.scan_type == scan_type.lower())

    if risk_label and risk_label.lower() != "all":
        query = query.filter(Scan.risk_label == risk_label)

    if search:
        query = query.filter(Scan.input_summary.ilike(f"%{search}%"))

    scans = query.order_by(desc(Scan.created_at)).offset(skip).limit(limit).all()
    return scans


@router.get("/scans/{scan_id}", response_model=ScanResponse)
def get_scan_by_id(scan_id: int, db: Session = Depends(get_db)):
    """Retrieve single scan record with associated findings."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found")
    return scan


@router.delete("/scans/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    """Delete a scan record and its cascaded findings."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found")
    db.delete(scan)
    db.commit()
    return {"status": "success", "message": f"Scan #{scan_id} deleted successfully"}


# ==========================================
# 3. DASHBOARD STATISTICS ENDPOINT
# ==========================================

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Aggregate high-level security metrics from MySQL."""
    total_scans = db.query(Scan).count()
    high_risk_detections = db.query(Scan).filter(Scan.risk_score >= 60).count()
    suspicious_urls = db.query(Scan).filter(Scan.scan_type == "url", Scan.risk_score >= 40).count()
    potential_job_scams = db.query(Scan).filter(
        Scan.scan_type.in_(["recruiter", "profile"]),
        Scan.risk_score >= 40
    ).count()

    # Risk distribution categories
    categories = [
        "Lower Observed Risk",
        "Caution",
        "Suspicious",
        "High Risk",
        "Very High Risk",
        "Insufficient Evidence"
    ]
    risk_counts = (
        db.query(Scan.risk_label, func.count(Scan.id))
        .group_by(Scan.risk_label)
        .all()
    )
    counts_map = {label: cnt for label, cnt in risk_counts}
    risk_distribution = []
    for cat in categories:
        cnt = counts_map.get(cat, 0)
        pct = round((cnt / total_scans * 100), 1) if total_scans > 0 else 0.0
        risk_distribution.append(DistributionItem(name=cat, count=cnt, percentage=pct))

    # Category distribution
    types = ["message", "url", "profile", "recruiter", "company", "document"]
    type_labels = {
        "message": "Message / Email",
        "url": "URL Scanner",
        "profile": "LinkedIn Profile",
        "recruiter": "Job & Recruiter",
        "company": "Company Checker",
        "document": "Document Scanner"
    }
    type_counts = (
        db.query(Scan.scan_type, func.count(Scan.id))
        .group_by(Scan.scan_type)
        .all()
    )
    type_map = {stype: cnt for stype, cnt in type_counts}
    category_distribution = []
    for t in types:
        cnt = type_map.get(t, 0)
        pct = round((cnt / total_scans * 100), 1) if total_scans > 0 else 0.0
        category_distribution.append(DistributionItem(name=type_labels.get(t, t.title()), count=cnt, percentage=pct))

    # Recent scans (latest 6)
    recent_scans = db.query(Scan).order_by(desc(Scan.created_at)).limit(6).all()

    return DashboardStatsResponse(
        total_scans=total_scans,
        high_risk_detections=high_risk_detections,
        suspicious_urls=suspicious_urls,
        potential_job_scams=potential_job_scams,
        risk_distribution=risk_distribution,
        category_distribution=category_distribution,
        recent_scans=recent_scans
    )


# ==========================================
# 4. REPORTS ENDPOINTS
# ==========================================

@router.get("/reports", response_model=List[ReportResponse])
def get_all_reports(db: Session = Depends(get_db)):
    """List all saved forensic security reports."""
    reports = db.query(Report).order_by(desc(Report.created_at)).all()
    return reports


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    """Retrieve full audit report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/reports", response_model=ReportResponse)
def create_report(payload: ReportCreateRequest, db: Session = Depends(get_db)):
    """Generate and store a structured forensic report for a given scan."""
    scan = db.query(Scan).filter(Scan.id == payload.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan #{payload.scan_id} not found")

    findings_summary = [
        {
            "indicator": f.indicator,
            "severity": f.severity,
            "strength": f.strength,
            "evidence": f.evidence,
            "explanation": f.explanation
        }
        for f in scan.findings
    ]

    report_payload = {
        "title": f"SCAMLENS AI Security Audit Report #{scan.id}",
        "scan_id": scan.id,
        "scan_type": scan.scan_type,
        "input_summary": scan.input_summary,
        "risk_score": scan.risk_score,
        "risk_label": scan.risk_label,
        "scoring_method": scan.scoring_method,
        "generated_at": datetime.utcnow().isoformat(),
        "findings_count": len(findings_summary),
        "findings": findings_summary,
        "sources_checked": scan.sources_checked or [],
        "unavailable_checks": scan.unavailable_checks or [],
        "limitations": scan.limitations or [],
        "recommendations": scan.recommendations or [],
        "disclaimer": "This report is generated by SCAMLENS AI using automated heuristic rules. It represents an estimated risk assessment and does not constitute absolute proof or guarantee of safety."
    }

    report = Report(
        scan_id=scan.id,
        report_type=payload.report_type or "comprehensive_audit",
        report_data=report_payload
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
