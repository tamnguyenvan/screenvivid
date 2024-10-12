import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import "../components"

Item {
    Layout.fillWidth: true
    Layout.preferredHeight: 50

    RowLayout {
        anchors.fill: parent

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            RowLayout {
                anchors.fill: parent

                ComboBox {
                    id: aspectRatios
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.margins: 4
                    Layout.preferredWidth: 150
                    property var aspectRatioMap: {
                                        "Auto": "auto",
                                        "Wide 16:9": "16:9",
                                        "Vertical 9:16": "9:16",
                                        "Classic 4:3": "4:3",
                                        "Tall 3:4": "3:4",
                                        "Square 1:1": "1:1",
                                        "Wide 16:10": "16:10",
                                        "Tall 10:16": "10:16"
                                    }

                                    currentIndex: 0
                                    model: Object.keys(aspectRatioMap)
                                    onCurrentIndexChanged: {
                                        videoController.aspect_ratio = aspectRatioMap[model[currentIndex]].toLowerCase()
                                        videoController.get_current_frame()
                                    }
                    background: Rectangle {
                        implicitWidth: 150
                        implicitHeight: 40
                        color: aspectRatios.pressed ? "#2c313c" : "#1e2228"
                        border.color: aspectRatios.pressed ? "#3d4450" : "#2c313c"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        leftPadding: 10
                        rightPadding: aspectRatios.indicator.width + aspectRatios.spacing
                        text: aspectRatios.displayText
                        font: aspectRatios.font
                        color: "#e8eaed"
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        width: aspectRatios.width - leftPadding - rightPadding
                    }
                    delegate: ItemDelegate {
                        width: aspectRatios.popup.width
                        height: 40
                        contentItem: Text {
                            text: modelData
                            color: "#e8eaed"
                            font: aspectRatios.font
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: 10
                        }
                        highlighted: aspectRatios.highlightedIndex === index
                        background: Rectangle {
                            color: highlighted ? "#3d4450" : "transparent"
                        }
                    }
                    popup: Popup {
                        y: aspectRatios.height + 4
                        x: -(width - aspectRatios.width) / 2
                        width: Math.max(aspectRatios.width, 180)  // Increased minimum width
                        implicitHeight: contentItem.implicitHeight
                        padding: 1
                        contentItem: ListView {
                            clip: true
                            implicitHeight: contentHeight
                            model: aspectRatios.popup.visible ? aspectRatios.delegateModel : null
                            currentIndex: aspectRatios.highlightedIndex
                            ScrollIndicator.vertical: ScrollIndicator {}
                        }
                        background: Rectangle {
                            border.color: "#3d4450"
                            color: "#1e2228"
                            radius: 4
                        }
                        enter: Transition {
                            NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 100 }
                        }
                        exit: Transition {
                            NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 100 }
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            RowLayout {
                anchors.centerIn: parent
                spacing: 10

                ToolButton {
                    icon.source: "qrc:/resources/icons/prev.svg"
                    icon.color: "#e8eaed"
                    onClicked: videoController.prev_frame()
                }
                ToolButton {
                    icon.source: isPlaying ? "qrc:/resources/icons/pause.svg" : "qrc:/resources/icons/play.svg"
                    icon.color: "#e8eaed"
                    onClicked: videoController.toggle_play_pause()
                }
                ToolButton {
                    icon.source: "qrc:/resources/icons/next.svg"
                    icon.color: "#e8eaed"
                    onClicked: videoController.next_frame()
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ToolButton {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                icon.source: "qrc:/resources/icons/cut.svg"
                icon.color: "#e8eaed"
                onClicked: clipTrackModel.cut_clip()
            }
        }
    }
}