import QtQuick 6.7
import QtQuick.Layouts 6.7
import QtQuick.Effects

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property int gridColumns: 7
    property int thumbnailCount: 17

    GridView {
        id: gridView
        anchors.fill: parent
        cellWidth: width / root.gridColumns
        cellHeight: cellWidth
        model: root.thumbnailCount

        delegate: Item {
            width: gridView.cellWidth
            height: gridView.cellHeight

            Item {
                width: gridView.cellWidth
                height: gridView.cellHeight

                Rectangle {
                    anchors.centerIn: parent
                    width: Math.min(parent.width, parent.height) * 0.9
                    height: width
                    color: "transparent"

                    Image {
                        id: thumbnail
                        anchors.fill: parent
                        anchors.margins: 1
                        source: "qrc:/resources/images/wallpapers/thumbnails/gradient-wallpaper-"
                                + (index + 1).toString().padStart(4, '0') + ".jpg"
                        fillMode: Image.PreserveAspectCrop
                        visible: false
                    }

                    MultiEffect {
                        source: thumbnail
                        anchors.fill: thumbnail
                        maskEnabled: true
                        maskSource: mask
                    }

                    Item {
                        id: mask
                        width: thumbnail.width
                        height: thumbnail.height
                        layer.enabled: true
                        visible: false

                        Rectangle {
                            id: maskRect
                            width: parent.width
                            height: parent.height
                            radius: 8
                            color: "black"
                        }
                    }

                    Rectangle {
                        anchors.fill: parent
                        color: "transparent"
                        border.color: "#303030"
                        border.width: 2
                        radius: 8
                    }
                }

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