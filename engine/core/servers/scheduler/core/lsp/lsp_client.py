from dataclasses import dataclass
from os import path
from threading import Event
from typing import Dict, Optional

from pylsp import uris

from ...core.lsp import SessionId, SessionOptions
from ...core.lsp.session import PUBLISH_DIAGNOSTICS, LspSession
from ...core.svc import get_svc
from ...logger import logger
from ...utils.platform_utils import platform_python_venv_path

document_uri = "file:///Untitled.py"

LSP_EXIT_TIMEOUT = 5000


class LspClient(object):
    _project_path: str
    _document_version: int = 1
    _document_text: str = ""
    _document_diags: Dict = None
    _pending_diag_event: Event = None

    _lsp_session: LspSession

    def __init__(self, project_id: str):
        self.svc = get_svc()
        self._project_path = path.join(path.abspath(self.svc.config.app_server.venv_base_dir), project_id)
        self._lsp_session = LspSession()
        self._lsp_session.enter()

    def initialize(self, session_options: SessionOptions):
        python_base_path = platform_python_venv_path(self._project_path)

        init = {
            "rootUri": uris.from_fs_path(self._project_path),
            "rootPath": self._project_path,
            "processId": 1,
            "capabilities": {
                "textDocument": {
                    "publishDiagnostics": {
                        "tagSupport": {
                            "valueSet": [
                                1,
                                2,
                            ]
                        },
                        "versionSupport": True,
                    },
                    "hover": {
                        "contentFormat": ["markdown", "plaintext"],
                    },
                    "signatureHelp": {},
                },
            },
        }

        if session_options.locale is not None:
            init["locale"] = session_options.locale

        self._document_text = session_options.code or ""

        self._lsp_session.initialize(init)

        # 监听来自 language server 的诊断信息
        def _handler(diag_info):
            # 更新缓存的诊断信息
            self._document_diags = diag_info

            if self._pending_diag_event is not None:
                self._pending_diag_event.set()

        self._lsp_session.set_notification_callback(PUBLISH_DIAGNOSTICS, _handler)

        # Update the settings
        self._lsp_session.notify_did_change_configuration(
            {
                "settings": {
                    "pylsp": {
                        "plugins": {
                            "pycodestyle": {"enabled": False},
                            "pyflakes": {"enabled": True},
                            "mccabe": {"enabled": True},
                            "pylint": {"enabled": False},
                            "jedi": {"environment": python_base_path},
                        },
                    }
                }
            }
        )

        # Simulate an "open file" event
        self._lsp_session.notify_did_open(
            {
                "textDocument": {
                    "uri": document_uri,
                    "languageId": "python",
                    "version": self._document_version,
                    "text": self._document_text,
                }
            }
        )

    def get_diagnostics(self, code: str):
        code_changed = self._document_text != code

        if not code_changed and self._document_diags is not None:
            return self._document_diags.get("diagnostics")

        if code_changed:
            self.update_text_document(code)

        if self._pending_diag_event is None or self._pending_diag_event.is_set():
            self._pending_diag_event = Event()

        self._pending_diag_event.wait(2)  # 2 seconds timeout

        if self._document_diags is not None:
            return self._document_diags.get("diagnostics")

    def get_hover_info(self, code: str, position):
        if self._document_text != code:
            self.update_text_document(code)

        params = {
            "textDocument": {
                "uri": document_uri,
            },
            "position": position,
        }

        return self._lsp_session.text_document_hover(params)

    def get_rename_edits(self, code: str, position, new_name: str):
        if self._document_text != code:
            self.update_text_document(code)

        params = {
            "textDocument": {
                "uri": document_uri,
            },
            "position": position,
            "newName": new_name,
        }

        return self._lsp_session.text_document_rename(params)

    def get_signature_help(self, code: str, position):
        if self._document_text != code:
            self.update_text_document(code)

        params = {
            "textDocument": {
                "uri": document_uri,
            },
            "position": position,
        }

        return self._lsp_session.text_document_signature_help(params)

    def get_completion(self, code: str, position):
        if self._document_text != code:
            self.update_text_document(code)

        params = {
            "textDocument": {
                "uri": document_uri,
            },
            "position": position,
        }

        return self._lsp_session.text_document_completion(params)

    def resolve_completion(self, completion_item):
        return self._lsp_session.completion_item_resolve(completion_item)

    def update_text_document(self, code: str) -> int:
        self._document_text = code
        self._document_version += 1

        logger.info(f"Updating text document to version ${self._document_version}")

        try:
            self._lsp_session.notify_did_change(
                {
                    "textDocument": {
                        "uri": document_uri,
                        "version": self._document_version,
                    },
                    "contentChanges": [{"text": code}],
                }
            )
            logger.info("Successfully sent text document to language server")
            return self._document_version
        except Exception as e:
            logger.error(f"Error sending text document to language server: ${e}")

    def shutdown(self):
        self._lsp_session.exit()


@dataclass
class Session:
    id: SessionId  # 唯一的会话 ID
    lang_client: Optional[LspClient] = None  # 语言客户端
    options: Optional[SessionOptions] = None  # 会话选项
