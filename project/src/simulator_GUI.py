import sys
import time
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton
)

from cpu import CPU
from mfr import *
from word import Word
import logging
import datetime


def set_log():
    loggers = logging.getLogger('root')
    loggers.setLevel(logging.DEBUG)

    # Create the Handler for logging data to a file
    logger_handler = logging.FileHandler(filename=datetime.datetime.now().strftime("%Y-%m-%d") + '.log')
    logger_handler.setLevel(logging.DEBUG)

    # Create a Formatter for formatting the log messages
    logger_formatter = logging.Formatter(
        '[%(levelname)s:%(asctime)s - %(filename)s:%(lineno)s:%(funcName)10s() - ] - %(message)s')

    # Add the Formatter to the Handler
    logger_handler.setFormatter(logger_formatter)

    # Add the Handler to the Logger
    loggers.addHandler(logger_handler)

# global variable to store the value of 16 button
button_value = "0000000000000000"
# new an instance of cpu
cpu_instance = CPU()
# store the name and value of register
reg_list = {}
# store signals, HLT and RUN
signal_list = {}


# create register creator class
class RegisterGUI(QWidget):
    def __init__(self, name, action, count, has_button, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("root")
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

    # click function of LD button
    def on_click(self):
        try:
            global button_value
            self.logger.info("ld on %s with value %s(%d)"%(self.reg_name,button_value,Word.from_bin_string(button_value)))
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
            self.logger.error("TrapErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            self.logger.error("OpCodeErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            self.halt_signal = 1
            self.logger.error("MemOverflowErr %s" % (e))
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]

        except Exception as e:
            self.logger.error(e)
            return

    # update the label of each register
    def refresh_label(self, Word):
        counter = 0
        for digit in Word.convert_to_binary()[16 - self.reg_count:][::-1]:
            if digit == "1":
                self.labels[self.reg_count - 1 - counter].setStyleSheet("background-color:rgb(255,0,0)")
            else:
                self.labels[self.reg_count - 1 - counter].setStyleSheet("background-color:rgb(0,0,0)")
            counter += 1


# class for init press button
class PressButton(QWidget):
    # button style for 0-15 press button, run and ss
    original_large_button_style_sheet = "QPushButton{background-color: rgb(255, 255, 255)}" \
                                        "QPushButton{border-radius: 10px}" \
                                        "QPushButton{border: 1px outset gray}" \
                                        "QPushButton{height: 60px}" \
                                        "QPushButton{width: 40px}"

    # button style for other button
    original_style_sheet = "QPushButton{background-color: rgb(255, 255, 255)}" \
                           "QPushButton{border-radius: 10px}" \
                           "QPushButton{border: 1px outset gray}" \
                           "QPushButton{height: 30px}" \
                           "QPushButton{width: 60px}"

    # pressed button style for 0-15 press button
    pressed_large_button_style_sheet = "QPushButton{background-color: rgb(150, 150, 150)}" \
                                       "QPushButton{border-radius: 10px}" \
                                       "QPushButton{border: 1px outset gray}" \
                                       "QPushButton{height: 60px}" \
                                       "QPushButton{width: 40px}"

    def __init__(self, name, action, has_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("root")
        self.button_name = name
        self.button_action = action
        self.has_value = has_value
        self.clicked = False
        self.button = self.create_button(self.button_name)

    # create button function
    def create_button(self, name):
        button = QPushButton(name, self)
        if self.button_name in [str(i) for i in range(0, 16)] or self.button_name == "Run" or self.button_name == "SS":
            button.setStyleSheet(self.original_large_button_style_sheet)
        else:
            button.setStyleSheet(self.original_style_sheet)
        button.clicked.connect(self.on_click)
        return button

    # click function for press button except LD
    def on_click(self):
        try:
            if self.button_name in [str(i) for i in range(0, 16)]:
                self.change_value()
            else:
                global signal_list
                global reg_list
                global cpu_instance
                signal_list["RUN"].setStyleSheet("background-color:rgb(255,0,0)")
                QApplication.processEvents()
                self.button_action()
                signal_list["RUN"].setStyleSheet("background-color:rgb(0,0,0)")
                refresh_all(reg_list, cpu_instance.get_all_reg())
        except MemReserveErr as e:
            self.logger.error("MemReserveErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_mem_reserve]
            return
        except TrapErr as e:
            self.logger.error("TrapErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            self.logger.error("OpCodeErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            self.halt_signal = 1
            self.logger.error("MemOverflowErr %s" % (e))
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]

        except Exception as e:
            self.logger.error(e)
            return

    # change the value of 16 press button
    def change_value(self):
        name = self.button_name
        global button_value
        if self.clicked:
            temp = list(button_value)
            temp[int(name)] = "0"
            button_value = "".join(temp)
            self.clicked = False
            self.button.setStyleSheet(self.original_large_button_style_sheet)
        else:
            temp = list(button_value)
            temp[int(name)] = "1"
            button_value = "".join(temp)
            self.clicked = True
            self.button.setStyleSheet(self.pressed_large_button_style_sheet)


# init the interface of simulator
class SimulatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        # self.value = ""
        self.init_ui()
        self.init_button_ui()
        self.init_signal_ui()
        self.setWindowTitle('Simulator')
        self.setGeometry(240, 200, 1260, 600)
        self.show()
        global reg_list
        global cpu_instance
        refresh_all(reg_list, cpu_instance.get_all_reg())

    # init run and halt signal light
    def init_signal_ui(self):
        hlt_text = QtWidgets.QLabel(self)
        hlt_text.setGeometry(QtCore.QRect(1120, 460, 41, 21))
        hlt_text.setText("Halt")
        self.hlt_label = QtWidgets.QLabel(self)
        self.hlt_label.setStyleSheet("background-color:rgb(0,0,0)")
        self.hlt_label.setGeometry(QtCore.QRect(1160, 460, 21, 21))
        self.hlt_label.setText("")
        run_text = QtWidgets.QLabel(self)
        run_text.setGeometry(QtCore.QRect(1120, 500, 41, 21))
        run_text.setText("Run")
        self.run_label = QtWidgets.QLabel(self)
        self.run_label.setStyleSheet("background-color:rgb(0,0,0)")
        self.run_label.setGeometry(QtCore.QRect(1160, 500, 21, 21))
        self.run_label.setText("")
        global signal_list
        signal_list["HLT"] = self.hlt_label
        signal_list["RUN"] = self.run_label

    def interactive_run(self):
        global cpu_instance
        cpu_instance.halt_signal = 0
        cpu_instance.logger.info("start run")
        while cpu_instance.halt_signal == 0:
            cpu_instance.run_single_cycle()
            # no need for additional refresh if halt
            if cpu_instance.halt_signal == 0:
                refresh_all(reg_list, cpu_instance.get_all_reg())
                # force refresh gui during run
                QApplication.processEvents()
                time.sleep(1)

    # init all the press buttons
    def init_button_ui(self):
        # name: x, y, width, height, has_value, action
        button_property = {
            "Store": [900, 400, 60, 30, False, cpu_instance.store],
            "St+": [980, 400, 60, 30, False, cpu_instance.store_plus],
            "Load": [1060, 400, 60, 30, False, cpu_instance.load],
            "Init": [1140, 400, 60, 30, False, cpu_instance.init_program],
            "SS": [980, 460, 40, 60, False, cpu_instance.run_single_cycle],
            "Run": [1060, 460, 40, 60, False, self.interactive_run],
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
            w[key] = PressButton(key, property[5], property[4], self)
            w[key].resize(property[2] + 10, property[3] + 10)
            w[key].move(property[0], property[1])

    # init all the registers
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


# The logger to handle logs
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setFont(QFont('Arial', 10))
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


# MyDialog used to open tracelog window
class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)

        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter(
            '[%(levelname)s:%(asctime)s - %(filename)s:%(lineno)s:%(funcName)10s() - ] - %(message)s'))
        logging.getLogger("root").addHandler(logTextBox)
        # You can control the logging level

        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)
        self.setGeometry(50, 100, 500, 400)


# global function to refresh all the registers after specific operation
def refresh_all(reg_list, reg_value):
    for reg in reg_list:
        reg_list[reg].refresh_label(Word.from_bin_string(reg_value[reg]))
    if cpu_instance.halt_signal == 1:
        signal_list["HLT"].setStyleSheet("background-color:rgb(255,0,0)")
    else:
        signal_list["HLT"].setStyleSheet("background-color:rgb(0,0,0)")


class ErrorApp:
    def raise_error(self):
        assert False


def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


def main():
    set_log()
    sys.except_hook = except_hook
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
