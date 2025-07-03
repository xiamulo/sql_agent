from metagpt.actions import Action
import re
from util.sqlutil import get_table_info,select_data_list,insert_data,select_data_sql
from datetime import datetime
from typing import Optional

class SqlWriteCode(Action):  # action是定义智能体所能执行的工具
    PROMPT_TEMPLATE: str = """
    # 数据库表结构
    {table_info}

    # 数据库管理员注意事项
    角色：作为一位经验丰富的数据库管理员，您的主要任务是根据数据分析师的数据需求以及数据库表结构，快速准确地生成MySQL查询语句。
    - 需要计算的需求不要管，数据分析师会进行计算
    - 根据数据分析师的数据需求编写MySQL语句，您的查询应遵循MySQL编码最佳实践，保证查询效率、可读性和维护性。
    - 使用MySQL数据库管理工具或MySQL编辑器来辅助编写和测试这些查询语句。
    - 确保查询语句能够在不同的数据集上具有良好的可扩展性和适应性。
    - 提供符合用户需求的查询示例，并在提交的SQL中给出这些示例。
    - 如果需要编写多个sql语句，请使用----分割sql语句。
    - 只需要编写sql语句即可，不要返回其他不想关信息或者废话。
    - 不要编写使用聚合函数进行计算的sql语句，用户自己会计算。
    - 一定要忽略数据分析师需要进行计算的需求
    - 不能创建索引。
    # SQL查询要求
    1. 力求完全满足需求，充分利用数据库系统的内置函数和特性。如果缺少必要功能，请考虑自定义函数或存储过程。
    2. 任务：根据提供的数据需求实现一个或多个SQL查询语句，注意只以SQL语句形式返回。您的查询语句将用于数据库操作，请确保实现的查询语句准确、高效且可复用。
    3. 编写查询前思考：这个查询需要解决什么问题？它需要返回哪些数据？
    4. 仔细检查确保查询语句没有语法错误，并符合数据库查询最佳实践。
    5. 在向QaEngineer提交查询语句前，请仔细检查以确保它们能够正确执行，并满足数据分析师的数据需求。
    6. 请勿使用表结构中未提及的数据库对象或字段。
    7. 根据QaEngineer的反馈以及提供的查询语句进行必要的优化和修改。
    8. 查询语句中应只包含必要的语句，避免包含不相关的子查询或联结。
    9. 查询必须基于数据分析师提供的描述，不得基于假设的需求。
    10.如果需要编写多个sql语句，请使用----分割sql语句。
    11. 不能创建索引。
    12. 只需要编写sql语句即可，不要返回其他不想关信息或者废话。
    13. 不要编写使用聚合函数进行计算的sql语句，用户自己会计算。
    14. 一定要忽略数据分析师需要进行计算的需求
    
    # 上下文
    # {context}

    # out_put
    SELECT * FROM user;

    """

    name: str = "SqlCoder"


    async def run(self,instruction: str):
        table_infos, f_names = get_table_info("wl_demo")
        table_info = ""
        for t in table_infos:
            table_info += "\n" + t
        # Begin a task that runs in the background.
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y年%m月%d日")
        current_time_str2 = current_time.strftime("%Y-%m")
        #y_query = re.sub('[^\u4e00-\u9fa5\d]+', '', instruction)
        code_text = ""
        prompt = self.PROMPT_TEMPLATE.format(context=instruction, table_info=table_info)
        while True:
            try:
                rsp = await self._aask(prompt)
                break
            except Exception as e:
                print(e)
        # print(rsp)
        # code_text = SqlWriteCode.parse_code(rsp)  # 获得结果
        return rsp

    @staticmethod
    def parse_code(rsp):
        pattern = r"```sql\n([\s\S]*?);?\n```"
        code_text = re.findall(pattern, rsp)
        return code_text