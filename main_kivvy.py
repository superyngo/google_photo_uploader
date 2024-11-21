from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from app.utils.logger import logger

class MyKivyApp(App):
    def build(self):
        # Log an info message when the app starts
        logger.info("Kivy application started")

        # Create a simple UI with a label and a button
        layout = BoxLayout(orientation='vertical')
        label = Label(text="Hello, Kivy!")
        button = Button(text="Click Me")

        # Log a message when the button is clicked
        button.bind(on_press=self.on_button_click)

        layout.add_widget(label)
        layout.add_widget(button)
        return layout

    def on_button_click(self, instance):
        logger.info("Button was clicked!")

if __name__ == '__main__':
    MyKivyApp().run()