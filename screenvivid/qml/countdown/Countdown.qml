import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import Qt.labs.platform

Window {
    id: root
    visible: true
    width: Math.max(Screen.height / 3, 400)
    height: Math.max(Screen.height / 3, 400)
    x: (Screen.desktopAvailableWidth - width) / 2
    y: (Screen.desktopAvailableHeight - height) / 2
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"
    title: qsTr("ScreenVivid")

    readonly property int countdownTime: 3
    property bool recording: false
    property int totalRecordingTime: 0 // In seconds

    Timer {
        id: recordingTimer
        interval: 1000
        repeat: true
        onTriggered: {
            totalRecordingTime++
        }
    }

    Item {
        anchors.fill: parent
        visible: !recording

        Rectangle {
            id: countdown
            anchors.fill: parent
            color: "#303030"
            radius: root.width / 2
            opacity: 0.9
            Timer {
                id: timer
                interval: 1000
                repeat: true
                running: true
                property int count: countdownTime
                onTriggered: {
                    count--
                    if (count == 0) {
                        timer.stop()
                        recording = true
                        screenRecorder.start_recording()
                        recordingTimer.start()
                        if (Qt.platform.os === "linux" || Qt.platform.os === "osx") {
                            root.showMinimized()
                        } else if (Qt.platform.os === "windows") {
                            root.hide()
                        }
                    }
                }
            }
        }

        // Border
        Rectangle {
            anchors.fill: parent
            radius: root.width / 2
            color: "transparent"
            border.width: 3
            border.color: "#c4c4c4"
        }

        // Countdown text
        Text {
            text: timer.count
            anchors.centerIn: parent
            font.pixelSize: 120
            font.weight: 700
            color: "white"
            visible: timer.count > 0
        }
    }

    // Minimized bar
    Rectangle {
        id: minimizedBar
        visible: recording
        height: 60
        width: Math.max(100, parent.width * 0.67)
        anchors.centerIn: parent
        radius: 10
        color: "#2e2e2e"
        opacity: 0.9

        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            border.width: 2
            border.color: "darkgray"
            opacity: 0.7
            color: "transparent"
        }

        RowLayout {
            anchors.fill: parent
            anchors.centerIn: parent
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            anchors.topMargin: 4
            anchors.bottomMargin: 4

            Item {
                Layout.fillHeight: true
                Layout.fillWidth: true

                Button {
                    anchors.centerIn: parent
                    width: Math.max(120, parent.width - 20)
                    height: parent.height

                    background: Rectangle {
                        color: parent.hovered ? Qt.lighter("red", 1.2) : "red"
                        radius: 10
                    }

                    contentItem: RowLayout {
                        anchors.centerIn: parent
                        spacing: 4

                        Image {
                            source: "qrc:/resources/icons/stop.svg"
                            width: 24
                            height: 24
                        }

                        Text {
                            text: Qt.formatTime(new Date(0, 0, 0, 0, 0, totalRecordingTime), "hh:mm:ss")
                            color: "white"
                            font.pixelSize: 16
                            font.bold: true
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            screenRecorder.stop_recording()
                            recordingTimer.stop()
                            root.hide()
                            tray.hide()
                            // Load and show studio here
                            var metadata = {
                                'mouse_events': screenRecorder.mouse_events,
                                'region': screenRecorder.region,
                                'recording': true
                            }
                            var success = videoController.load_video(screenRecorder.output_path, metadata)
                            if (success) {
                                clipTrackModel.set_fps(videoController.fps)
                                clipTrackModel.set_video_len(0, videoController.video_len)
                                studioLoader.source = ""
                                studioLoader.source = "qrc:/qml/studio/Studio.qml"
                                studioLoader.item.showMaximized()
                                tray.hide()
                            } else {}
                        }
                    }
                }
            }

            Item {
                Layout.fillHeight: true
                Layout.preferredWidth: 40

                ToolButton {
                    anchors.centerIn: parent
                    icon.source: "qrc:/resources/icons/trash.svg"
                    icon.width: 24
                    icon.height: 24
                    icon.color: "#e8eaed"
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            screenRecorder.cancel_recording()
                            Qt.quit()
                        }
                    }
                    background: Rectangle {
                        radius: width / 2
                        color: parent.hovered ? "#242424" : "#212121"
                    }
                }
            }
        }
    }

    SystemTrayIcon {
        id: tray
        visible: true
        icon.source: "qrc:/resources/icons/screenvivid.svg"
        menu: Menu {
            MenuItem {
                text: qsTr("Stop")
                onTriggered: {
                    screenRecorder.stop_recording()
                    root.hide()
                    var metadata = {
                        'mouse_events': screenRecorder.mouse_events,
                        'region': screenRecorder.region,
                        'recording': true
                    }
                    var success = videoController.load_video(screenRecorder.output_path, metadata)
                    if (success) {
                        clipTrackModel.set_fps(videoController.fps)
                        clipTrackModel.set_video_len(0, videoController.video_len)
                        studioLoader.source = ""
                        studioLoader.source = "qrc:/qml/studio/Studio.qml"
                        studioLoader.item.showMaximized()
                        tray.hide()
                    } else {}
                }
            }
            MenuItem {
                text: qsTr("Cancel")
                onTriggered: {
                    screenRecorder.cancel_recording()
                    Qt.quit()
                }
            }
        }
    }

    Loader {
        id: studioLoader
    }

    onClosing: {
        screenRecorder.cancel_recording()
        Qt.quit()
    }
}
