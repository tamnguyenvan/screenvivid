import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredHeight: 120

    property int selectedSize: 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Image {
                source: "qrc:/resources/icons/cursor.svg"
                sourceSize: Qt.size(24, 24)
                Layout.alignment: Qt.AlignVCenter
            }

            Label {
                text: qsTr("Cursor")
                font.pixelSize: 18
                font.weight: Font.Medium
                color: "#FFFFFF"
            }
        }

        Label {
            text: qsTr("Size")
            font.pixelSize: 14
            color: "#AAAAAA"
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Repeater {
                model: ["1x", "1.5x", "2x", "3x"]

                delegate: Button {
                    text: modelData
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40

                    background: Rectangle {
                        color: root.selectedSize === index ? "#3A3F4B" : "#222529"
                        radius: 8
                    }

                    contentItem: Text {
                        text: modelData
                        color: root.selectedSize === index ? "#FFFFFF" : "#AAAAAA"
                        font.pixelSize: 14
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        root.selectedSize = index
                        videoController.cursor_scale = parseFloat(modelData.replace("x", ""))
                        if (!isPlaying) {
                            videoController.get_current_frame()
                        }
                    }
                }
            }
        }
    }
}