from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, os, re

from datetime import datetime, timedelta

import json
import pandas as pd

from mylib.extendedCombo import ExtendedComboBox
from mylib.table import MyTable, Table
from mylib.webScraping import WebScraper

with open('config.json','r') as f:
	CONFIG = json.load(f)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Alipio Motos'
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']

		self._MAIN_WINDOW_LAYOUT = '''
			background-color: #3F3B93;
		'''

		self.now = datetime.now()

		self.filter = {}

		self.ws = WebScraper()

		self.setupUI()


	def setupUI(self):
		#Main Window Layout
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)
		self.setWindowTitle(self.title)
		self.setFixedSize(self.width, self.height)

		#Main Layout
		self.layout = QHBoxLayout()
		self.layout.setContentsMargins(5, 5, 5, 5)
		self.setLayout(self.layout)


		#Left Side
		#Left Side Layout
		self.left_layout = QVBoxLayout()
		self.layout.addLayout(self.left_layout)

		#Log
		self.table_model()

		#Buttons for Log
		self.label = QLabel(self)
		self.left_layout.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
		self.label.setMinimumWidth(int(self.width*0.6))
		self.label.setMinimumHeight(int(self.height*0.8))
		self.label.setStyleSheet('QLabel{background-color: green}')

		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())