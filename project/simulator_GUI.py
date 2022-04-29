import sys
import time
import traceback

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QRadioButton
)

from src.cpu import CPU
from src.mfr import *
from src.word import Word
import logging
import datetime


def set_log():
    loggers = logging.getLogger('cpu')
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
# ca
cache_list = {}
# rob
rob_list = {}
# bpb
bpb_list = {}



# create register creator class
class RegisterGUI(QWidget):
    def __init__(self, name, action, count, has_button, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("cpu")
        self.reg_name = name
        self.button_action = action
        self.reg_count = count
        self.has_button = has_button
        # add text label
        label_reg = QtWidgets.QLabel(self)
        label_reg.setGeometry(QtCore.QRect(0, 0, 41, 21))
        label_reg.setText(self.reg_name)
        # generate labels for binary indicator
        self.labels = [self.create_label() for _ in range(0, self.reg_count)]
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
            self.logger.info("ld on %s with value %s(%d)" %
                             (self.reg_name, button_value, Word.from_bin_string(button_value)))
            self.button_action(Word.from_bin_string(button_value))
            global reg_list
            global cpu_instance
            refresh_all(reg_list, cpu_instance.get_all_reg())
        except Exception as e:
            self.logger.error(e)
            return

    # update the label of each register
    def refresh_label(self, word):
        counter = 0
        for digit in word.convert_to_binary()[16 - self.reg_count:][::-1]:
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
        self.logger = logging.getLogger("cpu")
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
        global cpu_instance
        try:
            if self.button_name in [str(i) for i in range(0, 16)]:
                self.change_value()
            else:
                global signal_list
                global reg_list

                # set run on
                signal_list["RUN"].setStyleSheet("background-color:rgb(255,0,0)")
                # refresh gui
                QApplication.processEvents()
                # process
                self.button_action()
                # set run off
                signal_list["RUN"].setStyleSheet("background-color:rgb(0,0,0)")
                refresh_all(reg_list, cpu_instance.get_all_reg())
        except MemReserveErr as e:
            cpu_instance.trigger_mfr(0)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            self.logger.error("MemReserveErr %s" % e)
            cpu_instance.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_mem_reserve]
            return
        except TrapErr as e:
            cpu_instance.trigger_mfr(1)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            self.logger.error("TrapErr %s" % e)
            cpu_instance.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            cpu_instance.trigger_mfr(2)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            self.logger.error("OpCodeErr %s" % e)
            cpu_instance.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            cpu_instance.trigger_mfr(3)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            cpu_instance.halt_signal = 1
            self.logger.error("MemOverflowErr %s" % e)
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]

        except Exception as e:
            self.logger.error(e, traceback.format_exc())
            cpu_instance.halt_signal = 1
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


