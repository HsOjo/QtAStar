import time

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidgetItem, QCheckBox, QWidget, QRadioButton, QMessageBox

from app.main.map import Map
from app.res.main import Ui_MainWindow


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.events = kwargs.get('events')

        self.map = None
        self.speed = 0.1
        self.current_pos = None
        self.eight = False
        self.moving = False

        self.le_width.setText('16')
        self.le_height.setText('12')
        self.le_obstacle_num.setText('32')

        self.hs_speed.setValue((1 - self.speed) * self.hs_speed.maximum())

        self.cb_eight.clicked.connect(lambda _: setattr(self, 'eight', self.cb_eight.isChecked()))
        self.hs_speed.valueChanged.connect(lambda v: setattr(self, 'speed', (1000 - v) / 1000))
        self.pb_gen_map.clicked.connect(self._pb_gen_map_clicked)
        self.pb_gen_map.clicked.emit()

    def _pb_gen_map_clicked(self, e):
        # 生成地图按钮点击事件
        w = int(self.le_width.text())
        h = int(self.le_height.text())
        obstacle_num = int(self.le_obstacle_num.text())

        self.map = Map(w, h)
        self.map.generate_obstacle(obstacle_num)
        self.current_pos = None
        self.render_map()

    def clear_map(self):
        # 清空地图
        for n in range(self.gl_map.rowCount()):
            for m in range(self.gl_map.columnCount()):
                item = self.gl_map.itemAtPosition(n, m)  # type:QWidgetItem
                if item is not None:
                    widget = item.widget()
                    widget.hide()
                    widget.deleteLater()
                    self.gl_map.removeItem(item)

    def print_map(self):
        print('=' * (self.map.w * 3))

        for i in self.map:
            print(i)

        print('=' * (self.map.w * 3))

    def render_map(self):
        # 渲染地图
        self.clear_map()

        for y in range(self.map.h):
            for x in range(self.map.w):
                self.update_box(x, y)

    def callback_map_clicked(self, x, y):
        if self.moving:
            return

        # 地图盒子被点击事件
        if self.map[x, y] == 1:
            if self.current_pos is None:
                self.current_pos = (x, y)
                self.update_box(x, y, 2)
            else:
                path = self.map.find_path(self.current_pos, (x, y), self.eight)
                if path:
                    self.moving = True

                    for p in path:
                        self.update_box(*p, 3)
                    self.events['process_events']()

                    for i in range(len(path)):
                        for n in range(i - 1, i):
                            self.update_box(*path[n], 3 if n != 0 else 4)
                        self.update_box(*path[i], 2)
                        self.events['process_events']()
                        time.sleep(self.speed)

                    for p in path[0:-1]:
                        self.update_box(*p, 1)
                    self.current_pos = path[-1]

                    self.moving = False
                else:
                    QMessageBox.information(self, 'Error', '那里 (%d, %d) 去不了喔！' % (x, y))

    def update_box(self, x, y, stat=None):
        # 更新盒子状态
        if stat is None:
            stat = self.map[x, y]

        item = self.gl_map.itemAtPosition(y, x)

        new_widget = self.generate_box(stat)
        if item is not None:
            old_widget = item.widget()
            old_widget.hide()
            self.gl_map.replaceWidget(old_widget, new_widget)
            old_widget.deleteLater()
        else:
            self.gl_map.addWidget(new_widget, y, x)

        if stat == 1:
            new_widget.clicked.connect((lambda x, y: lambda: self.callback_map_clicked(x, y))(x, y))

        return new_widget

    def generate_box(self, stat):
        # 生成盒子
        if stat == 0:  # obstacle
            widget = QCheckBox()
            widget.setChecked(True)
            widget.setDisabled(True)
        elif stat == 1:  # free
            widget = QCheckBox()
            widget.setCheckable(False)
        elif stat == 2:  # current position
            widget = QRadioButton()
            widget.setChecked(True)
            widget.clicked.connect(lambda: widget.toggle())
        elif stat == 3:  # path
            widget = QRadioButton()
            widget.setDisabled(True)
        elif stat == 4:  # previous position
            widget = QRadioButton()
            widget.setDisabled(True)
            widget.setChecked(True)
        else:
            widget = QWidget()

        if isinstance(widget, QRadioButton):
            widget.setAutoExclusive(False)

        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        widget.setSizePolicy(sp)

        return widget
