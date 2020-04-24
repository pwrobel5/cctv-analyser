import tkinter
import tkinter.filedialog as filedialog

import PIL.Image
import PIL.ImageTk

from .video_capture import VideoCapture


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = None
        self.photo = None
        self.play_video = False

        # Canvas for video display
        self.canvas = tkinter.Canvas(window, width=800, height=680)
        self.canvas.pack()

        self.browse_button = tkinter.Button(window, text="Browse video file", command=self.browse)
        self.browse_button.pack(side=tkinter.RIGHT)

        self.play_button = tkinter.Button(window, text="Play video", command=self.play)
        self.play_button.pack(side=tkinter.LEFT)

        self.stop_button = tkinter.Button(window, text="Stop", command=self.stop)
        self.stop_button.pack(side=tkinter.LEFT)

        self.analyse_button = tkinter.Button(window, text="Analyse video", command=self.analyse)
        self.analyse_button.pack(side=tkinter.RIGHT)

        self.timing_scale_value = 0

        self.timing_scale = tkinter.Scale(window, command=self.move, orient=tkinter.HORIZONTAL, length=600,
                showvalue=0)

        self.delay = 15
        self.update()

        self.window.mainloop()

    def browse(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                self.video_source = VideoCapture(path)
            except ValueError:
                return

            width = self.video_source.width
            height = self.video_source.height
            self.canvas.config(width=width, height=height)

            ret, frame = self.video_source.get_frame()
            if ret:
                self.timing_scale.destroy()
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
                self.timing_scale = tkinter.Scale(self.window, command=self.move, orient=tkinter.HORIZONTAL,
                                                  length=600, showvalue=0, to=self.video_source.get_frames_num())
                self.timing_scale.pack(side=tkinter.BOTTOM)
                self.timing_scale_value = 0

    def play(self):
        self.play_video = True
        self.update()

    def stop(self):
        self.play_video = False

    def move(self, val):
        self.video_source.set_frame(int(val))
        self.timing_scale_value = int(val)
        print(val)


    def analyse(self):
        pass

    def update(self):
        # Get a frame from the video source
        if self.play_video:
            ret, frame = self.video_source.get_frame()

            if ret:
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
                self.timing_scale_value += 1
                self.timing_scale.set(self.timing_scale_value)

            self.window.after(self.delay, self.update)
