import QtQuick
import QtQuick.Layouts

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property int gridColumns: 7
    property int thumbnailCount: 20

    GridView {
        id: gridView
        anchors.fill: parent
        cellWidth: width / root.gridColumns
        cellHeight: cellWidth
        model: root.thumbnailCount

        delegate: Item {
            width: gridView.cellWidth
            height: gridView.cellHeight

            Image {
                anchors.centerIn: parent
                width: Math.min(parent.width, parent.height) * 0.9
                height: width
                source: "qrc:/resources/images/wallpapers/thumbnails/gradient-wallpaper-"
                        + (index + 1).toString().padStart(4, '0') + ".png"
                fillMode: Image.PreserveAspectCrop

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        videoController.background = {
                            "type": "wallpaper",
                            "value": index + 1
                        }
                        if (!isPlaying) {
                            videoController.get_current_frame()
                        }
                    }
                }
            }
        }
    }
}