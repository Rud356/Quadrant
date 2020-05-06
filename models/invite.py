from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Invite:
    id: int
    code: str
    endpoint: int
    expires_at: datetime
    # endless
    members_limit: int = -1