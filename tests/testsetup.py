# There might be a better solution for this, but I need this to be
# configured with all tests, and importing this module in all of them
# will do it.

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../pystr')
