import datetime
import time
import tkinter
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import cv2

import PIL.Image
import PIL.ImageTk

from tools.analyse import Analyser
from tools.VideoWriter import VideoWriter
from tools.object_detection.object_detector_graph import ObjectDetectorGraph
from tools.parameters import Parameters
from .parameters_window import ParametersWindow
from .video_capture import VideoCapture


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.path = None
        self.video_source = None
        self.current_frame = None
        self.photo = None
        self.play_video = False
        self.analyse_on_the_fly = False
        self.already_moving = False
        self.moving_list = [None, None]
        self.moving_list_frames = []
        self.motion_index = 0

        self.__set_style()
        self.__create_frames()
        self.__fill_display_frame()
        self.__fill_control_frame()
        self.__fill_analyse_frame()

        self.timing_scale_value = 0
        self.delay = 15
        self.update()
        self.analyser = None
        self.video_writer = None
        self.object_detector = ObjectDetectorGraph()

        self._parameters = Parameters()
        self._parameters.add_callback("_max_video_width", self.__update_canvas_size_without_video)
        self._parameters.add_callback("_max_video_height", self.__update_canvas_size_without_video)
        self._parameters_window = None

        self.window.resizable(False, False)

        self.window.mainloop()

    def __set_style(self):
        self.style = ttk.Style(self.window)
        self.style.layout("text.Horizontal.TProgressbar",
                          [("Horizontal.Progressbar.trough",
                            {"children": [("Horizontal.Progressbar.pbar",
                                           {"side": "left", "sticky": "ns"})],
                             "sticky": "nswe"}),
                           ("Horizontal.Progressbar.label", {"sticky": ""})])
        self.style.configure("text.Horizontal.TProgressbar", text="0 %")

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

        self.progress_bar = ttk.Progressbar(self.control_frame, orient=tkinter.HORIZONTAL,
                                            style="text.Horizontal.TProgressbar",
                                            length=600, mode="determinate")
        self.progress_bar.pack(side=tkinter.BOTTOM)

    def __fill_analyse_frame(self):
        self.fragment_list = ttk.Treeview(self.analyse_frame, columns=["beginning", "end"], show="headings")
        self.fragment_list.heading("beginning", text="beginning")
        self.fragment_list.heading("end", text="end")
        self.fragment_list.pack()

        self.analyse_checked = tkinter.IntVar()
        self.analyse_checkbox = tkinter.Checkbutton(self.analyse_frame, text="Analyse video on the fly",
                                                    command=self.analyse, variable=self.analyse_checked)
        self.analyse_checkbox.pack(side=tkinter.BOTTOM)

        self.set_parameters_button = tkinter.Button(self.analyse_frame, text="Set analysis parameters",
                                                    command=self.open_parameters_button)
        self.set_parameters_button.pack(side=tkinter.BOTTOM)

        self.undo_detection_button = tkinter.Button(self.analyse_frame, text="Undo detection",
                                                    command=self.undo_detection)
        self.undo_detection_button.pack(side=tkinter.BOTTOM)

        self.analyse_video_button = tkinter.Button(self.analyse_frame, text="Analyse video",
                                                   command=self.analyse_video)
        self.analyse_video_button.pack(side=tkinter.BOTTOM)

        self.save_video_button = tkinter.Button(self.analyse_frame, text="Save shortcut video",
                                                   command=self.save_shortcut)
        self.save_video_button.pack(side=tkinter.BOTTOM)

    def browse(self):
        self.path = filedialog.askopenfilename()
        if self.path:
            try:
                self.video_source = VideoCapture(self.path, self._parameters, self.__update_canvas_size_with_video)
            except ValueError:
                return

            self.__update_canvas_size_with_video()
            # self.delay = int(1000 / self.video_source.get_fps())  # 1000 to obtain delay in microseconds
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
        for i in self.moving_list_frames:
            print(i)

    def move(self, val):
        self.video_source.set_frame(int(val))
        self.timing_scale_value = int(val)

    def open_parameters_button(self):
        if self._parameters_window is None:
            self._parameters_window = ParametersWindow(self.window, self._parameters)
        else:
            self._parameters_window.show()

    def undo_detection(self):
        selection_list = self.fragment_list.selection()
        if len(selection_list) == 0:
            return

        for selected_fragment in selection_list:
            del(self.moving_list_frames[self.fragment_list.index(selected_fragment)])
            self.fragment_list.delete(selected_fragment)

    def save_shortcut(self):
        if self.analyser is None:
            return
        if self.video_writer is None:
            print(self.video_source.width)
            self.video_writer = VideoWriter(self.video_source.width, self.video_source.height, self.path)

        for motion in self.moving_list_frames:
            start_motion = motion[0]
            end_motion = motion[1]
            for frame_index in range(start_motion, end_motion + 1):
                print(frame_index)
                #self.video_writer.add_frame(self.video_source.get_frame_by_index(frame_index))
                self.video_writer.add_frame(self.video_source.get_frame_by_index(frame_index)[1])
        self.video_writer.release()

    def analyse(self):
        if self.analyser is None:
            self.__initialize_analyser()

        self.analyse_on_the_fly = bool(self.analyse_checked.get())

    def __initialize_analyser(self):
        self.analyser = Analyser(self._parameters, self.object_detector)
        self.jump_to_video_beginning()

    def analyse_video(self):
        if self.video_source is None:
            return

        if self.analyser is None:
            self.__initialize_analyser()

        ret, frame = self.video_source.get_frame()
        frames_number = self.video_source.get_frames_num()
        self.timing_scale_value = 1

        while ret:
            self.__analyse_frame_update_list(frame)
            ret, frame = self.video_source.get_frame()
            self.timing_scale_value += 1

            if self.timing_scale_value % 10 == 0:
                percent = 100.0 * self.timing_scale_value / frames_number
                self.__set_progress_bar_value(percent)

        if self.moving_list[0] is not None:
            self.moving_list[1] = self.timing_scale_value
            self.mark_fragment(self.moving_list)

        Analyser.destroy_windows()
        #self.video_writer.release()
        self.__set_progress_bar_value(100.0)
        self.jump_to_video_beginning()

        self.moving_list = [None, None]
        self.already_moving = False

    def __set_progress_bar_value(self, value):
        self.progress_bar["value"] = value
        self.style.configure("text.Horizontal.TProgressbar",
                             text="{:g} %".format(int(value)))
        self.window.update_idletasks()

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
                if self.analyse_on_the_fly:
                    frame = self.__analyse_frame_update_list(frame)
                self.current_frame = frame
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
                self.timing_scale_value += 1
                self.timing_scale.set(self.timing_scale_value)
                start_time = datetime.datetime(100, 1, 1, 0, 0, 0)
                self.timing_video.config(text=str((start_time + datetime.timedelta(
                    seconds=int(self.timing_scale_value / self.video_source.get_fps()))).time()))
            self.window.after(self.delay, self.update)

    def __analyse_frame_update_list(self, frame):
        analysed_frame, motion_detected, return_frame_index = self.analyser.analyse_frame(frame)
        if not motion_detected and self.already_moving:
            self.moving_list[1] = return_frame_index / self.video_source.get_fps()
            self.mark_fragment(self.moving_list)
            self.moving_list = [None, None]
            self.already_moving = False
            self.moving_list_frames[self.motion_index][1] = return_frame_index
            self.motion_index += 1
        elif motion_detected and not self.already_moving:
            self.moving_list[0] = return_frame_index / self.video_source.get_fps()
            self.already_moving = True
            self.moving_list_frames.append([return_frame_index, None])

        #if motion_detected:
        #    self.video_writer.write(analysed_frame)

        return analysed_frame

    def mark_fragment(self, moving_list):
        formatted = [time.strftime("%H:%M:%S", time.gmtime(element)) for element in moving_list]
        self.fragment_list.insert("", "end", values=formatted)
