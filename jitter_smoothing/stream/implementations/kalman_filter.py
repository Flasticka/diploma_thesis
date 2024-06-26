from filterpy.kalman import KalmanFilter
import numpy as np

from exceptions.not_valid_dimensionality_exception import NotValidDimensionalityException
from ..interfaces.jitter_smoothing_interface import JitterSmoothingInterface


class KalmanFilterStream(JitterSmoothingInterface):
    def __init__(self, initial_frame, q=0.05, r=1):
        self.result = initial_frame
        self.kf_states = []
        for i in range(initial_frame.shape[0]):
            f = KalmanFilter(dim_x=9, dim_z=3)
            initial_state_mean = np.hstack((initial_frame[i], np.zeros(6))).reshape(
                -1, 1
            )
            f.x = initial_state_mean
            f.F = np.array(
                [
                    [1, 0, 0, 1, 0, 0, 0.5, 0, 0],
                    [0, 1, 0, 0, 1, 0, 0, 0.5, 0],
                    [0, 0, 1, 0, 0, 1, 0, 0, 0.5],
                    [0, 0, 0, 1, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 1],
                ]
            )
            f.H = np.eye(3, 9)
            f.Q = q * np.eye(9)
            f.R = r * np.eye(3)
            self.kf_states.append(f)

    def smooth_frame(self, frame):
        self.result = []
        for i in range(frame.shape[0]):
            self.kf_states[i].predict()
            self.kf_states[i].update(frame[i])
            self.result.append(self.kf_states[i].x_post[:3, 0])

    def get_last_smoothed_frame(self):
        return np.array(self.result)


class KalmanFilterStream2D:
    def __init__(self, initial_frame, q=0.05, r=1):
        self.result = initial_frame
        self.kf_states = []
        for i in range(initial_frame.shape[0]):
            f = KalmanFilter(dim_x=6, dim_z=2)
            initial_state_mean = np.hstack((initial_frame[i], np.zeros(4))).reshape(
                -1, 1
            )
            f.x = initial_state_mean
            f.F = np.array(
                [
                    [1, 0, 1, 0, 0.5, 0],
                    [0, 1, 0, 1, 0, 0.5],
                    [0, 0, 1, 0, 1, 0],
                    [0, 0, 0, 1, 0, 1],
                    [0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1],
                ]
            )
            f.H = np.eye(2, 6)
            f.Q = q * np.eye(6)
            f.R = r * np.eye(2)

            self.kf_states.append(f)

    def smooth_frame(self, frame):
        self.result = []
        for i in range(frame.shape[0]):
            self.kf_states[i].predict()
            self.kf_states[i].update(frame[i])
            self.result.append(self.kf_states[i].x_post[:2, 0])

    def get_last_smoothed_frame(self):
        return np.array(self.result)


def get_kalman(initial_frame, q=0.05, r=1):
    if initial_frame.shape[1] == 2:
        return KalmanFilterStream2D(initial_frame, q, r)
    if initial_frame.shape[1] == 3:
        return KalmanFilterStream(initial_frame, q, r)
    raise NotValidDimensionalityException("initial_frame.shape[1] (cords dimensionality)", "2 or 3")
