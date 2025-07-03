from metagpt.actions import UserRequirement
from metagpt.roles import Role
from m_agent.action.SqlWriteCode import SqlWriteCode
from m_agent.action.SqlWriteTest import SqlWriteTest
from m_agent.action.SqlprojectTool import SqlprojectTool
from m_agent.action.SqlprojectContent import SqlprojectContent
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.utils.common import any_to_name
class Sqlproject(Role):#role是定义谁能执行action定义的功能
    name: str = "Gin"
    profile: str = "数据分析师"
    goal:str="准确理解并分析用户的数据需求，包括但不限于报表、指标和数据分析项目。将这些需求转化为具体、清晰的数据需求，以便数据库管理员能够高效地提供所需数据"
    constraints: str = (
        "1. 不要请求用户没要求你获取的数据"
        "2.如果无法明确用户需要什么数据请写下：Fail"
        "3.查询现行或者现有数据，统一用半年内的数据"
    )

    def __init__(self,task_id,**kwargs) -> None:
        super().__init__(**kwargs)
        self.task_id=task_id
        self._watch([SqlprojectTool])
        self._init_actions([SqlprojectContent])



    async def _act(self) -> Message:
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        todo = self.rc.todo
        context = self.get_memories()
        #context = self.get_memories()  # 使用所有记忆作为上下文
        context=context[0]
        code_text = await todo.run(context)  # 指定参数
        if code_text != "":
            msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        else:
            code_text="没找到相关数据，请检查您的问题是否有误"
            msg = Message(content=code_text, role=self.profile, cause_by=type(todo), send_to='Verus')

        return msg