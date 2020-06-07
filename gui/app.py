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

        self.video_source = None
        self.photo = None
        self.play_video = False
        self.analyse_video = False
        self.running_avg = False
        self.already_moving = False
        self.moving_list = [None, None]

        self.__create_frames__()
        self.__fill_display_frame__()
        self.__fill_control_frame__()
        self.__fill_analyse_frame__()

        self.timing_scale_value = 0
        self.delay = 15
        self.update()
        self.analyser = None

        self.window.mainloop()

    def __create_frames__(self):
        # highlightbackorund + highlightthickness only for testing element placing, remove in the future
        self.display_frame = tkinter.Frame(self.window, highlightbackground="black", highlightthickness=1)
        self.display_frame.grid(row=0, column=0)

        self.analyse_frame = tkinter.Frame(self.window, highlightbackground="black", highlightthickness=1)
        self.analyse_frame.grid(row=0, column=1)

        self.control_frame = tkinter.Frame(self.window, highlightbackground="black", highlightthickness=1)
        self.control_frame.grid(row=1, columnspan=2)

    def __fill_display_frame__(self):
        self.canvas = tkinter.Canvas(self.display_frame, width=300, height=300)
        self.canvas.pack()

    def __fill_control_frame__(self):
        self.browse_button = tkinter.Button(self.control_frame, text="Browse video file", command=self.browse)
        self.browse_button.pack(side=tkinter.RIGHT)

        self.play_button = tkinter.Button(self.control_frame, text="Play video", command=self.play)
        self.play_button.pack(side=tkinter.LEFT)

        self.stop_button = tkinter.Button(self.control_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tkinter.LEFT)

        self.timing_scale = tkinter.Scale(self.control_frame, command=self.move, orient=tkinter.HORIZONTAL, length=600,
                                          showvalue=0)
        self.timing_scale.pack(side=tkinter.TOP)

    def __fill_analyse_frame__(self):
        self.fragment_list = ttk.Treeview(self.analyse_frame, columns=["beginning", "end"], show="headings")
        self.fragment_list.pack()

        self.analyse_checked = tkinter.IntVar()
        self.analyse_checkbox = tkinter.Checkbutton(self.analyse_frame, text="Analyse video", command=self.analyse,
                                                    variable=self.analyse_checked)
        self.analyse_checkbox.pack(side=tkinter.BOTTOM)

        self.running_avg_checked = tkinter.IntVar()
        self.running_avg_checkbox = tkinter.Checkbutton(self.analyse_frame, text="Use running average",
                                                        command=self.use_running_avg,
                                                        variable=self.running_avg_checked)
        self.running_avg_checkbox.pack(side=tkinter.BOTTOM)

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
            self.timing_scale = tkinter.Scale(self.control_frame, command=self.move, orient=tkinter.HORIZONTAL,
                                              length=600, showvalue=0, to=self.video_source.get_frames_num())
            self.timing_scale.pack(side=tkinter.TOP)
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
