import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts

// Shape settings
ColumnLayout {
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 20

    // Label {
    //     text: qsTr("Shape")
    //     font.pixelSize: 16
    //     color: "#c2c2c2"
    // }

    Row {
        spacing: 8
        Image {
            source: "qrc:/resources/icons/shape.svg"
            sourceSize.width: 24
            sourceSize.height: 24
            Layout.alignment: Qt.AlignVCenter
            visible: true
        }
        Label {
            text: qsTr("Shape")
            font.pixelSize: 16
            anchors.bottom: parent.bottom
        }
    }

    // Add a margin = 10 for this layout
    ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin: 10
        spacing: 10

        // Padding
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

            RowLayout {
                spacing: 8
                Image {
                    source: "qrc:/resources/icons/padding.svg"
                    sourceSize.width: 24
                    sourceSize.height: 24
                    Layout.alignment: Qt.AlignVCenter
                    visible: true
                }
                Label {
                    text: qsTr("Padding")
                    font.pixelSize: 14
                    color: "#c2c2c2"
                }
            }

            RowLayout {
                Layout.fillWidth: true

                Slider {
                    id: paddingSlider
                    from: 0
                    to: 500
                    value: 100
                    Layout.fillWidth: true

                    onValueChanged: {
                        paddingLabel.updateText(
                                    value)
                        videoController.padding = Math.round(
                                    value)
                        if (!isPlaying) {
                            videoController.get_current_frame()
                        }
                    }
                }

                Label {
                    id: paddingLabel
                    text: paddingSlider.value.toFixed(0)
                    Layout.preferredWidth: 40
                    horizontalAlignment: Text.AlignRight

                    function updateText(value) {
                        text = value.toFixed(0)
                    }
                }
            }
        }

        // Inset
        // ColumnLayout {
        //     Layout.fillWidth: true
        //     spacing: 10

        //     RowLayout {
        //         Layout.fillWidth: true
        //         spacing: 8
        //         Image {
        //             source: "qrc:/resources/icons/inset.svg"
        //             sourceSize.width: 24
        //             sourceSize.height: 24
        //         }
        //         Label {
        //             text: qsTr("Inset")
        //             font.pixelSize: 14
        //             color: "#c2c2c2"
        //         }
        //     }

        //     RowLayout {
        //         Layout.fillWidth: true
        //         spacing: 10

        //         Slider {
        //             id: insetSlider
        //             from: 0
        //             value: 0
        //             to: 100
        //             Layout.fillWidth: true

        //             onValueChanged: {
        //                 insetLabel.updateText(value)
        //                 videoController.inset = Math.round(value)
        //                 if (!isPlaying) {
        //                     videoController.get_current_frame()
        //                 }
        //             }
        //         }

        //         Label {
        //             id: insetLabel
        //             text: insetSlider.value.toFixed(0)
        //             Layout.preferredWidth: 40
        //             horizontalAlignment: Text.AlignRight

        //             function updateText(value) {
        //                 text = value.toFixed(0)
        //             }
        //         }
        //     }
        // }

        // Roundness
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Image {
                    source: "qrc:/resources/icons/border.svg"
                    sourceSize.width: 24
                    sourceSize.height: 24
                }
                Label {
                    text: qsTr("Roundness")
                    font.pixelSize: 14
                    color: "#c2c2c2"
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Slider {
                    id: roundnessSlider
                    from: 0
                    to: 100
                    value: 14
                    Layout.fillWidth: true

                    onValueChanged: {
                        roundnessLabel.updateText(
                                    value)
                        videoController.border_radius = Math.round(
                                    value)
                        if (!isPlaying) {
                            videoController.get_current_frame()
                        }
                    }
                }

                Label {
                    id: roundnessLabel
                    text: roundnessSlider.value.toFixed(0)
                    Layout.preferredWidth: 40
                    horizontalAlignment: Text.AlignRight

                    function updateText(value) {
                        text = value.toFixed(0)
                    }
                }
            }
        }
    }

    Item {
        Layout.fillHeight: true
        Layout.fillWidth: true
    }
}