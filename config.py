from PySide6.QtCore import QSize
import numpy as np
from math import sqrt


WINDOW_TITLE = "Марковские цепи"

DEFAULT_MAXIMUM_IMG_SIZE = QSize(150, 240)

DEFAULT_APP_STYLE_SHEET = "background-color: rgb(71, 73, 76);"\
                           "color: white;"
DEFAULT_BUTTON_STYLE_SHEET = "background-color: rgb(61, 63, 66)"
DEFAULT_SLIDER_STYLE_SHEET = """
        QSlider::groove:horizontal {
    border: 1px solid #565a5e;
    height: 10px;
    background: rgb(100, 100, 100);
    margin: 0px;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: rgb(127, 0, 255);
    border: 1px solid #565a5e;
    width: 24px;
    height: 8px;
    border-radius: 4px;
}
        """


MAXIMUM_MATRIX_SIZE = 20
MAXIMUM_T = 100

EPS = 0.01

N = 100

P1 = np.matrix([[1/2, 1/2, 0, 0, 0],
               [3/4, 1/4, 0, 0, 0],
               [0, 0, 1/3, 2/3, 0],
               [0, 0, 1/2, 1/2, 0],
               [1/4, 1/4, 0, 0, 1/2]])

V0_A = np.array([1/3, 1/3, 0, 0, 1/3])
V0_B = np.array([0, 0, 1/2, 1/2, 0])

def is_equal(v1_: float, v2_: float = 0) -> bool:
    return abs(v1_ - v2_) <= EPS

def norm(v: np.array) -> float:
    n2 = 0.
    for i in range(len(v)):
        n2 += v[i] * v[i]
    return sqrt(n2)

GRAPH_OPTIONS = '''
  const options = {
  "nodes": {
    "physics": false
  },
  "edges": {
    "endPointOffset": {
      "to": 5
    },
    "color": {
      "inherit": true
    },
    "scaling": {
      "min": 5,
      "max": 40
    },
    "selfReference": {
      "size": 20,
      "angle": 1.17809724509617
    },
    "smooth": {
      "forceDirection": "none"
    }
  },
  "physics": {
    "minVelocity": 0.75
  }
}
'''
