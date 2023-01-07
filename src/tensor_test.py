from time import sleep
import torch
import torch.multiprocessing as mp

def run_thread_1(conn):
    # 在线程 1 中创建一个 tensor，并将其转移到默认的 GPU 上
    while True:
        # tensor = torch.rand(3, 3).cuda()
        tensor = torch.tensor([[1.3237, 0.7694, 0.2065],
                                [0.8730, 0.5003, 0.8849],
                                [0.4554, 1.8231, 0.0397]]).cuda()
        # tensor = torch.ones
        # 使用 Pipe 将 tensor 发送到线程 2
        conn.send(tensor)
        sleep(0.5)


def run_thread_2(conn):

    while True:
        sleep(0.5)
        # 使用 Pipe 接收来自线程 1 的 tensor
        tensor = conn.recv()

        # # 将 tensor 转移到线程 2 的默认 GPU 上
        # tensor = tensor.cuda()

        # 在线程 2 中使用 tensor
        result = tensor * 2
        print(result)

if __name__ == '__main__':
    # 创建一个 Pipe，其中一端连接到线程 1，另一端连接到线程 2
    # torch.multiprocessing.set_start_method("spawn")
    parent_conn, child_conn = mp.Pipe()

    # 创建线程 1 并将 Pipe 的一端作为参数传递
    t1 = mp.Process(target=run_thread_1, args=(parent_conn,))
    t1.start()
    # sleep(1)
    # 创建线程 2 并将 Pipe 的另一端作为参数传递
    t2 = mp.Process(target=run_thread_2, args=(child_conn,))
    t2.start()

    t1.join()
    t2.join()
