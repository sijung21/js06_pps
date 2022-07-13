import TEST_LOG
from datetime import datetime

print(datetime.now())
now = datetime.now()
date = now.strftime('%Y%m%d')
print(date)
print(type(date))

logger = TEST_LOG.CreateLogger("infinite")
logger.debug("infinite")

logger = TEST_LOG.CreateLogger("MyLogger")
logger.debug("infinite")