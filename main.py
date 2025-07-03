import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
import uuid
from util.sqlutil import insert_data,select_data_zb,update_data_zb
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)
class chat_Item(BaseModel):
    content: str = Field(..., description="用户需求")
    task_id:str= Field(None, description="用来获取最后结果的task_id")

class Task_Item(BaseModel):
    task_id: str = Field(..., description="任务id用于轮询检查是否添加完泛化关键词")

def get_mac():
    mac_num = uuid.getnode()
    mac = ':'.join(('%012X' % mac_num)[i:i + 2] for i in range(0, 12, 2))
    return mac_num


@app.post("/check_task")
async def check_task(item: Task_Item):
    """
    这个功能还没做
    无正确返回
    :param item:
    :return:
    """
    try:
        task_id = item.task_id
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sqls = """select * from agent_task_log where task_id='%s' and source='sql_result' and push_state=0 """ % task_id
        result = select_data_zb(sqls)
        if len(result)>=1:
            msg=result[0].get("content")
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {"msg": msg, "task_id": task_id, "end_time": end_time,"code":41006}
            up_sql="""update  agent_task_log set  push_state=1 where task_id='%s' and source='sql_result' """%task_id
            update_data_zb(up_sql)
            return JSONResponse(content=data, status_code=200)
        else:
            sqls = """select * from agent_task_log where task_id='%s' and source='SqlSummation' """ % task_id
            result = select_data_zb(sqls)
            if len(result)>=1:
                msg=result[0].get("content")
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {"msg": msg, "task_id": task_id, "end_time": end_time,"code":41003}
            else:
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {"msg": "任务进行中请稍后...", "task_id": task_id, "end_time": end_time,"code":41002}
    except Exception as e:
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {"msg": "查询任务状态失败，请联系管理员", "task_id": "", "end_time": end_time,"code":41004}
    return JSONResponse(content=data, status_code=200)


@app.post("/chat_msg")
async def chat_msg(item: chat_Item):
    try:
        content=item.content
        task_id = item.task_id
        if "删除" in content or "清空"  in content or "格式化"  in content or "消除" in content or "gpt" in content:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {"msg": "敏感操作，请联系管理员", "task_id": "", "end_time": end_time, "code": 41004}
            return JSONResponse(content=data, status_code=200)

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("添加到数据库")
        sql = """INSERT INTO chat_msg (content, task_id, task_state)  VALUES (%s, %s, %s);"""
        insert_data(sql, content, task_id, 1)
        data = {"msg": "发送成功请稍等...", "task_id": task_id, "end_time": end_time, "code": 41003}
    except Exception as e:
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data={"msg":"添加失败，请联系管理员","task_id":"","end_time":end_time,"code":41004}
    return JSONResponse(content=data, status_code=200)





@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == '__main__':
    uvicorn.run(app=app,host="0.0.0.0",port=8006)