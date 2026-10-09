-- SCAMLENS AI Database Schema
-- Database: scamlens_db
-- Target: MySQL 8.0+

CREATE DATABASE IF NOT EXISTS `scamlens_db`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `scamlens_db`;

-- 1. SCANS TABLE
CREATE TABLE IF NOT EXISTS `scans` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `scan_type` VARCHAR(50) NOT NULL COMMENT 'message, url, profile, recruiter, company, document',
  `input_summary` VARCHAR(500) NOT NULL COMMENT 'Sanitized summary of scanned target',
  `status` VARCHAR(50) NOT NULL DEFAULT 'completed',
  `risk_score` INT NOT NULL DEFAULT 0 COMMENT '0-100 or -1 if insufficient evidence',
  `risk_label` VARCHAR(50) NOT NULL COMMENT 'Lower Observed Risk, Caution, Suspicious, High Risk, Very High Risk, Insufficient Evidence',
  `scoring_method` VARCHAR(100) NOT NULL DEFAULT 'Deterministic Weighted Rule Engine v1.0',
  `sources_checked` JSON NULL,
  `unavailable_checks` JSON NULL,
  `limitations` JSON NULL,
  `recommendations` JSON NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_scan_type` (`scan_type`),
  INDEX `idx_risk_label` (`risk_label`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. FINDINGS TABLE
CREATE TABLE IF NOT EXISTS `findings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `scan_id` INT NOT NULL,
  `indicator` VARCHAR(255) NOT NULL,
  `severity` VARCHAR(50) NOT NULL COMMENT 'critical, high, medium, low, info',
  `strength` VARCHAR(50) NOT NULL COMMENT 'high, moderate, low',
  `evidence` TEXT NULL,
  `explanation` TEXT NOT NULL,
  INDEX `idx_finding_scan_id` (`scan_id`),
  CONSTRAINT `fk_findings_scan_id` FOREIGN KEY (`scan_id`)
    REFERENCES `scans` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. REPORTS TABLE
CREATE TABLE IF NOT EXISTS `reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `scan_id` INT NOT NULL,
  `report_type` VARCHAR(50) NOT NULL DEFAULT 'comprehensive_audit',
  `report_data` JSON NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_report_scan_id` (`scan_id`),
  INDEX `idx_report_created_at` (`created_at`),
  CONSTRAINT `fk_reports_scan_id` FOREIGN KEY (`scan_id`)
    REFERENCES `scans` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
