from m_agent.action.SimpleWriteTest import SimpleWriteTest
from m_agent.action.SimpleWriteReview import SimpleWriteReview
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.roles import Role
from pydantic import Field
class SimpleReviewer(Role):
    name: str = Field(default="Charlie")
    profile: str = Field(default="SimpleReviewer")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_actions([SimpleWriteReview])
        self._watch([SimpleWriteTest])