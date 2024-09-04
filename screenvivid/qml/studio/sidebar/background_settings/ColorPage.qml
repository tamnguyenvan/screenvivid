import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Dialogs

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property int gridColumns: 7
    property int coloCount: 20

    GridView {
        id: gridView
        anchors.fill: parent
        cellWidth: width / root.gridColumns
        cellHeight: cellWidth
        model: ['#FF3131', '#FF5757', '#FF66C4', '#CB6CE6', '#8C52FF', '#5E17EB', '#0097B2', '#0CC0DF', '#5CE1E6', '#38B6FF', '#5271FF', '#004AAD', '#00BF63', '#7ED957', '#C1FF72', '#FFDE59', '#FFBD59', '#FF914D', '#FA7420', '+']

        delegate: Item {
            width: gridView.cellWidth
            height: gridView.cellHeight

            Item {
                anchors.fill: parent

                Rectangle {
                    anchors.centerIn: parent
                    width: Math.min(parent.width, parent.height) * 0.9
                    height: width
                    color: modelData
                    visible: modelData.startsWith("#")

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            videoController.background = {
                                "type": "color",
                                "value": modelData
                            }
                            if (!isPlaying) {
                                videoController.get_current_frame()
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.centerIn: parent
                    width: Math.min(parent.width, parent.height) * 0.9
                    height: width

                    color: "white"
                    border.color: "black"
                    border.width: 1
                    visible: modelData === "+"

                    Text {
                        anchors.centerIn: parent
                        text: "+"
                        font.pixelSize: 24
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: colorDialog.open()
                    }
                }
            }
        }
    }

    ColorDialog {
        id: colorDialog
        title: "Choose a color"
        onAccepted: {
            var hexColor = "#" + colorDialog.selectedColor.toString().substr(1)
            videoController.background = {
                "type": "color",
                "value": hexColor
            }
            if (!isPlaying) {
                videoController.get_current_frame()
            }
        }
    }
}
