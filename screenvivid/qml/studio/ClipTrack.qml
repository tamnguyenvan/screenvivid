import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

FocusScope {
    id: clipTrack
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
        radius: 10
        color: clipTrack.backgroundColor
        border.width: clipTrack.borderWidth
        border.color: "transparent"

        Rectangle {
            width: parent.width - 2 * clipTrack.resizeHandleWidth
            height: parent.height
            x: clipTrack.resizeHandleWidth
            y: 0
            color: clipTrack.stripColor

            ColumnLayout {
                anchors.fill: parent
                Layout.alignment: Qt.AlignHCenter
                Layout.margins: 4
                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    Image {
                        source: "qrc:/resources/icons/clip.svg"
                    }
                    Label {
                        text: qsTr("Clip")
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 10

                    RowLayout {
                        Image {
                            source: "qrc:/resources/icons/zoom.svg"
                        }

                        Label {
                            text: clipLen.toFixed(1) + "s"
                        }

                        Image {
                            source: "qrc:/resources/icons/clock.svg"
                        }

                        Label {
                            text: qsTr("1x")
                        }
                    }
                }
            }
        }

        // Top border
        Rectangle {
            id: topEdge
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: resizeHandleWidth
            width: parent.width - 2 * resizeHandleWidth
            height: clipTrack.borderWidth
            color: "transparent"
        }

        // Bottom border
        Rectangle {
            id: bottomEdge
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: resizeHandleWidth
            width: parent.width - 2 * resizeHandleWidth
            height: clipTrack.borderWidth
            color: "transparent"
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton

            function highlight() {
                clipTrack.focus = true
                topEdge.color = clipTrack.borderColor
                bottomEdge.color = clipTrack.borderColor
                clipTrackRect.border.color = clipTrack.borderColor
            }

            onClicked: event => {
                if (event.button === Qt.LeftButton) {
                    clipTrack.leftMouseClicked(mouseX)
                    highlight()
                } else if (event.button == Qt.RightButton) {
                    clipTrack.rightMouseClicked(mouseX)
                    highlight()
                    menu.popup(mouseX, mouseY)
                }
            }
        }

        Menu {
            id: menu
            MenuItem {
                text: "Delete"
                onTriggered: {
                    if (index === 0) {
                        var startFrame = parseInt(clipTrackModel.get_clip(index).width / studioWindow.pixelsPerFrame)
                        videoController.trim_left(startFrame)
                    } else if (index === clipTrackModel.rowCount() - 1) {
                        const clipTrack = clipTrackModel.get_clip(index)
                        var endFrame = clipTrack.x / studioWindow.pixelsPerFrame
                        videoController.trim_right(endFrame)
                    }
                    clipTrackModel.delete_clip(index)
                }
            }
        }

    }

    onFocusChanged: {
        if (!clipTrack.focus) {
            topEdge.color = "transparent"
            bottomEdge.color = "transparent"
            clipTrackRect.border.color = "transparent"
        }
    }

    Component.onCompleted: {
        originalWidth = width
    }
}
