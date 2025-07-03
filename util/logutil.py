from loguru import logger
import os
import sys

def save_log(dirs,fileName):
    err_log_file_path = os.path.join(dirs, 'Log/%s/%serror_{time}.log' %(fileName,fileName))
    logger.add(sys.stderr, format="{time} {level} {message}",
               filter="my_module", level="INFO",enqueue=True)
    logger.add(err_log_file_path, rotation="10 MB", encoding='utf-8',
               level='ERROR', enqueue=True)
