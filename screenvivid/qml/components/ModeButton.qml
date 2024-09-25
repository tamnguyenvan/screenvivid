import QtQuick
import QtQuick.Controls

Button {
    id: modeButton

    required property string iconPath
    property string toolTipText: ""
    property bool activated: false

    background: Rectangle {
        anchors.fill: parent
        color: "transparent"
    }

    contentItem: Rectangle {
        id: content
        anchors.fill: parent
        color: modeButton.hovered ? (modeButton.activated ? "#101010" : "#242424") : (modeButton.activated ? "#151515" : "transparent")
        radius: 8

        Image {
            anchors.top: parent.top
            anchors.topMargin: 10
            anchors.horizontalCenter: parent.horizontalCenter
            width: 26
            height: 26
            source: iconPath
            fillMode: Image.PreserveAspectFit
        }

        Text {
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 4
            text: modeButton.text
            color: "#A9A9A9" // Darker text color
            font.pixelSize: 11
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
