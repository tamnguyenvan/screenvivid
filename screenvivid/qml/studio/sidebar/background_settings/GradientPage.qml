import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Dialogs 6.7

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredHeight: 200

    property var gradientColors: ["#8B5CF6", "#545EEE"]
    property real gradientAngle: 0
    readonly property color accentColor: "#545EEE"
    readonly property color accentColorLight: "#7778FF"

    ColumnLayout {
        anchors.fill: parent
        spacing: 15

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Left column: Color controls
            GridLayout {
                Layout.preferredWidth: parent.width * 0.6
                columns: 2

                // Start Color
                Label {
                    text: "Start Color:"
                    color: "#AAAAAA"
                }
                Rectangle {
                    width: 50
                    height: 25
                    color: gradientColors[0]
                    radius: 4
                    MouseArea {
                        anchors.fill: parent
                        onClicked: colorDialog1.open()
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                // End Color
                Label {
                    text: "End Color:"
                    color: "#AAAAAA"
                }
                Rectangle {
                    width: 50
                    height: 25
                    color: gradientColors[1]
                    radius: 4
                    MouseArea {
                        anchors.fill: parent
                        onClicked: colorDialog2.open()
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                // Angle Slider
                Label {
                    text: "Angle: " + gradientAngle.toFixed(0) + "°"
                    color: "#AAAAAA"
                }
                Slider {
                    id: angleSlider
                    Layout.fillWidth: true
                    from: 0
                    to: 360
                    value: gradientAngle
                    stepSize: 1
                    onValueChanged: gradientAngle = value
                }
            }

            // Right column: Gradient Preview
            Rectangle {
                id: gradientPreview
                Layout.preferredWidth: parent.width * 0.3
                Layout.preferredHeight: width
                radius: 8

                gradient: Gradient {
                    orientation: (gradientAngle / 360 + 1)
                    GradientStop { position: 0.0; color: gradientColors[0] }
                    GradientStop { position: 1.0; color: gradientColors[1] }
                }
            }
        }

        // Apply Button
        Button {
            id: applyButton
            text: qsTr("Apply")
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 120
            Layout.preferredHeight: 50

            contentItem: Text {
                text: parent.text
                font: parent.font
                color: "#FFFFFF"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                radius: 8
                gradient: Gradient {
                    GradientStop { position: 0.0; color: applyButton.pressed ? Qt.darker(root.accentColor, 1.4) :
                                                         applyButton.hovered ? Qt.darker(root.accentColor, 1.2) : root.accentColor }
                    GradientStop { position: 1.0; color: applyButton.pressed ? Qt.darker(root.accentColorLight, 1.2) :
                                                         applyButton.hovered ? Qt.darker(root.accentColorLight, 1.1) : root.accentColorLight }
                }
                Behavior on gradient {
                    ColorAnimation { duration: 150 }
                }
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
        title: "Choose start color"
        onAccepted: {
            gradientColors = [colorToHexString(selectedColor), gradientColors[1]]
        }
    }

    ColorDialog {
        id: colorDialog2
        title: "Choose end color"
        onAccepted: {
            gradientColors = [gradientColors[0], colorToHexString(selectedColor)]
        }
    }

    function colorToHexString(color) {
        return "#" + Qt.rgba(color.r, color.g, color.b, 1).toString().substr(1, 6)
    }
}