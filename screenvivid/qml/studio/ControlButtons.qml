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
                    Layout.preferredWidth: 120

                    currentIndex: 0
                    model: ["Auto", "16:9", "9:16", "4:3", "3:4", "1:1"]
                    onCurrentIndexChanged: {
                        videoController.aspect_ratio = model[currentIndex].toLowerCase()
                        videoController.get_current_frame()
                    }

                    background: Rectangle {
                        implicitWidth: 100
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
                        elide: Text.ElideNone
                        width: aspectRatios.width - leftPadding - rightPadding
                        clip: true
                    }

                    delegate: ItemDelegate {
                        width: aspectRatios.width
                        contentItem: Text {
                            text: modelData
                            color: "#e8eaed"
                            font: aspectRatios.font
                            elide: Text.ElideNone
                            verticalAlignment: Text.AlignVCenter
                            width: parent.width
                            clip: true
                        }
                        highlighted: aspectRatios.highlightedIndex === index
                        background: Rectangle {
                            color: highlighted ? "#3d4450" : "#1e2228"
                        }
                    }

                    popup: Popup {
                        y: aspectRatios.height - 1
                        width: aspectRatios.width
                        implicitHeight: contentItem.implicitHeight
                        padding: 1

                        contentItem: ListView {
                            clip: true
                            implicitHeight: contentHeight
                            model: aspectRatios.popup.visible ? aspectRatios.delegateModel : null
                            currentIndex: aspectRatios.highlightedIndex
                        }

                        background: Rectangle {
                            border.color: "#3d4450"
                            color: "#1e2228"
                            radius: 4
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