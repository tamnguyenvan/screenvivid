import QtQuick 6.7
import QtQuick.Controls 6.7

Rectangle {
    id: videoEdit
    color: "#131519"
    radius: 4

    property bool animationEnabled: true

    Flickable {
        id: scrollView
        anchors.fill: parent
        contentWidth: studioWindow.fps * studioWindow.videoLen * studioWindow.pixelsPerFrame + 200
        contentHeight: parent.height
        property real currentScrollX: 0

        Behavior on contentX {
            enabled: !isPlaying
            NumberAnimation {
                duration: 400
                easing.type: Easing.InOutQuad
            }
        }

        Item {
            width: parent.contentWidth
            height: videoEdit.height
            anchors.left: parent.left
            anchors.leftMargin: 20

            Timeline {}

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
                            timeSlider.animationEnabled = false
                            var targetFrame = Math.round(
                                        (x + mouseX) / studioWindow.pixelsPerFrame)
                            videoController.jump_to_frame(targetFrame)
                            clipTrackModel.set_cut_clip_data(index, mouseX)
                            timeSlider.animationEnabled = true
                        }
                    }
                }
            }

            TimeSlider {
                id: timeSlider
                onXChanged: {
                    var timeSliderGlobalX = timeSlider.mapToItem(scrollView, timeSlider.x, 0).x
                    var viewportWidth = scrollView.width
                    var threshold = viewportWidth * 0.85

                    // Kiểm tra xem timeSlider có vượt quá ngưỡng bên phải không
                    if (timeSliderGlobalX > threshold) {
                        // Tính toán vị trí mới cho contentX để giữ timeSlider trong tầm nhìn
                        var newContentX = timeSlider.x - (viewportWidth * 0.5)
                        // Đảm bảo contentX không vượt quá giới hạn
                        newContentX = Math.min(newContentX, scrollView.contentWidth - viewportWidth)
                        newContentX = Math.max(0, newContentX)
                        scrollView.contentX = newContentX
                    }

                    // Kiểm tra xem timeSlider có vượt quá ngưỡng bên trái không
                    var leftThreshold = viewportWidth * 0.15
                    if (timeSliderGlobalX < leftThreshold) {
                        var newContentX = timeSlider.x - (viewportWidth * 0.5)
                        newContentX = Math.max(0, newContentX)
                        scrollView.contentX = newContentX
                    }
                }
            }
        }
    }

    Connections {
        target: videoController
        function onPlayingChanged(playing) {
            if (!playing) {
                animationEnabled = true
            }
        }
    }
}