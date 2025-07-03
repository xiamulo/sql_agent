from m_agent.action.SimpleWriteTest import SimpleWriteTest
from m_agent.action.SimpleWriteCode import SimpleWriteCode
from m_agent.action.SimpleWriteReview import SimpleWriteReview
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.roles import Role
from pydantic import Field
class SimpleTester(Role):
    name: str =  "Bob"
    profile: str =  "SimpleTester"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_actions([SimpleWriteTest])
        self._watch([SimpleWriteCode])
        # self._watch([SimpleWriteCode, SimpleWriteReview])  # feel free to try this too

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        # context = self.get_memories(k=1)[0].content # use the most recent memory as context
        context = self.get_memories()  # use all memories as context

        code_text = await todo.run(context, k=5)  # specify arguments
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))

        return msg