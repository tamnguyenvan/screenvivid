import QtQuick
import QtQuick.Window
import QtQuick.Dialogs
import QtQuick.Controls.Material
import QtQuick.Layouts

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    Rectangle {
        anchors.fill: parent
        radius: 4
        clip: true
        color: "#131519"
        Image {
            id: videoPreview
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
            onStatusChanged: {
                if (status === Image.Error) {
                    console.error("Error loading image:", source)
                }
            }
        }
    }

    // Full screen button
    ToolButton {
        id: fullScreenButton
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 0
        icon.source: "qrc:/resources/icons/full_screen.svg"
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onPressed: {
                fullScreenWindow.showFullScreen()
            }
        }
    }

    // Full screen window
    Window {
        id: fullScreenWindow
        width: Screen.width
        height: Screen.height
        flags: Qt.Window | Qt.FramelessWindowHint
        visible: false

        readonly property string accentColor: "#e85c0d"
        Material.theme: Material.Dark
        Material.primary: accentColor
        Material.accent: accentColor

        Item {
            anchors.fill: parent
            focus: true

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onPositionChanged: {
                    controlBar.visible = true
                    hideControlBarTimer.restart()
                }
            }

            Image {
                id: fullScreenImage
                anchors.fill: parent
                source: videoPreview.source
                fillMode: Image.PreserveAspectFit
                anchors.centerIn: parent
            }

            // The progress bar and controls
            Rectangle {
                id: controlBar
                width: parent.width - 4
                height: 80
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                visible: false
                color: "#3c3c3c"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onPositionChanged: {
                        controlBar.visible = true
                        hideControlBarTimer.restart()
                    }
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 4

                    RowLayout {
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1

                        Text {
                            id: elapsedTime
                            text: qsTr("00:00")
                            color: "#fff"
                        }

                        Slider {
                            id: fullScreenTimeSlider
                            from: 0
                            to: 100
                            value: 0
                            Layout.fillWidth: true
                            Layout.preferredHeight: 12
                            onMoved: {
                                var currentFrame = parseInt(value * videoController.total_frames * 0.01)
                                videoController.jump_to_frame(currentFrame)
                            }
                        }

                        Text {
                            id: totalTime
                            text: qsTr("00:00")
                            color: "#fff"
                        }
                    }

                    RowLayout {
                        Layout.fillHeight: true
                        Layout.fillWidth: true

                        Layout.preferredHeight: 1

                        Item {
                            Layout.fillHeight: true
                            Layout.fillWidth: true
                        }

                        ToolButton {
                            icon.source: "qrc:/resources/icons/prev.svg"
                            icon.color: "#e8eaed"
                            onClicked: {
                                controlBar.visible = true
                                hideControlBarTimer.restart()
                                videoController.prev_frame()
                            }
                        }
                        ToolButton {
                            icon.source: isPlaying ? "qrc:/resources/icons/pause.svg" : "qrc:/resources/icons/play.svg"
                            icon.color: "#e8eaed"
                            onClicked: {
                                controlBar.visible = true
                                hideControlBarTimer.restart()
                                videoController.toggle_play_pause()
                            }
                        }
                        ToolButton {
                            icon.source: "qrc:/resources/icons/next.svg"
                            icon.color: "#e8eaed"
                            onClicked: {
                                videoController.next_frame()
                                controlBar.visible = true
                                hideControlBarTimer.restart()
                            }
                        }
                        Item {
                            Layout.fillHeight: true
                            Layout.fillWidth: true

                            ToolButton {
                                anchors.right: parent.right
                                icon.source: "qrc:/resources/icons/full_screen_exit.svg"
                                icon.color: "#e8eaed"
                                onClicked: {
                                    fullScreenWindow.hide()
                                }
                            }
                        }
                    }
                }
            }

            Timer {
                id: hideControlBarTimer
                interval: 2000
                repeat: false
                onTriggered: controlBar.visible = false
            }

            Keys.onPressed: event => {
                if (event.key === Qt.Key_Escape) {
                    fullScreenWindow.hide()
                } else if (event.key === Qt.Key_F) {
                    fullScreenWindow.hide()
                } else if (event.key === Qt.Key_Space) {
                    videoController.toggle_play_pause()
                    controlBar.visible = true
                    hideControlBarTimer.restart()
                } else if (event.key === Qt.Key_Left) {
                    videoController.prev_frame()
                    controlBar.visible = true
                    hideControlBarTimer.restart()
                } else if (event.key === Qt.Key_Right) {
                    videoController.next_frame()
                    controlBar.visible = true
                    hideControlBarTimer.restart()
                }
            }
        }

        Connections {
            target: videoController
            function onCurrentFrameChanged(currentFrame) {
                var progress = 100 * currentFrame / videoController.total_frames
                fullScreenTimeSlider.value = progress

                 // Update elapsed time
                var elapsedSeconds = currentFrame / videoController.fps
                elapsedTime.text = formatTime(elapsedSeconds)

                // Update total time
                var totalSeconds = videoController.total_frames / videoController.fps
                totalTime.text = formatTime(totalSeconds)
            }

            function formatTime(seconds) {
                var minutes = Math.floor(seconds / 60)
                var remainingSeconds = Math.floor(seconds % 60)
                return String(minutes).padStart(2, '0') + ":" + String(remainingSeconds).padStart(2, '0')
            }
        }
    }

    Connections {
        target: videoController
        function onFrameReady(frame) {
            videoPreview.source = "image://frames/frame?" + Date.now()
        }
    }

    Shortcut {
        sequence: "F"
        onActivated: {
            fullScreenWindow.showFullScreen()
        }
    }
}
