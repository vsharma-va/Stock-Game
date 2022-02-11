import sys
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QThread, QThreadPool, QTimer
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import Src.data_handling.scraper as scraper
import Src.threads.threadClasses as threadClasses
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import mplcursors


def printProgressTemp(price: float):
    print(price)


class DlgMain(QMainWindow):

    def __init__(self):
        super(DlgMain, self).__init__()
        uic.loadUi('../../UI/Main_Window.ui', self)
        self.FirstTab()
        self.createMainFrameGraph()

    def FirstTab(self):
        self.browse = scraper.ContUpdatedPrice()
        self.threadpool = QThreadPool()

        self.vertical = QVBoxLayout()

        self.lnEdtSearch = self.findChild(QLineEdit, "lnEdtSearch")
        self.btnSearch = self.findChild(QPushButton, "btnSearch")
        self.cmbFilter = self.findChild(QComboBox, "cmbFilter")
        self.cmbStyle = self.findChild(QComboBox, "cmbStyle")
        self.frmSuggestions = self.findChild(QFrame, "frmSuggestions")
        self.frmCharts = self.findChild(QFrame, "frmCharts")
        self.widCharts = self.findChild(QWidget, "widCharts")
        self.lstWidSuggestions = self.findChild(QListWidget, "lstWidSuggestions")
        self.rdBtnIndian = self.findChild(QRadioButton, "rdBtnIndian")
        self.rdBtnRest = self.findChild(QRadioButton, "rdBtnRest")
        self.lblText = self.findChild(QLabel, "lblText")
        self.lblCurrentPrice = self.findChild(QLabel, "lblCurrentPrice")

        self.btnSearch.clicked.connect(self.evt_btnSearch_clicked)
        self.lstWidSuggestions.itemClicked.connect(self.evt_lstWidSuggestions_itemClicked)

    def openSuggestionsBox(self):
        currentHeightFrm = self.frmSuggestions.height()
        animation = QPropertyAnimation(self.frmSuggestions, b"maximumHeight")
        animation.setDuration(500)
        animation.setStartValue(currentHeightFrm)
        animation.setEndValue(250)
        animation.setEasingCurve(QEasingCurve.InQuart)

        group = QParallelAnimationGroup(self.frmSuggestions)
        group.addAnimation(animation)
        group.start()

    def closeSuggestionsBox(self):
        currentHeightFrm = self.frmSuggestions.height()
        animation = QPropertyAnimation(self.frmSuggestions, b"maximumHeight")
        animation.setDuration(500)
        animation.setStartValue(currentHeightFrm)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.InQuart)

        group = QParallelAnimationGroup(self.frmSuggestions)
        group.addAnimation(animation)
        group.start()

    def populateSuggestionsBox(self, which_stocks: str, search: str, filter: str):
        if which_stocks == "Indian Stocks":
            if filter.lower() == "live":
                self.browse.setup(search)
                suggestions = self.browse.getSuggestions()
                self.lstWidSuggestions.addItems(suggestions[0])
                self.openSuggestionsBox()

    def runLiveIndianStock(self, browse: scraper.ContUpdatedPrice, index: int):
        indianStockWorker = threadClasses.GetLiveStockPriceIndian(self, browse, index)
        self.threadpool.start(indianStockWorker)
        indianStockWorker.signals.progress.connect(printProgressTemp)
        indianStockWorker.signals.file_path.connect(self.drawLiveGraphAndLabel)

    def createMainFrameGraph(self):
        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setParent(self.widCharts)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.widCharts)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)
        self.widCharts.setLayout(vbox)

    def getDataLiveGraph(self, item):
        with open(item[0], 'r', encoding='utf-8') as file_read:
            data = file_read.readlines()
        time_stamp = []
        price = []
        data.pop(0)
        for i in data:
            time_stamp.append(i.replace('\n', '').split(",")[0])
            price.append(float(i.replace('\n', '').split(",")[1]))
        return [time_stamp, price]

    def createLiveGraph(self, data):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel("Dates")
        self.axes.set_ylabel("Price")
        self.axes.set_xticklabels(data[0], Rotation=70)
        line = self.axes.plot(data[0], data[1])
        cursor = mplcursors.cursor(line)
        self.canvas.draw()

    def drawLiveGraphAndLabel(self, item):
        data = self.getDataLiveGraph(item)
        self.createLiveGraph(data)
        self.updateLabelWithPrice(data)

    def updateLabelWithPrice(self, data):
        self.lblCurrentPrice.setText(f'{data[1][-1]}')

    # def calculateLiveGraph(self, item):
        # liveSeries = QLineSeries()
        # pen = liveSeries.pen()
        # pen.setWidth(3)
        # liveSeries.setPen(pen)
        # with open(item[0], 'r', encoding='utf-8') as file_read:
        #     data = file_read.readlines()
        # time_stamp = []
        # price = []
        # data.pop(0)
        # for i in data:
        #     time_stamp.append(i.replace('\n', '').split(",")[0])
        #     price.append(float(i.replace('\n', '').split(",")[1]))
        #
        # counter = 0
        # for z in price:
        #     liveSeries.append(counter, float(z))
        #     counter += 1
        #
        # max_price = sorted(price, key=float)[-1]
        # min_price = sorted(price, key=float)[0]
        # print(max_price)
        #
        # liveChart = QChart()
        # liveChart.addSeries(liveSeries)
        # liveChart.setAnimationOptions(QChart.SeriesAnimations)
        # liveChart.setTitle(item[1])
        #
        # axis_x = QBarCategoryAxis()
        # axis_x.append(time_stamp)
        # axis_x.setLabelsAngle(70)
        #
        # liveChart.addAxis(axis_x, Qt.AlignBottom)
        # liveSeries.attachAxis(axis_x)
        #
        # self.axis_y = QCategoryAxis(labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue, startValue=0.0)
        # liveChart.setAxisY(self.axis_y)
        #
        # liveSeries.attachAxis(self.axis_y)
        #
        # for s in self.axis_y.categoriesLabels():
        #     self.axis_y.remove(s)
        # for i in range(int(min_price), int(max_price) + 1, 5):
        #     self.axis_y.append(str(i), i)
        # self.axis_y.setRange(min_price, max_price)
        #
        # liveChart.legend().setVisible(True)
        # liveChart.legend().setAlignment(Qt.AlignBottom)
        #
        # chart_view = custom_chart_view.ChartView(liveChart)
        # chart_view.setRenderHint(QPainter.Antialiasing)
        #
        # chart_view.setRubberBand(QChartView.HorizontalRubberBand)
        #
        # for i in reversed(range(self.vertical.count())):
        #     self.vertical.itemAt(i).widget().setParent(None)
        #
        # self.vertical.addWidget(chart_view)
        # self.widCharts.setLayout(self.vertical)
        #
        # liveSeries.hovered.connect(chart_view.showToolTipLiveGraph)

    def evt_btnSearch_clicked(self):
        if self.lnEdtSearch.text() != '':
            if self.rdBtnIndian.isChecked():
                self.populateSuggestionsBox("Indian Stocks", self.lnEdtSearch.text(), self.cmbFilter.currentText())
            elif self.rdBtnRest.isChecked():
                self.populateSuggestionsBox("Rest", self.lnEdtSearch.text(), self.cmbFilter.currentText())

    def evt_lstWidSuggestions_itemClicked(self, item):
        self.closeSuggestionsBox()
        if self.rdBtnIndian.isChecked() and self.cmbFilter.currentText().lower() == "live":
            self.browse.selectAndClickSuggestions(self.lstWidSuggestions.row(item))
            self.runLiveIndianStock(self.browse, self.lstWidSuggestions.row(item))


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlgMain = DlgMain()
    dlgMain.show()
    sys.exit(app.exec_())
