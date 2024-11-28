# main.py

from kivy.app import App
from app import MainLayout  # Import MainLayout from the app package

class MideoToGPhotoApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    MideoToGPhotoApp().run()

