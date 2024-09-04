import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Button {
    id: customButton
    property color primaryColor: Material.primaryColor
    property color pressedColor: Material.accentColor
    property color hoverColor: Qt.lighter(primaryColor, 1.1)
    property int buttonRadius: 10
    property string iconSource: ""
    property int iconSize: 24

    background: Rectangle {
        color: customButton.down ? pressedColor : primaryColor
        Behavior on color {
            ColorAnimation {
                duration: 200
            }
        }
        radius: buttonRadius
    }

    contentItem: RowLayout {
        spacing: 8

        Image {
            source: customButton.iconSource
            sourceSize.width: customButton.iconSize
            sourceSize.height: customButton.iconSize
            Layout.alignment: Qt.AlignVCenter
            visible: source !== ""
        }

        Text {
            text: customButton.text
            font: customButton.font
            color: "white"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
        }
    }

    HoverHandler {
        onHoveredChanged: {
            if (hovered) {
                customButton.background.color = hoverColor
            } else {
                customButton.background.color = primaryColor
            }
        }
    }
}
