#!/usr/bin/env python3
"""
Simple Calculator GUI (no .ui) implementing floating-point + - * / operations.

Run:
    python3 calculator.py

This will try to import PyQt5 and fall back to PySide6 if PyQt5 is not available.
"""
import sys

# try PyQt5, then PySide6
try:
    from PyQt5.QtWidgets import (
        QApplication,
        QWidget,
        QLineEdit,
        QPushButton,
        QGridLayout,
        QVBoxLayout,
        QSizePolicy,
    )
    from PyQt5.QtCore import Qt, QEvent
    QT_BINDING = "PyQt5"
except Exception:
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QWidget,
            QLineEdit,
            QPushButton,
            QGridLayout,
            QVBoxLayout,
            QSizePolicy,
        )
        from PySide6.QtCore import Qt, QEvent
        QT_BINDING = "PySide6"
    except Exception:
        raise RuntimeError("Please install PyQt5 or PySide6 to run this application.")


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(360, 520)  # calculator-like size

        self._create_ui()
        self._connect_signals()

        # internal state
        self.left_operand = None
        self.pending_op = None
        self.waiting_for_new_number = True  # start with empty display

    def _create_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # display
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(70)
        self.display.setStyleSheet("font-size: 24px; padding-right: 8px;")
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(self.display)

        # grid of buttons roughly matching the sketched layout.
        grid = QGridLayout()
        main_layout.addLayout(grid)

        # Buttons layout:
        # right column contains operators and equals (taller)
        btn_defs = [
            # row, col, text, rowspan, colspan
            (0, 0, "←", 1, 1),  # backspace
            (0, 1, "÷", 1, 1),
            (0, 2, "×", 1, 1),
            (0, 3, "−", 1, 1),

            (1, 0, "7", 1, 1),
            (1, 1, "8", 1, 1),
            (1, 2, "9", 1, 1),
            (1, 3, "+", 2, 1),  # plus spans two rows (taller)

            (2, 0, "4", 1, 1),
            (2, 1, "5", 1, 1),
            (2, 2, "6", 1, 1),

            (3, 0, "1", 1, 1),
            (3, 1, "2", 1, 1),
            (3, 2, "3", 1, 1),
            (3, 3, "=", 2, 1),  # equals tall on the right column

            (4, 0, "0", 1, 2),  # zero spans two columns
            (4, 2, ".", 1, 1),
            (4, 3, "C", 1, 1),  # clear
        ]

        self.buttons = {}
        for r, c, text, rs, cs in btn_defs:
            btn = QPushButton(text)
            # set a reasonable min size; allow layout to manage exact sizes
            btn.setMinimumSize(60 * cs, 52 * rs)
            btn.setStyleSheet("font-size: 18px;")
            grid.addWidget(btn, r, c, rs, cs)
            self.buttons[text] = btn

        # Make keys expand reasonably if layout changes
        for i in range(4):
            grid.setColumnStretch(i, 1)

    def _connect_signals(self):
        # digit buttons
        for ch in "0123456789":
            if ch in self.buttons:
                self.buttons[ch].clicked.connect(lambda _, ch=ch: self._digit_clicked(ch))

        # decimal point
        self.buttons["."].clicked.connect(self._dot_clicked)

        # operations (map displayed symbols to internal ops)
        self.buttons["+"].clicked.connect(lambda: self._operator_clicked("+"))
        self.buttons["−"].clicked.connect(lambda: self._operator_clicked("-"))
        self.buttons["×"].clicked.connect(lambda: self._operator_clicked("*"))
        self.buttons["÷"].clicked.connect(lambda: self._operator_clicked("/"))

        # equals
        self.buttons["="].clicked.connect(self._equals_clicked)

        # clear and backspace
        self.buttons["C"].clicked.connect(self._clear)
        self.buttons["←"].clicked.connect(self._backspace)

        # keyboard support: install event filter on the main window
        self.installEventFilter(self)

    def eventFilter(self, watched, event):
        # allow keyboard input to control calculator
        if event.type() == QEvent.KeyPress:
            key = event.key()
            text = event.text()
            if text.isdigit():
                self._digit_clicked(text)
                return True
            if text == ".":
                self._dot_clicked()
                return True
            if key in (Qt.Key_Plus,):
                self._operator_clicked("+")
                return True
            if key in (Qt.Key_Minus, Qt.Key_Underscore):
                self._operator_clicked("-")
                return True
            if key in (Qt.Key_Asterisk,):
                self._operator_clicked("*")
                return True
            if key in (Qt.Key_Slash,):
                self._operator_clicked("/")
                return True
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self._equals_clicked()
                return True
            if key == Qt.Key_Backspace:
                self._backspace()
                return True
            if key in (Qt.Key_C, Qt.Key_Escape):
                self._clear()
                return True
        return super().eventFilter(watched, event)

    def _digit_clicked(self, ch):
        if self.waiting_for_new_number:
            # start a new number
            if ch == "0":
                # avoid multiple leading zeros like "000"
                self.display.setText("0")
            else:
                self.display.setText(ch)
            self.waiting_for_new_number = False
        else:
            current = self.display.text()
            # avoid leading zeros like "012" unless there's a dot
            if current == "0" and ch == "0":
                return
            if current == "0" and ch != "0" and "." not in current:
                self.display.setText(ch)
            else:
                self.display.setText(current + ch)

    def _dot_clicked(self):
        if self.waiting_for_new_number:
            self.display.setText("0.")
            self.waiting_for_new_number = False
        else:
            if "." not in self.display.text():
                self.display.setText(self.display.text() + ".")

    def _operator_clicked(self, op):
        try:
            cur_val = float(self.display.text())
        except Exception:
            cur_val = 0.0

        if self.left_operand is None:
            self.left_operand = cur_val
        else:
            # if there's a pending operator, evaluate it first (allow chaining)
            if self.pending_op is not None and not self.waiting_for_new_number:
                result = self._evaluate(self.left_operand, cur_val, self.pending_op)
                self.left_operand = result
                # show result
                self.display.setText(self._format_number(result))

        self.pending_op = op
        self.waiting_for_new_number = True

    def _equals_clicked(self):
        if self.pending_op is None:
            return
        try:
            cur_val = float(self.display.text())
        except Exception:
            cur_val = 0.0
        result = self._evaluate(self.left_operand if self.left_operand is not None else 0.0, cur_val, self.pending_op)
        self.display.setText(self._format_number(result))
        # reset state: allow further operations with this result
        self.left_operand = None
        self.pending_op = None
        self.waiting_for_new_number = True

    def _clear(self):
        self.display.setText("0")
        self.left_operand = None
        self.pending_op = None
        self.waiting_for_new_number = True

    def _backspace(self):
        if self.waiting_for_new_number:
            # nothing to backspace; keep as 0
            self.display.setText("0")
            return
        text = self.display.text()
        if len(text) <= 1:
            self.display.setText("0")
            self.waiting_for_new_number = True
        else:
            new = text[:-1]
            self.display.setText(new)

    def _evaluate(self, a, b, op):
        try:
            if op == "+":
                return a + b
            elif op == "-":
                return a - b
            elif op == "*":
                return a * b
            elif op == "/":
                if b == 0.0:
                    # signal an error
                    return float("inf")
                return a / b
        except Exception:
            return 0.0

    def _format_number(self, v: float) -> str:
        # Format floats so they look nice: truncate unnecessary trailing zeros
        if v == float("inf"):
            return "Error"
        # Avoid scientific notation for typical calculator ranges
        text = ("{:.10f}".format(v)).rstrip("0").rstrip(".")
        if text == "":"
            text = "0"
        return text


def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    # call the appropriate exec method for the binding
    try:
        # PySide6 and modern bindings expose exec()
        exit_code = app.exec()
    except TypeError:
        # PyQt5 older binding may require exec_()
        exit_code = app.exec_()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
