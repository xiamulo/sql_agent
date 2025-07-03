from metagpt.actions import Action
import re
from util.sqlutil import get_table_info,select_data_list,insert_data,select_data_sql
from datetime import datetime
from metagpt.actions import Action, ActionOutput
from typing import Optional

class SqlprojectContent(Action):  # action是定义智能体所能执行的工具
    PROMPT_TEMPLATE:str = """
    # 数据库表结构
    {table_info}
    # 注意事项
    角色：您是一位经验丰富的数据分析师；您的主要任务是准确理解并分析用户的数据需求以及意图，根据数据库表结构将这些需求转化为具体、清晰、可执行的数据查询请求，以便数据库管理员能够高效地提供所需数据。
    - 在与数据库管理员沟通时，要使用标准的数据查询语言和技术术语和清晰、精确的数据需求描述，确保准确无误，以便数据库管理员可以编写有效的SQL查询语句
    - 不要请求用户没要求你获取的数据
    - 一定不能编写sql示例给数据库管理员
    - 如果无法明确用户需要什么数据请写下：Fail
    # 数据需求明确化
    1.明确需求。在与数据库管理员沟通前，确保您完全理解用户的业务需求和数据分析目标。
    2.任务：明确您需要哪些数据来完成分析任务，比如特定的时间范围、数据字段、数据量级等。
    3.需求描述：准备一个清晰的需求描述，包括所需数据的类型、格式、关键指标等，以便数据库管理员能够理解并准确执行。
    4.请确保您的需求描述没有遗漏任何关键信息，并且尽可能具体。
    5.请确保您的需求与数据库管理员提供的表结构和字段相匹配。
    6.确保您的数据请求基于用户实际提供的描述，不要请求用户没要求你获取的数据。
    7.您的数据需求应基于用户实际提供的描述，避免基于个人假设或猜测。
    8.查询现行或者现有数据，统一用半年内的数据
    9.如果无法明确用户需要什么数据请写下：Fail
    # context
    # {context}
    # 示例需求
    需求描述：
    1. ...
    2. ...
    """

    name: str = "SqlprojectContent"


    async def run(self,instruction: str):
        #y_query = re.sub('[^\u4e00-\u9fa5\d]+', '', instruction)
        code_text = ""
        table_infos, f_names = get_table_info("wl_demo")
        table_info = ""
        for t in table_infos:
            table_info += "\n" + t
        prompt = self.PROMPT_TEMPLATE.format(context=instruction, table_info=table_info)
        while True:
            try:
                rsp = await self._aask(prompt)
                break
            except Exception as e:
                print(e)

        if "Fail" in rsp or "无法明确" in rsp:
            rsp=""
        return rsp

    @staticmethod
    def parse_code(rsp):
        pattern = r'```sql```'
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text