# class for init press button
class KeyboardButton(QWidget):
    # button style for 0-15 press button, run and ss
    original_large_button_style_sheet = "QPushButton{background-color: rgb(255, 255, 255)}" \
                                        "QPushButton{border-radius: 10px}" \
                                        "QPushButton{border: 1px outset gray}" \
                                        "QPushButton{height: 40px}" \
                                        "QPushButton{width: 60px}"

    # button style for other button
    original_style_sheet = "QPushButton{background-color: rgb(255, 255, 255)}" \
                           "QPushButton{border-radius: 10px}" \
                           "QPushButton{border: 1px outset gray}" \
                           "QPushButton{height: 40px}" \
                           "QPushButton{width: 40px}"

    def __init__(self, name, single_step_run, interactive_run, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("cpu")
        self.button_name = name
        self.single_step_run = single_step_run
        self.interactive_run = interactive_run
        self.button = self.create_button(self.button_name)

    # create button function
    def create_button(self, name):
        button = QPushButton(name, self)
        if self.button_name in ["enter"]:
            self.resize(70, 50)
            button.setStyleSheet(self.original_large_button_style_sheet)
        else:
            self.resize(50, 50)
            button.setStyleSheet(self.original_style_sheet)
        button.clicked.connect(self.on_click)
        return button

    # click function for press button except LD
    def on_click(self):
        global cpu_instance
        try:
            value = self.button_name
            if self.button_name == "enter":
                cpu_instance.keyboard_input_action("\r")
                # TODO remove
                # logging.getLogger("output2").debug("\r")
            else:
                if ord(value) <= ord("Z") and ord(value) >= ord("A"):
                    value = (chr(ord(value)+32))
                cpu_instance.keyboard_input_action(value)
                # logging.getLogger("output2").debug(self.button_name)

            signal_list["RUN"].setStyleSheet("background-color:rgb(255,0,0)")
            # refresh gui
            QApplication.processEvents()
            # process
            if cpu_instance.run_mode == 1:
                self.interactive_run()
            elif cpu_instance.run_mode == 0:
                self.single_step_run()
            else:
                self.logger.debug("illegal input %s detected" % value)
            # set run off
            signal_list["RUN"].setStyleSheet("background-color:rgb(0,0,0)")
            refresh_all(reg_list, cpu_instance.get_all_reg())
        except MemReserveErr as e:
            cpu_instance.trigger_mfr(0)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            self.logger.error("MemReserveErr %s" % (e))
            cpu_instance.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_mem_reserve]
            return
        except TrapErr as e:
            cpu_instance.trigger_mfr(1)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            self.logger.error("TrapErr %s" % (e))
            cpu_instance.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            cpu_instance.trigger_mfr(2)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            self.logger.error("OpCodeErr %s" % (e))
            cpu_instance.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            cpu_instance.trigger_mfr(3)
            refresh_all(reg_list, cpu_instance.get_all_reg())
            cpu_instance.halt_signal = 1
            self.logger.error("MemOverflowErr %s" % (e))
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]

        except Exception as e:
            self.logger.error(e, traceback.format_exc())
            cpu_instance.halt_signal = 1
            return


