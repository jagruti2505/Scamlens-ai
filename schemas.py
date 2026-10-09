from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# ANALYSIS INPUT SCHEMAS
# ==========================================

class MessageScanRequest(BaseModel):
    message_text: str = Field(..., min_length=3, description="Suspicious email or text message")
    sender_details: Optional[str] = Field(None, description="Sender name, address, or phone number")
    related_url: Optional[str] = Field(None, description="Associated link or domain found in message")


class UrlScanRequest(BaseModel):
    url: str = Field(..., min_length=3, description="Target URL or domain to scan")
    context: Optional[str] = Field(None, description="Surrounding message or referral context")


class ProfileScanRequest(BaseModel):
    profile_url: Optional[str] = Field(None, description="LinkedIn or social profile URL")
    profile_text: str = Field(..., min_length=5, description="Pasted profile bio, headline, work history")
    name_employer: Optional[str] = Field(None, description="Reported name and employer")
    recruitment_message: Optional[str] = Field(None, description="Outreach or InMail message received")


class RecruiterScanRequest(BaseModel):
    recruiter_name: Optional[str] = Field(None, description="Recruiter contact name")
    recruiter_email: Optional[str] = Field(None, description="Recruiter email address")
    company_name: Optional[str] = Field(None, description="Target company being represented")
    company_website: Optional[str] = Field(None, description="Company website or portal URL")
    job_title: Optional[str] = Field(None, description="Offered position title")
    job_description: Optional[str] = Field(None, description="Job duties or posting text")
    salary_details: Optional[str] = Field(None, description="Offered compensation or hourly rate")
    recruitment_message: Optional[str] = Field(None, description="Recruitment communication or interview transcript")
    requested_fees: Optional[str] = Field(None, description="Any requested equipment, training, registration, or badge fees")


class CompanyScanRequest(BaseModel):
    company_name: str = Field(..., min_length=2, description="Target business or company name")
    website: Optional[str] = Field(None, description="Official company website URL")
    email_domain: Optional[str] = Field(None, description="Contact email address or domain")
    registration_id: Optional[str] = Field(None, description="Corporate registration, tax ID, or CIN")
    additional_context: Optional[str] = Field(None, description="Supporting context or inquiry notes")


# ==========================================
# FINDINGS & RESULT SCHEMAS
# ==========================================

class FindingResponse(BaseModel):
    id: Optional[int] = None
    indicator: str
    severity: str  # critical, high, medium, low, info
    strength: str  # high, moderate, low
    evidence: Optional[str] = None
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class ScanResponse(BaseModel):
    id: int
    scan_type: str
    input_summary: str
    status: str
    risk_score: int
    risk_label: str
    scoring_method: str
    sources_checked: List[str] = []
    unavailable_checks: List[str] = []
    limitations: List[str] = []
    recommendations: List[str] = []
    created_at: datetime
    findings: List[FindingResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ReportCreateRequest(BaseModel):
    scan_id: int
    report_type: Optional[str] = "comprehensive_audit"


class ReportResponse(BaseModel):
    id: int
    scan_id: int
    report_type: str
    report_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DistributionItem(BaseModel):
    name: str
    count: int
    percentage: float = 0.0


class DashboardStatsResponse(BaseModel):
    total_scans: int
    high_risk_detections: int
    suspicious_urls: int
    potential_job_scams: int
    risk_distribution: List[DistributionItem]
    category_distribution: List[DistributionItem]
    recent_scans: List[ScanResponse]
