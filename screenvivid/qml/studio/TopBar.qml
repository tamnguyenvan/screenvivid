import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

RowLayout {
    Layout.fillWidth: true
    Layout.maximumHeight: 50
    Layout.topMargin: 4
    Layout.bottomMargin: 4

    Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
    }

    Button {
        icon.source: "qrc:/resources/icons/export.svg"
        text: qsTr("Export")
        // Material.background: "#4329F4"
        // Material.foreground: "white"
        Material.background: studioWindow.accentColor

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor

            onPressed: {
                videoController.pause()
                exportDialog.open()
            }
        }
    }
}