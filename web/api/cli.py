import sys
from domain_list import result_list

args = sys.argv[1]
# style = sys.argv[2] - json or other style out

results = result_list(args)
print(results)