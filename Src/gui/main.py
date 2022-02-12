import csv
import sys
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QThread, QThreadPool, QTimer
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import Src.data_handling.scraper as scraper
import Src.threads.threadClasses as threadClasses
import Src.data_handling.data as data
from matplotlib.backends import qt_compat

use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import mplcursors
from pathlib import Path


def printProgressTemp(price: float):
    print(price)


class DlgMain(QMainWindow):

    def __init__(self):
        super(DlgMain, self).__init__()
        uic.loadUi('../../UI/Main_Window.ui', self)
        self.dataClass = data.Data()
        self.FirstTab()
        self.SecondTab()
        self.firstTimeSetupFirstTab()
        self.createMainFrameGraph()
        self.displayPastPurchases()

    def FirstTab(self):
        self.browse = scraper.ContUpdatedPrice()
        self.threadpool = QThreadPool()
        self.currentCompanyName = None

        self.vertical = QVBoxLayout()

        self.lnEdtSearch = self.findChild(QLineEdit, "lnEdtSearch")
        self.lnEdtQuantity = self.findChild(QLineEdit, "lnEdtQuantity")
        self.btnSearch = self.findChild(QPushButton, "btnSearch")
        self.btnBuy = self.findChild(QPushButton, "btnBuy")
        self.btnConfirmBuy = self.findChild(QPushButton, "btnConfirmBuy")
        self.btnCancelBuy = self.findChild(QPushButton, "btnCancelBuy")
        self.cmbFilter = self.findChild(QComboBox, "cmbFilter")
        self.cmbStyle = self.findChild(QComboBox, "cmbStyle")
        self.frmSuggestions = self.findChild(QFrame, "frmSuggestions")
        self.frmCharts = self.findChild(QFrame, "frmCharts")
        self.frmPullUpFrameBuy = self.findChild(QFrame, "frmPullUpFrameBuy")
        self.frmBuy = self.findChild(QFrame, "frmBuy")
        self.frmFilter = self.findChild(QFrame, "frmFilter")
        self.frmSearch = self.findChild(QFrame, "frmSearch")
        self.frmStats = self.findChild(QFrame, "frmStats")
        self.widCharts = self.findChild(QWidget, "widCharts")
        self.lstWidSuggestions = self.findChild(QListWidget, "lstWidSuggestions")
        self.rdBtnIndian = self.findChild(QRadioButton, "rdBtnIndian")
        self.rdBtnRest = self.findChild(QRadioButton, "rdBtnRest")
        self.lblText = self.findChild(QLabel, "lblText")
        self.lblCurrentPrice = self.findChild(QLabel, "lblCurrentPrice")
        self.lblCurrentBalance = self.findChild(QLabel, "lblCurrentBalance")
        self.lblTextCurrentAmount = self.findChild(QLabel, "lblTextCurrentAmount")
        self.lblCurrentSelectionCost = self.findChild(QLabel, "lblCurrentSelectionCost")

        self.btnSearch.clicked.connect(self.evt_btnSearch_clicked)
        self.btnBuy.clicked.connect(self.evt_btnBuy_clicked)
        self.btnConfirmBuy.clicked.connect(self.evt_btnConfirmBuy_clicked)
        self.btnCancelBuy.clicked.connect(self.evt_btnCancelBuy_clicked)
        self.lstWidSuggestions.itemClicked.connect(self.evt_lstWidSuggestions_itemClicked)
        self.lnEdtQuantity.textEdited.connect(self.evt_lnEdtQuantity_editingFinished)
        self.lnEdtQuantity.editingFinished.connect(self.evt_lnEdtQuantity_editingFinished)

        self.fadeWidgetOut(self.btnBuy)
        self.btnBuy.setEnabled(False)

    def firstTimeSetupFirstTab(self):
        balance = self.dataClass.getUserBalance()
        if balance[0]:
            self.lblCurrentBalance.setText(balance[1])
        else:
            self.setUserCurrentBalance('10000')

    def setUserCurrentBalance(self, balance: str):
        self.lblCurrentBalance.setText(f'{balance}')

    def openConfirmBuyFrame(self):
        currentHeightFrm = self.frmPullUpFrameBuy.height()
        animation = QPropertyAnimation(self.frmPullUpFrameBuy, b"maximumHeight")
        animation.setDuration(500)
        animation.setStartValue(currentHeightFrm)
        animation.setEndValue(500)
        animation.setEasingCurve(QEasingCurve.InQuart)

        group = QParallelAnimationGroup(self.frmPullUpFrameBuy)
        group.addAnimation(animation)
        group.start()

        self.fadeWidgetOut(self.frmSuggestions)
        self.fadeWidgetOut(self.frmCharts)
        self.fadeWidgetOut(self.frmBuy)
        self.fadeWidgetOut(self.frmFilter)
        self.fadeWidgetOut(self.frmSearch)
        self.fadeWidgetOut(self.frmStats)

        self.frmSuggestions.setEnabled(False)
        self.frmCharts.setEnabled(False)
        self.frmBuy.setEnabled(False)
        self.frmFilter.setEnabled(False)
        self.frmSearch.setEnabled(False)
        self.frmStats.setEnabled(False)

    def closeConfirmBuyFrame(self):
        currentHeightFrm = self.frmPullUpFrameBuy.height()
        animation = QPropertyAnimation(self.frmPullUpFrameBuy, b"maximumHeight")
        animation.setDuration(500)
        animation.setStartValue(currentHeightFrm)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.InQuart)

        group = QParallelAnimationGroup(self.frmPullUpFrameBuy)
        group.addAnimation(animation)
        group.start()

        self.fadeWidgetIn(self.frmSuggestions)
        self.fadeWidgetIn(self.frmCharts)
        self.fadeWidgetIn(self.frmBuy)
        self.fadeWidgetIn(self.frmFilter)
        self.fadeWidgetIn(self.frmSearch)
        self.fadeWidgetIn(self.frmStats)

        self.frmSuggestions.setEnabled(True)
        self.frmCharts.setEnabled(True)
        self.frmBuy.setEnabled(True)
        self.frmFilter.setEnabled(True)
        self.frmSearch.setEnabled(True)
        self.frmStats.setEnabled(True)

    def fadeWidgetOut(self, widget: QWidget):
        opacityEffect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacityEffect)

        opacityAnimation = QPropertyAnimation(opacityEffect, b"opacity")
        opacityAnimation.setDuration(750)
        opacityAnimation.setStartValue(1)
        opacityAnimation.setEndValue(0.5)

        group = QParallelAnimationGroup(widget)
        group.addAnimation(opacityAnimation)
        group.start()

    def fadeWidgetIn(self, widget: QWidget):
        opacityEffect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacityEffect)

        opacityAnimation = QPropertyAnimation(opacityEffect, b"opacity")
        opacityAnimation.setDuration(750)
        opacityAnimation.setStartValue(0.5)
        opacityAnimation.setEndValue(1)

        group = QParallelAnimationGroup(widget)
        group.addAnimation(opacityAnimation)
        group.start()

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
                self.lstWidSuggestions.clear()
                self.lstWidSuggestions.addItems(suggestions[0])
                self.openSuggestionsBox()

    def runLiveIndianStock(self, browse: scraper.ContUpdatedPrice, index: int):
        indianStockWorker = threadClasses.GetLiveStockPriceIndian(self, browse, index)
        self.threadpool.start(indianStockWorker)
        indianStockWorker.signals.progress.connect(printProgressTemp)
        indianStockWorker.signals.file_path.connect(self.drawLiveGraphAndLabel)

    def createMainFrameGraph(self):
        self.fig = Figure((0.5, 0.5))
        self.canvas = FigureCanvas(self.fig)

        self.fig.tight_layout()

        self.canvas.setParent(self.widCharts)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.widCharts)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)
        self.widCharts.setLayout(vbox)

    def createLiveGraph(self, data, companyName: str):
        self.fig.clear()
        with plt.style.context(('bmh')):
            self.axes = self.fig.add_subplot(111)
        self.axes.set_ylabel("Price")
        self.axes.set_xticklabels(data[0], Rotation=70)
        self.axes.set_title(f'{companyName}')
        line = self.axes.plot(data[0], data[1])
        cursor = mplcursors.cursor(line)
        self.canvas.draw()

    def drawLiveGraphAndLabel(self, item):
        self.currentCompanyName = item[1]
        data = self.dataClass.getDataLiveGraph(item)
        self.createLiveGraph(data, self.currentCompanyName)
        self.updateLabelWithPrice(data)

    def updateLabelWithPrice(self, data):
        self.lblCurrentPrice.setText(f'{data[1][-1]}')

    def displayWarningBox(self, functionName: str, displayText: str):
        QMessageBox.warning(self, f'Error {functionName}', displayText,
                                  QMessageBox.Ok)

    def buyStocks(self, cost: float) -> bool:
        if cost > float(self.lblCurrentBalance.text()):
            self.displayWarningBox('buyStocks', 'Not Enough Funds')
            return False
        else:
            self.lblCurrentBalance.setText(str(float(self.lblCurrentBalance.text()) - cost))
            return True

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
        self.fadeWidgetIn(self.btnBuy)
        self.btnBuy.setEnabled(True)
        self.closeSuggestionsBox()
        if self.rdBtnIndian.isChecked() and self.cmbFilter.currentText().lower() == "live":
            self.browse.selectAndClickSuggestions(False, index=self.lstWidSuggestions.row(item))
            self.runLiveIndianStock(self.browse, self.lstWidSuggestions.row(item))

    def evt_btnBuy_clicked(self):
        self.openConfirmBuyFrame()

    def evt_btnCancelBuy_clicked(self):
        self.closeConfirmBuyFrame()

    def evt_lnEdtQuantity_editingFinished(self):
        if self.lnEdtQuantity.text() != '':
            cost = int(self.lnEdtQuantity.text()) * float(self.lblCurrentPrice.text())
            self.lblCurrentSelectionCost.setText(str(cost))
        else:
            self.lblCurrentSelectionCost.setText('0')

    def evt_btnConfirmBuy_clicked(self):
        if self.lnEdtQuantity.text() == '':
            self.displayWarningBox('evt_btnConfirmBuy_clicked', 'Input Box can not be Empty!')
        else:
            cost = float(int(self.lnEdtQuantity.text()) * float(self.lblCurrentPrice.text()))
            success = self.buyStocks(cost)
            if success:
                x = self.currentCompanyName.split(' ')
                x.pop(-1)
                companyName = ' '.join(x)
                self.dataClass.saveUserInformation('bought', self.lblCurrentBalance.text(), [companyName,
                                                                                             self.lnEdtQuantity.text(),
                                                                                             str(cost)])
                self.displayPastPurchases()
                self.closeConfirmBuyFrame()

    def closeEvent(self, event):
        self.dataClass.saveUserInformation('exit', self.lblCurrentBalance.text())
        self.browse.quitDriver()
        threadClasses.e.set()
        event.accept()

    def SecondTab(self):
        self.tblWidHistory = self.findChild(QTableWidget, "tblWidHistory")
        self.btnSell = self.findChild(QPushButton, "btnSell")
        self.btnCancelSell = self.findChild(QPushButton, "btnCancelSell")
        self.btnConfirmSell = self.findChild(QPushButton, "btnConfirmSell")
        self.frmPullUpFrameSell = self.findChild(QFrame, "frmPullUpFrameSell")
        self.frmTableHistory = self.findChild(QFrame, "frmTableHistory")
        self.cmbWhichComp = self.findChild(QComboBox, "cmbWhichComp")
        self.spnBxQuantity = self.findChild(QSpinBox, "spnBxQuantity")

        self.btnSell.clicked.connect(self.evt_btnSell_clicked)
        self.btnCancelSell.clicked.connect(self.evt_btnCancelSell_clicked)
        self.btnConfirmSell.clicked.connect(self.evt_btnConfirmSell_clicked)

    def displayPastPurchases(self):
        items = self.dataClass.getPastPurchases()
        if len(items[0]) != 0:
            companyName = items[0]
            quantity = items[1]
            cost = items[2]

            row = 0
            column = 0
            if len(companyName) != 0:
                self.tblWidHistory.blockSignals(True)
                self.tblWidHistory.setRowCount(0)
                self.tblWidHistory.setRowCount(len(companyName))
                self.tblWidHistory.setColumnCount(3)
                for i in range(len(companyName)):
                    self.tblWidHistory.setItem(row, column, QTableWidgetItem(companyName[i]))
                    row += 1
                row = 0
                column += 1
                for i in range(len(quantity)):
                    self.tblWidHistory.setItem(row, column, QTableWidgetItem(quantity[i]))
                    row += 1
                row = 0
                column += 1
                for i in range(len(cost)):
                    self.tblWidHistory.setItem(row, column, QTableWidgetItem(cost[i]))
                    row += 1
                row = 0

            self.tblWidHistory.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.tblWidHistory.setRowCount(0)
            self.tblWidHistory.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def populateCmbWhichComp(self):
        items = self.dataClass.getPastPurchases()
        companyName = items[0]

        if len(companyName) != 0:
            self.cmbWhichComp.addItems(companyName)

    def populateSpnBxQuantity(self):
        items = self.dataClass.getPastPurchases()
        selectedCompanyName = self.cmbWhichComp.currentText()
        index = items[0].index(selectedCompanyName)
        self.spnBxQuantity.setMinimum(1)
        self.spnBxQuantity.setMaximum(int(items[1][index]))

    def openConfirmSellFrame(self):
        currentHeightFrm = self.frmPullUpFrameSell.height()
        animation = QPropertyAnimation(self.frmPullUpFrameSell, b"maximumHeight")
        animation.setDuration(500)
        animation.setStartValue(currentHeightFrm)
        animation.setEndValue(500)
        animation.setEasingCurve(QEasingCurve.InQuart)

        group = QParallelAnimationGroup(self.frmPullUpFrameSell)
        group.addAnimation(animation)
        group.start()

        self.fadeWidgetOut(self.frmTableHistory)

        self.frmTableHistory.setEnabled(False)

    def closeConfirmSellFrame(self):
        currentHeightFrm = self.frmPullUpFrameSell.height()
        animation = QPropertyAnimation(self.frmPullUpFrameSell, b"maximumHeight")
        animation.setDuration(500)
        animation.setStartValue(currentHeightFrm)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.InQuart)

        group = QParallelAnimationGroup(self.frmPullUpFrameSell)
        group.addAnimation(animation)
        group.start()

        self.fadeWidgetIn(self.frmTableHistory)

        self.frmTableHistory.setEnabled(True)

    def sellStocks(self):
        companyName = self.cmbWhichComp.currentText()
        quantity = self.spnBxQuantity.cleanText()
        self.browse.selectAndClickSuggestions(True, companyNameWithCode=companyName)
        currentPrice = self.browse.getUpdatedPrice()
        updatedPrice = float(self.lblCurrentBalance.text()) + (currentPrice * float(quantity))

        self.lblCurrentBalance.setText(str(updatedPrice))
        self.dataClass.saveUserInformation("sold", purchaseDetails=[companyName, quantity, currentPrice * float(quantity)])
        self.displayWarningBox("sellStocks", "Operation Completed Successfully!")
        self.displayPastPurchases()
        self.closeConfirmSellFrame()

    def evt_btnSell_clicked(self):
        print("sell clicked")
        self.openConfirmSellFrame()
        self.populateCmbWhichComp()
        self.populateSpnBxQuantity()

    def evt_btnCancelSell_clicked(self):
        self.closeConfirmSellFrame()

    def evt_btnConfirmSell_clicked(self):
        self.sellStocks()



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
