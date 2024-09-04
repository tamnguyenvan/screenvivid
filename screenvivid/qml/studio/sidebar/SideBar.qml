import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "./background_settings"
import "./shape_settings"

Rectangle {
    Layout.fillHeight: true
    implicitWidth: 400
    color: "#131519"
    radius: 4

    Flickable {
        anchors.fill: parent
        contentWidth: parent.width
        contentHeight: contentColumn.height
        boundsMovement: Flickable.StopAtBounds
        boundsBehavior: Flickable.StopAtBounds
        clip: true

        ColumnLayout {
            id: contentColumn
            width: parent.width
            spacing: 20
            anchors {
                left: parent.left
                right: parent.right
                top: parent.top
                margins: 20
            }

            BackgroundSettings {
                Layout.fillWidth: true
                Layout.preferredHeight: 300
            }

            ShapeSettings {
                Layout.fillWidth: true
                Layout.preferredHeight: 300
            }
        }
    }
}