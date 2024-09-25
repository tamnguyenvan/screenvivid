import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: recordButton
    implicitWidth: 50
    implicitHeight: 50
    Layout.alignment: Qt.AlignCenter

    background: Item {
        anchors.fill: parent
        Rectangle {
            id: outerCircle
            anchors.centerIn: parent
            anchors.fill: parent
            radius: width / 2
            color: "transparent"
            border.color: "white"
            border.width: 5
        }

        Rectangle {
            id: innerCircle
            anchors.centerIn: parent
            width: 36
            height: 36
            radius: width / 2
            color: recordButton.hovered ? Qt.lighter("red", 1.3) : "red"
            Behavior on color {
                ColorAnimation {
                    duration: 200
                }
            }
        }
    }
}
