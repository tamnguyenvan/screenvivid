import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ToolButton {
    id: root
    icon.source: "qrc:/resources/icons/record.svg"
    icon.width: 26
    icon.height: 26

    Behavior on icon.color {
        ColorAnimation {
            duration: 200
        }
    }

    background: Rectangle {
        radius: width / 2
        color: root.hovered ? "#242424" : "#212121"
    }
}
