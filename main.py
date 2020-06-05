import requests
import csv
from bs4 import BeautifulSoup
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem
from datetime import date, datetime

#pobranie danych - web scraping, 
response = requests.get("https://www.bankier.pl/waluty/kursy-walut/nbp")
response.encoding = 'utf-8'
#parser BeautifulSoup rozpoznaje znaczniki HTML, przez co łatwiej można obsłużyć dane (np po znaczniku "td")
soup = BeautifulSoup(response.text, 'html.parser')
kurs = soup.find_all("td")

#tworzenie tablicy 2 wymiarowej (5 właściwości - pól, dla 32 walut pobranych ze strony i 1 dla PLN)
currencyRate = [None]*33
k = 0

#pętla tworząca dwuwymiarową tablicę z danymi
for i in range(len(currencyRate)-1):
    oneCurrency = []
    for j in range(5):
        dataComma = kurs[k + j].text
        #na stronie liczby zapisane są ze znakiem ',' przez co należy wymienić te znaki na "." aby Python rozpoznawał je jako liczby a nie napisy, aby można było wykonywac operacyje arytmetyczne na nich
        dataDot = dataComma.replace(",", ".")
        #pobrane dane ze strony nie mają jednoltej struktury, zawierają się w nich bloki z reklamami itd. Aby pobrać do tabeli tylko interesujące mnie dane użyłam kilku warunków
        if (len(dataDot) == 0):
            oneCurrency.append("-")
        elif (len(dataDot) <= 2):
            oneCurrency.append("-")
            k += 1
        elif (dataDot == '\n\n'):
            k += 1
        else:
            oneCurrency.append(dataDot)

    currencyRate[i] = oneCurrency
    k += 5

#na stronie z których pobierałam dane nie było PLN, dodaje je ręcznie w celu przeliczania
currencyRate[32] = ["złotówka polska", "Polska", "1 PLN", "1", "0"]

