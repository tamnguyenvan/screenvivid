import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    id: backgroundSettings
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 10

    RowLayout {
        Layout.fillWidth: true
        spacing: 8
        Image {
            source: "qrc:/resources/icons/background.svg"
            sourceSize: Qt.size(24, 24)
            Layout.alignment: Qt.AlignVCenter
        }

        Label {
            text: qsTr("Background")
            font.pixelSize: 16
        }
    }

    TabBar {
        id: backgroundSettingsBar
        Layout.fillWidth: true
        Layout.preferredHeight: 50

        Repeater {
            model: ["Wallpaper", "Gradient", "Color", "Image"]

            TabButton {
                text: modelData
                Layout.fillWidth: true
            }
        }
    }

    StackLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        currentIndex: backgroundSettingsBar.currentIndex

        WallpaperPage {}
        GradientPage {}
        ColorPage {}
        ImagePage {}
    }
}