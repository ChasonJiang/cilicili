
from queue import Queue
import time,threading
q=Queue(maxsize=10)
 
def product(name):
    count=1
    while True:
        q.put('气球兵{}'.format(count))
        print ('{}训练气球兵{}只'.format(name,count))
        count+=1
        # time.sleep(1)
def consume(name):
    while True:
        print ('{}使用了{}'.format(name,q.get()))
        time.sleep(0.5)
        q.task_done()

if __name__ == '__main__':
    t1=threading.Thread(target=product,args=('wpp',))
    t2=threading.Thread(target=consume,args=('ypp',))
    t3=threading.Thread(target=consume,args=('others',))
    
    t1.start()
    t2.start()
    t3.start()
