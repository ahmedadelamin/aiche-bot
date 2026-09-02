import logging
import sys
import traceback
logging.basicConfig(filename='C:\\Users\\ahmed\\Downloads\\bot_deploy\\test.log', level=logging.DEBUG)
try:
    with open('/home/AmirEhab/users.json', 'w') as f:
        pass
except Exception as e:
    logging.error("Failed", exc_info=True)
