import imageio
import sys
import matplotlib.pyplot as plt
import numpy

outputs = imageio.imread(sys.argv[1])
targets = imageio.imread(sys.argv[2])
background_threshold = -0.0
background_threshold = 0.5 * (background_threshold + 1) * 255

outputs_mask = numpy.any(outputs > background_threshold, axis=2)
targets_mask = numpy.any(targets > background_threshold, axis=2)
outputs_masked = outputs.copy()
outputs_masked[numpy.logical_not(outputs_mask)] = 0
targets_masked = targets.copy()
targets_masked[numpy.logical_not(targets_mask)] = 0

tp = numpy.sum(numpy.logical_and(outputs_mask, targets_mask))
fp = numpy.sum(numpy.logical_and(outputs_mask, numpy.logical_not(targets_mask)))
fn = numpy.sum(numpy.logical_and(numpy.logical_not(outputs_mask), targets_mask))
prc = 1.0 * tp / (tp + fp)
rcl = 1.0 * tp / (tp + fn)
print("%.3f/%.3f"%(prc,rcl))

plt.subplot(2,2,1)
plt.imshow(outputs)
plt.subplot(2,2,2)
plt.imshow(targets)
plt.subplot(2,2,3)
plt.imshow(outputs_masked)
plt.subplot(2,2,4)
plt.imshow(targets_masked)
plt.show()
