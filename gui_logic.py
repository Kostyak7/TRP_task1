import os
import numpy as np
import networkx as nx
from math import sqrt
from pyvis.network import Network
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, \
    QVBoxLayout, QPushButton, QLineEdit, QLabel, QGridLayout, \
    QHBoxLayout, QCheckBox, QSlider, QDialog, \
    QMenuBar, QComboBox, QFormLayout, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt
from trp_logic import Logic
import config as cf


class MainWindow(QMainWindow):
    def __init__(self, app_: QApplication):
        super().__init__()
        self.app = app_
        self.setStyleSheet(cf.DEFAULT_APP_STYLE_SHEET)
        self.window_manager = WindowManager(self)
        self.setCentralWidget(self.window_manager)
        self.__window_init()
    
    def __window_init(self) -> None:
        self.setWindowTitle(cf.WINDOW_TITLE)

    def exit(self) -> None:
        self.app.exit()


class WindowManager(QWidget):
    def __init__(self, main_window_):
        super().__init__()
        self.main_window = main_window_
        self.main_app_widget = MainAppWidget(self)
        
        self.active_widget = self.main_app_widget
        self._widgets_to_layout()
        self.active_widget.set_active()
    
    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.main_app_widget)
        
        self.setLayout(layout)

    def __deactivate_widget(self) -> None:
        self.active_widget.set_active(False)
    
    def __run_widget(self, widget_) -> None:
        self.__deactivate_widget()
        self.active_widget = widget_
        self.active_widget.set_active()

    def run_main_app(self) -> None:
        self.__run_widget(self.main_app_widget)
    
    def exit(self) -> None:
        self.main_window.exit()


class ICentralWidget(QWidget):
    def __init__(self, window_manager_):
        super().__init__(window_manager_)
        self.window_manager = window_manager_
        self.set_active(False)
    
    def _widgets_to_layout(self) -> None: ...

    def set_active(self, is_activate_: bool = True) -> None:
        self.setVisible(is_activate_)


class AbstractToolDialog(QDialog):
    def __init__(self, name_: str, parent_: QWidget = None):
        super().__init__(parent_)
        self.name = name_
        self.setWindowTitle(self.name)

    def _widgets_to_layout(self) -> None: ...

    def close(self) -> None:
        super().close()

    def cancel_action(self) -> None:
        self.close()

    def run(self) -> None:
        self.show()


class ProbabilityEdit(QLineEdit):
    def __init__(self, def_value_: float, parent_: QWidget = None):
        super().__init__(str(def_value_), parent_)
        self.value = def_value_
        self.setValidator(QDoubleValidator(0., 1., 2))
        self.textChanged.connect(self.edit_action)

        self.setFixedWidth(50)
    
    def set_value(self, value_: float) -> None:
        if value_ >= 0 and value_ <= 1:
            self.value = value_
            if self.value == 0:
                self.setText('0')
            else:
                self.setText(str(round(self.value, 2)))


    def edit_action(self, text_: str) -> None:
        if len(text_ ):
            self.value = float(text_.replace(',', '.')) 


