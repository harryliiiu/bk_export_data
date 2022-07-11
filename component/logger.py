import logging
from config import config

logging.basicConfig(filename=config.get("LOG_PATH_NAME"),
                    level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d  %H:%M:%S %a'  # 注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    )
logger = logging.getLogger()
ch = logging.StreamHandler()
# logger.addHandler(ch)