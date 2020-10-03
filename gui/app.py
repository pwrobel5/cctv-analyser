import tkinter
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk

import datetime

from tools.analyse import Analyser
from tools.parameters import Parameters
from .parameters_window import ParametersWindow
from .video_capture import VideoCapture


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = None
        self.current_frame = None
        self.photo = None
        self.play_video = False
        self.analyse_video = False
        self.already_moving = False
        self.moving_list = [None, None]

        self.__create_frames()
        self.__fill_display_frame()
        self.__fill_control_frame()
        self.__fill_analyse_frame()

        self.timing_scale_value = 0
        self.delay = 15
        self.update()
        self.analyser = None

        self._parameters = Parameters()
        self._parameters.add_callback("_max_video_width", self.__update_canvas_size_without_video)
        self._parameters.add_callback("_max_video_height", self.__update_canvas_size_without_video)
        self._parameters_window = None

        self.window.resizable(False, False)

        self.window.mainloop()

    def __create_frames(self):
        # TODO - highlightbackorund + highlightthickness only for testing element placing, remove in the future
        self.display_frame = tkinter.Frame(self.window, highlightbackground="black", highlightthickness=1)
        self.display_frame.grid(row=0, column=0)

        self.analyse_frame = tkinter.Frame(self.window, highlightbackground="black", highlightthickness=1)
        self.analyse_frame.grid(row=0, column=1)

        self.control_frame = tkinter.Frame(self.window, highlightbackground="black", highlightthickness=1)
        self.control_frame.grid(row=1, columnspan=2)

    def __fill_display_frame(self):
        self.canvas = tkinter.Canvas(self.display_frame, width=300, height=300)
        self.canvas.pack()

    def __fill_control_frame(self):
        self.browse_button = tkinter.Button(self.control_frame, text="Browse video file", command=self.browse)
        self.browse_button.pack(side=tkinter.RIGHT)

        self.timing_video = tkinter.Label(self.control_frame, text="00:00:00", width=7)
        self.timing_video.pack(side=tkinter.RIGHT)

        self.play_button = tkinter.Button(self.control_frame, text="Play video", command=self.play)
        self.play_button.pack(side=tkinter.LEFT)

        self.stop_button = tkinter.Button(self.control_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tkinter.LEFT)

        self.timing_scale = tkinter.Scale(self.control_frame, command=self.move, orient=tkinter.HORIZONTAL, length=600,
                                          showvalue=0)
        self.timing_scale.pack(side=tkinter.TOP)

    def __fill_analyse_frame(self):
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

        self.set_parameters_button = tkinter.Button(self.analyse_frame, text="Set analysis parameters",
                                                    command=self.open_parameters_button)
        self.set_parameters_button.pack(side=tkinter.BOTTOM)

    def browse(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                self.video_source = VideoCapture(path, self._parameters, self.__update_canvas_size_with_video)
            except ValueError:
                return

            self.__update_canvas_size_with_video()
            self.delay = int(1000 / self.video_source.get_fps())  # 1000 to obtain delay in microseconds
            self.jump_to_video_beginning()

    def __update_canvas_size(self, width, height):
        self.canvas.config(width=width, height=height)

    def __update_canvas_size_without_video(self):
        width = self._parameters.max_video_width
        height = self._parameters.max_video_height
        self.__update_canvas_size(width, height)

    def __update_canvas_size_with_video(self):
        if self.video_source is not None:
            width = self.video_source.width
            height = self.video_source.height
            self.__update_canvas_size(width, height)

            if not self.play_video:
                self.__resize_photo(width, height)

    def __resize_photo(self, width, height):
        if self.current_frame is not None:
            image = PIL.Image.fromarray(self.current_frame)
            image = image.resize((int(width), int(height)), PIL.Image.ANTIALIAS)
            self.photo = PIL.ImageTk.PhotoImage(image=image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

    def play(self):
        if not self.play_video:
            self.play_video = True
            self.update()

    def stop(self):
        self.play_video = False

    def move(self, val):
        self.video_source.set_frame(int(val))
        self.timing_scale_value = int(val)

    def open_parameters_button(self):
        if self._parameters_window is None:
            self._parameters_window = ParametersWindow(self.window, self._parameters)
        else:
            self._parameters_window.show()

    def analyse(self):
        if self.analyser is None:
            ret, reference_frame = self.video_source.get_frame_by_index(self._parameters.first_reference_frame_index)
            if not ret:
                print("Error with loading reference frame")

            if self._parameters.use_running_average:
                running_average_initial_frames = self.__read_initial_average_frames()
                self.analyser = Analyser(reference_frame, self._parameters, running_average_initial_frames)
            else:
                self.analyser = Analyser(reference_frame, self._parameters)

        self.analyse_video = bool(self.analyse_checked.get())

    def __read_initial_average_frames(self):
        result = []
        factor = self.video_source.get_frames_num() / self._parameters.running_avg_start_frame_number
        frame_index = 0

        for _ in range(0, self._parameters.running_avg_start_frame_number):
            _, frame = self.video_source.get_frame_by_index(frame_index)
            result.append(frame)
            frame_index = int(frame_index + factor)

        return result

    def jump_to_video_beginning(self):
        self.video_source.set_frame(0)

        ret, frame = self.video_source.get_frame()
        if ret:
            self.timing_scale.destroy()
            self.current_frame = frame
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            self.timing_scale = tkinter.Scale(self.control_frame, command=self.move, orient=tkinter.HORIZONTAL,
                                              length=600, showvalue=0, to=self.video_source.get_frames_num())
            self.timing_scale.pack(side=tkinter.TOP)
            self.timing_scale_value = 0

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
                self.current_frame = frame
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
                self.timing_scale_value += 1
                self.timing_scale.set(self.timing_scale_value)
                start_time = datetime.datetime(100, 1, 1, 0, 0, 0)
                self.timing_video.config(text=str((start_time + datetime.timedelta(seconds=int(self.timing_scale_value /
                                                                                               self.video_source.get_fps()))).time()))
            self.window.after(self.delay, self.update)

    def use_running_avg(self):
        self._parameters.use_running_average = bool(self.running_avg_checked.get())
