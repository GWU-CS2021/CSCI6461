import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton, QPlainTextEdit
)

from simulator.CSCI6461.project.src.cpu import CPU
from simulator.CSCI6461.project.src.mfr import *
from simulator.CSCI6461.project.src.word import Word
import logging
import datetime

def set_log():
    loggers = logging.getLogger('root')
    loggers.setLevel(logging.DEBUG)

    # Create the Handler for logging data to a file
    logger_handler = logging.FileHandler(filename=datetime.datetime.now().strftime("%Y-%m-%d") + '.log')
    logger_handler.setLevel(logging.DEBUG)

    # Create a Formatter for formatting the log messages
    logger_formatter = logging.Formatter('[%(levelname)s:%(asctime)s - %(filename)s:%(lineno)s:%(funcName)10s() - ] - %(message)s')

    # Add the Formatter to the Handler
    logger_handler.setFormatter(logger_formatter)

    # Add the Handler to the Logger
    loggers.addHandler(logger_handler)

button_value = "0000000000000000"
cpu_instance = CPU()
reg_list = {}


# Create register creator class.
class RegisterGUI(QWidget):
    def __init__(self, name, action, count, has_button, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reg_name = name
        self.button_action = action
        self.reg_count = count
        self.has_button = has_button
        # add text label
        label_reg = QtWidgets.QLabel(self)
        label_reg.setGeometry(QtCore.QRect(0, 0, 41, 21))
        label_reg.setText(self.reg_name)
        # generate labels for binary indicator
        self.labels = [self.create_label() for i in range(0, self.reg_count)]
        counter = 0
        for label in self.labels:
            label.setGeometry(QtCore.QRect(50 + counter * 30, 0, 21, 21))
            counter += 1

        # add LD button
        if has_button:
            push_button_reg = QtWidgets.QPushButton("LD", self)
            push_button_reg.setGeometry(QtCore.QRect(50 + self.reg_count * 30, 0, 41, 21))
            push_button_reg.setAutoFillBackground(False)
            push_button_reg.clicked.connect(self.on_click)

    def create_label(self):
        label = QtWidgets.QLabel(self)
        label.setStyleSheet("background-color:rgb(0,0,0)")
        label.setText("")
        return label

    def on_click(self):
        try:
            global button_value
            self.button_action(Word.from_bin_string(button_value))
            global reg_list
            global cpu_instance
            refresh_all(reg_list, cpu_instance.get_all_reg())
        except MemReserveErr as e:
            self.logger.error("MemReserveErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_mem_reserve]
            return
        except TrapErr as e:
            logging.error("TrapErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            logging.error("OpCodeErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            self.halt_signal = 1
            logging.error("MemOverflowErr %s" % (e))
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]

        except Exception as e:
            logging.error(e)
            return

    def refresh_label(self, Word):
        counter = 0
        for digit in Word.convert_to_binary()[16-self.reg_count:][::-1]:
            if digit == "1":
                self.labels[self.reg_count - 1 - counter].setStyleSheet("background-color:rgb(255,0,0)")
            else:
                self.labels[self.reg_count - 1 - counter].setStyleSheet("background-color:rgb(0,0,0)")
            counter += 1


class PressButton(QWidget):
    original_style_sheet = "background-color: rgb(255, 255, 255);" \
                           "border-radius: 10px;" \
                           "border: 1px outset gray;"

    pressed_style_sheet = "background-color: rgb(150, 150, 150);" \
                          "border-radius: 10px;" \
                          "border: 1px outset gray;"

    def __init__(self, name, action, has_value, x, y, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button_name = name
        self.button_action = action
        self.has_value = has_value
        self.x_pos = x
        self.y_pos = y
        self.width = width
        self.height = height
        self.clicked = False
        self.button = self.create_button(self.button_name)

    def create_button(self, name):
        button = QPushButton(name, self)
        button.setStyleSheet(self.original_style_sheet)
        button.clicked.connect(self.on_click)
        return button

    def on_click(self):
        try:
            if self.button_name in [str(i) for i in range(0, 16)]:
                self.change_value()
            else:
                self.button_action()

                global reg_list
                global cpu_instance
                refresh_all(reg_list, cpu_instance.get_all_reg())
        except MemReserveErr as e:
            self.logger.error("MemReserveErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_mem_reserve]
            return
        except TrapErr as e:
            logging.error("TrapErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            logging.error("OpCodeErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            self.halt_signal = 1
            logging.error("MemOverflowErr %s" % (e))
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]

        except Exception as e:
            logging.error(e)
            return

    def change_value(self):
        name = self.button_name
        global button_value
        if self.clicked:
            temp = list(button_value)
            temp[int(name)] = "0"
            button_value = "".join(temp)
            self.clicked = False
            self.button.setStyleSheet(self.original_style_sheet)
        else:
            temp = list(button_value)
            temp[int(name)] = "1"
            button_value = "".join(temp)
            self.clicked = True
            self.button.setStyleSheet(self.pressed_style_sheet)
        print(button_value)



# def LD():
#     # TODO
#     # change it to refresh panel data function.
#     cpu_instance.
#     refresh_all(reg_list, cpu_instance.get_all_reg())


def store():
    pass


def store_plus():
    pass


def init():
    pass


def load():
    pass


def single_step():
    pass


def run():
    pass


class SimulatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        # self.value = ""
        self.init_ui()
        self.init_button_ui()
        self.setWindowTitle('Simulator')
        self.setGeometry(240, 200, 1260, 600)
        self.show()
        global reg_list
        global cpu_instance
        refresh_all(reg_list, cpu_instance.get_all_reg())

    def init_button_ui(self):
        # name: x, y, width, height, has_value, action
        button_property = {
            "Store": [900, 400, 60, 30, False, cpu_instance.store],
            "St+": [980, 400, 60, 30, False, cpu_instance.store_plus],
            "Load": [1060, 400, 60, 30, False, cpu_instance.load],
            "Init": [1140, 400, 60, 30, False, cpu_instance.memory.init_program],
            "SS": [980, 460, 40, 60, False, cpu_instance.run_single_cycle],
            "Run": [1060, 460, 40, 60, False, cpu_instance.run],
            "0": [100, 460, 40, 60, True, "change_value"],
            "1": [150, 460, 40, 60, True, "change_value"],
            "2": [200, 460, 40, 60, True, "change_value"],
            "3": [250, 460, 40, 60, True, "change_value"],
            "4": [300, 460, 40, 60, True, "change_value"],
            "5": [350, 460, 40, 60, True, "change_value"],
            "6": [400, 460, 40, 60, True, "change_value"],
            "7": [450, 460, 40, 60, True, "change_value"],
            "8": [500, 460, 40, 60, True, "change_value"],
            "9": [550, 460, 40, 60, True, "change_value"],
            "10": [600, 460, 40, 60, True, "change_value"],
            "11": [650, 460, 40, 60, True, "change_value"],
            "12": [700, 460, 40, 60, True, "change_value"],
            "13": [750, 460, 40, 60, True, "change_value"],
            "14": [800, 460, 40, 60, True, "change_value"],
            "15": [850, 460, 40, 60, True, "change_value"],
        }
        w = {}
        for key in button_property:
            property = button_property[key]
            w[key] = PressButton(key, property[5], property[4], property[0], property[1], property[2], property[3],
                                 self)
            w[key].setGeometry(QtCore.QRect(property[0], property[1], property[2], property[3]))

    def init_ui(self):
        map_reg_location = {
            # name: x_location,y_location,reg_count,button_function,has_button
            "GPR0": [40, 70, 16, cpu_instance.gpr[0].set, True],
            "GPR1": [40, 110, 16, cpu_instance.gpr[1].set, True],
            "GPR2": [40, 150, 16, cpu_instance.gpr[2].set, True],
            "GPR3": [40, 190, 16, cpu_instance.gpr[3].set, True],
            "IXR1": [40, 280, 16, cpu_instance.ixr[1].set, True],
            "IXR2": [40, 320, 16, cpu_instance.ixr[2].set, True],
            "IXR3": [40, 360, 16, cpu_instance.ixr[3].set, True],
            "PC": [780, 70, 12, cpu_instance.pc.set, True],
            "MAR": [780, 110, 12, cpu_instance.mar.set, True],
            "MBR": [660, 150, 16, cpu_instance.mbr.set, True],
            "IR": [660, 190, 16, cpu_instance.ir.set, False],
            "MFR": [1020, 230, 4, cpu_instance.mfr.set, False],
        }
        global reg_list
        for key in map_reg_location:
            location = map_reg_location[key]
            reg_list[key] = RegisterGUI(key, location[3], location[2], location[4], self)
            if location[4]:
                width = location[2] * 30 + 100
            else:
                width = location[2] * 30 + 50
            reg_list[key].setGeometry(location[0], location[1], width, 40)


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setFont(QFont('Arial', 10))
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)

        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('[%(levelname)s:%(asctime)s - %(filename)s:%(lineno)s:%(funcName)10s() - ] - %(message)s'))
        logging.getLogger("root").addHandler(logTextBox)
        # You can control the logging level

        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)
        self.setGeometry(0,0,500,400)



def refresh_all(reg_list, reg_value):
    for reg in reg_list:
        reg_list[reg].refresh_label(Word.from_bin_string(reg_value[reg]))


class ErrorApp:
    # ...

    def raise_error(self):
        assert False


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)




def main():
    set_log()
    sys.excepthook = excepthook
    e = ErrorApp()
    app = QApplication(sys.argv)
    # init GUI
    ex = SimulatorGUI()
    # init LOGBOX
    dlg = MyDialog()
    dlg.show()
    dlg.raise_()
    sys.exit(app.exec_())





if __name__ == '__main__':
    main()