class MatrixEditWidget(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.N = cf.N
        self.N_editor = QLineEdit(str(self.N), self)
        self.N_editor.setValidator(QIntValidator(0, 150))
        self.N_editor.textChanged.connect(self.N_edit_action)
        self.n = 5
        self.edit_matrix = []
        self.__edit_matrix_init()
        self.edit_vector = []
        self.__edit_vector_init()
        self.size_editor = QComboBox(self)
        self.size_editor.addItems([str(i + 1) for i in range(cf.MAXIMUM_MATRIX_SIZE)])
        self.size_editor.currentIndexChanged.connect(self.size_edit_action)
        self.size_editor.setCurrentIndex(self.n - 1)
        self.reshape(8)
        self._widgets_to_layout()
    
    def __edit_matrix_init(self) -> None:
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            tmp_arr = []
            for j in range(cf.MAXIMUM_MATRIX_SIZE):
                tmp_arr.append(ProbabilityEdit(0., self))
                tmp_arr[-1].setToolTip(f"{i} -> {j}")
            self.edit_matrix.append(tmp_arr)
    
    def __edit_vector_init(self) -> None:
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            self.edit_vector.append(ProbabilityEdit(0., self))
            self.edit_vector[i].setToolTip(str(i))

    def _widgets_to_layout(self) -> None:
        layout = QFormLayout()
        layout.addRow("Количество\nтраекторий", self.N_editor)
        layout.addRow("Размерность", self.size_editor)
        tmp = QGridLayout()
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            for j in range(cf.MAXIMUM_MATRIX_SIZE):
                tmp.addWidget(self.edit_matrix[i][j], i, j)
        w = QWidget()
        w.setLayout(tmp)
        layout.addRow("Матрица", None)
        layout.addWidget(w)

        tmp = QGridLayout()
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            tmp.addWidget(self.edit_vector[i], 1, i)
        w = QWidget()
        w.setLayout(tmp)
        layout.addRow("Вектор", None)
        layout.addWidget(w)

        self.setLayout(layout)
    
    def reshape(self, n_: int) -> None:
        if n_ == self.n:
            return
        if n_ > cf.MAXIMUM_MATRIX_SIZE:
            n_ = cf.MAXIMUM_MATRIX_SIZE
        if n_ < 1:
            n_ = 1
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            self.edit_vector[i].setVisible(i < n_)
            for j in range(cf.MAXIMUM_MATRIX_SIZE):
                self.edit_matrix[i][j].setVisible(i < n_ and j < n_)
        self.n = n_

    def N_edit_action(self, text_: str) -> None:
        self.N = int(text_) if len(text_) and text_.isdigit() else self.N   

    def size_edit_action(self, index_: int) -> None:
        self.reshape(index_ + 1)

    def set_from_logic(self, logic_: Logic) -> None:
        self.N = logic_.N
        P = logic_.get_matrix()
        self.reshape(len(P))
        v = logic_.get_vector(0)
        for i in range(self.n):
            self.edit_vector[i].set_value(v[i])
            for j in range(self.n):
                self.edit_matrix[i][j].set_value(P[i, j])    

    def set_to_logic(self, logic_: Logic) -> None:
        P = []
        v = []
        for i in range(self.n):
            v.append(self.edit_vector[i].value)
            P.append([])
            for j in range(self.n):
                P[i].append(self.edit_matrix[i][j].value)
        logic_.set_matrix(np.matrix(P))
        logic_.set_vector(np.array(v))
        logic_.N = self.N

    def check_stochastic(self) -> bool:
        vvalue = 0
        for i in range(self.n):
            vvalue += self.edit_vector[i].value
            mvalue = 0
            for j in range(self.n):
                mvalue += self.edit_matrix[i][j].value
            if not cf.is_equal(mvalue, 1):
                return False
        return cf.is_equal(vvalue, 1)
        
        
class  SettingsDialog(AbstractToolDialog):
    def __init__(self, main_app_):
        super().__init__("Настройки", main_app_)
        self.main_app = main_app_
        self.is_check_stochastic = True
        self.stochastic_checkbox = QCheckBox(self)
        self.stochastic_checkbox.setChecked(self.is_check_stochastic)
        self.stochastic_checkbox.stateChanged.connect(self.stochastic_change_action)
        self.matrix_edit_widget = MatrixEditWidget(self)
        self.matrix_edit_widget.set_from_logic(self.main_app.logic)
        
        self.ok_button = QPushButton("Ок")
        self.ok_button.clicked.connect(self.accept_action)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel_action)

        self._widgets_to_layout()

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp = QFormLayout()
        tmp.addRow("Проверка на\nстохастичность", self.stochastic_checkbox)
        layout.addLayout(tmp)
        layout.addWidget(self.matrix_edit_widget)
        tmp = QHBoxLayout()
        tmp.addWidget(self.ok_button)
        tmp.addWidget(self.cancel_button)
        layout.addLayout(tmp)
        self.setLayout(layout)
    
    def stochastic_change_action(self, state_: bool) -> None:
        self.is_check_stochastic = state_

    def accept_action(self) -> None:
        if self.is_check_stochastic and not self.matrix_edit_widget.check_stochastic():
            QMessageBox.warning(self.main_app, "Что-то не так", "Матрица или вектор не являются стохастическими", QMessageBox.Ok)
            return
        self.matrix_edit_widget.set_to_logic(self.main_app.logic)
        self.main_app.t_widget.set_value(1)
        self.close()
    
    def run(self) -> None:
        self.matrix_edit_widget.set_from_logic(self.main_app.logic)
        self.show()


