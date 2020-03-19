import sys
from tfrecord_lite import tf_record_iterator
import numpy

it = tf_record_iterator(sys.argv[1])
n = next(it)

for k in n:
	A = numpy.array(n[k])
#	print(A)
	print(k,type(n[k]),A.shape, A.dtype, A if 'dim' in k else '')
