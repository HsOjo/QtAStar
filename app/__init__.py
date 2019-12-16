import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from app.main import MainWindow


class Application:
    def __init__(self, args):
        self.hook_exception()
        self.qt = QApplication(args)
        self.events = dict(
            process_events=self.qt.processEvents
        )
        self.main = MainWindow(events=self.events)

    def run(self):
        self.main.show()
        return self.qt.exec_()

    def hook_exception(self):
        def boom(type, value, tb):
            from io import StringIO
            import traceback
            with StringIO() as io:
                traceback.print_exception(type, value, tb, file=io)
                io.seek(0)
                exc = io.read()
            self.callback_exception(exc)

        sys.excepthook = boom

    def callback_exception(self, e):
        print(e)
        QMessageBox.warning(self.main, 'Error', e)
