import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredHeight: 60

    readonly property color accentColor: "#545EEE"
    signal exportClicked()

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20

        Item {
            Layout.fillWidth: true
        }

        Button {
            id: exportButton
            text: qsTr("Export")
            Layout.preferredWidth: 120
            Layout.preferredHeight: 50

            background: Rectangle {
                color: exportButton.pressed ? Qt.darker(root.accentColor, 1.2) :
                       exportButton.hovered ? Qt.lighter(root.accentColor, 1.1) : root.accentColor
                radius: 8
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }
            }

            contentItem: RowLayout {
                spacing: 4
                Image {
                    source: "qrc:/resources/icons/export.svg"
                    sourceSize: Qt.size(20, 20)
                    Layout.alignment: Qt.AlignVCenter
                }
                Text {
                    text: exportButton.text
                    color: "#FFFFFF"
                    font.pixelSize: 16
                    Layout.alignment: Qt.AlignVCenter
                }
            }

            onClicked: {
                console.log('click')
                videoController.pause()
                exportDialog.open()
            }
        }
    }
}