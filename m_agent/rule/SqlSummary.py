from metagpt.actions import UserRequirement
from metagpt.roles import Role
from m_agent.action.SqlWriteCode import SqlWriteCode
#from m_agent.action.SqlprojectTool import SqlprojectTool
from m_agent.action.SqlWriteTest import SqlWriteTest
from m_agent.action.SqlSummaction import SqlSummation
from metagpt.schema import Message
from metagpt.logs import logger
from util.sqlutil import insert_data_zb
class SqlSummary(Role):#role是定义谁能执行action定义的功能
    name: str = "Verus"
    profile: str = "数据分析工程师"
    goal:str ="准确理解用户数据需求，根据相关数据运用统计学和数据分析方法对数据进行深入计算分析。将结果转化为直观、易理解的文本"
    constraints: str = (
        "1. 必须能够理解和分析来自不同业务领域的数据需求，包括财务、运营、市场营销等,以确保分析结果的准确性和深度。"
        "2. 分析结果应通俗易懂并且简单明了，避免行业术语，确保用户无需专业背景即可理解。"
        "3. 拥有强大的计算能力。"
        "4. 对比价格时必须注意汇率换算，汇率为1美元可以兑换7元人民币。"
        "5.如果没找到相关数据请直接返回'没找到相关数据，请检查您的问题是否有误'"
        "6. 一定要返回markdown格式的文本。"
        "7.返回字数一定不能超过400字"

    )

    def __init__(self,task_id, **kwargs) -> None:
        super().__init__(**kwargs)
        self.task_id=task_id
        self._watch([SqlWriteTest])  # 监听老板给的信息，以及数据库管理员的信息
        self._init_actions([SqlSummation])  # 设置初始化执行人，他会自己选择action完成任务



    async def _act(self) -> Message:
        logger.info(f"{self._setting[0]}: ready to {self.rc.todo}")
        todo = self.rc.todo
        msgs=[]
        contexts = self.get_memories()
        msgs.append(contexts[0])
        msgs.append(contexts[-1])
        # context = self.get_memories(k=1)[0].content # 使用最近的记忆作为上下文
        context = msgs  # 使用所有记忆作为上下文

        code_text = await todo.run(context)  # 指定参数
        sqls = """INSERT INTO agent_task_log (task_id, source, content, status) VALUES (%s,  %s, %s, %s);"""
        insert_data_zb(sqls, self.task_id, self.rc.todo.name, code_text, 1)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))

        return msg