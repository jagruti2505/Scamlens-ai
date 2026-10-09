// The five text-based scanners. Each is a configuration of the shared AnalyzerForm.
import { Briefcase, Building2, Link2, MessageSquareWarning, UserSearch } from 'lucide-react'
import AnalyzerForm from '../components/AnalyzerForm'
import { api } from '../services/api'

export function AnalyzeMessage() {
  return (
    <AnalyzerForm
      icon={MessageSquareWarning}
      title="Message & Email Scanner"
      subtitle="Paste a suspicious SMS, WhatsApp message or email. We check for payment requests, urgency, credential requests, impersonation and risky links."
      submit={api.analyzeMessage}
      validate={(v) => (!v.message.trim() ? 'Please paste the message or email text.' : '')}
      fields={[
        { name: 'message', label: 'Message or email text', type: 'textarea', rows: 9, placeholder: 'Paste the full message here…' },
        { name: 'sender', label: 'Sender details', optional: true, span: 1, placeholder: 'e.g. Support <alerts@example.com>' },
        { name: 'related_url', label: 'Related URL', optional: true, span: 1, type: 'url', placeholder: 'https://…' },
      ]}
      example={{
        message: 'URGENT: Dear customer, your SBI account will be suspended within 24 hours. Share your OTP and click the link below to update your KYC: http://sbi-kyc-update.xyz/login',
        sender: 'SBI Support <sbi.alerts.team@gmail.com>',
      }}
      tips={['Requests for OTP, PIN, password or card details', 'Upfront fees, gift cards, crypto', 'Threats, deadlines and pressure',
        'Official-sounding messages from free email', 'Look-alike or disguised links']}
    />
  )
}

export function ScanUrl() {
  return (
    <AnalyzerForm
      icon={Link2}
      title="URL Scanner"
      subtitle="Check a link before you open it. The link is analyzed as text — it is not visited unless live checks are enabled on the server."
      submit={api.analyzeUrl}
      validate={(v) => (!v.url.trim() ? 'Please enter a URL.' : '')}
      fields={[
        { name: 'url', label: 'URL', type: 'url', placeholder: 'https://example.com/login' },
        { name: 'context', label: 'Where did you get this link?', type: 'textarea', rows: 4, optional: true,
          placeholder: 'Paste the message that contained the link (optional)' },
      ]}
      example={{ url: 'http://paypa1-account-verify.com/secure/login', context: 'Your PayPal account is limited. Verify immediately to avoid suspension.' }}
      tips={['Look-alike brand names and misspellings', 'Raw IP addresses and hidden "@" tricks', 'Punycode (foreign look-alike letters)',
        'Shorteners, free hosting, risky domain endings', 'Optional: Google Safe Browsing lookup']}
    />
  )
}

export function ProfileChecker() {
  return (
    <AnalyzerForm
      icon={UserSearch}
      title="LinkedIn Profile Checker"
      subtitle="Paste the profile details and any message you received. We cannot open LinkedIn for you, so the check uses only what you paste."
      submit={api.analyzeProfile}
      validate={(v) => (!v.profile_url.trim() && !v.profile_text.trim() && !v.recruitment_message.trim()
        ? 'Provide a profile URL, the profile text or the recruitment message.' : '')}
      fields={[
        { name: 'name', label: 'Name on profile', optional: true, span: 1, placeholder: 'e.g. Ananya Sharma' },
        { name: 'employer', label: 'Claimed employer', optional: true, span: 1, placeholder: 'e.g. Global Tech Ltd' },
        { name: 'profile_url', label: 'Profile URL', type: 'url', optional: true, placeholder: 'https://www.linkedin.com/in/…' },
        { name: 'profile_text', label: 'Profile description / pasted profile text', type: 'textarea', rows: 6, optional: true,
          placeholder: 'Headline, about section, experience, number of connections…' },
        { name: 'recruitment_message', label: 'Message they sent you', type: 'textarea', rows: 5, optional: true },
      ]}
      example={{
        name: 'Rahul Mehta', employer: 'Google',
        profile_text: 'Senior HR Recruiter hiring for Google, Amazon, Microsoft and Deloitte. 100% guaranteed placement. 23 connections',
        recruitment_message: 'Hi, you are shortlisted. Complete our certification and pay the certification fee of Rs 3,000. Contact me on WhatsApp: hr.rahul.recruit@gmail.com',
      }}
      tips={['Claims of recruiting for many big brands', 'Certification or training fees', 'Guaranteed placement promises',
        'Moving chat to WhatsApp / Telegram', 'Free email used for a corporate role']}
    />
  )
}

