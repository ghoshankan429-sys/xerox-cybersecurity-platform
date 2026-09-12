import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.security.dependencies import get_current_user
from app.schemas.threat import (
    ThreatReport,
    URLScanRequest,
    ScanHistoryItem,
    StatsSummary,
)
from app.services.url_analysis_service import URLAnalysisService

router = APIRouter()


@router.post(
    "/url",
    response_model=ThreatReport,
    status_code=status.HTTP_200_OK,
    summary="Analyze suspicious URL for security threats",
)
async def analyze_url_endpoint(
    request_data: URLScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ThreatReport:
    """Performs deterministic static heuristic analysis and threat intelligence checks
    on a target URL. NEVER opens socket connections to the target (strict SSRF prevention).
    Persists scan and forensic findings scoped to the authenticated user.
    """
    cleaned_url = request_data.url.strip()
    if not cleaned_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL target cannot be empty.",
        )

    service = URLAnalysisService()
    try:
        report = await service.analyze_url(
            raw_url=cleaned_url,
            user_id=current_user.id,
            db=db,
        )
        return report
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL security analysis failed: {str(exc)}",
        )


@router.get(
    "/history",
    response_model=List[ScanHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Retrieve user's historical security scans",
)
async def get_history_endpoint(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ScanHistoryItem]:
    """Retrieves paginated scan history strictly scoped to the authenticated user."""
    service = URLAnalysisService()
    return await service.get_user_history(
        user_id=current_user.id,
        db=db,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/stats/summary",
    response_model=StatsSummary,
    status_code=status.HTTP_200_OK,
    summary="Get user security telemetry statistics",
)
@router.get(
    "/summary/stats",
    response_model=StatsSummary,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_stats_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StatsSummary:
    """Returns aggregated threat telemetry statistics for the authenticated user."""
    service = URLAnalysisService()
    return await service.get_stats_summary(user_id=current_user.id, db=db)


@router.get(
    "/{scan_id}",
    response_model=ThreatReport,
    status_code=status.HTTP_200_OK,
    summary="Retrieve full threat report by scan ID",
)
async def get_scan_report_endpoint(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ThreatReport:
    """Loads a full ThreatReport by scan ID, enforcing strict tenant isolation."""
    service = URLAnalysisService()
    report = await service.get_scan_report(
        scan_id=scan_id,
        user_id=current_user.id,
        db=db,
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan report not found or access denied.",
        )
    return report
