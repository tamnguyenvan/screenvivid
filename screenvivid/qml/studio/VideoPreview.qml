import QtQuick 6.7
import QtQuick.Window 6.7
import QtQuick.Dialogs 6.7
import QtQuick.Controls.Material 6.7
import QtQuick.Layouts 6.7
import "." // Import current directory components

Item {
    id: root
    objectName: "videoPreview"
    Layout.fillWidth: true
    Layout.fillHeight: true
    
    // Zoom control properties
    property bool zoomActive: false
    property real zoomCenterX: 0.5
    property real zoomCenterY: 0.5
    property real zoomScale: 2.0

    // Shortcut management
    QtObject {
        id: shortcutManager
        function handleToggleFullScreenVideoPreview() {
            if (fullScreenWindow.visibility == Window.FullScreen) {
                fullScreenWindow.close()
            } else {
                fullScreenWindow.showFullScreen()
            }
        }
    }

    Shortcut {
        sequence: "F"
        context: Qt.ApplicationShortcut
        onActivated: {
            shortcutManager.handleToggleFullScreenVideoPreview()
        }
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
        
        // Zoom control UI (simple inline implementation)
        Item {
            id: zoomControlUI
            anchors.fill: parent
            visible: zoomActive
            
            // Background to capture mouse events
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.CrossCursor
                    
                    onClicked: (mouse) => {
                        if (zoomActive) {
                            zoomCrosshair.x = mouse.x - zoomCrosshair.width / 2
                            zoomCrosshair.y = mouse.y - zoomCrosshair.height / 2
                            
                            zoomCenterX = (mouse.x) / parent.width
                            zoomCenterY = (mouse.y) / parent.height
                        }
                    }
                }
            }
            
            // Zoom crosshair indicator
            Item {
                id: zoomCrosshair
                width: 100
                height: 100
                x: parent.width * zoomCenterX - width / 2
                y: parent.height * zoomCenterY - height / 2
                
                // Crosshair design
                Rectangle {
                    anchors.centerIn: parent
                    width: 2
                    height: parent.height
                    color: "#545EEE"
                    opacity: 0.8
                }
                
                Rectangle {
                    anchors.centerIn: parent
                    height: 2
                    width: parent.width
                    color: "#545EEE"
                    opacity: 0.8
                }
                
                Rectangle {
                    anchors.centerIn: parent
                    width: 20
                    height: 20
                    radius: 10
                    color: "transparent"
                    border.width: 2
                    border.color: "#545EEE"
                    opacity: 0.8
                }
                
                // Make the crosshair draggable
                MouseArea {
                    anchors.fill: parent
                    drag.target: parent
                    drag.minimumX: -width/2
                    drag.maximumX: zoomControlUI.width - width/2
                    drag.minimumY: -height/2
                    drag.maximumY: zoomControlUI.height - height/2
                    
                    onPositionChanged: {
                        if (drag.active) {
                            var centerPointX = parent.x + width/2
                            var centerPointY = parent.y + height/2
                            
                            zoomCenterX = centerPointX / zoomControlUI.width
                            zoomCenterY = centerPointY / zoomControlUI.height
                        }
                    }
                }
            }
            
            // Zoom controls panel
            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 20
                width: 200
                height: 120
                color: "#2A2A2A"
                opacity: 0.8
                radius: 10
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8
                    
                    Text {
                        text: "Zoom Control"
                        font.bold: true
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        Layout.fillWidth: true
                    }
                    
                    // Zoom scale slider
                    RowLayout {
                        spacing: 5
                        Layout.fillWidth: true
                        
                        Text {
                            text: "Scale:"
                            color: "white"
                        }
                        
                        Slider {
                            id: zoomSlider
                            from: 1.0
                            to: 4.0
                            value: zoomScale
                            Layout.fillWidth: true
                            onValueChanged: {
                                zoomScale = value
                            }
                        }
                        
                        Text {
                            text: zoomSlider.value.toFixed(1) + "x"
                            color: "white"
                            width: 30
                        }
                    }
                    
                    // Control buttons
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignRight
                        spacing: 10
                        
                        Button {
                            text: "Cancel"
                            onClicked: {
                                zoomActive = false
                            }
                        }
                        
                        Button {
                            text: "Apply Zoom"
                            highlighted: true
                            onClicked: {
                                applyZoom()
                                zoomActive = false
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Function to apply zoom
    function applyZoom() {
        // Get current absolute frame position (including start_frame offset)
        var currentFrame = videoController.absolute_current_frame
        
        // Create a zoom effect of about 2 seconds (60 frames = 2s at default 30fps)
        var startFrame = Math.max(videoController.start_frame, currentFrame - 30) 
        var endFrame = Math.min(videoController.end_frame, currentFrame + 30)
        
        console.log("Adding zoom effect from frame", startFrame, "to", endFrame)
        console.log("Zoom parameters: center=(" + zoomCenterX.toFixed(2) + "," + zoomCenterY.toFixed(2) + 
                   "), scale=" + zoomScale.toFixed(2))
        
        // Apply zoom effect via controller (using absolute frame positions)
        videoController.add_zoom_effect(startFrame, endFrame, {
            "x": zoomCenterX,
            "y": zoomCenterY,
            "scale": zoomScale
        })
        
        // Force an update to the current frame to see the zoom immediately
        videoController.get_current_frame()
    }

    // Control buttons
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        spacing: 10
        
        // Zoom button
        ToolButton {
            id: zoomButton
            icon.source: "qrc:/resources/icons/zoom.svg"
            icon.color: "#e8eaed"
            onClicked: {
                zoomActive = true
            }
            
            ToolTip.text: "Add Zoom Effect"
            ToolTip.visible: hovered
            ToolTip.delay: 500
        }
        
        // Full screen button
        ToolButton {
            id: fullScreenButton
            icon.source: "qrc:/resources/icons/full_screen.svg"
            icon.color: "#e8eaed"
            onClicked: {
                fullScreenWindow.showFullScreen()
            }
            
            ToolTip.text: "Full Screen"
            ToolTip.visible: hovered
            ToolTip.delay: 500
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

        Rectangle {
            anchors.fill: parent
            focus: true
            color: "#131519"

            Keys.onPressed: (event) => {
                if (event.key === Qt.Key_F) {
                    shortcutManager.handleToggleFullScreenVideoPreview()
                    event.accepted = true
                } else if (event.key === Qt.Key_Escape) {
                    shortcutManager.handleToggleFullScreenVideoPreview()
                    event.accepted = true
                }
            }

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