export function RecruiterDetector() {
  return (
    <AnalyzerForm
      icon={Briefcase}
      title="Recruiter & Job Scam Detector"
      subtitle="Enter what you know about the job offer. Upfront fees, instant offers and free-email recruiters are the strongest warning signs."
      submit={api.analyzeRecruiter}
      validate={(v) => (!['job_description', 'recruitment_message', 'requested_fees', 'recruiter_email', 'salary'].some((k) => v[k].trim())
        ? 'Add at least the recruitment message, job description, salary, recruiter email or requested fees.' : '')}
      fields={[
        { name: 'recruiter_name', label: 'Recruiter name', optional: true, span: 1 },
        { name: 'recruiter_email', label: 'Recruiter email', type: 'email', optional: true, span: 1, placeholder: 'name@company.com' },
        { name: 'company_name', label: 'Company name', optional: true, span: 1 },
        { name: 'company_website', label: 'Company website', type: 'url', optional: true, span: 1, placeholder: 'https://…' },
        { name: 'job_title', label: 'Job title', optional: true, span: 1 },
        { name: 'salary', label: 'Salary details', optional: true, span: 1, placeholder: 'e.g. ₹45,000 per month' },
        { name: 'job_description', label: 'Job description', type: 'textarea', rows: 4, optional: true },
        { name: 'recruitment_message', label: 'Recruitment message', type: 'textarea', rows: 5, optional: true },
        { name: 'requested_fees', label: 'Fees requested (registration, training, interview, certification…)', optional: true,
          placeholder: 'e.g. ₹2,500 registration fee — leave blank if none', hint: 'Genuine employers do not charge candidates.' },
      ]}
      example={{
        recruiter_name: 'Priya HR', recruiter_email: 'priya.amazonhiring@gmail.com', company_name: 'Amazon',
        job_title: 'Work from home data entry', salary: 'Earn ₹3000 per day', job_description: 'Simple typing work.',
        recruitment_message: 'Congratulations! You are selected without interview. Pay the registration fee via UPI today only and contact HR on WhatsApp.',
        requested_fees: '₹1,999 registration fee',
      }}
      tips={['Registration / training / kit fees', 'Selection without interview', 'Recruiter email vs company domain',
        'Unrealistic pay for little work', 'Urgency and off-platform chat']}
    />
  )
}

export function CompanyChecker() {
  return (
    <AnalyzerForm
      icon={Building2}
      title="Company Checker"
      subtitle="Check whether a company's online details are consistent. We show clearly what could not be verified."
      submit={api.analyzeCompany}
      validate={(v) => (!v.company_name.trim() ? 'Please enter the company name.' : '')}
      fields={[
        { name: 'company_name', label: 'Company name', span: 1, placeholder: 'e.g. Bright Future Placements' },
        { name: 'website', label: 'Website', type: 'url', optional: true, span: 1, placeholder: 'https://…' },
        { name: 'email_domain', label: 'Email domain or address', optional: true, span: 1, placeholder: 'e.g. company.com or hr@company.com' },
        { name: 'registration_id', label: 'Registration ID', optional: true, span: 1, placeholder: 'e.g. CIN / trade licence' },
        { name: 'context', label: 'Additional context', type: 'textarea', rows: 4, optional: true,
          placeholder: 'How did they contact you? What are they asking for?' },
      ]}
      example={{ company_name: 'Global Careers Pvt Ltd', website: 'https://global-careers-hiring.xyz', email_domain: 'globalcareers.hr@gmail.com',
        context: 'They asked for a refundable deposit before sending the offer letter.' }}
      tips={['Free email used as company email', 'Email domain vs website domain', 'Risky or look-alike website domains',
        'Registration ID format (not verified)', 'Fee and pressure tactics in context']}
    />
  )
}
