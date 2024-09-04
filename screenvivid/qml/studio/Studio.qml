import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material
import "./sidebar"

Window {
    id: studioWindow

    readonly property int defaultWidth: Screen.width
    readonly property int defaultHeight: Screen.height
    readonly property int minWidth: Screen.width / 2
    readonly property int minHeight: Screen.height / 2
    readonly property string accentColor: "#545eee"
    readonly property string backgroundColor: "#0B0D0F"

    width: defaultWidth
    height: defaultHeight
    minimumWidth: minWidth
    minimumHeight: minHeight
    title: qsTr("ScreenVivid")
    visible: true
    visibility: Window.Maximized

    Material.theme: Material.Dark
    Material.primary: accentColor
    Material.accent: accentColor

    property bool isPlaying: false
    property int fps: 30
    property int totalFrames: 0
    property int pixelsPerFrame: 6
    property real videoLen: 0
    property int frameWidth: 0
    property int frameHeight: 0

    Connections {
        target: videoController
        function onPlayingChanged(playing) {
            isPlaying = playing
        }
    }

    ExportDialog {
        id: exportDialog
        parent: Overlay.overlay
        exportFps: videoController.fps
    }

    Rectangle {
        anchors.fill: parent
        color: "#0B0D0F"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 15
            spacing: 0

            TopBar {
                id: topbar
                Layout.fillWidth: true
                Layout.preferredHeight: 50
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                RowLayout {
                    anchors.fill: parent
                    spacing: 30

                    MainContent {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }

                    ColumnLayout {
                        Layout.fillHeight: true
                        Layout.preferredWidth: 400

                        SideBar {
                            id: sidebar
                            Layout.preferredWidth: 400
                            Layout.fillHeight: true
                        }

                        Item {
                            Layout.preferredHeight: 50
                            Layout.preferredWidth: 400
                        }
                    }
                }
            }

            VideoEdit {
                id: videoEdit
                Layout.fillWidth: true
                Layout.preferredHeight: 180
            }

        }
    }

    Component.onCompleted: {
        fps = videoController.fps
        totalFrames = videoController.total_frames
        videoLen = videoController.video_len
        videoController.get_current_frame()
        videoController.aspect_ratio = "auto"
    }

    onClosing: {
        Qt.quit()
    }

    Shortcut {
        sequence: "Space"
        onActivated: {
            videoController.toggle_play_pause()
        }
    }

    Shortcut {
        sequence: "Left"
        onActivated: {
            videoController.prev_frame()
        }
    }

    Shortcut {
        sequence: "Right"
        onActivated: {
            videoController.next_frame()
        }
    }

    Shortcut {
        sequences: [StandardKey.Undo]
        onActivated: {
            clipTrackModel.undo()
            videoController.undo()
        }
    }
}