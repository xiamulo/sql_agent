from metagpt.actions import UserRequirement
from metagpt.roles import Role
from m_agent.action.SimpleWriteCode import SimpleWriteCode
from metagpt.schema import Message
from metagpt.logs import logger
from pydantic import Field

class SimpleCoder(Role):
    name: str = "Gin2"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self._init_actions([SimpleWriteCode])