import argparse
import signal
import time

from gui.video_capture import VideoCapture
from tools.analyse import Analyser
from tools.object_detection.object_detector_graph import ObjectDetectorGraph
from tools.parameters import Parameters

running_analysis = True


def read_parameters_from_file(file_name, parameters):
    input_file = open(file_name, "r")

    parameters_values = []
    for line in input_file:
        splitted = line.split()
        parameters_values.append((splitted[0], splitted[1]))

    input_file.close()

    for parameter_name, value in parameters_values:
        attribute_type = type(getattr(parameters, parameter_name))
        value = attribute_type(value)
        setattr(parameters, parameter_name, value)


def write_parameters_to_file(file_name, parameters):
    output_file = open(file_name, "w")

    output_file.write("max_video_width {}\n".format(parameters.max_video_width))
    output_file.write("max_video_height {}\n".format(parameters.max_video_height))

    output_file.write("blur_size {}\n".format(parameters.blur_size))
    output_file.write("minimal_move_area {}\n".format(parameters.minimal_move_area))
    output_file.write("bg_subtractor {}\n".format(parameters.bg_subtractor))

    output_file.write("begin_with_sigmadelta {}\n".format(parameters.begin_with_sigmadelta))
    output_file.write("sigmadelta_frames {}\n".format(parameters.sigmadelta_frames))

    output_file.write("use_threshold {}\n".format(parameters.use_threshold))
    output_file.write("delta_threshold {}\n".format(parameters.delta_threshold))
    output_file.write("dilation_iterations {}\n".format(parameters.dilation_iterations))

    output_file.write("max_contours {}\n".format(parameters.max_contours))
    output_file.write("minimal_move_frames {}\n".format(parameters.minimal_move_frames))
    output_file.write("max_break_length {}\n".format(parameters.max_break_length))

    output_file.write("object_detection_interval {}\n".format(parameters.object_detection_interval))

    output_file.close()


def initialize_video_capture(input_name, parameters):
    try:
        video_capture = VideoCapture(input_name, parameters)
        return video_capture
    except ValueError as e:
        print(e)
        exit(1)
    except TypeError:
        print("Incorrect device index")
        exit(1)


def format_time(moment):
    return time.strftime("%H:%M:%S", time.gmtime(moment))


def sigint_handler(signum, frame):
    global running_analysis
    running_analysis = False


def main():
    argparser = argparse.ArgumentParser(description="Console version of CCTV analyser")
    argparser.add_argument("input_video", nargs="?", type=str, help="Path to video file or video device index")
    argparser.add_argument("-dev", action="store_true", help="Given input is device index")
    argparser.add_argument("-param", type=str, help="External file with analysis parameters")

    args = argparser.parse_args()
    input_name = args.input_video
    use_device = args.dev
    parameter_file = args.param

    if use_device:
        input_name = int(input_name)

    parameters = Parameters()
    video_capture = initialize_video_capture(input_name, parameters)

    if parameter_file:
        read_parameters_from_file(parameter_file, parameters)
    else:
        write_parameters_to_file("config.txt", parameters)

    object_detector = ObjectDetectorGraph()
    analyser = Analyser(parameters, object_detector, show_preview=False)
    already_moving = False

    print("Beginning analysis...")

    frame_counter = 1
    ret, frame = video_capture.get_frame()
    while running_analysis and (ret or use_device):
        analysed_frame, motion_detected, return_frame_index = analyser.analyse_frame(frame)
        if not motion_detected and already_moving:
            already_moving = False
            formatted = format_time(return_frame_index / video_capture.get_fps())
            print("Fragment end: {}".format(formatted))
        elif motion_detected and not already_moving:
            already_moving = True
            formatted = format_time(return_frame_index / video_capture.get_fps())
            print("Fragment beginning: {}".format(formatted))

        ret, frame = video_capture.get_frame()
        frame_counter += 1

    print("Waiting for object detection to finish...")
    analyser.wait_for_detection()
    if already_moving:
        formatted = format_time(frame_counter / video_capture.get_fps())
        print("Fragment end: {}".format(formatted))

    print("Analysis completed")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    main()
