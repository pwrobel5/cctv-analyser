import tkinter
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk

from tools.analyse import Analyser
from .video_capture import VideoCapture


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("775x400")

        self.video_source = None
        self.photo = None
        self.play_video = False
        self.analyse_video = False
        self.running_avg = False
        self.already_moving = False
        self.moving_list = [None, None]

        # Canvas for video display
        self.canvas = tkinter.Canvas(window, width=300, height=300)
        self.canvas.place(x=0, y=0)

        self.fragment_list = ttk.Treeview(columns=["beginning", "end"], show="headings")
        self.fragment_list.place(x=350, y=0)

        self.browse_button = tkinter.Button(window, text="Browse video file", command=self.browse)
        self.browse_button.place(x=350, y=350)

        self.play_button = tkinter.Button(window, text="Play video", command=self.play)
        self.play_button.place(x=0, y=350)

        self.stop_button = tkinter.Button(window, text="Stop", command=self.stop)
        self.stop_button.place(x=100, y=350)

        self.analyse_checked = tkinter.IntVar()
        self.analyse_checkbox = tkinter.Checkbutton(window, text="Analyse video", command=self.analyse,
                                                    variable=self.analyse_checked)
        self.analyse_checkbox.place(x=350, y=300)

        self.running_avg_checked = tkinter.IntVar()
        self.running_avg_checkbox = tkinter.Checkbutton(window, text="Use running average", command=self.use_running_avg,
                                                        variable=self.running_avg_checked)
        self.running_avg_checkbox.place(x=500, y=300)

        self.timing_scale_value = 0

        self.timing_scale = tkinter.Scale(window, command=self.move, orient=tkinter.HORIZONTAL, length=600,
                                          showvalue=0)

        self.delay = 15
        self.update()
        self.analyser = None

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
            self.delay = int(1000 / self.video_source.get_fps())  # 1000 to obtain delay in microseconds
            self.jump_to_video_beginning()

    def play(self):
        self.play_video = True
        self.update()

    def stop(self):
        self.play_video = False

    def move(self, val):
        self.video_source.set_frame(int(val))
        self.timing_scale_value = int(val)

    def analyse(self):
        """
        to parametrize:
          first reference frame - maybe user could set which is correct?
          size of Gaussian smoothing
          eventual resizing - would make the process faster
          do we really need to convert image to grayscale?
          delta threshold - how much different from black must be area to consider it as a movement
          minimum area to detect motion
        """
        if self.analyser is None:
            reference_frame = self.jump_to_video_beginning()
            self.analyser = Analyser(reference_frame, use_running_average=self.running_avg)

        self.analyse_video = bool(self.analyse_checked.get())

    def jump_to_video_beginning(self):
        self.video_source.set_frame(0)

        ret, frame = self.video_source.get_frame()
        if ret:
            self.timing_scale.destroy()
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            self.timing_scale = tkinter.Scale(self.window, command=self.move, orient=tkinter.HORIZONTAL,
                                              length=600, showvalue=0, to=self.video_source.get_frames_num())
            self.timing_scale.place(x=0, y=325)
            self.timing_scale_value = 0
        return frame

    def update(self):
        # Get a frame from the video source
        if self.play_video:
            ret, frame = self.video_source.get_frame()

            if ret:
                if self.analyse_video:
                    frame, motion_detected = self.analyser.analyse_frame(frame)
                    if not motion_detected and self.already_moving:
                        self.moving_list[1] = self.timing_scale_value / self.video_source.get_fps()
                        self.fragment_list.insert('', 'end', values=self.moving_list)
                        self.moving_list = [None, None]
                        self.already_moving = False
                    elif motion_detected and not self.already_moving:
                        self.moving_list[0] = self.timing_scale_value / self.video_source.get_fps()
                        self.already_moving = True
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
                self.timing_scale_value += 1
                self.timing_scale.set(self.timing_scale_value)

            self.window.after(self.delay, self.update)

    def use_running_avg(self):
        self.running_avg = bool(self.running_avg_checked.get())
