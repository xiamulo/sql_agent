from metagpt.actions import UserRequirement
from metagpt.roles import Role
from m_agent.action.SqlWriteCode import SqlWriteCode
from m_agent.action.SqlWriteTest import SqlWriteTest
from m_agent.action.SqlprojectTool import SqlprojectTool
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.utils.common import any_to_name
from util.sqlutil import insert_data_zb
class Sqltool(Role):#role是定义谁能执行action定义的功能
    name: str = "toolgin"
    profile: str = "数据分析师3"
    goal:str="精准理解用户数据需求，根据需求选择对应的API。"
    constraints: str = (
        "1. 能够准确理解用户的需求选择正确的API"
        "2.一周的数据从周一到周日计算，计算月的数据从1号到月底"
        "3.一次只能选择一个API，如果没找到对应API的则输出Fail即可"
        "4.只能按照output格式输出json，一定不能输出其他文字信息"
    )

    def __init__(self,task_id,**kwargs) -> None:
        super().__init__(**kwargs)
        self.task_id=task_id
        self._watch([UserRequirement])
        self._init_actions([SqlprojectTool])

    def convert_to_chinese_num(self,num):
        CN_NUM = {
            '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
            '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
        }

        CN_UNIT = {
            0: '', 1: '十', 2: '百', 3: '千', 4: '万', 5: '十',
            6: '百', 7: '千', 8: '亿', 9: '十', 10: '百', 11: '千',
            12: '兆', 13: '十', 14: '百', 15: '千'
        }

        if num < 0:
            return "负" + self.convert_to_chinese_num(-num)

        str_num = str(num)
        len_num = len(str_num)

        if len_num == 1:
            return CN_NUM[str_num]

        chinese_num = ""
        for i, digit in enumerate(str_num):
            if digit != '0':
                chinese_num += CN_NUM[digit] + CN_UNIT[len_num - i - 1]
            else:
                if not chinese_num.endswith(CN_NUM['0']):
                    chinese_num += CN_NUM['0']

        # 处理10-19的读法问题
        chinese_num = chinese_num.replace('一十', '十')

        # 处理连续零的情况
        while '零零' in chinese_num:
            chinese_num = chinese_num.replace('零零', '零')

        # 处理单位前的零的情况
        for unit in ['万', '亿', '兆']:
            if chinese_num.endswith('零' + unit):
                chinese_num = chinese_num.replace('零' + unit, unit)

        # 处理最后一个零的情况
        if chinese_num.endswith('零'):
            chinese_num = chinese_num[:-1]

        return chinese_num

    def dict_to_natural_language(self,dict_list):
        """
        Convert a list of dictionaries to a natural language description.

        :param dict_list: List of dictionaries to convert
        :return: A string with the natural language description
        """
        natural_text = "以下是查询出来的总的数据共"+str(len(dict_list))+"条，请根据以下数据进行分析\n"

        for i, dictionary in enumerate(dict_list, 1):
            natural_text += f"第{self.convert_to_chinese_num(i)}条数据："
            for key, value in dictionary.items():
                try:
                    natural_text += key+"为："+dictionary.get(key)+" "
                except Exception as e:
                    natural_text += key + "为：未查询到数据"
            natural_text=natural_text+"\n"
        # natural_text += f"提单号：{dictionary.get('提单', '未提供')}，"
            # natural_text += f"由船公司{dictionary.get('船司', '未提供')}处理。"
            # natural_text += f"实际到港时间为{dictionary.get('实际到港时间', '未提供')}，"
            # natural_text += f"实际开船时间为{dictionary.get('实际开船时间', '未提供')}。\n"
            # natural_text += f"货物可提取时间定于{dictionary.get('可提时间', '未提供')}，"
            # natural_text += f"提柜时间为{dictionary.get('提柜时间', '未提供')}，"
            # natural_text += f"最终还柜时间为{dictionary.get('还柜时间', '未提供')}。\n\n"

        return natural_text.strip()

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        todo = self.rc.todo
        # context = self.get_memories(k=1)[0].content # 使用最近的记忆作为上下文
        context = self.get_memories()  # 使用所有记忆作为上下文
        code_text = await todo.run(context)  # 指定参数
        if code_text=="":
            msg = Message(content=code_text, role=self.profile, cause_by=type(todo),send_to="Gin")
        else:
            code_texts=""
            #code_texts = "以下根据您的需求查询出来的数据，共有" + str(len(code_text)) + "条\n"
            i=0
            co=code_text
            code_text=self.dict_to_natural_language(code_text)
            #code_text=str(code_text)
            code_text="#sql语句\n"+"SELECT 提单, 船司, 实际到港时间, 实际开船时间, 可提时间,提柜时间,还柜时间 FROM 提单时效表 WHERE 实际到港时间 BETWEEN '2023-11-01' AND '2023-11-07'"+"\n#数据库查询结果\n"+code_text
            # for c in code_text:
            #     i=i+1
            #     code_texts=code_texts+"第"+i+"条数据"+str(c)+"\n"
            #code_text=code_texts
            msg = Message(content=code_text, role=self.profile, cause_by=type(todo),send_to='Verus')
            sqls = """INSERT INTO agent_task_log (task_id, source, content, status) VALUES (%s,  %s, %s, %s);"""
            jsons=str(co).replace("'",'"')
            insert_data_zb(sqls, self.task_id, "sql_result", jsons, 1)
        return msg