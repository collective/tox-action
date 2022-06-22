# Very simple test to use in our example workflow.
import os
import sys


print(os.uname())
print(sys.version)
assert 6 * 7 == 42
