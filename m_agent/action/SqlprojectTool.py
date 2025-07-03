import json

from metagpt.actions import Action
import re
from util.sqlutil import get_table_info,select_data_list,insert_data,select_data_sql
from datetime import datetime
from metagpt.actions import Action, ActionOutput
from typing import Optional

class SqlprojectTool(Action):  # action是定义智能体所能执行的工具
    PROMPT_TEMPLATE:str = """{
   "注意事项": {
    "角色": "您是一位能够调用API进行数据获取的数据分析师；您的主要任务是准确理解并分析context中用户的需求，并从以下API列表中选择对应的api",
    "使用指南": "使用API进行数据获取时，要熟悉并遵循API文档中的规范和参数设置，确保能够准确调用API获取所需数据，。如果没找到合适的api必须返回Fail",
    "输出要求": "不要返回其他不相关的信息,只需要返回json即可，必须按照规定的output格式进行返回json字符串。如果没找到合适的api必须返回Fail"
  },
  "API列表": [
    {
      "API名称": "get_Waybill_id",
      "描述": "查询运单的当前位置或者运单的数据可以用这个。查询订单的当前位置或者订单的数据也可以用这个。",
      "参数": {
        "Waybill_id": {
          "是否必须": true,
          "类型": "字符串"
        }
      }
    },
    {
      "API名称": "get_week_sj_td",
      "描述": "查询时间段内有多少实际到港的提单。,
      "参数": {
        "start_date": {
          "是否必须": true,
          "类型": "字符串"
        },
        "end_date": {
          "是否必须": true,
          "类型": "字符串"
        }
      }
    },
    {
      "API名称": "get_week_td",
      "描述": "查询时间段内有多少预计到港的提单。",
      "参数": {
        "start_date": {
          "是否必须": true,
          "类型": "字符串"
        },
        "end_date": {
          "是否必须": true,
          "类型": "字符串"
        }
      }
    },
    {
      "API名称": "get_t_id",
      "描述": "查询提单的当前位置或者提单的数据。",
      "参数": {
        "t_id": {
          "是否必须": true,
          "类型": "字符串"
        }
      }
    },
    {
      "API名称": "get_gh_id",
      "描述": "查询柜号的当前位置或者柜号的数据。",
      "参数": {
        "gh_id": {
          "是否必须": true,
          "类型": "字符串"
        }
      }
    },
    {
      "API名称": "get_type_price",
      "描述": "根据报价类型查询哪家的报价最低。报价类型有以下参数，1.海运费，2.空运费，3陆运费",
      "参数": {
        "price_type": {
          "是否必须": true,
          "类型": "字符串"
        }
      }
    },
    {
      "API名称": "get_dontkonw_tool",
      "描述": "参数对不上或者不知道选什么api用这个",
      "参数": {
            不需要参数
        }
      }
    },
    {
      "API名称": "get_cs_time",
      "描述": "根据船司名查到港时效，还柜时效，提柜时效，开船可提时效，到港可提时效，船司名有以下参数COSCO，EXX，CLX+，EMC，EMC(定提)，CLX，ZIM，OOCL，COSCO（定提），COSCO（华东定提），WHL，MSK，EMC(DG)，CMA，其他，ONE，HMM，HLC(赫伯罗特)，MSC地中海航运)，COSCO（NY），EMC-华东，COSCO-华东，YML，ZIM(NY)，",
      "参数": {
            不需要参数
        }
      }
    }
    {
      "API名称": "get_yd_time",
      "描述": "根据运单id查询运单的轨迹之间的耗时。轨迹有以下参数，1.已产生预报，2.货物进入操作中心，3.已释放，4.已装柜，5.官网更新，6.已装船，7.已开船，8.预计到港，9.已靠港，10.已卸船，11.预约提柜，12.已提柜，13.预计，14.已拆柜，15.正在预约，16.已还柜，17.签收完成，18.签收完成",
      "参数": {
        "Waybill_id":{
        "是否必须": true,
        "类型": "字符串"
        "注释":"运单id"
        }
        "start_locus": {
          "是否必须": true,
          "类型": "字符串"
           "注释":"开始轨迹"
        },
        "end_locus": {
          "是否必须": true,
          "类型": "字符串"
          "注释":"结束轨迹"
        }
      }
    },
  ],
  "数据需求明确化与API调用策略": [
    "明确需求。在调用API前，确保您完全理解用户的业务需求和数据分析目标。",
    "任务：明确您需要使用哪个API获取数据来完成分析任务。一次只能选择一个API,如果没找到对应API的则输出Fail即可",
    "时间要求:1.一周的数据从周一到周日计算。"
    "需求描述：根据这些需求选择API调用参数。",
    "确保需求没有遗漏任何关键信息，并且尽可能具体，以便正确设置API调用参数。",
    "确保您的需求与API提供的数据类型和结构相匹配。"
    "只能按照output格式输出json，一定不能输出其他文字信息"
  ],
  "context": "{contexts}",
  "output": {
    "function_name": "{这里填写调用的API名称}",
    "function_arg": "{这里填写调用API时使用的参数}"
  }
}
"""

    name: str = "SqlprojectTool"

    def get_dontkonw_tool(self,function_args):
        return "Fail"

    def get_yd_time(self,function_args):
        Waybill_id=function_args.get('Waybill_id')
        start_locus=function_args.get('start_locus')
        end_locus = function_args.get('end_locus')
        sqls = """
        SELECT 运单号, 轨迹中文描述, 轨迹时间 
        FROM 运单轨迹表 
        WHERE 运单号 = '{yd}' 
        AND (轨迹中文描述 LIKE '%{ms}%' OR 轨迹中文描述 LIKE '%{ms2}%');
                """.format(yd=Waybill_id,ms=start_locus, ms2=end_locus)
        result = select_data_list(sqls)
        return result

    def get_week_sj_td(self,function_args):
        start_date=function_args.get('start_date')
        end_date = function_args.get('end_date')

        sqls = """
                SELECT 提单, 船司, 实际到港时间, 实际开船时间, 可提时间,提柜时间,还柜时间
        FROM 提单时效表
        WHERE 实际到港时间 BETWEEN '%s' AND '%s';
                """%(start_date,end_date)
        result = select_data_list(sqls)
        print(len(result))
        return result

    def get_week_td(self,function_args):
        start_date=function_args.get('start_date')
        end_date = function_args.get('end_date')

        sqls = """
                SELECT 提单, 船司, 预计到港时间, 预计开船时间, 可提时间,提柜时间,还柜时间
        FROM 提单时效表
        WHERE 预计到港时间 BETWEEN '%s' AND '%s';
                """%(start_date,end_date)
        result = select_data_list(sqls)
        return result

    def get_type_price(self,function_args):
        price_type = function_args.get("price_type")
        sqls="""
        SELECT 船司, 报价类型, 币类型, 价格, 开始时间, 结束时间 FROM 运单成本表 WHERE 报价类型 = '%s'
        """%price_type
        result = select_data_list(sqls)
        return result
    def get_gh_id(self,function_args):
        t_id=function_args.get("t_id")
        sqls = """SELECT 提单号, 轨迹英文描述, 轨迹中文描述, 轨迹时间 
        FROM 运单轨迹表 
        WHERE 提单号 = '%s' 
        ORDER BY 轨迹时间 DESC""" % t_id
        result = select_data_list(sqls)
        return result
    def get_cs_time(self,function_args):
        return "Fail"
    def get_t_id(self,function_args):
        t_id=function_args.get("t_id")
        sqls = """SELECT 提单号, 轨迹英文描述, 轨迹中文描述, 轨迹时间 
        FROM 运单轨迹表 
        WHERE 提单号 = '%s' 
        ORDER BY 轨迹时间 DESC LIMIT 10""" % t_id
        result = select_data_list(sqls)
        return result

    def get_Waybill_id(self,function_args):
        Waybill_id=function_args.get("Waybill_id")
        sqls = """SELECT 运单号, 轨迹英文描述, 轨迹中文描述, 轨迹时间 
        FROM 运单轨迹表 
        WHERE 运单号 = '%s' 
        ORDER BY 轨迹时间 DESC""" % Waybill_id
        result = select_data_list(sqls)
        return result
    @staticmethod
    def parse_code(rsp):
        if "json" in rsp:
            pattern = r"```json\n([\s\S]*?);?\n```"
            code_text = re.findall(pattern, rsp)
            return code_text
        else:
            code_text = [rsp]
            return code_text

    async def run(self,instruction: str):
        #y_query = re.sub('[^\u4e00-\u9fa5\d]+', '', instruction)
        code_text = ""

        available_functions = {
            "get_Waybill_id": self.get_Waybill_id,
            "get_t_id":self.get_t_id,
            "get_week_td":self.get_week_td,
            "get_week_sj_td":self.get_week_sj_td,
            "get_gh_id":self.get_gh_id,
            "get_yd_time":self.get_yd_time,
            "get_type_price":self.get_type_price,
            "get_cs_time":self.get_cs_time,
            "get_dontkonw_tool":self.get_dontkonw_tool,
        }
        while True:
            try:
                prompt = self.PROMPT_TEMPLATE.replace("contexts", str(instruction))
                while True:
                    try:
                        rsp = await self._aask(prompt)
                        break
                    except Exception as e:
                        print(e)
                if "Fail" in rsp:
                    rsp=''
                    print("没找到合适的API")
                    break
                else:
                    jsons=SqlprojectTool.parse_code(rsp)[0]
                    jsons = json.loads(jsons)
                    """
                    模型不稳定，会出现output的文本进行干扰，这里加上存不存在output的判断
                    """
                    if "output" in jsons:
                        function_name = jsons["output"]["function_name"]
                        function_to_call = available_functions[function_name]
                        function_args = jsons["output"]['function_arg']
                    else:
                        function_name = jsons["function_name"]
                        function_to_call = available_functions[function_name]
                        function_args = jsons['function_arg']
                    #args1=function_args[0]
                    function_response = function_to_call(
                        function_args=function_args,
                    )
                    rsp=function_response
                    if "Fail" in rsp:
                        rsp = ''
                    break
            except Exception as e:
                print(e)
        return rsp

