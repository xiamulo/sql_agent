import sys
import os
curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
path = os.path.dirname(sys.path[0])
if path not in sys.path:
    sys.path.append(path)
import asyncio
import os
# 请在环境变量或配置文件中设置您的 OpenAI API 密钥
# os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
# os.environ['OPENAI_API_BASE']="your_openai_api_base_url"
# os.environ["OPENAI_API_MODEL"] = "gpt-4-32k"
import re
import time

#os.environ["MAX_TOKENS"] = "10000"
from metagpt.team import Team
from datetime import datetime

# 获取当前日期时间


from metagpt.logs import logger

from m_agent.rule.SqlCoder import SqlCoder
from m_agent.rule.SqlProject import Sqlproject
from m_agent.rule.SqlTester import SqlTester
from m_agent.rule.SqlSummary import SqlSummary
from m_agent.rule.Sqltool import Sqltool
from util.sqlutil import insert_data,select_data_sql,update_data
async def main(

        #类似一三四798六43零二这种中文加数字的11位的中国手机号
        #类似纯数字的链接例如8899.cc这种，注意不是带http和https的链接
        #姓名
        #这周会到港的提单有哪些
        idea: str = None,
        task_id: str = None,
        investment: float = 6.0,
        n_round: int = 9,

):
    try:
        task_id=task_id
        team = Team()
        #将四个rule注册到环境中
        team.hire(
            [
                Sqltool(task_id),
                Sqlproject(task_id),
                SqlCoder(task_id),
                SqlTester(task_id),
                SqlSummary(task_id)
            ]
        )

        team.invest(investment=investment)
        team.run_project(idea)
        await team.run(n_round=n_round)
    except Exception as e:
        print("运行失败")


async def run_tasks():
    while True:
        sql = """select content,task_id from chat_msg where task_state=1"""
        result = select_data_sql(sql)
        tasks = []
        count = 0
        for res in result:
            if len(result)>0:
                # count=count+1
                # if count>3:
                #     break
                content = res.get('content')
                task_id = res.get('task_id')
                up_sql="""update chat_msg set task_state=3 where task_id='%s'"""%task_id
                try:
                    update_data(up_sql)
                except Exception as e:
                    print(e)
                #key_word = key_word.replace("包含","")
                idea=content
                if len(idea)<6:
                    break
                current_datetime = datetime.now()
                weekday_number = current_datetime.weekday()
                # 格式化日期输出为 "年月日"
                current_datetime = current_datetime.strftime("%Y年%m月%d日")
                weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"]

                # 获取星期的中文表达
                weekday_chinese = weekdays[weekday_number]
                if "年" in idea or "月" in idea or "日" in idea or  "时" in idea or  "周" in idea:
                    idea="今天是"+current_datetime+weekday_chinese+","+idea
                #idea='提取'+key_word+'，并将结果用list返回'
                asyncio.create_task(main(idea, task_id))
                print("执行一条")
            #else:
                #time.sleep(5)
        await asyncio.sleep(0.1)
        #print("一轮结束，等待下一轮关键词到来")


if __name__ == '__main__':
    try:
        asyncio.run(run_tasks())
    except Exception as e:
        print("运行失败"+str(e))