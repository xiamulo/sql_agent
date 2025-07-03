from metagpt.actions import Action
import re
from util.sqlutil import select_data_list,get_table_info
from util.sqlutil import insert_data_zb
from typing import Optional
PROMPT_TEMPLATE = """
# 数据库表结构
{table_info}
Role: 您是一位资深开发与质量保证工程师，您的任务是根据数据库表结构对SQL语句中使用到的字段进行严格审查，确保符合数据分析师的明确需求。
如果运行结果无误，您需要给予明确的批准并将结果返回给数据分析师。
若运行结果显示有错误，您必须指出错误发生在SQL语句的哪一部分，并提供详细的修正指导给数据库管理员。
如果运行结果无误，但是运行结果为空请检查sql语句中的字段是否与数据分析师提出的需求一致并提供详细的修正指导给数据库管理员
以下是SQL语句和输出信息：
{context}
---
## instruction:
请总结SQL语句执行错误的原因，根据数据库表结构给出具体的修正指导。
## Status:
注意如果结果不为空，只是sql语句不规范请请写下：PASS。
如果SQL语句完全正常工作，不需要任何改动，请写下：PASS。
如果SQL语句存在逻辑错误、执行错误或是字段使用错误，请写下：FAIL。
在此部分一定要写一个词：PASS或FAIL。
"""



class SqlWriteTest(Action):
    name: str = "SqlWriteTest"
    context: Optional[str] = None
    """
    测试人员

    """




    @staticmethod
    def parse_code(rsp):
        if "sql" in rsp:
            pattern = r"```sql\n([\s\S]*?);?\n```"
            code_text = re.findall(pattern, rsp)
            return code_text
        else:
            code_text=[rsp]
            return code_text


    def clean_code(self,source_code):
        source_code = str(source_code).replace("[","").replace("]","")
        sql_statements = re.findall(r'(SELECT.*?)(?=--|$)', str(source_code), re.DOTALL)
        sql_List=[]
        # 输出 SQL 语句
        for i, sql in enumerate(sql_statements, 1):
            # 移除尾部的分号和空格
            sql = sql.strip().rstrip(';')
            sql=sql.replace(r"\\n","")
            sql=sql.replace("\\n","")
            sql_List.append(sql)
        return sql_List
    def run_code(self,code_text):
        sql_List=[]
        try:
            source_code = code_text[-1].content
            source_code = SqlWriteTest.parse_code(source_code)
            if "--" in source_code[0]:
                source_code=self.clean_code(source_code)
            for code in source_code:
                try:
                    code=code
                    result = select_data_list(code)
                    sql_List.append({"sql_code":code,"result":result})
                except Exception as e:
                    sql_List.append({"sql_code": code, "result": str(e)})
            return sql_List
        except Exception as e:
            return sql_List

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
        sum_dict=0
        for s in dict_list:
            sum_dict=len(s)+sum_dict
        natural_text = "\n"+"## 数据查询结果"+"\n以下是查询出来的数据共"+str(sum_dict)+"条，请根据以下数据进行分析\n"
        if len(dict_list)==1:
            for i, dictionary in enumerate(dict_list[0], 1):
                natural_text += f"第{self.convert_to_chinese_num(i)}条数据："
                for key, value in dictionary.items():
                    try:
                        natural_text += key+"为："+dictionary.get(key)+" "
                    except Exception as e:
                        natural_text += key + "为：未查询到数据"
                natural_text=natural_text+"\n"
        else:
            b=0
            for d in dict_list:
                for i, dictionary in enumerate(d, 1):
                    b=b+1
                    natural_text += f"第{self.convert_to_chinese_num(b)}条数据："
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

    async def run(self, context:str) :
        table_infos, f_names = get_table_info("wl_demo")
        table_info = ""
        for t in table_infos:
            table_info += "\n" + t
        source_code = context[-1].content
        if source_code=="":
            return "PASS"
        task=context[0]
        context=context
        sql_List = self.run_code(context)
        i=0
        content=""
        sqls_result=""
        llm_result=[]
        for sqls in sql_List:
            i=i+1
            code = sqls.get("sql_code")
            result = sqls.get("result")
            llm_result.append(result)
            if len(sql_List)>1:
                sqls_result=sqls_result+str(result)+"----"
            else:
                sqls_result = sqls_result + str(result)
            content=content+"\n"+"## sql语句\n## 第"+str(i)+"个Sql\n"+code+"```\n## 运行输出\n## 第"+str(i)+"个sql运行输出结果:"+str(result)

        if "----" in sqls_result:
            sqls_result = sqls_result.rstrip("-")
        prompt = PROMPT_TEMPLATE.format(context=content, table_info=table_info)
        while True:
            try:
                rsp = await self._aask(prompt)
                break
            except Exception as e:
                print(e)
        if "PASS" in rsp:
            rsp = self.dict_to_natural_language(llm_result)
            rsp=rsp+"------#数据库查询结果\n"+str(content)
        # code_text = SimpleWriteTest.parse_code(rsp)
        return rsp