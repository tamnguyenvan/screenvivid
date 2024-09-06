import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredHeight: 300

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Image {
                source: "qrc:/resources/icons/shape.svg"
                sourceSize: Qt.size(24, 24)
                Layout.alignment: Qt.AlignVCenter
            }

            Label {
                text: qsTr("Shape")
                font.pixelSize: 18
                font.weight: Font.Medium
                color: "#FFFFFF"
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 10
            spacing: 40

            // Padding
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Image {
                        source: "qrc:/resources/icons/padding.svg"
                        sourceSize: Qt.size(20, 20)
                        Layout.alignment: Qt.AlignVCenter
                    }

                    Label {
                        text: qsTr("Padding")
                        font.pixelSize: 14
                        color: "#AAAAAA"
                    }

                    Item { Layout.fillWidth: true }

                    Label {
                        id: paddingLabel
                        text: paddingSlider.value.toFixed(0)
                        font.pixelSize: 14
                        color: "#FFFFFF"
                    }
                }

                Slider {
                    id: paddingSlider
                    from: 0
                    to: 500
                    value: 100
                    Layout.fillWidth: true

                    background: Rectangle {
                        x: paddingSlider.leftPadding
                        y: paddingSlider.topPadding + paddingSlider.availableHeight / 2 - height / 2
                        width: paddingSlider.availableWidth
                        height: 4
                        radius: 2
                        color: "#2A2E32"

                        Rectangle {
                            width: paddingSlider.visualPosition * parent.width
                            height: parent.height
                            color: "#545EEE"
                            radius: 2
                        }
                    }

                    handle: Rectangle {
                        x: paddingSlider.leftPadding + paddingSlider.visualPosition * (paddingSlider.availableWidth - width)
                        y: paddingSlider.topPadding + paddingSlider.availableHeight / 2 - height / 2
                        width: 16
                        height: 16
                        radius: 8
                        color: paddingSlider.pressed ? "#FFFFFF" : "#DDDDDD"
                    }

                    onValueChanged: {
                        paddingLabel.text = value.toFixed(0)
                        videoController.padding = Math.round(value)
                        if (!isPlaying) {
                            videoController.get_current_frame()
                        }
                    }
                }
            }

            // Roundness
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Image {
                        source: "qrc:/resources/icons/border.svg"
                        sourceSize: Qt.size(20, 20)
                        Layout.alignment: Qt.AlignVCenter
                    }

                    Label {
                        text: qsTr("Roundness")
                        font.pixelSize: 14
                        color: "#AAAAAA"
                    }

                    Item { Layout.fillWidth: true }

                    Label {
                        id: roundnessLabel
                        text: roundnessSlider.value.toFixed(0)
                        font.pixelSize: 14
                        color: "#FFFFFF"
                    }
                }

                Slider {
                    id: roundnessSlider
                    from: 0
                    to: 100
                    value: 14
                    Layout.fillWidth: true

                    background: Rectangle {
                        x: roundnessSlider.leftPadding
                        y: roundnessSlider.topPadding + roundnessSlider.availableHeight / 2 - height / 2
                        width: roundnessSlider.availableWidth
                        height: 4
                        radius: 2
                        color: "#2A2E32"

                        Rectangle {
                            width: roundnessSlider.visualPosition * parent.width
                            height: parent.height
                            color: "#545EEE"
                            radius: 2
                        }
                    }

                    handle: Rectangle {
                        x: roundnessSlider.leftPadding + roundnessSlider.visualPosition * (roundnessSlider.availableWidth - width)
                        y: roundnessSlider.topPadding + roundnessSlider.availableHeight / 2 - height / 2
                        width: 16
                        height: 16
                        radius: 8
                        color: roundnessSlider.pressed ? "#FFFFFF" : "#DDDDDD"
                    }

                    onValueChanged: {
                        roundnessLabel.text = value.toFixed(0)
                        videoController.border_radius = Math.round(value)
                        if (!isPlaying) {
                            videoController.get_current_frame()
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
}