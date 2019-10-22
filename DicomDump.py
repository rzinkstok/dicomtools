from PySide2 import QtCore, QtGui, QtWidgets
import pydicom
import sys


class DicomDumpApp(QtWidgets.QMainWindow):
	def __init__(self, dcmfile=None):
		super(DicomDumpApp, self).__init__()
		self.createInterface()
		self.filename = dcmfile
		self.dataset = None
		self.ancestors = []
		self.searchresults = []
		self.currentsearchresult = None

		if self.filename:
			self.openFile()
		
	def createInterface(self):
		self.resize(1280,800)
		self.setWindowTitle('DicomDump')
		
		mainframe = QtWidgets.QFrame()
		mainlayout = QtWidgets.QVBoxLayout()
		
		slayout = QtWidgets.QHBoxLayout()
		
		openbutton = QtWidgets.QPushButton("Open...")
		openbutton.clicked.connect(self.getFileName)
		slayout.addWidget(openbutton)
		
		slayout.addStretch(1)
		
		slayout.addWidget(QtWidgets.QLabel("Search:"))
		
		self.slineedit = QtWidgets.QLineEdit()
		self.slineedit.setMaximumWidth(500)
		self.slineedit.textChanged.connect(self.search)
		slayout.addWidget(self.slineedit)
		
		prevb = QtWidgets.QPushButton("<")
		prevb.clicked.connect(self.prevResult)
		slayout.addWidget(prevb)
		
		self.sresultlabel = QtWidgets.QLabel("- / -")
		self.sresultlabel.setMinimumWidth(50)
		self.sresultlabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
		slayout.addWidget(self.sresultlabel)
		
		nextb = QtWidgets.QPushButton(">")
		nextb.clicked.connect(self.nextResult)
		slayout.addWidget(nextb)
		
		self.includevalue = QtWidgets.QCheckBox("include value")
		self.includevalue.stateChanged.connect(self.toggleIncludeValue)
		slayout.addWidget(self.includevalue)
		
		slayout.addStretch(1)
		
		savebutton = QtWidgets.QPushButton("Save as txt...")
		savebutton.clicked.connect(self.save)
		slayout.addWidget(savebutton)
		qbutton = QtWidgets.QPushButton("Quit")
		qbutton.clicked.connect(QtCore.QCoreApplication.instance().quit)
		slayout.addWidget(qbutton)
				
		mainlayout.addLayout(slayout)
		
		self.dicomtree = QtWidgets.QTreeWidget()
		self.dicomtree.setColumnCount(6)
		self.dicomtree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		self.dicomtree.setHeaderLabels(["Tree structure", "Tag", "Description", "VR", "VM", "Value"])
		self.dicomtree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		
		mainlayout.addWidget(self.dicomtree)
		
		mainframe.setLayout(mainlayout)
		self.setCentralWidget(mainframe)
		
		self.center()
		self.show()

	def center(self):
		qr = self.frameGeometry()
		QtWidgets.QDesktopWidget()
		cp = QtWidgets.QDesktopWidget().availableGeometry(self).center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
		
	def getFileName(self):
		self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open DICOM file', '.')[0]
		if self.filename:
			self.openFile()
		
	def openFile(self):
		self.dicomtree.clear()
		self.dataset = None
		try:
			self.dataset = pydicom.read_file(self.filename, force=True)
		except pydicom.filereader.InvalidDicomError:
			self.messageBox('Error', 'Invalid DICOM file', self.filename + ' is not a valid DICOM file!')
			self.filename = None
			self.setWindowTitle('DicomDump')
			return
		
		self.setWindowTitle('DicomDump: '+self.filename)
		self.loadTree()
		
	def loadTree(self):
		self.dataset.decode()
		
		metainfoitem = QtWidgets.QTreeWidgetItem()
		metainfoitem.setText(0, 'Metadata')
		datasetitem = QtWidgets.QTreeWidgetItem()
		datasetitem.setText(0, 'Dataset')
		
		self.ancestors = []
		self.ancestors.append(metainfoitem)
		self.handleDataset(self.dataset.file_meta)
		self.dicomtree.addTopLevelItem(metainfoitem)
		self.ancestors = []
		
		self.ancestors.append(datasetitem)
		self.handleDataset(self.dataset)
		self.dicomtree.addTopLevelItem(datasetitem)
		
		self.dicomtree.expandAll()
		
	def handleDataset(self, ds):
		for de in ds:
			tagitem = self.addTag(de)
			
			if de.VR == "SQ":
				self.ancestors.append(tagitem)
				self.handleSequence(de.value)
				self.ancestors.pop()
	
	def handleSequence(self, sq):
		for ds in sq:
			self.ancestors.append(self.addTag())
			self.handleDataset(ds)
			self.ancestors.pop()
		
	def addTag(self, de=None):
		tagitem = QtWidgets.QTreeWidgetItem()
		
		if not de:
			tagitem.setText(0, 'item')
			self.ancestors[-1].addChild(tagitem)
			return tagitem

		tagitem.setText(1, str(de.tag).replace(" ", ""))
		tagitem.setText(2, str(de.description()))
		tagitem.setText(3, str(de.VR))
		tagitem.setText(4, str(de.VM))
		if de.VR != "SQ":
			tagitem.setText(5, str(de.value))
			tagitem.setText(0, "element")
		else:
			tagitem.setText(5, "Sequence of length "+str(len(de.value)))
			tagitem.setText(0, "sequence")
			
		if len(self.ancestors) == 0:
			self.dicomtree.addTopLevelItem(tagitem)
		else:
			self.ancestors[-1].addChild(tagitem)
		return tagitem	
	
	def search(self, s):
		self.dicomtree.clearSelection()
		self.currentsearchresult = 0
		self.searchresults = None
		
		if len(s) < 2:
			self.sresultlabel.setText("- / -")
			return
		
		flags = QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive
		
		self.searchresults = self.dicomtree.findItems(s, flags, 0)
		self.searchresults.extend(self.dicomtree.findItems(s, flags, 1))
		self.searchresults.extend(self.dicomtree.findItems(s, flags, 2))
		self.searchresults.extend(self.dicomtree.findItems(s, flags, 3))
		if self.includevalue.isChecked():
			self.searchresults.extend(self.dicomtree.findItems(s, flags, 5))
		
		if len(self.searchresults) > 0:
			self.sresultlabel.setText("%d/%d" % (self.currentsearchresult+1, len(self.searchresults)))
			self.currentsearchresult = 0
			self.searchresults[self.currentsearchresult].setSelected(True)
			self.dicomtree.scrollTo(self.dicomtree.indexFromItem(self.searchresults[self.currentsearchresult]))
		else:
			self.sresultlabel.setText("%d/%d" % (0, len(self.searchresults)))
	
	def prevResult(self):
		if not self.searchresults:
			return
		self.searchresults[self.currentsearchresult].setSelected(False)
		if self.currentsearchresult == 0:
			self.currentsearchresult = len(self.searchresults)-1
		else:
			self.currentsearchresult -= 1
		self.searchresults[self.currentsearchresult].setSelected(True)
		self.dicomtree.scrollTo(self.dicomtree.indexFromItem(self.searchresults[self.currentsearchresult]))
		self.sresultlabel.setText("%d/%d" % (self.currentsearchresult+1, len(self.searchresults)))
		
	def nextResult(self):
		if not self.searchresults:
			return
		self.searchresults[self.currentsearchresult].setSelected(False)
		if self.currentsearchresult == len(self.searchresults)-1:
			self.currentsearchresult = 0
		else:
			self.currentsearchresult += 1
		self.searchresults[self.currentsearchresult].setSelected(True)
		self.dicomtree.scrollTo(self.dicomtree.indexFromItem(self.searchresults[self.currentsearchresult]))
		self.sresultlabel.setText("%d/%d" % (self.currentsearchresult+1, len(self.searchresults)))
		
	def toggleIncludeValue(self, i):
		self.search(self.slineedit.text())
	
	def messageBox(self, type, title, text, inftext=None):
		msgbox = QtWidgets.QMessageBox()
		msgbox.setWindowTitle(title)
		msgbox.setText(text)
		if inftext is not None:
			msgbox.setInformativeText(inftext)
		if type == "information":
			icon = QtWidgets.QMessageBox.Information
		elif type == "warning":
			icon = QtWidgets.QMessageBox.Warning
		elif type == "error":
			icon = QtGui.QMessageBox.Critical
		else:
			icon = QtWidgets.QMessageBox.Information
		msgbox.setIcon(icon)
		msgbox.exec_()			
	
	def getDepth(self, item):
		depth = 0
		while item:
			depth += 1
			item = item.parent()
		return depth

	def save(self):
		fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file as...', '.')[0]
		if not fn:
			return
		fp = open(fn, 'w')
		twis = QtWidgets.QTreeWidgetItemIterator(self.dicomtree)
		while twis.value():
			twi = twis.value()
			tabstring = "\t"*(self.getDepth(twi)-1)
			fp.write(tabstring)
			for i in range(twi.columnCount()):
				fp.write(twi.text(i))
				if i != twi.columnCount()-1:
					fp.write("\t")
				else:
					fp.write("\n")
			twis += 1
		fp.close()
		self.messageBox('information', 'Save successful', 'Data written to '+fn)
		

if __name__ == "__main__":
	if len(sys.argv) == 2:
		dcmfile = sys.argv[1]
	else:
		dcmfile = None

	app = QtWidgets.QApplication(sys.argv)

	ddapp = DicomDumpApp(dcmfile)
	sys.exit(app.exec_())
