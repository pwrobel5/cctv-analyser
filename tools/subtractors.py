import enum


class BgSubtractorType(enum.Enum):
    MOG2 = 0
    KNN = 1
    ViBe = 2
    SigmaDelta = 3
    AdaptiveSegmenter = 4
