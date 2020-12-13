from .defaults import *

DEFAULT_MODE = {
    "max_video_width": MAX_VIDEO_WIDTH,
    "max_video_height": MAX_VIDEO_HEIGHT,
    "blur_size": BLUR_SIZE,
    "minimal_move_area": MINIMAL_MOVE_AREA,
    "bg_subtractor": BG_SUBTRACTOR.name,
    "begin_with_sigmadelta": True,
    "sigmadelta_frames": SIGMADELTA_FRAMES,
    "use_threshold": True,
    "delta_threshold": DELTA_THRESHOLD,
    "dilation_iterations": DILATION_ITERATIONS,
    "max_contours": MAX_CONTOURS,
    "minimal_move_frames": MINIMAL_MOVE_FRAMES,
    "max_break_length": MAX_BREAK_LENGTH,
    "object_detection_interval": OBJECT_DETECTION_INTERVAL
}

FAST_MODE = {
    "max_video_width": MAX_VIDEO_WIDTH,
    "max_video_height": MAX_VIDEO_HEIGHT,
    "blur_size": BLUR_SIZE,
    "minimal_move_area": MINIMAL_MOVE_AREA,
    "bg_subtractor": BG_SUBTRACTOR.name,
    "begin_with_sigmadelta": True,
    "sigmadelta_frames": SIGMADELTA_FRAMES,
    "use_threshold": False,
    "delta_threshold": DELTA_THRESHOLD,
    "dilation_iterations": DILATION_ITERATIONS,
    "max_contours": MAX_CONTOURS,
    "minimal_move_frames": MINIMAL_MOVE_FRAMES,
    "max_break_length": MAX_BREAK_LENGTH,
    "object_detection_interval": 60
}

CHANGING_LIGHT_MODE = {
    "max_video_width": MAX_VIDEO_WIDTH,
    "max_video_height": MAX_VIDEO_HEIGHT,
    "blur_size": BLUR_SIZE,
    "minimal_move_area": 75,
    "bg_subtractor": BgSubtractorType.ViBe.name,
    "begin_with_sigmadelta": True,
    "sigmadelta_frames": SIGMADELTA_FRAMES,
    "use_threshold": True,
    "delta_threshold": DELTA_THRESHOLD,
    "dilation_iterations": DILATION_ITERATIONS,
    "max_contours": 100,
    "minimal_move_frames": MINIMAL_MOVE_FRAMES,
    "max_break_length": MAX_BREAK_LENGTH,
    "object_detection_interval": OBJECT_DETECTION_INTERVAL
}
