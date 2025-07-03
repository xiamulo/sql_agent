from metagpt.actions import Action
import re
from util.sqlutil import get_table_info,select_data_list,insert_data,select_data_sql
class SimpleWriteCode(Action):
    PROMPT_TEMPLATE: str = """
    # 数据库表结构
    {table_info}
    # 注意事项
    角色：您是一位经验丰富的数据分析师；您的主要任务是理解老板需求以及意图，根据数据库表结构将需求和意图转化为具体的数据查询请求，提交给数据库管理员。
    您需要与数据库管理员沟通，提供清晰、精确的数据需求描述，以便数据库管理员可以编写有效的SQL查询语句。
    您应使用数据分析工具来分析数据库管理员提供的数据，并从中提取有价值的信息。
    在接收到查询结果后，您必须根据用户需求对数据进行进一步分析，并提供洞察。

    数据需求明确化
    1.明确需求。在与数据库管理员沟通前，确保您完全理解用户的业务需求和数据分析目标。
    2.任务：明确您需要哪些数据来完成分析任务，比如特定的时间范围、数据字段、数据量级等。
    3.需求描述：准备一个清晰的需求描述，包括所需数据的类型、格式、关键指标等，以便数据库管理员能够理解并准确执行。
    4.请确保您的需求描述没有遗漏任何关键信息，并且尽可能具体。
    5.在收到查询结果后，仔细检查数据是否符合您的需求，并准备好可能的后续问题或进一步的数据请求。
    6.请确保您的需求与数据库管理员提供的表结构和字段相匹配。
    7.根据查询结果，与数据库管理员进行沟通以优化和调整查询语句，以获得更准确或更高效的数据。
    8.确保您的数据请求专注于所需数据，避免请求不必要的信息。
    9.您的数据需求应基于用户实际提供的描述，避免基于个人假设或猜测。
    # context
    # {instruction}
    """

    name: str = "SimpleWriteCode"

    async def run(self, instruction: str):
        table_infos, f_names = get_table_info("wl_demo")
        table_info = ""
        for t in table_infos:
            table_info += "\n" + t
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction, table_info=table_info)
        rsp = await self._aask(prompt)
        return rsp

    @staticmethod
    def parse_code(rsp):
        pattern = r'```python(.*)```'
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text