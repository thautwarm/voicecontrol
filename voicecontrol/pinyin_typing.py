import os

from pynput.keyboard import Key, Controller
import psutil

from voicecontrol.st import *

keyboard = Controller()
voice_input_exe = "iFlyVoice.exe"


def get_process(name: str):
    for p in psutil.process_iter():
        if p.name() == name:
            return p


def pressed(k):
    keyboard.press(k)
    keyboard.release(k)


def get_en_US_model_path():
    import speech_recognition as sr
    import os.path as p

    return p.join(p.dirname(sr.__file__), "pocketsphinx-data", "en-US")


class 休息模式(DSModel, CommandsFromMethods):
    path = get_en_US_model_path()
    decider = staticmethod(just_hyp)

    def okay(self, st: StateMachine):
        st.model = 控制模式()


class 输入模式(DSModel, CommandsFromMethods):
    path = get_en_US_model_path()
    decider = staticmethod(just_hyp)

    def okay(self, st: StateMachine):
        p = get_process("iFlyVoice.exe")
        if p:
            p.kill()
        st.model = 控制模式()


class 控制模式(DSModel, CommandsFromMethods):
    path = os.path.join(os.path.dirname(__file__), "models", "control")
    decider = staticmethod(vote_most_common_word)

    def 符(self, st: StateMachine):
        tb = ('，', " 。","“”", "！","？","【】","「」","（）")
        tb = ('，', " 。","“”", "！","？","【】","「」","（）")
        
        i = st.state
        if i <= len(tb):
            for k in tb[i-1]:
                keyboard.press(k)
        st.state = 1
    
    def 五(self, st: StateMachine):
        st.state += 5

    def 四(self, st: StateMachine):
        st.state += 4

    def 三(self, st: StateMachine):
        st.state += 3

    def 二(self, st: StateMachine):
        st.state += 2

    def 一(self, st: StateMachine):
        st.state += 1

    def 上(self, st: StateMachine):
        for _ in range(st.state):
            pressed(Key.up)
        st.state = 1

    def 下(self, st: StateMachine):
        for _ in range(st.state):
            pressed(Key.down)
        st.state = 1

    def 左(self, st: StateMachine):
        for _ in range(st.state):
            pressed(Key.left)
        st.state = 1

    def 右(self, st: StateMachine):
        for _ in range(st.state):
            pressed(Key.right)
        st.state = 1

    def 撤(self, st: StateMachine):
        with keyboard.pressed(Key.ctrl):
            pressed("z")

    def 重(self, st: StateMachine):
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.shift):
                pressed("z")

    def 删除(self, st: StateMachine):
        for _ in range(st.state):
            pressed(Key.backspace)
        st.state = 1

    def 首(self, st: StateMachine):
        with keyboard.pressed(Key.ctrl):
            pressed("a")

    def 末(self, st: StateMachine):
        with keyboard.pressed(Key.ctrl):
            pressed("e")

    def 行(self, st: StateMachine):
        pressed(Key.enter)

    def 休息(self, st: StateMachine):
        st.model = 休息模式()

    def 输入(self, st: StateMachine):
        st.model = 输入模式()
        keyboard.press(Key.f8)


def main():
    from voicecontrol.indicator import create_root

    st = StateMachine(1, 控制模式())
    st.add_event(create_root())
    st.start_loop()
