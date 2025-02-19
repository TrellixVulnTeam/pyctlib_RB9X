import sys
import os
import logging as syslogging
from sys import getsizeof

sys.path.append(os.path.abspath("."))
import zytlib
import pathlib
import numpy as np
from zytlib import vector, IndexMapping, scope, vhelp
from zytlib.vector import chain_function
from fuzzywuzzy import fuzz
from zytlib.filemanager import path, get_relative_path, file
from zytlib import touch
from zytlib.wrapper import generate_typehint_wrapper
import argparse
import time
from datetime import timedelta
from time import sleep
from zytlib.utils import totuple
from zytlib.touch import once
from zytlib import Logger
import math
import random
from termcolor import colored

# logger = Logger(False, True)
logger = Logger()

# logger.info("test")
# logger.info(colored('hello', 'red'), colored('world', 'green'))

# logger = Logger(True, False, deltatime=True, notion_page_link="https://www.notion.so/zhangyiteng/fe15b30065114f648a8dd16fc214e702")

for step in range(20):

    logger.variable("train.loss", step ** 0.5)
    logger.variable("val.loss", step ** 0.5)
    logger.variable("loss[train]", step ** 0.5 + random.random())
    logger.variable("loss[val]", step ** 0.5 + 0.5 * random.random())
    logger.variable("train.x", step ** 0.5)
    logger.variable("train.y", step ** 0.5)
    logger.variable("train.z", step ** 0.5)
    logger.variable("train.w[a]", 1 + random.random())
    logger.variable("train.w[b]", 2 + random.random())
    logger.variable("train.w[c]", 3 + random.random())
    logger.variable("train.w[d]", 4 + random.random())
    logger.update_notion("current_epoch", step)

Logger.plot_variable_dict(logger.variable_dict, hline=["bottom"], saved_path="Log/test.pdf")
