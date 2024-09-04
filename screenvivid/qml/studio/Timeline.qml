import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts

// Timeline
Repeater {
    model: Math.ceil(studioWindow.videoLen) + 1

    Item {
        width: studioWindow.fps * studioWindow.pixelsPerFrame
        height: 60
        x: studioWindow.fps * studioWindow.pixelsPerFrame * index
        // y: 10

        readonly property int timeLabelWidth: 20

        Item {
            width: parent.timeLabelWidth
            height: parent.height

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                Item {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }

                Label {
                    Layout.alignment: Qt.AlignCenter
                    text: qsTr("" + index)
                }

                Item {
                    Layout.alignment: Qt.AlignCenter

                    Rectangle {
                        width: 4
                        height: 4
                        radius: 2
                        color: "white"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }
            }
        }
        MouseArea {
            anchors.fill: parent
            onClicked: {
                var xPos = Math.max(
                            0,
                            studioWindow.fps * studioWindow.pixelsPerFrame * index + mouseX
                            - parent.timeLabelWidth / 2)
                var currentFrame = Math.round(
                            xPos / studioWindow.pixelsPerFrame)
                videoController.jump_to_frame(
                            currentFrame)
            }
        }
    }
}