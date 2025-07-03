from metagpt.roles import Role
from m_agent.action.SimpleWriteCode import SimpleWriteCode
from m_agent.action.SimpleRunCode import SimpleRunCode
from metagpt.schema import Message
from metagpt.logs import logger
class RunnableCoder(Role):
    def __init__(
        self,
        name: str = "Alice",
        profile: str = "RunnableCoder",
        **kwargs,
    ):
        super().__init__(name, profile, **kwargs)
        self._init_actions([SimpleWriteCode, SimpleRunCode])#初始化定义的一个写代码action和一个执行代码的action
        self._set_react_mode(react_mode="by_order")
        """
        设置角色对监听到的消息做出反应的策略，
        react:llm标准思考-行动循环，交替思考和行动,
        “by_order”：每次按照_init_actions中定义的顺序切换选择action
        “plan_and_act”：首先计划，然后执行操作序列，即
        """


    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备 {self._rc.todo}")
        # 通过在底层按顺序选择动作
        # todo 首先是 SimpleWriteCode() 然后是 SimpleRunCode()
        todo = self._rc.todo

        msg = self.get_memories(k=1)[0] # 得到最相似的 k 条消息
        result = await todo.run(msg.content)

        msg = Message(content=result, role=self.profile, cause_by=type(todo))
        self._rc.memory.add(msg)
        return msg