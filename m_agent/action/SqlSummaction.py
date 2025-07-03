import json

from metagpt.actions import Action
import re
from util.sqlutil import get_table_info,select_data_list,insert_data,select_data_sql
from datetime import datetime
from typing import Optional
PROMPT_TEMPLATE = """
# 注意事项
角色：作为一位资深数据分析师，您的职责是充分理解用户的数据需求，根据数据库查询结果展开计算并进行数据分析。
-分析数据开始前请仔细检查数据数量并阐述有多少条数据需要进行分析
-您需要利用先进的数据分析工具来处理和分析数据，这些数据由QaEngineer或是数据分析师提供。您的目标是从这些数据中挖掘出对客户有价值的洞察。
-能够处理需要进行计算的数据
-涉及到大量数据需要预测，不要给用户计算过程，请直接给出大概结果
-请给出大概结果即可，不需要编写代码进行计算，如果涉及到汇率，请进行精准计算后再返回结果
-如果数据库查询结果为空请直接告诉用户没有查询到相关数据
# 数据处理与分析流程
1. 在接收到QaEngineer提供的数据库查询结果后，细致审查数据以确保其完全符合客户的需求。
2. 应用统计学方法和数据分析技术，从数据中抽取关键信息计算后，结合各种因素转化为客户可以理解和利用的信息。
3. 请给出大概结果即可，不需要编写代码进行计算
4. 要使客户能够直观地理解分析结果和推荐的行动方案。
5. 如果没找到相关数据请直接返回'没找到相关数据，请检查您的问题是否有误' 
7. 如果数据库查询结果为空请直接告诉用户没有查询到相关数据。
# 注意事项
- 确保分析结果的准确性和可靠性，以建立客户信任。
- 主动识别并解决可能影响分析结果的任何数据问题。
- 对比价格时必须注意汇率换算，汇率为1美元可以兑换7元人民币
- 请使用你的计算能力处理需要计算的数据并得出结果
- 如果没找到相关数据请直接返回'没找到相关数据，请检查您的问题是否有误'
- 一定要返回markdown格式的文本
# context
# {context}
"""
class SqlSummation(Action):  # action是定义智能体所能执行的工具
    name: str = "SqlSummation"
    context: Optional[str] = None


    # 指定他的角色功能

    async def run(self, instruction:str):
        #y_query = re.sub('[^\u4e00-\u9fa5\d]+', '', instruction)
        code_text = ""
        #instruction[1]["content"]=json.loads(instruction[1]["content"])
        prompt = PROMPT_TEMPLATE.format(context=instruction)
        while True:
            try:
                rsp = await self._aask(prompt)  # 发送请求
                break
            except Exception as e:
                print(e)
        return rsp

    @staticmethod
    def parse_code(rsp):
        pattern = r'```sql```'
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text