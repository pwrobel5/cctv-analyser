import tkinter
import tkinter.ttk as ttk

from tools.subtractors import BgSubtractorType


# TODO - make function to create label + entry and avoid repeating it

# wrapper class to have consistency with other elements
# and to not have it as a special case in __fill_entries_with_current_parameters below
class CheckbuttonEntry(tkinter.Checkbutton):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.var = kw["variable"]

    def insert(self, _, value):
        if value:
            self.select()
        else:
            self.deselect()

    def get(self):
        return self.var.get()

    def delete(self, index, end):
        pass


class ParametersWindow(tkinter.Toplevel):
    def __init__(self, parent, parameters):
        self.original_frame = parent
        tkinter.Toplevel.__init__(self)

        self._parameters = parameters
        self.title("Set analysis parameters")
        self._entries_values = []

        self.__create_frames()
        self.__fill_video_size_frame()
        self.__fill_analyse_parameters_frame()
        self.__fill_buttons_frame()
        self.__fill_entries_with_current_parameters()

    def __create_frames(self):
        current_row = 0

        self._video_size_frame = tkinter.LabelFrame(self, text="Video size settings")
        self._video_size_frame.grid(row=current_row)
        current_row += 1

        self._analyse_parameters_frame = tkinter.LabelFrame(self, text="Motion analysis settings")
        self._analyse_parameters_frame.grid(row=current_row)
        current_row += 1

        self._running_avg_parameters_frame = tkinter.LabelFrame(self, text="Running average settings")
        self._running_avg_parameters_frame.grid(row=current_row)
        current_row += 1

        self._buttons_frame = tkinter.Frame(self)
        self._buttons_frame.grid(row=current_row)

    def __fill_video_size_frame(self):
        current_row = 0

        width_label = tkinter.Label(self._video_size_frame, text="Max video width")
        width_label.grid(row=current_row, column=0)

        width_entry = tkinter.Entry(self._video_size_frame)
        width_entry.grid(row=current_row, column=1)
        self._entries_values.append((width_entry, "max_video_width"))
        current_row += 1

        height_label = tkinter.Label(self._video_size_frame, text="Max video height")
        height_label.grid(row=current_row, column=0)

        height_entry = tkinter.Entry(self._video_size_frame)
        height_entry.grid(row=current_row, column=1)
        self._entries_values.append((height_entry, "max_video_height"))

    def __fill_analyse_parameters_frame(self):
        current_row = 0

        blur_size_label = tkinter.Label(self._analyse_parameters_frame, text="Gaussian blur size")
        blur_size_label.grid(row=current_row, column=0)

        blur_size_entry = tkinter.Entry(self._analyse_parameters_frame)
        blur_size_entry.grid(row=current_row, column=1)
        self._entries_values.append((blur_size_entry, "blur_size"))
        current_row += 1

        delta_threshold_label = tkinter.Label(self._analyse_parameters_frame, text="Delta threshold")
        delta_threshold_label.grid(row=current_row, column=0)

        delta_threshold_entry = tkinter.Entry(self._analyse_parameters_frame)
        delta_threshold_entry.grid(row=current_row, column=1)
        self._entries_values.append((delta_threshold_entry, "delta_threshold"))
        current_row += 1

        dilation_iterations_label = tkinter.Label(self._analyse_parameters_frame, text="Dilation iterations")
        dilation_iterations_label.grid(row=current_row, column=0)

        dilation_iterations_entry = tkinter.Entry(self._analyse_parameters_frame)
        dilation_iterations_entry.grid(row=current_row, column=1)
        self._entries_values.append((dilation_iterations_entry, "dilation_iterations"))
        current_row += 1

        minimal_move_area_label = tkinter.Label(self._analyse_parameters_frame, text="Minimal area to detect move")
        minimal_move_area_label.grid(row=current_row, column=0)

        minimal_move_area_entry = tkinter.Entry(self._analyse_parameters_frame)
        minimal_move_area_entry.grid(row=current_row, column=1)
        self._entries_values.append((minimal_move_area_entry, "minimal_move_area"))
        current_row += 1

        bg_subtractor_label = tkinter.Label(self._analyse_parameters_frame, text="Background subtractor")
        bg_subtractor_label.grid(row=current_row, column=0)

        # it is garbage collected, to work properly it needs to be class attribute
        self.bg_subtractor_value_type = tkinter.StringVar()
        bg_subtractor_combobox = ttk.Combobox(self._analyse_parameters_frame,
                                              textvariable=self.bg_subtractor_value_type)
        bg_subtractor_combobox["values"] = [subtractor.name for subtractor in BgSubtractorType]
        bg_subtractor_combobox.grid(row=current_row, column=1)
        self._entries_values.append((bg_subtractor_combobox, "bg_subtractor"))
        current_row += 1

        self.begin_with_sigmadelta_value_type = tkinter.BooleanVar()
        begin_with_sigmadelta_checkbutton = CheckbuttonEntry(self._analyse_parameters_frame,
                                                             text="Use SigmaDelta at the beginning",
                                                             variable=self.begin_with_sigmadelta_value_type)
        begin_with_sigmadelta_checkbutton.grid(row=current_row, columnspan=2)
        self._entries_values.append((begin_with_sigmadelta_checkbutton, "begin_with_sigmadelta"))
        current_row += 1

        sigmadelta_frames_label = tkinter.Label(self._analyse_parameters_frame, text="SigmaDelta frames")
        sigmadelta_frames_label.grid(row=current_row, column=0)

        sigmadelta_frames_entry = tkinter.Entry(self._analyse_parameters_frame)
        sigmadelta_frames_entry.grid(row=current_row, column=1)
        self._entries_values.append((sigmadelta_frames_entry, "sigmadelta_frames"))
        current_row += 1

        self.use_threshold_value_type = tkinter.BooleanVar()
        use_threshold_checkbutton = CheckbuttonEntry(self._analyse_parameters_frame,
                                                     text="Use thresholding",
                                                     variable=self.use_threshold_value_type)
        use_threshold_checkbutton.grid(row=current_row, columnspan=2)
        self._entries_values.append((use_threshold_checkbutton, "use_threshold"))
        current_row += 1

        max_contours_label = tkinter.Label(self._analyse_parameters_frame, text="Max contours")
        max_contours_label.grid(row=current_row, column=0)

        max_contours_entry = tkinter.Entry(self._analyse_parameters_frame)
        max_contours_entry.grid(row=current_row, column=1)
        self._entries_values.append((max_contours_entry, "max_contours"))
        current_row += 1

        minimal_move_frames_label = tkinter.Label(self._analyse_parameters_frame, text="Minimal frames number")
        minimal_move_frames_label.grid(row=current_row, column=0)

        minimal_move_frames_entry = tkinter.Entry(self._analyse_parameters_frame)
        minimal_move_frames_entry.grid(row=current_row, column=1)
        self._entries_values.append((minimal_move_frames_entry, "minimal_move_frames"))
        current_row += 1

        max_break_length_label = tkinter.Label(self._analyse_parameters_frame, text="Max break length")
        max_break_length_label.grid(row=current_row, column=0)

        max_break_length_entry = tkinter.Entry(self._analyse_parameters_frame, text="Max break length")
        max_break_length_entry.grid(row=current_row, column=1)
        self._entries_values.append((max_break_length_entry, "max_break_length"))

    def __fill_buttons_frame(self):
        current_row = 0

        self._save_button = tkinter.Button(self._buttons_frame, text="Save", command=self.save_parameters)
        self._save_button.grid(row=current_row, column=0)

        self._close_button = tkinter.Button(self._buttons_frame, text="Cancel", command=self.cancel)
        self._close_button.grid(row=current_row, column=1)

    def __fill_entries_with_current_parameters(self):
        for entry, attribute in self._entries_values:
            entry.delete(0, "end")
            entry.insert(0, getattr(self._parameters, attribute))

    def show(self):
        self.__fill_entries_with_current_parameters()
        self.deiconify()

    def save_parameters(self):
        for entry, attribute in self._entries_values:
            attribute_type = type(getattr(self._parameters, attribute))
            value = attribute_type(entry.get())
            setattr(self._parameters, attribute, value)

        self.withdraw()

    def cancel(self):
        self.withdraw()
