import QtQuick
import QtQuick.Controls

Item {
    id: timeSlider
    width: 20
    height: 220

    property string color: "#484554"

    Rectangle {
        id: timeSliderHead
        width: parent.width
        height: parent.width
        radius: parent.width / 2

        color: parent.color

        MouseArea {
            anchors.fill: parent

            drag {
                target: timeSlider
                axis: Drag.XAxis
                smoothed: true
                minimumX: 0
            }

            onReleased: {
                var currentFrame = Math.round(
                            timeSlider.x / studioWindow.pixelsPerFrame)
                videoController.jump_to_frame(currentFrame)
            }
        }
    }

    Rectangle {
        id: timeSliderBody
        width: 3
        height: parent.height
        anchors.horizontalCenter: parent.horizontalCenter
        color: parent.color
    }

    Connections {
        target: videoController
        function onCurrentFrameChanged(currentFrame) {
            timeSlider.x = currentFrame * studioWindow.pixelsPerFrame
        }
    }
}
