import QtQuick
import QtQuick.Window
import QtQuick.Controls.Material

Window {
    id: mainWindow
    width: Screen.desktopAvailableWidth
    height: Screen.desktopAvailableHeight
    visible: true
    color: "transparent"

    Component.onCompleted: {
        windowController.get_window_position()
        screenvivid.source = ""
        screenvivid.source = "qrc:/qml/entry/ScreenVivid.qml"
        mainWindow.hide()
    }

    Loader { id: screenvivid }
}