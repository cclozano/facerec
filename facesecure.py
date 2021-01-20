# coding:utf-8
import time
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import cv2
from recognition import Recognition
from enrollment import Enrollment


class MainScreen(Screen):
    camera = ObjectProperty(None)

    def on_enter(self):
        self.camera.start()

    def on_leave(self):
        self.camera.stop()


class LoginScreen(Screen):

    def do_login(self, user_pin):
        if user_pin == '0000':
            self.manager.current = 'settings'


class AccessGrantedScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class EnrollScreen(Screen):
    camera = ObjectProperty(None)

    def on_enter(self):
        self.camera.start()

    def on_leave(self):
        self.camera.stop()

    def do_enroll(self, user_name):
        self.camera.enroll(user_name)


class EnrollmentCamera(Image):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enrollment = Enrollment()
        self.capture = None

    def start(self):
        if not self.capture:
            self.capture = cv2.VideoCapture(0)

        fps = 30
        self.update_event = Clock.schedule_interval(self.update, 1.0 / fps)
        # self.recognized_person = None
        # self.c = 0

    def stop(self):
        if self.capture:
            self.capture.release()
            self.capture = None
            Clock.unschedule(self.update_event)

    def enroll(self, user_name):
        self.enrollment.do(user_name)

    def update(self, dt):
        ret, frame = self.capture.read()

        if ret:

            self.enrollment.rval = ret
            self.enrollment.img = frame

            if self.enrollment.is_working():
                buf1 = self.enrollment.frame

            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            # buf1, person = self.recognition.do(ret, frame)

            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture


class RecognitionCamera(Image):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recognition = None
        self.capture = None

    def start(self):
        self.recognition = Recognition()
        fps = 30
        if not self.capture:
            self.capture = cv2.VideoCapture(0)

        self.update_event = Clock.schedule_interval(self.update, 1.0 / fps)
        self.recognized_person = None
        self.c = 0

    def stop(self):
        if self.capture:
            self.capture.release()
            self.capture = None
            Clock.unschedule(self.update_event)

    def update(self, dt):
        if not self.capture:
            return

        ret, frame = self.capture.read()

        if ret:
            # convert it to texture
            # buf1 = cv2.flip(frame, 0)
            buf1, person = self.recognition.do(ret, frame)

            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

            # Grant access afer 30 retries
            if person and person == self.recognized_person:
                self.c += 1
                if self.c == 30:
                    self.parent.parent.manager.current = 'access_granted'
            else:
                self.c = 0

            print(self.c)

            self.recognized_person = person


class FaceSecureApp(App):
    camera = ObjectProperty(None)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AccessGrantedScreen(name='access_granted'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(EnrollScreen(name='enroll'))
        return sm

    def on_stop(self):
        # without this, app will not exit even if the window is closed
        if self.camera:
            self.camera.capture.release()


if __name__ == '__main__':
    FaceSecureApp().run()