# use CacheFormatter to change cache display to DEC/BIN/HEX
class CacheFormatter(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        radiobutton = QRadioButton("BIN", self)
        radiobutton.setChecked(True)
        radiobutton.values = 2
        radiobutton.toggled.connect(self.on_click)

        radiobutton = QRadioButton("DEC", self)
        radiobutton.values = 10
        radiobutton.toggled.connect(self.on_click)
        radiobutton.move(0, 20)

        radiobutton = QRadioButton("HEX", self)
        radiobutton.values = 16
        radiobutton.toggled.connect(self.on_click)
        radiobutton.move(0, 40)

        input_text = QtWidgets.QLabel(self)
        input_text.setGeometry(QtCore.QRect(20, 80, 41, 21))
        input_text.setText("Legend")
        input_text = QtWidgets.QLabel(self)
        input_text.setGeometry(QtCore.QRect(0, 100, 41, 21))
        input_text.setText("Update")
        self.input_label = QtWidgets.QLabel(self)
        self.input_label.setStyleSheet("background-color:rgb(0,0,128)")
        self.input_label.setGeometry(QtCore.QRect(50, 100, 21, 21))
        self.input_label.setText("")
        input_text = QtWidgets.QLabel(self)
        input_text.setGeometry(QtCore.QRect(0, 130, 41, 21))
        input_text.setText("Hit")
        self.input_label = QtWidgets.QLabel(self)
        self.input_label.setStyleSheet("background-color:rgb(0,128,0)")
        self.input_label.setGeometry(QtCore.QRect(50, 130, 21, 21))
        self.input_label.setText("")
        input_text = QtWidgets.QLabel(self)
        input_text.setGeometry(QtCore.QRect(0, 160, 41, 21))
        input_text.setText("Replace")
        self.input_label = QtWidgets.QLabel(self)
        self.input_label.setStyleSheet("background-color:rgb(128,0,0)")
        self.input_label.setGeometry(QtCore.QRect(50, 160, 21, 21))
        self.input_label.setText("")

    def on_click(self):
        radio_button = self.sender()
        global cpu_instance
        if radio_button.isChecked():
            cpu_instance.cache_display = radio_button.values
            refresh_cache()


# interactive run, refresh ui after each cycle
def interactive_run():
    cpu_instance.run_mode = 1
    cpu_instance.halt_signal = 0
    cpu_instance.logger.info("start run")
    while cpu_instance.halt_signal == 0 and cpu_instance.input_signal == -1:
        cpu_instance.run_single_cycle()
        # no need for additional refresh if halt
        if cpu_instance.halt_signal == 0 and cpu_instance.input_signal == -1:
            refresh_all(reg_list, cpu_instance.get_all_reg())
            # force refresh gui during run
            QApplication.processEvents()
            time.sleep(0.01)


def single_step():
    cpu_instance.run_mode = 0
    cpu_instance.run_single_cycle()


class SimulatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        # self.value = ""
        self.init_ui()
        self.init_button_ui()
        self.init_signal_ui()
        self.setWindowTitle('Simulator')
        self.init_cache_indicator()

        self.init_output_box()
        self.init_logbox()
        self.init_keyboard()
        self.init_bpb_indicator()
        self.setGeometry(10, 100, 1900, 900)
        self.show()
        global reg_list
        global cpu_instance
        refresh_all(reg_list, cpu_instance.get_all_reg())

    def init_output_box(self):
        # init output box
        output_box = QtWidgets.QGroupBox("output", self)
        log_text_box = QTextEditLogger(output_box, "insert")
        # You can format what is printed to text box
        log_text_box.setFormatter(logging.Formatter(
            '%(message)s'))
        logging.getLogger("output2").setLevel(logging.DEBUG)
        logging.getLogger("output2").addHandler(log_text_box)
        log_text_box.widget.setGeometry(10, 20, 300, 470)
        output_box.setGeometry(1550, 50, 320, 500)

    def init_logbox(self):
        # init debug logging
        log_box = QtWidgets.QGroupBox("simulator_log", self)
        log_text_box = QTextEditLogger(log_box, "append")
        # You can format what is printed to text box
        log_text_box.setFormatter(logging.Formatter(
            '[%(levelname)s:%(asctime)s - %(filename)s:%(lineno)s:%(funcName)10s() - ] - %(message)s'))
        logging.getLogger("cpu").addHandler(log_text_box)
        # You can control the logging level
        log_text_box.widget.setGeometry(10, 20, 300, 270)
        log_box.setGeometry(1550, 550, 320, 300)

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
        run_text.setGeometry(QtCore.QRect(1120, 490, 41, 21))
        run_text.setText("Run")
        self.run_label = QtWidgets.QLabel(self)
        self.run_label.setStyleSheet("background-color:rgb(0,0,0)")
        self.run_label.setGeometry(QtCore.QRect(1160, 490, 21, 21))
        self.run_label.setText("")
        input_text = QtWidgets.QLabel(self)
        input_text.setGeometry(QtCore.QRect(1120, 520, 41, 21))
        input_text.setText("Input")
        self.input_label = QtWidgets.QLabel(self)
        self.input_label.setStyleSheet("background-color:rgb(0,0,0)")
        self.input_label.setGeometry(QtCore.QRect(1160, 520, 21, 21))
        self.input_label.setText("")
        global signal_list
        signal_list["HLT"] = self.hlt_label
        signal_list["RUN"] = self.run_label
        signal_list["INPUT"] = self.input_label




    def init_keyboard(self):
        # init keyboard here
        keyboard_box = QtWidgets.QGroupBox("keyboard", self)
        # name: x, y, width, height, has_value, action
        x1_offset, y1_offset = 20, 20
        x2_offset, y2_offset = 50, 70
        x3_offset, y3_offset = 70, 120
        x4_offset, y4_offset = 90, 170
        button_property = {
            "1": [0 + x1_offset, y1_offset],
            "2": [50 + x1_offset, y1_offset],
            "3": [100 + x1_offset, y1_offset],
            "4": [150 + x1_offset, y1_offset],
            "5": [200 + x1_offset, y1_offset],
            "6": [250 + x1_offset, y1_offset],
            "7": [300 + x1_offset, y1_offset],
            "8": [350 + x1_offset, y1_offset],
            "9": [400 + x1_offset, y1_offset],
            "0": [450 + x1_offset, y1_offset],
            "Q": [0 + x2_offset, y2_offset],
            "W": [50 + x2_offset, y2_offset],
            "E": [100 + x2_offset, y2_offset],
            "R": [150 + x2_offset, y2_offset],
            "T": [200 + x2_offset, y2_offset],
            "Y": [250 + x2_offset, y2_offset],
            "U": [300 + x2_offset, y2_offset],
            "I": [350 + x2_offset, y2_offset],
            "O": [400 + x2_offset, y2_offset],
            "P": [450 + x2_offset, y2_offset],
            "A": [0 + x3_offset, y3_offset],
            "S": [50 + x3_offset, y3_offset],
            "D": [100 + x3_offset, y3_offset],
            "F": [150 + x3_offset, y3_offset],
            "G": [200 + x3_offset, y3_offset],
            "H": [250 + x3_offset, y3_offset],
            "J": [300 + x3_offset, y3_offset],
            "K": [350 + x3_offset, y3_offset],
            "L": [400 + x3_offset, y3_offset],
            "enter": [450 + x3_offset, y3_offset],
            "Z": [0 + x4_offset, y4_offset],
            "X": [50 + x4_offset, y4_offset],
            "C": [100 + x4_offset, y4_offset],
            "V": [150 + x4_offset, y4_offset],
            "B": [200 + x4_offset, y4_offset],
            "N": [250 + x4_offset, y4_offset],
            "M": [300 + x4_offset, y4_offset],
        }
        keyboard_button = {}
        for key in button_property:
            b_property = button_property[key]
            keyboard_button[key] = KeyboardButton(key, single_step, interactive_run, keyboard_box)
            keyboard_button[key].move(b_property[0], b_property[1])
        keyboard_box.setGeometry(20, 550, 600, 300)

    def init_bpb_indicator(self):
        # init cache indicator here
        cache_box = QtWidgets.QGroupBox("Branch Prediction Buffer", self)
        self.tableWidget_0 = QTableWidget(cache_box)
        self.tableWidget_0.setRowCount(16)
        self.tableWidget_0.setColumnCount(2)
        self.tableWidget_0.setGeometry(10, 15, 250, 510)
        self.tableWidget_0.setHorizontalHeaderItem(0, QTableWidgetItem("Address"))
        self.tableWidget_0.setHorizontalHeaderItem(1, QTableWidgetItem("Predict"))
        header = self.tableWidget_0.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_0.verticalHeader().setStretchLastSection(True)
        self.tableWidget_0.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.tableWidget_1 = QTableWidget(cache_box)
        self.tableWidget_1.setRowCount(8)
        self.tableWidget_1.setColumnCount(2)
        self.tableWidget_1.setGeometry(10, 530, 250, 270)
        self.tableWidget_1.setHorizontalHeaderItem(0, QTableWidgetItem("Command"))
        self.tableWidget_1.setHorizontalHeaderItem(1, QTableWidgetItem("Status"))
        header = self.tableWidget_1.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_1.verticalHeader().setStretchLastSection(True)
        self.tableWidget_1.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        global cpu_instance, cache_list,bpb_list,rob_list
        index = 0
        for _ in cpu_instance.bpb.buffer:
            bpb_list["Address" + str(index)] = QTableWidgetItem("0000000000000000")
            bpb_list["Predict" + str(index)] = QTableWidgetItem("0")

            self.tableWidget_0.setVerticalHeaderItem(index, QTableWidgetItem(str(index)))
            self.tableWidget_0.setItem(index, 0, bpb_list["Address" + str(index)])
            self.tableWidget_0.setItem(index, 1, bpb_list["Predict" + str(index)])

            index += 1
        index = 0
        for _ in cpu_instance.bpb.rob.buffer:
            rob_list["Command" + str(index)] = QTableWidgetItem("")
            rob_list["Status" + str(index)] = QTableWidgetItem("")

            self.tableWidget_1.setVerticalHeaderItem(index, QTableWidgetItem(str(index)))
            self.tableWidget_1.setItem(index, 0, rob_list["Command" + str(index)])
            self.tableWidget_1.setItem(index, 1, rob_list["Status" + str(index)])

            index += 1

        # cache_list["address3"].setBackground(QtGui.QColor(100,100,150))
        cache_box.setGeometry(1250, 50, 270, 800)

    def init_cache_indicator(self):
        # init cache indicator here
        cache_box = QtWidgets.QGroupBox("cache", self)
        cache_formatter = CacheFormatter(cache_box)
        cache_formatter.move(520, 20)
        self.tableWidget_0 = QTableWidget(cache_box)
        self.tableWidget_0.setRowCount(8)
        self.tableWidget_0.setColumnCount(2)
        self.tableWidget_0.setGeometry(10, 20, 250, 270)
        self.tableWidget_0.setHorizontalHeaderItem(0, QTableWidgetItem("Address"))
        self.tableWidget_0.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        header = self.tableWidget_0.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_0.verticalHeader().setStretchLastSection(True)
        self.tableWidget_0.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.tableWidget_1 = QTableWidget(cache_box)
        self.tableWidget_1.setRowCount(8)
        self.tableWidget_1.setColumnCount(2)
        self.tableWidget_1.setGeometry(265, 20, 250, 270)
        self.tableWidget_1.setHorizontalHeaderItem(0, QTableWidgetItem("Address"))
        self.tableWidget_1.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        header = self.tableWidget_1.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget_1.verticalHeader().setStretchLastSection(True)
        self.tableWidget_1.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        global cpu_instance, cache_list
        index = 0
        for _ in cpu_instance.memory.cache:
            cache_list["address" + str(index)] = QTableWidgetItem("0000000000000000")
            cache_list["value" + str(index)] = QTableWidgetItem("0000000000000000")
            if index < 8:
                self.tableWidget_0.setVerticalHeaderItem(index, QTableWidgetItem(str(index)))
                self.tableWidget_0.setItem(index, 0, cache_list["address" + str(index)])
                self.tableWidget_0.setItem(index, 1, cache_list["value" + str(index)])
            else:
                self.tableWidget_1.setVerticalHeaderItem(index % 8, QTableWidgetItem(str(index)))
                self.tableWidget_1.setItem(index % 8, 0, cache_list["address" + str(index)])
                self.tableWidget_1.setItem(index % 8, 1, cache_list["value" + str(index)])
            index += 1
        # cache_list["address3"].setBackground(QtGui.QColor(100,100,150))
        cache_box.setGeometry(640, 550, 600, 300)

    # interactive run to refresh and run one command every 0.01 second

    def load_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', "", '')
        if file_path == "":
            return
        cpu_instance.load_file(file_path)

    # init all the press buttons
    def init_button_ui(self):
        # name: x, y, width, height, has_value, action
        button_property = {
            "Store": [900, 400, 60, 30, False, cpu_instance.store],
            "St+": [980, 400, 60, 30, False, cpu_instance.store_plus],
            "Load": [1060, 400, 60, 30, False, cpu_instance.load],
            "Init": [1140, 400, 60, 30, False, cpu_instance.init_program],
            "LdFile": [820, 400, 60, 30, False, self.load_file],
            "SS": [980, 460, 40, 60, False, single_step],
            "Run": [1060, 460, 40, 60, False, interactive_run],
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
            b_property = button_property[key]
            w[key] = PressButton(key, b_property[5], b_property[4], self)
            w[key].resize(b_property[2] + 10, b_property[3] + 10)
            w[key].move(b_property[0], b_property[1])

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
            "CC": [1020, 270, 4, cpu_instance.cc.set, False],
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
    def __init__(self, parent, append_mode):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setFont(QFont('Arial', 10))
        self.widget.setReadOnly(True)

        self.append_mode = append_mode

    def emit(self, record):
        msg = self.format(record)
        if self.append_mode == "append":
            self.widget.appendPlainText(msg)
        else:
            self.widget.insertPlainText(msg)
        self.widget.moveCursor(QtGui.QTextCursor.End)


def refresh_cache():
    index = 0
    for cache in cpu_instance.memory.cache:
        if cpu_instance.cache_display == 10:
            address = str(cache.addr)
            value = str(cache.value)
        elif cpu_instance.cache_display == 16:
            address = cache.addr.convert_to_hex()
            value = cache.value.convert_to_hex()
        else:
            address = cache.addr.convert_to_binary()
            value = cache.value.convert_to_binary()
        cache_list["address" + str(index)].setText(address)
        cache_list["value" + str(index)].setText(value)
        cache_list["address" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        cache_list["value" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        if cpu_instance.memory.cache_update_at == index:
            cache_list["address" + str(index)].setBackground(QtGui.QColor(0, 0, 128))
            cache_list["value" + str(index)].setBackground(QtGui.QColor(0, 0, 128))
        elif cpu_instance.memory.cache_hit_at == index:
            cache_list["address" + str(index)].setBackground(QtGui.QColor(0, 128, 0))
            cache_list["value" + str(index)].setBackground(QtGui.QColor(0, 128, 0))

        elif cpu_instance.memory.cache_replace_at == index:
            cache_list["address" + str(index)].setBackground(QtGui.QColor(128, 0, 0))
            cache_list["value" + str(index)].setBackground(QtGui.QColor(128, 0, 0))
        else:
            cache_list["address" + str(index)].setBackground(QtGui.QColor(255, 255, 255))
            cache_list["value" + str(index)].setBackground(QtGui.QColor(255, 255, 255))
            cache_list["address" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            cache_list["value" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        index += 1

    index = 0
    for rob_line in cpu_instance.bpb.rob.buffer:
        rob_list["Command" + str(index)].setText(rob_line.command)
        rob_list["Status" + str(index)].setText(rob_line.status)
        index += 1

    index = 0
    for bpb_line in cpu_instance.bpb.buffer:
        predict = str(bpb_line.value)
        if cpu_instance.cache_display == 10:
            address = str(bpb_line.addr)
        elif cpu_instance.cache_display == 16:
            address = bpb_line.addr.convert_to_hex()
        else:
            address = bpb_line.addr.convert_to_binary()
        bpb_list["Address" + str(index)].setText(address)
        bpb_list["Predict" + str(index)].setText(predict)
        bpb_list["Address" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        bpb_list["Predict" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        if cpu_instance.bpb.cache_update_at == index:
            bpb_list["Address" + str(index)].setBackground(QtGui.QColor(0, 0, 128))
            bpb_list["Predict" + str(index)].setBackground(QtGui.QColor(0, 0, 128))
        elif cpu_instance.bpb.cache_hit_at == index:
            bpb_list["Address" + str(index)].setBackground(QtGui.QColor(0, 128, 0))
            bpb_list["Predict" + str(index)].setBackground(QtGui.QColor(0, 128, 0))

        elif cpu_instance.bpb.cache_replace_at == index:
            bpb_list["Address" + str(index)].setBackground(QtGui.QColor(128, 0, 0))
            bpb_list["Predict" + str(index)].setBackground(QtGui.QColor(128, 0, 0))
        else:
            bpb_list["Address" + str(index)].setBackground(QtGui.QColor(255, 255, 255))
            bpb_list["Predict" + str(index)].setBackground(QtGui.QColor(255, 255, 255))
            bpb_list["Address" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            bpb_list["Predict" + str(index)].setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        index += 1


# global function to refresh all the registers after specific operation
def refresh_all(reg_list_local, reg_value):
    for reg in reg_list_local:
        reg_list_local[reg].refresh_label(Word.from_bin_string(reg_value[reg]))
    if cpu_instance.halt_signal == 1:
        signal_list["HLT"].setStyleSheet("background-color:rgb(255,0,0)")
    else:
        signal_list["HLT"].setStyleSheet("background-color:rgb(0,0,0)")
    if cpu_instance.input_signal != -1:
        signal_list["INPUT"].setStyleSheet("background-color:rgb(255,0,0)")
    else:
        signal_list["INPUT"].setStyleSheet("background-color:rgb(0,0,0)")
    refresh_cache()


class ErrorApp:
    def raise_error(self):
        assert False


def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


def main():
    set_log()
    sys.except_hook = except_hook
    _ = ErrorApp()
    app = QApplication(sys.argv)
    # init GUI
    _ = SimulatorGUI()
    # init LOGBOX
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
