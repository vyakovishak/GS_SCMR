from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QColor
from PySide6.QtWidgets import QProxyStyle, QStyle, QStyleOptionButton, QWidget, QPushButton, QApplication, QLineEdit, \
    QComboBox


class CustomStyle(QProxyStyle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def drawControl(self, element, option, painter, widget=None):
        """
        :param element:
        :param option:
        :param painter:
        :param widget:
        """

        if element == QStyle.CE_PushButton:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)

            button_option = QStyleOptionButton()
            button_option.initFrom(widget)

            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(button_option.rect.width() - 10, 0)
            path.lineTo(button_option.rect.width(), 10)
            path.lineTo(button_option.rect.width(), button_option.rect.height())
            path.lineTo(10, button_option.rect.height())
            path.lineTo(0,button_option.rect.height()-10)
            path.closeSubpath()

            if button_option.state & QStyle.State_MouseOver:
                painter.fillPath(path, QBrush(Qt.darkGray))
            elif button_option.state & QStyle.State_Sunken:
                painter.fillPath(path, QBrush(Qt.gray))
            else:
                painter.fillPath(path, QBrush(QColor("darkorange")))

            painter.setPen(QColor("white"))
            painter.drawPath(path)

            painter.setPen(Qt.NoPen)
            painter.drawText(button_option.rect, Qt.AlignCenter, button_option.text)

            painter.restore()
        else:
            super().drawControl(element, option, painter, widget)


def override_ui_elements(cls):
    class Wrapped(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.customize_ui()

        def customize_ui(self):
            # Modify the UI elements here
            for widget in self.findChildren(QWidget):
                # Customize the widget appearance
                if isinstance(widget, QPushButton):
                    widget.setStyle(CustomStyle(QApplication.style()))
                elif isinstance(widget, QLineEdit):
                    widget.setStyleSheet("background-color: yellow;")
                elif isinstance(widget, QComboBox):
                    widget.setStyleSheet("background-color: green;")
                # Add more conditions for other UI elements as needed

    return Wrapped
