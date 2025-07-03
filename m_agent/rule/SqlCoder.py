from metagpt.schema import Message
from m_agent.action.SqlWriteCode import SqlWriteCode
from m_agent.action.SqlprojectContent import SqlprojectContent
from metagpt.logs import logger
from metagpt.roles import Role
from util.sqlutil import insert_data_zb
from pydantic import Field
class SqlCoder(Role):
    name: str = "Alice"
    profile: str = "数据库管理员"
    goal: str='编写准确的MySQL查询语句，以响应数据分析师的数据检索和分析需求。确保查询结果的正确性.'
    constraints: str = (

        "1. 应当确保查询语句能够在不同的数据集上具有良好的可扩展性和适应性。"
        "2. 在必要时，应提供查询优化建议和性能调优方案，以帮助维护数据库的长期健康。"
        "3. 如果需要编写多个mysql语句，请使用----分割mysql语句"
        "4. 只需要编写mysql语句即可，不要返回其他不想关信息或者废话"
        "5. 不要编写使用聚合函数进行计算的sql语句，数据分析师自己会计算"
        "6. 一定要忽略数据分析师需要进行计算的需求"
        "7. 需要计算的需求不要管，数据分析师会进行计算"
    )


    def __init__(self,task_id, **kwargs):
        super().__init__(**kwargs)
        self.task_id=task_id
        self._init_actions([SqlWriteCode])
        self._watch([SqlprojectContent])
        # self._watch([SimpleWriteCode, SimpleWriteReview])  # feel free to try this too

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        contexts = self.get_memories()
        # context = self.get_memories(k=1)[0].content # use the most recent memory as context
        context = contexts[1]  # use all memories as context
        code_text = await todo.run(context)  # specify arguments
        sqls = """INSERT INTO agent_task_log (task_id, source, content, status) VALUES (%s,  %s, %s, %s);"""
        insert_data_zb(sqls, self.task_id, self.rc.todo.name, code_text, 1)
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))
        
        return msg