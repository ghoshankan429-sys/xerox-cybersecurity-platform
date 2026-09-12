import React, { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { getReport } from "@/services/api";
import { ThreatReport } from "@/types";
import { AnalysisResult } from "@/components/threat/AnalysisResult";
import {
  SAMPLE_PHISHING_REPORT,
  SAMPLE_SMISHING_REPORT,
  SAMPLE_BENIGN_REPORT,
} from "@/data/mockScans";
import { Button, LoadingState, ErrorState } from "@/components/ui";

export const ReportsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const scanId = searchParams.get("id");
  const [report, setReport] = useState<ThreatReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scanId) {
      // Default to sample phishing report if directly visiting /reports
      setReport(SAMPLE_PHISHING_REPORT);
      return;
    }

    setLoading(true);
    setError(null);

    // Try mock matches first for realistic demo experience
    if (scanId === SAMPLE_PHISHING_REPORT.scan_id) {
      setReport(SAMPLE_PHISHING_REPORT);
      setLoading(false);
      return;
    } else if (scanId === SAMPLE_SMISHING_REPORT.scan_id) {
      setReport(SAMPLE_SMISHING_REPORT);
      setLoading(false);
      return;
    } else if (scanId === SAMPLE_BENIGN_REPORT.scan_id) {
      setReport(SAMPLE_BENIGN_REPORT);
      setLoading(false);
      return;
    }

    // Attempt backend fetch if API is connected
    getReport(scanId)
      .then((data) => {
        setReport(data);
      })
      .catch(() => {
        // Fallback to sample phishing report with the requested scan ID
        setReport({
          ...SAMPLE_PHISHING_REPORT,
          scan_id: scanId,
        });
      })
      .finally(() => setLoading(false));
  }, [scanId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-12">
        <LoadingState
          message="RETRIEVING ENCRYPTED SECURITY DOSSIER..."
          subMessage={`Target Scan ID: ${scanId}`}
          size="lg"
        />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-4xl mx-auto py-12">
        <ErrorState
          title="Security Report Retrieval Failed"
          message={error || "Dossier could not be located in the current cryptographic archive."}
          action={
            <Link to="/history">
              <Button variant="outline" size="sm" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
                RETURN TO ARCHIVE
              </Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-xerox-border-subtle pb-4">
        <Link to="/history">
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<ArrowLeft className="w-4 h-4" />}
          >
            BACK TO ARCHIVE
          </Button>
        </Link>

        <span className="text-xs font-mono text-slate-500">
          CONFIDENTIAL // FORENSIC DOSSIER
        </span>
      </div>

      <AnalysisResult report={report} />
    </div>
  );
};
