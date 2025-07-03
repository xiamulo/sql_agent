from m_agent.action.SqlWriteTest import SqlWriteTest
from m_agent.action.SqlWriteCode import SqlWriteCode
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.roles import Role
from util.sqlutil import insert_data_zb
class SqlTester(Role):
    name: str = "Bob"
    profile: str = "QaEngineer"
    goal: str  = "检验MySQL语句的语法正确性、执行效率、数据准确性和逻辑一致性"
    constraints: str  = (
        "1. 请忽略数据分析师需要进行计算的需求后检查sql语句中的字段是否与数据分析师提出的需求一致"
    )

    def __init__(self,task_id, **kwargs) -> None:
        super().__init__(**kwargs)
        self.task_id=task_id
        self._init_actions([SqlWriteTest])#让这个角色能执行SimpleWriteTest中的模版
        self._watch([SqlWriteCode])#让这个测试角色能看到程序员写了什么

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        # context = self.get_memories(k=1)[0].content # 使用最近的记忆作为上下文
        context = self.get_memories() # 使用所有记忆作为上下文

        code_text = await todo.run(context) # 指定参数
        if "FAIL" not in code_text:
            sqls_result = code_text.split("------")[1]
            sqls_result = sqls_result.split("第1个sql运行输出结果:")[1]
            code_text = code_text.split("------")[0]
            sqls = """INSERT INTO agent_task_log (task_id, source, content, status) VALUES (%s,  %s, %s, %s);"""
            jsons = sqls_result.replace("'", '"')
            insert_data_zb(sqls, self.task_id, "sql_result", jsons, 1)
            msg = Message(content=code_text, role=self.profile, cause_by=type(todo),send_to="Verus")
            sqls = """INSERT INTO agent_task_log (task_id, source, content, status) VALUES (%s,  %s, %s, %s);"""
            insert_data_zb(sqls, self.task_id, self.rc.todo.name, code_text, 1)
        else:
            msg = Message(content=code_text, role=self.profile, cause_by=type(todo),send_to="Alice")
            sqls = """INSERT INTO agent_task_log (task_id, source, content, status) VALUES (%s,  %s, %s, %s);"""
            insert_data_zb(sqls, self.task_id, self.rc.todo.name, code_text, 0)
        # if "PASS" in msg.content:
        #     msg = Message(content="PASS", role=self.profile, cause_by=type(todo))
        return msg