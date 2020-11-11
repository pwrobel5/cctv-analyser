import tkinter
import tkinter.ttk as ttk

from tools.subtractors import BgSubtractorType


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
        self.__fill_running_avg_parameters_frame()
        self.__fill_buttons_frame()
        self.__fill_entries_with_current_parameters()

    def __create_frames(self):
        self._video_size_frame = tkinter.LabelFrame(self, text="Video size settings")
        self._video_size_frame.grid(row=0)

        self._analyse_parameters_frame = tkinter.LabelFrame(self, text="Motion analysis settings")
        self._analyse_parameters_frame.grid(row=1)

        self._running_avg_parameters_frame = tkinter.LabelFrame(self, text="Running average settings")
        self._running_avg_parameters_frame.grid(row=2)

        self._buttons_frame = tkinter.Frame(self)
        self._buttons_frame.grid(row=3)

    def __fill_video_size_frame(self):
        width_label = tkinter.Label(self._video_size_frame, text="Max video width")
        width_label.grid(row=0, column=0)

        width_entry = tkinter.Entry(self._video_size_frame)
        width_entry.grid(row=0, column=1)
        self._entries_values.append((width_entry, "max_video_width"))

        height_label = tkinter.Label(self._video_size_frame, text="Max video height")
        height_label.grid(row=1, column=0)

        height_entry = tkinter.Entry(self._video_size_frame)
        height_entry.grid(row=1, column=1)
        self._entries_values.append((height_entry, "max_video_height"))

    def __fill_analyse_parameters_frame(self):
        first_reference_frame_label = tkinter.Label(self._analyse_parameters_frame, text="First reference frame index")
        first_reference_frame_label.grid(row=0, column=0)

        first_reference_frame_entry = tkinter.Entry(self._analyse_parameters_frame)
        first_reference_frame_entry.grid(row=0, column=1)
        self._entries_values.append((first_reference_frame_entry, "first_reference_frame_index"))

        blur_size_label = tkinter.Label(self._analyse_parameters_frame, text="Gaussian blur size")
        blur_size_label.grid(row=1, column=0)

        blur_size_entry = tkinter.Entry(self._analyse_parameters_frame)
        blur_size_entry.grid(row=1, column=1)
        self._entries_values.append((blur_size_entry, "blur_size"))

        delta_threshold_label = tkinter.Label(self._analyse_parameters_frame, text="Delta threshold")
        delta_threshold_label.grid(row=2, column=0)

        delta_threshold_entry = tkinter.Entry(self._analyse_parameters_frame)
        delta_threshold_entry.grid(row=2, column=1)
        self._entries_values.append((delta_threshold_entry, "delta_threshold"))

        minimal_move_area_label = tkinter.Label(self._analyse_parameters_frame, text="Minimal area to detect move")
        minimal_move_area_label.grid(row=3, column=0)

        minimal_move_area_entry = tkinter.Entry(self._analyse_parameters_frame)
        minimal_move_area_entry.grid(row=3, column=1)
        self._entries_values.append((minimal_move_area_entry, "minimal_move_area"))

        dilation_iterations_label = tkinter.Label(self._analyse_parameters_frame, text="Dilation iterations")
        dilation_iterations_label.grid(row=4, column=0)

        dilation_iterations_entry = tkinter.Entry(self._analyse_parameters_frame)
        dilation_iterations_entry.grid(row=4, column=1)
        self._entries_values.append((dilation_iterations_entry, "dilation_iterations"))

        reference_frame_refresh_frequency_label = tkinter.Label(self._analyse_parameters_frame,
                                                                text="Refresh reference label frequency")
        reference_frame_refresh_frequency_label.grid(row=5, column=0)

        reference_frame_refresh_frequency_entry = tkinter.Entry(self._analyse_parameters_frame)
        reference_frame_refresh_frequency_entry.grid(row=5, column=1)
        self._entries_values.append((reference_frame_refresh_frequency_entry, "reference_frame_refresh_frequency"))

        bg_subtractor_label = tkinter.Label(self._analyse_parameters_frame, text="Background subtractor")
        bg_subtractor_label.grid(row=6, column=0)

        # it is garbage collected, to work properly it needs to be class attribute
        self.bg_subtractor_value_type = tkinter.StringVar()
        bg_subtractor_combobox = ttk.Combobox(self._analyse_parameters_frame,
                                              textvariable=self.bg_subtractor_value_type)
        bg_subtractor_combobox["values"] = [subtractor.name for subtractor in BgSubtractorType]
        bg_subtractor_combobox.grid(row=6, column=1)
        self._entries_values.append((bg_subtractor_combobox, "bg_subtractor"))

    def __fill_running_avg_parameters_frame(self):
        running_avg_alpha_label = tkinter.Label(self._running_avg_parameters_frame, text="Alpha")
        running_avg_alpha_label.grid(row=0, column=0)

        running_avg_alpha_entry = tkinter.Entry(self._running_avg_parameters_frame)
        running_avg_alpha_entry.grid(row=0, column=1)
        self._entries_values.append((running_avg_alpha_entry, "running_avg_alpha"))

        running_avg_start_frame_number_label = tkinter.Label(self._running_avg_parameters_frame,
                                                             text="Number of frames taken at start")
        running_avg_start_frame_number_label.grid(row=1, column=0)

        running_avg_start_frame_number_entry = tkinter.Entry(self._running_avg_parameters_frame)
        running_avg_start_frame_number_entry.grid(row=1, column=1)
        self._entries_values.append((running_avg_start_frame_number_entry, "running_avg_start_frame_number"))

    def __fill_buttons_frame(self):
        self._save_button = tkinter.Button(self._buttons_frame, text="Save", command=self.save_parameters)
        self._save_button.grid(row=0, column=0)

        self._close_button = tkinter.Button(self._buttons_frame, text="Cancel", command=self.cancel)
        self._close_button.grid(row=0, column=1)

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
