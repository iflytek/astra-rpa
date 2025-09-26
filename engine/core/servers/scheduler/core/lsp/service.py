import json
from typing import Optional
from uuid import uuid4

from ...logger import logger
from . import SessionId, SessionOptions
from .lsp_client import LspClient, Session

# Map of active sessions indexed by ID
active_sessions: dict[SessionId, Session] = {}

# List of inactive sessions that can be reused.
inactive_sessions: list[Session] = []

# Maximum time a session can be idle before it is closed.
maxSessionLifetime = 1 * 60 * 1000  # 1 minute

# 最大的缓存 lsp 实例的数量
max_inactive_session_count = 10


def get_session_by_id(session_id: SessionId) -> Optional[Session]:
    session = active_sessions.get(session_id)
    return session


def create_session(session_options: SessionOptions) -> SessionId:
    """
    Allocate a new session and return its ID.
    """

    # See if there are any inactive sessions that can be reused.
    compatible_session = get_compatible_session(session_options)

    if compatible_session:
        return restart_session(compatible_session, session_options)

    return start_session(session_options)


def start_session(session_options: SessionOptions = None) -> SessionId:
    """
    Start a new session and return its ID.
    """
    logger.info("Starting new session")

    session_id = str(uuid4())
    lang_client = LspClient(session_options.project_id)

    active_sessions[session_id] = Session(
        id=session_id,
        options=session_options,
        lang_client=lang_client,
    )

    lang_client.initialize(session_options=session_options)

    if session_options.code:
        lang_client.get_diagnostics(session_options.code)
        logger.info("Received diagnostics from warm up")

    return session_id


def restart_session(session: Session, session_options: SessionOptions = None) -> SessionId:
    logger.info(f"Restarting inactive session ${session.id}")

    session.options = session_options
    active_sessions[session.id] = session

    if session.lang_client and session_options.code is not None:
        session.lang_client.get_diagnostics(session_options.code)

    return session.id


def close_session(session_id: SessionId):
    session = active_sessions.get(session_id)

    if session is None:
        return

    active_sessions.pop(session_id)
    inactive_sessions.append(session)

    if len(inactive_sessions) > max_inactive_session_count:
        logger.info("Inactive session count exceeded max limit, closing oldest session")
        inactive_session = inactive_sessions.pop(0)
        inactive_session.lang_client.shutdown()

    logger.info(f"Recycling session (currently ${len(inactive_sessions)} in inactive queue)")


def get_diagnostics(session: Session, session_options: SessionOptions):
    lang_client = session.lang_client
    if lang_client is None:
        return

    return lang_client.get_diagnostics(session_options.code)


def get_hover_info(session: Session, session_options: SessionOptions):
    lang_client = session.lang_client
    if lang_client is None:
        return

    return lang_client.get_hover_info(session_options.code, session_options.position)


def get_rename_edits(session: Session, session_options: SessionOptions):
    lang_client = session.lang_client
    if lang_client is None:
        return

    return lang_client.get_rename_edits(session_options.code, session_options.position, session_options.newName)


def get_signature_help(session: Session, session_options: SessionOptions):
    lang_client = session.lang_client
    if lang_client is None:
        return

    return lang_client.get_signature_help(session_options.code, session_options.position)


def get_completion(session: Session, session_options: SessionOptions):
    lang_client = session.lang_client
    if lang_client is None:
        return

    return lang_client.get_completion(session_options.code, session_options.position)


def resolve_completion(session: Session, session_options: SessionOptions):
    lang_client = session.lang_client
    if lang_client is None:
        return

    return lang_client.resolve_completion(session_options.completionItem)


def get_compatible_session(session_options: SessionOptions = None) -> Optional[Session]:
    """查找可复用的 session"""
    logger.info("Looking for compatible session")

    keys_to_pick = ["locale", "project_id", "config_overrides"]
    requested_options = {k: getattr(session_options, k) for k in keys_to_pick}
    logger.info("Requested options: %s", json.dumps(requested_options))

    def find_session(sessions: list[Session]) -> Optional[Session]:
        for index, session in enumerate(sessions):
            existing_options = {k: getattr(session.options, k) for k in keys_to_pick}
            logger.info("Existing options: %s", json.dumps(existing_options))

            if requested_options != existing_options:
                continue

            logger.info("Found compatible session")
            return sessions.pop(index)  # 从列表中移除并返回会话

        return None

    # 1. 先从 active sessions 中查找
    active_session = find_session(list(active_sessions.values()))
    if active_session:
        return active_session

    # 2. 再从 inactive sessions 中查找
    inactive_session = find_session(inactive_sessions)
    if inactive_session:
        return inactive_session

    logger.info("No compatible session found")
    return None
