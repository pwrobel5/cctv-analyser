import enum


class BgSubtractorType(enum.Enum):
    KNN = 0
    ViBe = 1
    SigmaDelta = 2
    AdaptiveSegmenter = 3
