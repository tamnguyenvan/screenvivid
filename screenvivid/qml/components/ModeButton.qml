import QtQuick 6.7
import QtQuick.Controls 6.7

Button {
    id: root
    required property string iconPath
    property string toolTipText: ""
    property bool activated: false

    background: Rectangle {
        anchors.fill: parent
        color: root.hovered ? (root.activated ? "#101010" : "#242424") : (root.activated ? "#151515" : "transparent")
        radius: 14
    }

    contentItem: Item {
        anchors.fill: parent
        anchors.centerIn: parent

        Image {
            anchors.centerIn: parent
            width: 36
            height: 36
            source: iconPath
            fillMode: Image.PreserveAspectFit
        }
    }

    ToolTip {
        visible: hovered
        delay: 800
        timeout: 5000
        text: qsTr(toolTipText)
        background: Rectangle {
            color: "#1d1d1d"
            radius: 10
        }
    }
}