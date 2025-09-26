from fastapi import APIRouter, Depends, HTTPException

from ...core.environment.venv import create_project_venv
from ...core.lsp import SessionOptions, service
from ...core.svc import Svc, get_svc
from ...logger import logger

router = APIRouter()


@router.post("/session")
async def create_session(req: SessionOptions, svc: Svc = Depends(get_svc)):
    if req.project_id is None:
        raise HTTPException(status_code=400, detail={"message": "project_id is required"})

    try:
        create_project_venv(svc, req.project_id)
        session_id = service.create_session(req)
        return {"sessionId": session_id}
    except Exception as err:
        logger.error("createNewSession returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})


@router.delete("/session/{sid}")
async def close_session(sid: str):
    return service.close_session(sid)


@router.post("/session/{sid}/diagnostics")
async def get_diagnostics(sid: str, req: SessionOptions):
    session = service.get_session_by_id(sid)

    if session is None:
        raise HTTPException(status_code=400, detail="Unknown session ID")

    try:
        diagnostics = service.get_diagnostics(session, req)
        return {"diagnostics": diagnostics}
    except Exception as err:
        logger.error("getDiagnostics returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})


@router.post("/session/{sid}/hover")
async def get_hover_info(sid: str, req: SessionOptions):
    session = service.get_session_by_id(sid)

    if session is None:
        raise HTTPException(status_code=400, detail="Unknown session ID")

    try:
        hover = service.get_hover_info(session, req)
        return {"hover": hover}
    except Exception as err:
        logger.error("getHoverInfo returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})


@router.post("/session/{sid}/rename")
async def get_rename_edits(sid: str, req: SessionOptions):
    session = service.get_session_by_id(sid)

    if session is None:
        raise HTTPException(status_code=400, detail="Unknown session ID")

    try:
        edits = service.get_rename_edits(session, req)
        return {"edits": edits}
    except Exception as err:
        logger.error("getRenameEdits returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})


@router.post("/session/{sid}/signature")
async def get_signature_help(sid: str, req: SessionOptions):
    session = service.get_session_by_id(sid)

    if session is None:
        raise HTTPException(status_code=400, detail="Unknown session ID")

    try:
        signature_help = service.get_signature_help(session, req)
        return {"signatureHelp": signature_help}
    except Exception as err:
        logger.error("getSignatureHelp returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})


@router.post("/session/{sid}/completion")
async def get_completion(sid: str, req: SessionOptions):
    session = service.get_session_by_id(sid)

    if session is None:
        raise HTTPException(status_code=400, detail="Unknown session ID")

    try:
        completion_list = service.get_completion(session, req)
        return {"completionList": completion_list}
    except Exception as err:
        logger.error("getCompletion returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})


@router.post("/session/{sid}/completionresolve")
async def resolve_completion(sid: str, req: SessionOptions):
    session = service.get_session_by_id(sid)

    if session is None:
        raise HTTPException(status_code=400, detail="Unknown session ID")

    try:
        completion_item = service.resolve_completion(session, req)
        return {"completionItem": completion_item}
    except Exception as err:
        logger.error("resolveCompletion returning a 500: ", exc_info=err)
        raise HTTPException(status_code=500, detail={"message": err or "An unexpected error occurred"})
