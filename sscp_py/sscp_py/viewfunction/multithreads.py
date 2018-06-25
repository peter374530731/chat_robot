import threading
import time
import inspect
import ctypes

#停止线程方法
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

#停止线程方法
def stop_thread(thread):
    return_msg = ''
    try:
        _async_raise(thread.ident, SystemExit)
    except Exception as e:
        return_msg = str(e)
    finally:
        return return_msg


#测试使用
class TestThread(threading.Thread):
    def run(self):
        print("begin")
        while True:
            time.sleep(0.1)
            print("end")


if __name__ == "__main__":
    t = TestThread()
    t.start()
    time.sleep(3)
    stop_thread(t)
    print("stoped")