import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property var gradientColors: ["#4A249D", "#009FBD"]
    property real gradientAngle: 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        Rectangle {
            id: gradientPreview
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            radius: 8

            gradient: Gradient {
                orientation: (gradientAngle / 360 + 1)
                GradientStop { position: 0.0; color: gradientColors[0] }
                GradientStop { position: 1.0; color: gradientColors[1] }
            }
        }

        GridLayout {
            columns: 2
            Layout.fillWidth: true
            rowSpacing: 15
            columnSpacing: 10

            Label {
                text: "Angle:"
                color: "#AAAAAA"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Slider {
                    id: angleSlider
                    Layout.fillWidth: true
                    from: 0
                    to: 360
                    value: gradientAngle
                    stepSize: 1

                    background: Rectangle {
                        x: angleSlider.leftPadding
                        y: angleSlider.topPadding + angleSlider.availableHeight / 2 - height / 2
                        width: angleSlider.availableWidth
                        height: 4
                        radius: 2
                        color: "#2A2E32"

                        Rectangle {
                            width: angleSlider.visualPosition * parent.width
                            height: parent.height
                            color: "#3A7BED"
                            radius: 2
                        }
                    }

                    handle: Rectangle {
                        x: angleSlider.leftPadding + angleSlider.visualPosition * (angleSlider.availableWidth - width)
                        y: angleSlider.topPadding + angleSlider.availableHeight / 2 - height / 2
                        width: 16
                        height: 16
                        radius: 8
                        color: angleSlider.pressed ? "#FFFFFF" : "#DDDDDD"
                    }

                    onValueChanged: gradientAngle = value
                }

                Label {
                    text: gradientAngle.toFixed(0) + "°"
                    color: "#FFFFFF"
                    font.pixelSize: 14
                }
            }

            Label {
                text: "Start Color:"
                color: "#AAAAAA"
            }
            Rectangle {
                width: 50
                height: 30
                color: gradientColors[0]
                radius: 4
                MouseArea {
                    anchors.fill: parent
                    onClicked: colorDialog1.open()
                    cursorShape: Qt.PointingHandCursor
                }
            }

            Label {
                text: "End Color:"
                color: "#AAAAAA"
            }
            Rectangle {
                width: 50
                height: 30
                color: gradientColors[1]
                radius: 4
                MouseArea {
                    anchors.fill: parent
                    onClicked: colorDialog2.open()
                    cursorShape: Qt.PointingHandCursor
                }
            }
        }

        Button {
            text: qsTr("Apply")
            Layout.alignment: Qt.AlignCenter
            implicitWidth: 120
            implicitHeight: 40

            contentItem: Text {
                text: parent.text
                font: parent.font
                color: "#FFFFFF"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                color: parent.down ? "#2A5CA8" : "#3A7BED"
                radius: 8
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    videoController.background = {
                        "type": "gradient",
                        "value": {
                            "colors": gradientColors,
                            "angle": gradientAngle
                        }
                    }
                    if (!isPlaying) {
                        videoController.get_current_frame()
                    }
                }
            }
        }
    }

    ColorDialog {
        id: colorDialog1
        title: "Choose first color"
        onAccepted: {
            gradientColors = [colorToHexString(selectedColor), gradientColors[1]]
        }
    }

    ColorDialog {
        id: colorDialog2
        title: "Choose second color"
        onAccepted: {
            gradientColors = [gradientColors[0], colorToHexString(selectedColor)]
        }
    }

    function colorToHexString(color) {
        return "#" + Qt.rgba(color.r, color.g, color.b, 1).toString().substr(1, 6)
    }
}