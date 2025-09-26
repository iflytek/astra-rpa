from typing import Dict, Optional

from pydantic import BaseModel, Field

SessionId = str


class SessionOptions(BaseModel):
    type_checking_mode: Optional[str] = None
    config_overrides: Optional[dict[str, bool]] = Field(default_factory=dict)
    locale: Optional[str] = None
    code: Optional[str] = None
    position: Optional[dict[str, int]] = None
    newName: Optional[str] = None
    completionItem: Optional[dict] = None
    project_id: Optional[str] = None
