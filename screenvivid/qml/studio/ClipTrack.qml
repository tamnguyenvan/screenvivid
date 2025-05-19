import QtQuick 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls 6.7

FocusScope {
    id: root
    implicitWidth: 100
    implicitHeight: 60

    signal positionChanged(real x)
    signal leftMouseClicked(real clickX)
    signal rightMouseClicked(real clickX)

    property int resizeHandleWidth: 10
    property bool resizing: false
    property real clipLen: 0
    property int originalWidth: 0

    readonly property string borderColor: "#e8eaed"
    readonly property int borderWidth: 2
    readonly property int borderRadius: 10
    readonly property string backgroundColor: "#7778ff"
    readonly property string stripColor: "#545eee"

    Behavior on x {
        NumberAnimation {
            duration: 2000
            easing.type: Easing.OutQuad
        }
    }

    Rectangle {
        id: clipTrackRect
        anchors.fill: parent
        radius: borderRadius
        color: root.backgroundColor

        Rectangle {
            width: parent.width - 2 * root.resizeHandleWidth
            height: parent.height
            x: root.resizeHandleWidth
            y: 0
            color: root.stripColor

            ColumnLayout {
                anchors.fill: parent
                spacing: 2

                // First row
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height / 2 - 1
                    clip: true

                    RowLayout {
                        anchors.centerIn: parent
                        width: Math.min(parent.width, implicitWidth)
                        spacing: 4

                        Image {
                            source: "qrc:/resources/icons/clip.svg"
                            Layout.preferredWidth: 16
                            Layout.preferredHeight: 16
                        }
                        Label {
                            text: qsTr("Clip")
                            elide: Text.ElideRight
                        }
                    }
                }

                // Second row
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height / 2 - 1
                    clip: true

                    RowLayout {
                        anchors.centerIn: parent
                        width: Math.min(parent.width, implicitWidth)
                        spacing: 4

                        Image {
                            source: "qrc:/resources/icons/zoom.svg"
                            Layout.preferredWidth: 16
                            Layout.preferredHeight: 16
                        }
                        Label {
                            text: clipLen.toFixed(1) + "s"
                            elide: Text.ElideRight
                        }
                        Image {
                            source: "qrc:/resources/icons/clock.svg"
                            Layout.preferredWidth: 16
                            Layout.preferredHeight: 16
                        }
                        Label {
                            text: qsTr("1x")
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            radius: root.borderRadius
            border.width: root.borderWidth
            border.color: root.focus ? root.borderColor : "transparent"
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton

            function highlight() {
                root.focus = true
            }

            onClicked: event => {
                if (event.button === Qt.LeftButton) {
                    root.leftMouseClicked(mouseX)
                    highlight()
                } else if (event.button == Qt.RightButton) {
                    root.rightMouseClicked(mouseX)
                    highlight()
                    menu.popup(mouseX, mouseY)
                }
            }
        }
        Menu {
            id: menu
            width: 200

            background: Rectangle {
                implicitWidth: 200
                implicitHeight: 40
                color: "#2C2C2C"
                border.color: "#3A3A3A"
                radius: 8
            }

            MenuItem {
                id: deleteMenuItem
                width: parent.width
                height: 40

                contentItem: Row {
                    spacing: 10
                    leftPadding: 10

                    Image {
                        source: "qrc:/resources/icons/trash.svg"
                        width: 16
                        height: 16
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: qsTr("Delete")
                        color: deleteMenuItem.highlighted ? "#FFFFFF" : "#CCCCCC"
                        font.pixelSize: 14
                        font.weight: Font.Medium
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                background: Rectangle {
                    color: deleteMenuItem.highlighted ? "#4A4A4A" : "transparent"
                    radius: 4
                }

                onTriggered: {
                    if (clipTrackModel.rowCount() === 1) {
                        return
                    }
                    if (index === 0) {
                        var startFrame = parseInt(clipTrackModel.get_clip(index).width / studioWindow.pixelsPerFrame)
                        videoController.trim_left(startFrame)
                        videoController.jump_to_frame(0)
                    } else if (index === clipTrackModel.rowCount() - 1) {
                        const clipTrack = clipTrackModel.get_clip(index)
                        var relativeEndFrame = clipTrack.x / studioWindow.pixelsPerFrame
                        var endFrame = videoController.start_frame + relativeEndFrame
                        videoController.trim_right(endFrame)
                        videoController.jump_to_frame(Math.max(0, relativeEndFrame - 5))
                    }
                    clipTrackModel.delete_clip(index)
                }
            }
        }
    }

    Component.onCompleted: {
        originalWidth = width
    }
}
