import QtQuick
import QtQuick.Controls

Rectangle {
    id: videoEdit
    color: "#131519"
    radius: 4

    ScrollView {
        anchors.fill: parent
        contentWidth: studioWindow.fps * studioWindow.videoLen * studioWindow.pixelsPerFrame + 200
        contentHeight: parent.height

        Item {
            width: parent.contentWidth
            height: videoEdit.height
            anchors.left: parent.left
            anchors.leftMargin: 20

            Timeline {}

            // Clip tracks
            Item {
                id: tracks
                width: parent.width
                height: 60
                y: 75
                anchors.left: parent.left
                anchors.leftMargin: 10

                Repeater {
                    model: clipTrackModel

                    ClipTrack {
                        x: modelData.x
                        height: 60
                        width: modelData.width
                        clipLen: modelData.clip_len

                        onLeftMouseClicked: function (mouseX) {
                            // Update the frame
                            var targetFrame = Math.round(
                                        (x + mouseX) / studioWindow.pixelsPerFrame)
                            videoController.jump_to_frame(targetFrame)

                            clipTrackModel.set_cut_clip_data(index, mouseX)
                        }
                    }
                }
            }

            TimeSlider {
                id: timeSlider
            }
        }
    }
}