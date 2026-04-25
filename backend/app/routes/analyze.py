"""
SAR Multi-Agent Backend — Analyze Route
========================================
Exposes the ``/analyze`` POST endpoint that drives the
entire SAR analysis pipeline.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.core.exceptions import PipelineError, InputValidationError
from app.core.logger import logger
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from app.services.pipeline_service import execute_analysis

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Run SAR Analysis Pipeline",
    description=(
        "Accepts raw input data, runs it through the full multi-agent "
        "pipeline (InputHandler → Preprocessing → FeatureProcessing → "
        "AnalysisEngine → OutputFormatter), and returns the structured "
        "SAR report with execution metadata."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Pipeline failure"},
    },
)
async def analyze(body: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    """Execute the full SAR analysis pipeline.

    Args:
        body:    JSON body conforming to ``AnalyzeRequest``.
        request: Starlette request (used for correlation ID).

    Returns:
        ``AnalyzeResponse`` with the final SAR output and metadata.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(
        "POST /analyze — payload with %d key(s) (request_id=%s)",
        len(body.input_data),
        request_id,
    )

    try:
        response = await execute_analysis(body)
        return response

    except InputValidationError as exc:
        logger.warning("Input validation failed: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "error": exc.message,
                "detail": exc.details,
                "request_id": request_id,
            },
        )

    except PipelineError as exc:
        logger.error("Pipeline error: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": exc.message,
                "detail": exc.details,
                "request_id": request_id,
            },
        )

    except Exception as exc:
        logger.critical(
            "Unhandled exception in /analyze: %s",
            str(exc), exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "request_id": request_id,
            },
        )
