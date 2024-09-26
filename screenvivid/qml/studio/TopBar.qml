import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredHeight: 60

    readonly property color accentColor: "#545EEE"
    readonly property color accentColorLight: "#7778FF"
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
                radius: 8
                gradient: Gradient {
                    GradientStop { position: 0.0; color: exportButton.pressed ? Qt.darker(root.accentColor, 1.4) :
                                                         exportButton.hovered ? Qt.darker(root.accentColor, 1.2) : root.accentColor }
                    GradientStop { position: 1.0; color: exportButton.pressed ? Qt.darker(root.accentColorLight, 1.2) :
                                                         exportButton.hovered ? Qt.darker(root.accentColorLight, 1.1) : root.accentColorLight }
                }
                Behavior on gradient {
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
                    Layout.alignment: Qt.AlignVCenter
                }
            }

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
}