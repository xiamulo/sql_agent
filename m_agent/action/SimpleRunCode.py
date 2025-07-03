from metagpt.actions import Action
import subprocess
from metagpt.logs import logger
import re
class SimpleRunCode(Action):
    PROMPT_TEMPLATE = """
        运行结果：{result}
        code：{code}
        你是一个精通python的中文nlp工程师你非常严谨，请结合给你的任务以及运行结果检查给你的code为什么实际输出结果是返回为空，请按内容要求修改正确代码返回给用户
        #内容要求
        1.一定不能将正则表达式与jieba同时使用或前后使用只能单独使用一种
        2.可以使用正则表达式或者jieba以及其他nlp的库进行提取，注意一定不能都使用，使用了jieba一定不可以再用正则
        3.不要使用jieba.load_userdict，不要简化代码，一定要完整的实现用户需求
        4.一定要返回list给用户
        返回``python your_code_here``，不带其他文本，
        你的代码：
        """
    def __init__(self, name="SimpleRunCode", context=None, llm=None):
        super().__init__(name, context, llm)

    def run_code(self,code_text):
        try:
            source_code = code_text
            res = source_code.split(r"\b")
            # res = source_code.split("\b")
            if len(res) >= 3:
                source_code = source_code.replace(r"\b", "")
            #source_code = source_code.replace("print(", "#print(")
            content = re.findall(r'text1 = "(.*?)"',source_code)
            if len(content)==0:
                content = re.findall(r"\('(.*?)'\)", source_code)
            if len(content)==0:
                content = re.findall(r'\("(.*?)"\)', source_code)
            if len(content)==0:
                content = re.findall(r"text1 = '(.*?)'",source_code)
            content=content[0]
            exec(source_code)
            def_name = re.findall(r"def (.*?)\(", source_code)[0]
            r = eval(def_name)
            check_result_List = r(content)
            return check_result_List
        except Exception as e:
            return str(e)

    @staticmethod
    def parse_code(rsp):
        pattern = r'```python(.*)```'
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else rsp
        return code_text

    async def run(self, code_text: str):
        result=self.run_code(code_text)
        code_result = result
        if len(code_result)==0:
            prompt = self.PROMPT_TEMPLATE.format(code=code_text,result=code_result)
            print(prompt)
            rsp = await self._aask(prompt)  # 发送请求
            code_text = SimpleRunCode.parse_code(rsp)  # 获得结果
            return code_text
        return code_result