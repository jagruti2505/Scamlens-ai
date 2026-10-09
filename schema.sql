-- SCAMLENS AI — MySQL schema (MySQL 8.0+ recommended, 5.7.8+ works)
--
-- You do NOT have to run this file: the backend creates these tables
-- automatically on startup (SQLAlchemy create_all). Use it if you prefer
-- to create the tables yourself in MySQL Workbench.

CREATE DATABASE IF NOT EXISTS scamlens_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scamlens_db;

CREATE TABLE IF NOT EXISTS scans (
  id                 INT          NOT NULL AUTO_INCREMENT,
  scan_type          VARCHAR(32)  NOT NULL,           -- message | url | profile | recruiter | company | document
  input_summary      VARCHAR(500) NOT NULL,           -- short, privacy-safe description (no raw message)
  status             VARCHAR(32)  NOT NULL,           -- completed | insufficient_evidence
  risk_score         INT          NULL,               -- 0-100, NULL when evidence is insufficient
  risk_label         VARCHAR(40)  NOT NULL,
  scoring_method     VARCHAR(255) NOT NULL,
  summary            TEXT         NULL,
  sources_checked    JSON         NOT NULL,
  unavailable_checks JSON         NOT NULL,
  limitations        JSON         NOT NULL,
  recommendations    JSON         NOT NULL,
  created_at         DATETIME     NOT NULL,           -- UTC
  PRIMARY KEY (id),
  INDEX ix_scans_scan_type (scan_type),
  INDEX ix_scans_status (status),
  INDEX ix_scans_risk_score (risk_score),
  INDEX ix_scans_risk_label (risk_label),
  INDEX ix_scans_created_at (created_at),
  INDEX ix_scans_type_created (scan_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS findings (
  id          INT          NOT NULL AUTO_INCREMENT,
  scan_id     INT          NOT NULL,
  rule_id     VARCHAR(64)  NOT NULL,
  indicator   VARCHAR(160) NOT NULL,
  severity    VARCHAR(16)  NOT NULL,                  -- low | medium | high | critical
  strength    VARCHAR(16)  NOT NULL,                  -- weak | moderate | strong
  weight      INT          NOT NULL DEFAULT 0,
  evidence    TEXT         NOT NULL,                  -- redacted excerpt
  explanation TEXT         NOT NULL,
  PRIMARY KEY (id),
  INDEX ix_findings_scan_id (scan_id),
  CONSTRAINT fk_findings_scan FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reports (
  id          INT         NOT NULL AUTO_INCREMENT,
  scan_id     INT         NOT NULL,
  report_type VARCHAR(32) NOT NULL,                   -- summary | detailed
  report_data JSON        NOT NULL,                   -- snapshot of stored scan data
  created_at  DATETIME    NOT NULL,
  PRIMARY KEY (id),
  INDEX ix_reports_scan_id (scan_id),
  INDEX ix_reports_created_at (created_at),
  CONSTRAINT fk_reports_scan FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
