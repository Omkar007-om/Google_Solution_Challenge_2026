"""
SAR Multi-Agent Backend — Analyze Route
========================================
Exposes the ``/analyze`` POST endpoint that drives the
entire SAR analysis pipeline.
"""

from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

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
async def analyze(
    body: AnalyzeRequest,
    request: Request,

) -> AnalyzeResponse:
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


@router.post(
    "/analyze/csv",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Run SAR Analysis Pipeline From CSV",
    description=(
        "Accepts a CSV transaction file, maps the available columns into the "
        "canonical transaction structure, executes all seven SAR agents in "
        "sequence, and returns the formatted SAR report."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid CSV file"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Pipeline failure"},
    },
)
async def analyze_csv(
    request: Request,
    file: UploadFile = File(...),
    subject_account: str | None = Form(default=None),

) -> AnalyzeResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Only .csv files are supported",
                "request_id": request_id,
            },
        )

    try:
        content = await file.read()
        rows, columns = _read_csv(content)
        body = AnalyzeRequest(
            input_data={
                "subject_account": subject_account,
                "transactions": rows,
                "metadata": {
                    "source_filename": file.filename,
                    "csv_columns": columns,
                },
            }
        )
        return await execute_analysis(body)

    except InputValidationError as exc:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": exc.message,
                "detail": exc.details,
                "request_id": request_id,
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": str(exc),
                "request_id": request_id,
            },
        )
    except Exception as exc:
        logger.critical("Unhandled exception in /analyze/csv: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "request_id": request_id,
            },
        )


def _read_csv(content: bytes) -> tuple[list[dict[str, str]], list[str]]:
    if not content:
        raise ValueError("CSV file is empty")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("CSV file must include a header row")

    rows = [
        {str(key).strip(): (value or "").strip() for key, value in row.items() if key is not None}
        for row in reader
    ]
    rows = [row for row in rows if any(value for value in row.values())]
    if not rows:
        raise ValueError("CSV file does not contain transaction rows")

    return rows, [str(column).strip() for column in reader.fieldnames]
