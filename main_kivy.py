import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

# Import core logic
# We need to make sure the path is correct for imports if running from a different dir,
# but since this is in the root, it should be fine.
from core.controller import Controller
from core.exceptions import DownloadException, InvalidURLException

class DownloadLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        # Title
        self.add_widget(Label(text='Ctrl+S Tube Downloader', font_size='24sp', size_hint_y=None, height=50))

        # URL Input
        self.url_input = TextInput(hint_text='Paste YouTube URL here', multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.url_input)

        # Download Button
        self.download_btn = Button(text='Download', size_hint_y=None, height=50)
        self.download_btn.bind(on_press=self.start_download)
        self.add_widget(self.download_btn)

        # Progress Bar
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        self.add_widget(self.progress_bar)

        # Status Label
        self.status_label = Label(text='Ready', size_hint_y=None, height=40)
        self.add_widget(self.status_label)

        # Controller
        self.controller = Controller()

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Please enter a URL"
            return

        self.download_btn.disabled = True
        self.status_label.text = "Starting download..."
        self.progress_bar.value = 0

        # Run in a separate thread to not freeze UI
        threading.Thread(target=self.download_thread, args=(url,), daemon=True).start()

    def download_thread(self, url):
        try:
            # Determine output path
            if platform == 'android':
                from android.storage import primary_external_storage_path
                download_dir = os.path.join(primary_external_storage_path(), 'Download', 'CtrlSTube')
            else:
                download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'CtrlSTube')
            
            os.makedirs(download_dir, exist_ok=True)

            def progress_callback(percent, status_msg):
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self.update_progress(percent, status_msg))

            self.controller.download(
                url=url,
                output_path=download_dir,
                quality="720p", # Default for mobile
                format="mp4",   # Default for mobile
                progress_callback=progress_callback
            )
            
            Clock.schedule_once(lambda dt: self.download_complete(True))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_complete(False, str(e)))

    def update_progress(self, percent, status_msg):
        self.progress_bar.value = percent
        self.status_label.text = status_msg

    def download_complete(self, success, error_msg=None):
        self.download_btn.disabled = False
        if success:
            self.status_label.text = "Download Complete!"
            self.progress_bar.value = 100
            self.url_input.text = ""
        else:
            self.status_label.text = f"Error: {error_msg}"
            self.progress_bar.value = 0

class CtrlSTubeApp(App):
    def build(self):
        return DownloadLayout()

if __name__ == '__main__':
    CtrlSTubeApp().run()
