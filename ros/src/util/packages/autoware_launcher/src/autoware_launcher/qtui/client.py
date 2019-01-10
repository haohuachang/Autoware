from python_qt_binding import QtCore
from python_qt_binding import QtWidgets

from ..core  import console
from ..core  import fspath
from .guimgr import AwQtGuiManager
from .mirror import AwLaunchTreeMirror

# For Gui Manager
from .window     import AwMainWindow
from .treeview   import AwTreeViewPanel
from .treeview   import AwControlPanel
from .procmgr    import AwProcessPanel
from .summary    import AwSummaryPanel
from .network    import AwTcpServerPanel
from .starter    import AwStarterPanel
from .simulation import AwSimulationWidget


class AwQtGuiClient(object):

    def __init__(self, sysarg, server):
        self.__sysarg = sysarg
        self.__panels = []
        self.__guimgr = AwQtGuiManager(self)
        self.__mirror = AwLaunchTreeMirror(self)

        self.__server = server
        self.__server.register_client(self)

    def guimgr(self):
        return self.__guimgr

    def select_config(self, lpath): # ToDo: consider moving to guimgr
        self.__treeview.select_config(lpath)



    def start2(self):

        application = QtWidgets.QApplication(self.__sysarg)
        resolution = application.desktop().screenGeometry()
        resolution = min(resolution.width(), resolution.height())

        stylesheet = []
        stylesheet.append("#FrameHeader { border-top: 1px solid; } #FrameHeader, #FrameWidget { padding: 5px; border-bottom: 1px solid; border-left: 1px solid; border-right: 1px solid; }")
        stylesheet.append("* { font-size: " + str(resolution/100) + "px; }")
        application.setStyleSheet(" ".join(stylesheet))

        self.__treeview   = AwTreeViewPanel(self) # ToDo: consider moving to guimgr
        self.__control    = AwControlPanel(self)  # ToDo: consider moving to guimgr
        self.__summary    = AwSummaryPanel(self)  # ToDo: consider moving to guimgr
        self.__process    = AwProcessPanel(self)  # ToDo: consider moving to guimgr
        self.__network    = AwTcpServerPanel()
        self.__starter    = AwStarterPanel(self)
        self.__simulation = AwSimulationWidget(self.__guimgr)

        tabwidget = QtWidgets.QTabWidget()
        tabwidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        tabwidget.addTab(self.__summary, "Summary")
        tabwidget.addTab(self.__process, "Process")

        #vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vsplitter = QtWidgets.QWidget()
        vsplitter.setLayout(QtWidgets.QVBoxLayout())
        vsplitter.layout().setContentsMargins(0, 0, 0, 0)
        vsplitter.layout().setSpacing(0)
        vsplitter.layout().addWidget(self.__treeview)
        vsplitter.layout().addWidget(self.__control)

        hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        hsplitter.addWidget(vsplitter)
        hsplitter.addWidget(tabwidget)

        mainwidget = QtWidgets.QTabWidget()
        mainwidget.addTab(hsplitter,      "Details")
        mainwidget.addTab(self.__starter, "Starter")
        mainwidget.addTab(self.__network, "Network")

        mainsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        mainsplitter.addWidget(self.__simulation)
        mainsplitter.addWidget(mainwidget)

        #dock = QtWidgets.QDockWidget()
        #dock.setWidget( )
        #window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

        window = AwMainWindow(self)
        window.setCentralWidget(mainsplitter)
        window.show()

        self.__server.register_runner(self.__process)
        self.__process.register_server(self.__server)

        self.__server.register_client(self.__network)
        self.__network.register_server(self.__server)

        self.__panels.append(self.__treeview)
        self.__panels.append(self.__summary)
        self.__panels.append(self.__process)
        #self.__panels.append(self.__control)

        self.__treeview.register_select_listener(self.__summary)
        self.__treeview.register_select_listener(self.__process)
        self.__treeview.register_select_listener(self.__control)

        self.__server.make_profile("root/default")
        return application.exec_()



    def profile_updated(self):
        self.__mirror.clear()
        for panel in self.__panels: panel.profile_cleared()

        for lpath in self.__server.list_node():
            lnode = self.__mirror.create(lpath)
            for panel in self.__panels: panel.config_created(lnode)

        self.__treeview.expandAll()
        #self.__treeview.expandToDepth(0)

    def node_created(self, lpath):
        print "node_created: " + lpath
        lnode = self.__mirror.create(lpath)
        for panel in self.__panels: panel.config_created(lnode)

        lpath = fspath.parentpath(lpath)
        while lpath:
            print "node_updated: " + lpath
            self.__mirror.clear(lpath)
            self.__summary.node_updated(lpath)
            lpath = fspath.parentpath(lpath)

    def node_updated(self, lpath):
        while lpath:
            print "node_updated: " + lpath
            self.__mirror.clear(lpath)
            self.__summary.node_updated(lpath)
            lpath = fspath.parentpath(lpath)

    def status_updated(self, lpath, state):
        print "status_updated:" + lpath + " " + str(state)
        self.__treeview.status_updated(lpath, state)



    def save_profile(self, fpath):
        self.__server.save_profile(fpath)

    def load_profile(self, fpath):
        self.__server.load_profile(fpath)

    def find_node(self, lpath):
        return self.__server.find_node(lpath)

    def launch_config(self, lpath, xmode):
        return self.__server.launch_node(lpath, xmode)

    def create_node(self, lpath, ppath):
        return self.__server.create_node(lpath, ppath)

    def update_node(self, lpath, ldata):
        return self.__server.update_node(lpath, ldata)


