import QtQuick 6.7
import QtQuick.Window 6.7
import QtQuick.Dialogs 6.7
import QtQuick.Controls.Material 6.7
import QtQuick.Layouts 6.7

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    // Shortcut management
    QtObject {
        id: shortcutManager
        function handleToggleFullScreenVideoPreview() {
            fullScreenWindow.showFullScreen()
        }
    }

    Shortcut {
        sequence: "F"
        context: Qt.WindowShortcut
        onActivated: shortcutManager.handleToggleFullScreenVideoPreview()
    }

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
        flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        visible: false

        readonly property string accentColor: "#131519"
        Material.theme: Material.Dark
        Material.primary: accentColor
        Material.accent: accentColor

        // Shortcut management
        QtObject {
            id: videoPreviewShortcutManager
            readonly property bool isMac: Qt.platform.os === "osx"
            readonly property string undoModifier: isMac ? "Meta" : "Ctrl"
            
            function handleUndo() {
                clipTrackModel.undo()
                videoController.undo()
            }

            function handlePlayPause() {
                videoController.toggle_play_pause()
            }

            function handlePrevFrame() {
                videoController.prev_frame()
            }

            function handleNextFrame() {
                videoController.next_frame()
            }
        }

        Shortcut {
            sequence: "Space"
            onActivated: videoPreviewShortcutManager.handlePlayPause()
        }

        Shortcut {
            sequence: "Left"
            onActivated: videoPreviewShortcutManager.handlePrevFrame()
        }

        Shortcut {
            sequence: "Right"
            onActivated: videoPreviewShortcutManager.handleNextFrame()
        }

        Shortcut {
            sequence: videoPreviewShortcutManager.undoModifier + "+Z"
            onActivated: videoPreviewShortcutManager.handleUndo()
        }

        Rectangle {
            anchors.fill: parent
            focus: true
            color: "#131519"

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

                            background: Rectangle {
                                x: fullScreenTimeSlider.leftPadding
                                y: fullScreenTimeSlider.topPadding + fullScreenTimeSlider.availableHeight / 2 - height / 2
                                width: fullScreenTimeSlider.availableWidth
                                height: 6
                                radius: 2
                                color: "#2A2E32"

                                Rectangle {
                                    width: fullScreenTimeSlider.visualPosition * parent.width
                                    height: parent.height
                                    color: "#545EEE"
                                    radius: 2
                                }
                            }

                            handle: Rectangle {
                                x: fullScreenTimeSlider.leftPadding + fullScreenTimeSlider.visualPosition * (fullScreenTimeSlider.availableWidth - width)
                                y: fullScreenTimeSlider.topPadding + fullScreenTimeSlider.availableHeight / 2 - height / 2
                                width: 16
                                height: 16
                                radius: 8
                                color: fullScreenTimeSlider.pressed ? "#FFFFFF" : "#DDDDDD"
                            }

                            onMoved: {
                                var currentFrame = parseInt(value * videoController.end_frame * 0.01)
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
                                icon.source: "qrc:/resources/icons/exit_full_screen.svg"
                                icon.color: "#e8eaed"
                                onClicked: {
                                    fullScreenWindow.close()
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
                    fullScreenWindow.close()
                } else if (event.key === Qt.Key_F) {
                    fullScreenWindow.close()
                }
            }
        }

        Connections {
            target: videoController
            function onCurrentFrameChanged(currentFrame) {
                var progress = 100.0 * currentFrame / (videoController.end_frame - videoController.start_frame)
                fullScreenTimeSlider.value = progress

                 // Update elapsed time
                var elapsedSeconds = currentFrame / videoController.fps
                elapsedTime.text = formatTime(elapsedSeconds)

                // Update total time
                var totalSeconds = parseFloat(videoController.end_frame - videoController.start_frame) / videoController.fps
                totalSeconds = Math.ceil(totalSeconds)
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
}