class ProbabilityText(QLabel):
    def __init__(self, value_: float, parent_: QWidget = None):
        super().__init__(parent_)
        self.value = value_
        self.set_value(self.value)
        self.setFixedWidth(50)

    def set_value(self, value_: float) -> None:
        if value_ >= 0 and value_ <= 1:
            self.value = value_
            if self.value == 0:
                self.setText('0')
            else:
                self.setText(str(round(self.value, 2))) 


class VectorWidget(QWidget):
    def __init__(self, parent_: QWidget):
        super().__init__(parent_)
        self.vector = []
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            self.vector.append(ProbabilityText(0., self))
            self.vector[i].setToolTip(str(i))
        
        self._widgets_to_layout()
        
    def _widgets_to_layout(self) -> None:
        layout = QGridLayout()
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            layout.addWidget(self.vector[i], 1, i)
        self.setLayout(layout)


class MatrixWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.n = 0
        self.matrix = []
        self.__matrix_init()
        self.vector = VectorWidget(self)
        self.svector = VectorWidget(self)
        self.norm_label = QLabel(self)

        self._widgets_to_layout()

    def __matrix_init(self) -> None:
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            tmp_arr = []
            for j in range(cf.MAXIMUM_MATRIX_SIZE):
                tmp_arr.append(ProbabilityText(0., self))
                tmp_arr[-1].setToolTip(f"{i} -> {j}")
            self.matrix.append(tmp_arr)

    def _widgets_to_layout(self) -> None:
        layout = QFormLayout()
        tmp = QGridLayout()
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            for j in range(cf.MAXIMUM_MATRIX_SIZE):
                tmp.addWidget(self.matrix[i][j], i, j)
        w = QWidget()
        w.setLayout(tmp)
        layout.addRow("Матрица", None)
        layout.addWidget(w)
        
        layout.addRow("Вектор", None)
        layout.addWidget(self.vector)

        layout.addRow("Статистический\nВектор", None)
        layout.addWidget(self.svector)
        layout.addRow("Норма разности", self.norm_label)
        self.setLayout(layout)

    def reshape(self, n_: int) -> None:
        if n_ == self.n:
            return
        if n_ > cf.MAXIMUM_MATRIX_SIZE:
            n_ = cf.MAXIMUM_MATRIX_SIZE
        if n_ < 1:
            n_ = 1
        for i in range(cf.MAXIMUM_MATRIX_SIZE):
            self.vector.vector[i].setVisible(i < n_)
            self.svector.vector[i].setVisible(i < n_)
            for j in range(cf.MAXIMUM_MATRIX_SIZE):
                self.matrix[i][j].setVisible(i < n_ and j < n_)
        self.n = n_

    def set_from_logic(self, logic_: Logic, t_: int = 1) -> None:
        P = logic_.get_matrix(t_)
        self.reshape(len(P))
        v = np.array(logic_.get_vector(t_))
        sv = logic_.get_statistic_vector(t_)
        n2 = 0
        for i in range(self.n):
            n2 += (v[i] - sv[i]) * (v[i] - sv[i])
            self.vector.vector[i].set_value(v[i])
            self.svector.vector[i].set_value(sv[i])
            for j in range(self.n):
                self.matrix[i][j].set_value(P[i, j])
        self.norm_label.setText("\t" + str(round(sqrt(n2), 4)))

    
class GraphWidget(QWidget):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.webEngineView = QWebEngineView()
        
        self._widgets_to_layout()
    
    def set_from_graph(self, G_: nx.DiGraph, name_: str = "test0.html") -> None:
        view = Network(height=380, directed=True, notebook=False)
        view.set_options(cf.GRAPH_OPTIONS)
        view.from_nx(G_, show_edge_weights=True)
        view.write_html(name_)
        with open(name_, 'r') as f:
            html = f.read()
            self.webEngineView.setHtml(html)
    
    def set_from_logic(self, logic_: Logic, t_: int = 1) -> None:
        name = "test1.html"
        G = logic_.get_graph(logic_.get_matrix(t_))
        view = Network(height=450,directed=True, notebook=False)
        view.set_options(cf.GRAPH_OPTIONS)
        view.from_nx(G, show_edge_weights=True) 
        view.write_html(name)
        with open(name, 'r') as f:
            html = f.read()
            self.webEngineView.setHtml(html)

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.webEngineView)
        self.setLayout(layout)


