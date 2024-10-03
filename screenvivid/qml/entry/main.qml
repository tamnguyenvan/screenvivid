import QtQuick
import QtQuick.Window
import QtQuick.Controls.Material

Window {
    id: mainWindow
    width: Screen.desktopAvailableWidth
    height: Screen.desktopAvailableHeight
    visible: true
    color: "transparent"
    title: qsTr("ScreenVivid")

    Component.onCompleted: {
        logger.debug("Getting window position")
        windowController.get_window_position()
        screenvivid.source = ""
        screenvivid.source = "qrc:/qml/entry/ScreenVivid.qml"
        mainWindow.hide()
        logger.debug("Hide initial window and open control window")
    }

    Loader { id: screenvivid }
}