#klasa kantor - obsługująca logikę i GUI aplikacji, dziedziczy właściwości i metody z klasy QWidget z  PyQt5
class Cantor(QWidget):
    def __init__(self, parent=None):
        #zwracanie klasy rodzica i wywołanie jego konstrukta
        super().__init__(parent)
        #w metodzie interfejs() stworzone zostało GUI aplikacji
        self.interfejs()

    def interfejs(self):
        self.currentBuingIndex = 0
        self.currentSaleIndex = 0
        #PyQt5 - dodanie etykiet aplikacji
        labelBuying = QLabel("Kupno:", self)
        labelSale = QLabel("Sprzedaż:", self)
        labelAmount = QLabel("Ilość:", self)
        labelRate = QLabel("Aktualne kursy:", self)
        labelRateAmount = QLabel("Po wymianie otrzymasz:", self)

        #Przypisanie dodanych widgetów (etykiet) do układu tabelarycznego QGridLayout
        layoutTable = QGridLayout()
        layoutTable.addWidget(labelBuying, 0, 0)
        layoutTable.addWidget(labelSale, 0, 1)
        layoutTable.addWidget(labelAmount, 0, 2)
        layoutTable.addWidget(labelRate, 0, 4)
        layoutTable.addWidget(labelRateAmount, 3, 0)

        #Przypisanie utworzonego układu do layoutu aplikacji
        self.setLayout(layoutTable)
        #Określenie podstawowych parametrów okna aplikacji
        self.setGeometry(100, 100, 100, 100)
        self.setWindowIcon(QIcon('1.png'))
        self.setWindowTitle("Kantor walutowy")
        self.setStyleSheet("color: #1a1a1a;"
                           "background-color: white;"
                           "selection-color: black;"
                           "selection-background-color: #c9fb0f;"
                           "font: 15px;")

        #PyQt5 - dodanie selectów 
        self.comboBuing = QComboBox()
        self.comboSale = QComboBox()
        #Pętla dodająca do selectów nazwy walut - z tablicy currencyRate
        for i in range(len(currencyRate)):
            self.comboBuing.addItem(currencyRate[i][0])
            self.comboSale.addItem(currencyRate[i][0])
        #Połączenie kliknięcia elementów z metodami
        self.comboBuing.currentIndexChanged.connect(self.selectionBuingChange)
        self.comboSale.currentIndexChanged.connect(self.selectionSaleChange)
        #PyQt5 - dodanie pól edycyjnych 
        self.moneyAmount = QLineEdit()
        self.inputResult = QLineEdit()
        self.inputResult.setToolTip(
            '<b>Wpisz kwotę, którą chcesz wymienić</b>')
        #Dodawanie do układu layoutu stworzonych elementów
        layoutTable.addWidget(self.comboBuing, 1, 0)
        layoutTable.addWidget(self.comboSale, 1, 1)
        layoutTable.addWidget(self.moneyAmount, 1, 2)
        layoutTable.addWidget(self.inputResult, 4, 0)

        #PyQt5 - dodanie przycisków i powiązań ich z metodami
        buttonResult = QPushButton("&OBLICZ", self)
        buttonResult.clicked.connect(self.calculate)
        buttonResult.setStyleSheet("color: black;"
                                   "background-color: #c9fb0f;"
                                   "selection-color: yellow;"
                                   "font: bold 15px;"
                                   "border: 1px solid #c9fb0f;"
                                   "border-radius: 6px;"
                                   "background-color: qlineargradient(x1: 1, y1: 1, x2: 0, y2: 0, stop: 0 #c9fb0f, stop: 1 #a7d108);"
                                   "padding-top: 10px;"
                                   "padding-bottom: 10px;")

        buttonEnd = QPushButton("&Zakończ działanie programu", self)
        buttonEnd.resize(buttonEnd.sizeHint())
        buttonEnd.clicked.connect(self.endAction)
        buttonEnd.setStyleSheet("color: black;"
                                "background-color: #c9fb0f;"
                                "font: bold 15px;"
                                "border: 1px solid #c9fb0f;"
                                "border-radius: 6px;"
                                "background-color: qlineargradient(x1: 1, y1: 1, x2: 0, y2: 0, stop: 0 #c9fb0f, stop: 1 #a7d108);"
                                "padding: 7px;")

        buttonSaveFile = QPushButton("&Zapisz kursy do pliku csv", self)
        buttonSaveFile.clicked.connect(self.saveFile)
        buttonSaveFile.setStyleSheet("color: black;"
                                     "font: bold 15px;"
                                     "border: 1px solid #899cf0;"
                                     "border-radius: 6px;"
                                     "background-color: qlineargradient(x1: 1, y1: 1, x2: 0, y2: 0, stop: 0 #899cf0, stop: 1 #5c76ea);"
                                     "padding: 7px;")

        layoutTableH = QHBoxLayout()
        layoutTableH.addWidget(buttonResult)
        layoutTable.addLayout(layoutTableH, 2, 0, 1, 3)
        layoutTable.addWidget(buttonEnd, 15, 30, 1, 2)
        layoutTable.addWidget(buttonSaveFile, 15, 28, 1, 2)

        #Wyświetlenie okna aplikacji na ekranie
        self.show()

        #PyQt5 - dodanie tabeli z danymi kursów
        self.tableRates = QTableWidget()
        self.tableRates.setRowCount(32)
        self.tableRates.setColumnCount(5)
        #Określenie nazw kolumn tabeli
        self.tableRates.setHorizontalHeaderLabels(
            ['Nazwa waluty', 'Państwo', 'Symbol', 'Średni kurs', 'Zmiana %'])
        #Pętla w pętli dodająca kolejne komórki tabeli z danych umieszczonych w tablicy currencyRate
        for i in range(len(currencyRate)-1):
            for j in range(5):
                self.tableRates.setItem(
                    i, j, QTableWidgetItem(currencyRate[i][j]))
                #Sprawdzanie czy dodawane są wartości z kolumny nr 4 - Zmiana %
                if (j == 4):
                    #sprawdzanie czy zmiana procentowa była >= 0 i kolorowanie  tej komórki na zielono
                    if (float(currencyRate[i][j].replace("%", "")) >= 0):
                        self.tableRates.item(i, j).setBackground(
                            QtGui.QColor(53, 229, 57))
                    #sprawdzanie czy zmiana procentowa była < 0 i kolorowanie  tej komórki na czerwono
                    else:
                        self.tableRates.item(i, j).setBackground(
                            QtGui.QColor(229, 57, 53))

        layoutTable.addWidget(self.tableRates, 1, 4, 10, 28)

    #funkcja selectionBuingChange - przypisuje indeks wybranej waluty kupna
    def selectionBuingChange(self, i):
        self.currentBuingIndex = i
        print("Wybrane waluty:", self.currentBuingIndex, self.currentSaleIndex)

    #funkcja selectionSaleChange - przypisuje indeks wybranej waluty sprzedaży
    def selectionSaleChange(self, i):
        self.currentSaleIndex = i
        print("Wybrane waluty 2:", self.currentBuingIndex, self.currentSaleIndex)

    #funkcja calculate - oblicza ilość gotówki po przewalutowaniu, wykonuje się po kliknięciu przycisku "Oblicz"
    def calculate(self):
        try:
            amount = float(self.moneyAmount.text())
            #zabezpieczenie przed wpisaniem ujemnych danych
            if (amount < 0):
                QMessageBox.warning(self, "Błąd", "Wprowadzono błędne dane! Kwota nie może być mniejsza od 0", QMessageBox.Ok)
            else:
                #niektóre waluty mają mnożnik przy wymianie, gdyż są znacznie większe czy mniejsze od innych, pobieranie go za pomocą split         
                multiplierBase = currencyRate[self.currentSaleIndex][2].split() #dzięki split dane zapisują się w postaci tablicy, na pierwszym miejscu jest mnożnik, a na drugim symbol waluty
                multiplier = int(multiplierBase[0])
                #Obliczanie wpisanej kwoty po przewalutowaniu i zaokrąglanie jej do 2 miejsc po przecinku
                result = round(multiplier * amount * float(currencyRate[self.currentBuingIndex][3]) / float(
                    currencyRate[self.currentSaleIndex][3]), 2)
                #Wyświetlanie w inpucie otrzymanej, przeliczonej kwoty wraz z jej symbolem
                self.inputResult.setText(
                    str(result) + " [" + multiplierBase[1] + "]")
        #zabezpieczenie przed błędnie wpisanymi danymi
        except ValueError:
            QMessageBox.warning(
                self, "Błąd", "Wprowadzono błędne dane! Wpisz kwotę, którą chcesz wymienić w formacie 100.50", QMessageBox.Ok)

    #Funkcja zapisująca plik .csv z aktualnymi kursami
    def saveFile(self):
        #pobieranie daty i aktualnego czasu
        time  = date.today()
        today = str(time)
        now = str(datetime.now())
        hour = [None]
        hour[0] = now
        #otworzenie pliku .csv
        with open('sales'+today+'.csv', 'a+') as csv_file:
            #określenie ustawień dla pliku csv: jego ogranicznika i lineterminator (dzięki lineterminator='\r' dane zapisują się wiersz po wierszu, a  nie robią się przerwy)
            csv_writer = csv.writer(csv_file, delimiter=',', lineterminator='\r')
            #zapis czasu w komórce pliku
            csv_writer.writerow(hour)
            #pętla zapisująca kolejne komórki pliku z danych z tablicy currencyRate
            for i in range(len(currencyRate)-1):
                csv_writer.writerow(currencyRate[i])
        #wyświetlanie komunikatu do użytkownika o zapisaniu pliku
        QMessageBox.information(
                self, "Kantor walut", "Zapisano dane do pliku 'sales"+today+".csv'. Plik znajduje się w głównym folderze programu", QMessageBox.Ok)

    def endAction(self):
        self.close()

    #Funkcja wyświetlajaca komunikat po kliknięciu przycisku zakmniecia programu
    def closeEvent(self, event):
        answear = QMessageBox.question(
            self, 'Komunikat',
            "Czy na pewno koniec?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if answear == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    import sys
    #stworzenie obiektu, który reprezentujuje aplikację
    #Parametry (sys.argv) umożliwiają aplikacji otrzymywanie parametrów z linii poleceń 
    app = QApplication(sys.argv)
    #Instancja klasy 'Cantor' -  czyli tworzenie obiektu reprezentującego okno aplikacji
    window = Cantor()
    #Główna pętla programu, wszystkie zdarzenie systemowe i te wywołane przez użytwkonika programu, przekazywane są do widżetów PyQt5 programu
    #Metoda sys.exit() zapewnia poprawne zakończenie aplikacji i zwracanie informacji o jej stanie
    sys.exit(app.exec_())
