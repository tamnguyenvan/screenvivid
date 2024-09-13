import QtQuick 6.7
import QtQuick.Controls.Material 6.7
import QtQuick.Layouts 6.7

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredHeight: 500

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            spacing: 12
            Image {
                source: "qrc:/resources/icons/background.svg"
                sourceSize: Qt.size(24, 24)
                Layout.alignment: Qt.AlignVCenter
            }
            Label {
                text: qsTr("Background")
                font.pixelSize: 18
                font.weight: Font.Medium
                color: "#FFFFFF"
            }
        }

        TabBar {
            id: backgroundSettingsBar
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            background: Rectangle {
                color: "#2A2E32"
                radius: 8
            }
            Repeater {
                model: ["Wallpaper", "Gradient", "Color", "Image"]
                TabButton {
                    text: modelData
                    Layout.fillWidth: true
                    height: 40
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: parent.checked ? "#FFFFFF" : "#AAAAAA"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: parent.checked ? Material.primary : "transparent"
                        radius: 8
                    }
                }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            StackLayout {
                width: root.width
                currentIndex: backgroundSettingsBar.currentIndex

                WallpaperPage {}
                GradientPage {}
                ColorPage {}
                ImagePage {}
            }
        }
    }
}