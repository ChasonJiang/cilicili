# from player.utils.DisplayDevice import *
import cProfile
import os 
if __name__ == "__main__":
    # cProfile.run("main()")
    # import pycuda.driver as drv
    # drv.init()
    # dev = drv.Device(0)
    # print('Trying to create context....')
    # ctx = dev.make_context()
    # print(f'Context created on device: {dev.name()}')
    # ctx.pop()
    # del ctx
    # print('Context removed.\nEnd of test')
    # import pycuda.driver as cuda
    # import pycuda.gl as cudagl
    # import atexit

    # cuda.init()
    # assert cuda.Device.count() >= 1
    # dev = cuda.Device(0)
    # ctx = dev.make_context()
    # device = ctx.get_device()

    # atexit.register(ctx.pop)
    print(os.environ["PATH"])
