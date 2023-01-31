import pycuda.driver as cuda
import pycuda.gl as cudagl
import atexit

cuda.init()
assert cuda.Device.count() >= 1
dev = cuda.Device(0)
ctx = dev.make_context()
device = ctx.get_device()

atexit.register(ctx.pop)
