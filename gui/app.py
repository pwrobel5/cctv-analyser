import tkinter
import tkinter.filedialog as filedialog


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = None

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

        self.window.mainloop()

    def browse(self):
        path = filedialog.askopenfilename()
        if path:
            self.video_source = path

    def play(self):
        pass

    def stop(self):
        pass

    def analyse(self):
        pass
