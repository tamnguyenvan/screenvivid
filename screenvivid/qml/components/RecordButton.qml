import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ToolButton {
    id: root
    icon.source: "qrc:/resources/icons/record.svg"
    icon.color: "white"
    icon.width: 26
    icon.height: 26

    Behavior on icon.color {
        ColorAnimation {
            duration: 200
        }
    }

    background: Rectangle {
        radius: 8
        color: root.hovered ? "#242424" : "#212121"
    }
}
