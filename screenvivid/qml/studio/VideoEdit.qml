import QtQuick 6.7
import QtQuick.Controls 6.7
import "." // Import current directory components

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

        ScrollBar.horizontal: ScrollBar {
            id: hScrollBar
            background: Rectangle {
                color: "transparent"
            }
            contentItem: Rectangle {
                implicitWidth: 100
                implicitHeight: 10
                radius: height / 2
                color: {
                    if (hScrollBar.pressed) return "#81848c"  // Pressed state
                    if (hScrollBar.hovered) return "#6e7177"  // Hover state
                    return "#5d6067"  // Normal state
                }
            }
        }

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
            
            // Zoom effects track - inline implementation
            Item {
                id: zoomTrack
                width: parent.width
                height: 30
                y: 145 // Position below the clip track
                anchors.left: parent.left
                anchors.leftMargin: 10
                
                Rectangle {
                    anchors.fill: parent
                    color: "#282C33"
                    opacity: 0.7
                    radius: 4
                }
                
                // Zoom effects renderer
                Repeater {
                    model: videoController.zoom_effects
                    
                    delegate: Rectangle {
                        property var effect: modelData
                        
                        // Convert from absolute to relative frame positions for display
                        // This ensures proper positioning on the timeline
                        property int relativeStartFrame: Math.max(0, effect.start_frame - videoController.start_frame)
                        property int relativeEndFrame: Math.min(videoController.end_frame - videoController.start_frame, 
                                                             effect.end_frame - videoController.start_frame)
                        
                        x: relativeStartFrame * studioWindow.pixelsPerFrame
                        y: 2
                        width: (relativeEndFrame - relativeStartFrame) * studioWindow.pixelsPerFrame
                        height: parent.height - 4
                        radius: 4
                        
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#2969E7" }
                            GradientStop { position: 1.0; color: "#545EEE" }
                        }
                        
                        // Zoom indicator
                        Row {
                            anchors.centerIn: parent
                            spacing: 4
                            visible: width > 80
                            
                            Image {
                                source: "qrc:/resources/icons/zoom.svg"
                                width: 16
                                height: 16
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: (effect.params.scale).toFixed(1) + "x"
                                color: "white"
                                font.pixelSize: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                        
                        // Hover state
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            onEntered: {
                                parent.opacity = 0.8
                            }
                            
                            onExited: {
                                parent.opacity = 1.0
                            }
                            
                            onClicked: {
                                contextMenu.popup()
                            }
                        }
                        
                        // Context menu
                        Menu {
                            id: contextMenu
                            
                            MenuItem {
                                text: "Remove Zoom Effect"
                                onTriggered: {
                                    console.log("Removing zoom effect from frame", effect.start_frame, "to", effect.end_frame)
                                    videoController.remove_zoom_effect(effect.start_frame, effect.end_frame)
                                }
                            }
                            
                            MenuItem {
                                text: "Edit Zoom Effect"
                                onTriggered: {
                                    // Jump to middle of zoom effect (using absolute frame numbers)
                                    var middleFrame = effect.start_frame + Math.floor((effect.end_frame - effect.start_frame) / 2)
                                    videoController.jump_to_frame(middleFrame)
                                    
                                    console.log("Editing zoom effect. Jumping to frame:", middleFrame)
                                    
                                    // Activate zoom control in the VideoPreview
                                    var videoPreview = studioWindow.findChild("videoPreview")
                                    if (videoPreview) {
                                        videoPreview.zoomActive = true
                                        videoPreview.zoomCenterX = effect.params.x
                                        videoPreview.zoomCenterY = effect.params.y
                                        videoPreview.zoomScale = effect.params.scale
                                        console.log("Zoom controls activated with:", 
                                                  effect.params.x, effect.params.y, effect.params.scale)
                                    } else {
                                        console.error("Could not find videoPreview component")
                                    }
                                }
                            }
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
        
        function onZoomEffectsChanged() {
            // The Repeater should automatically update when the model changes
            // This is just to make sure it's working
            console.log("Zoom effects changed, count:", videoController.zoom_effects.length)
            for (var i = 0; i < videoController.zoom_effects.length; i++) {
                var effect = videoController.zoom_effects[i]
                console.log("  Zoom effect " + i + ":", effect.start_frame, "-", effect.end_frame,
                           ", scale:", effect.params.scale)
            }
            
            zoomTrack.visible = false
            zoomTrack.visible = true
        }
    }
}