class ParameterTWidget(QWidget):
    def __init__(self, main_app_) -> None:
        super().__init__(main_app_)
        self.main_app = main_app_
        self.slider = QSlider(Qt.Horizontal, self)
        self.t_value_widget = QLabel("1", self)
        self.__slider_init()

        self._widgets_to_layout()

    def __slider_init(self) -> None:
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setRange(1, cf.MAXIMUM_T)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.change_t_parameter)
    
    def _widgets_to_layout(self) -> None:
        layout = QFormLayout()
        layout.addWidget(self.slider)
        layout.addRow("t   =", self.t_value_widget)
        self.setLayout(layout)
    
    def value(self) -> int:
        return self.slider.value()
    
    def set_value(self, t_: int = 1) -> None:
        self.slider.setValue(t_)
        self.change_t_parameter()
    
    def change_t_parameter(self) -> None:
        t = self.slider.value()
        self.main_app.matrix_widget.set_from_logic(self.main_app.logic, t)
        self.main_app.graph_widget.set_from_logic(self.main_app.logic, t)
        self.main_app.trajectory_widget.set_new_trajectory()
        self.t_value_widget.setText(str(t))


class TrajectoryWidget(QWidget):
    def __init__(self, main_app_):
        super().__init__(main_app_)
        self.main_app = main_app_
        self.graph_widget = GraphWidget(self)
        self.graph_widget.setMinimumHeight(400)
        self.button = QPushButton("Показать траекторию")
        self.button.clicked.connect(self.set_new_trajectory)
        self.button.setMaximumWidth(200)
        
        self.set_new_trajectory()
        self._widgets_to_layout()
    
    def _widgets_to_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.graph_widget)
        layout.addWidget(self.button)
        self.setLayout(layout)
    
    def set_new_trajectory(self) -> None:
        t = self.main_app.t_widget.value()
        tr = self.main_app.logic.get_trajectory(t)
        M = [] * (t + 1)
        for i in range(t + 1):
            M.append([0] * (t + 1))
            if i < t:
                M[i][i + 1] = 1
        G = nx.from_numpy_array(np.matrix(M), create_using=nx.DiGraph)
        for i in range(t + 1):
            G.nodes[i]['label'] = str(tr[i])
            G.nodes[i]['title'] = str(tr[i])
        self.graph_widget.set_from_graph(G)
           

class MainAppWidget(ICentralWidget):
    def __init__(self, window_manager_):
        super().__init__(window_manager_)
        self.logic = Logic()
        self.settings_dialog = SettingsDialog(self)
        self.t_widget = ParameterTWidget(self)
        self.matrix_widget = MatrixWidget(self)
        self.matrix_widget.set_from_logic(self.logic)
        self.graph_widget = GraphWidget(self)
        self.graph_widget.set_from_logic(self.logic)
        self.trajectory_widget = TrajectoryWidget(self)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)
        self.window_manager.main_window.setMenuBar(self.menu_bar)
        self.settings_action = self.menu_bar.addAction("Настройки") 
        self.menu_bar.addSeparator()
        self.exit_action = self.menu_bar.addAction("Выход")
        self.__actions_init()

        self._widgets_to_layout()

    def __actions_init(self) -> None:
        self.settings_action.triggered.connect(self.settings_dialog.run)
        self.exit_action.triggered.connect(self.window_manager.exit)

    def _widgets_to_layout(self) -> None:
        layout = QVBoxLayout()
        tmp = QHBoxLayout()
        tmp.addWidget(self.matrix_widget)
        tmp.addWidget(self.graph_widget)
        layout.addLayout(tmp)
        layout.addWidget(self.t_widget)
        layout.addWidget(self.trajectory_widget)
        self.setLayout(layout)