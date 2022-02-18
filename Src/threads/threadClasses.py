from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
import Src.data_handling.scraper as scraper
import Src.gui.main as main
from pathlib import Path
import csv
from datetime import datetime
from threading import Event


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    progress = QtCore.pyqtSignal(float)
    file_path = QtCore.pyqtSignal(list)


e = Event()


class GetLiveStockPriceIndian(QtCore.QRunnable):
    def __init__(self, mainClass: main.DlgMain, browse: scraper.ContUpdatedPrice, num: int):
        super(GetLiveStockPriceIndian, self).__init__()
        self.mainClass = mainClass
        self.browse = browse
        self.num = num
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        end = False
        while not end:
            if self.mainClass.cmbFilter.currentText().lower() == "live":
                now = datetime.now()
                price = self.browse.getUpdatedPrice()
                self.signals.progress.emit(price)
                allSuggestions = self.browse.getSuggestions()
                company = allSuggestions[0]
                symbol_unclean = allSuggestions[1][self.num].split(" ")
                print(symbol_unclean)
                symbol_clean = [v for v in symbol_unclean if v != ""]
                fileName = company[self.num] + f' {symbol_clean[0]}' + f' {symbol_clean[2]}' + \
                           f' {now.strftime("%d_%m_%y")}'
                filePath = Path(f"../../Data/{fileName}.csv")
                if filePath.is_file():
                    with open(filePath, 'a', encoding='utf-8', newline='') as file_append:
                        writer = csv.writer(file_append)
                        writer.writerow([f"{now.strftime('%H:%M')}", f'{price}'])
                    file_append.close()
                else:
                    with open(filePath, 'w', encoding='utf-8', newline='') as file_write:
                        writer = csv.writer(file_write)
                        writer.writerow(['timestamp', 'price'])
                        writer.writerow([f"{now.strftime('%H:%M')}", f'{price}'])
                    file_write.close()
                self.signals.file_path.emit([str(filePath), fileName])
                e.wait(timeout=120)
            else:
                self.signals.finished.emit()
                end = True
