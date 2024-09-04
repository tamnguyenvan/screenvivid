import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Controls.Material

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property var gradientColors: ["#4A249D", "#009FBD"]
    property string gradientType: "LinearGradient"
    property real gradientAngle: 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 4

        // Preview
        Rectangle {
            id: gradientPreview
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            radius: 4

            Gradient {
                id: linearGradient
                orientation: (gradientAngle / 360 + 1)
                GradientStop {
                    position: 0.0
                    color: gradientColors[0]
                }
                GradientStop {
                    position: 1.0
                    color: gradientColors[1]
                }
            }
            gradient: gradientType === "LinearGradient" ? linearGradient : null
        }

        // Options
        GridLayout {
            columns: 2
            Layout.fillWidth: true
            Layout.preferredHeight: 30

            Label {
                text: "Angle:"
            }

            SpinBox {
                Layout.fillWidth: true
                Layout.preferredHeight: 30
                from: 0
                to: 360
                value: gradientAngle
                stepSize: 1
                editable: true

                onValueChanged: gradientAngle = value
            }

            Label {
                text: "Start Color:"
            }
            Rectangle {
                width: 50
                height: 30
                color: gradientColors[0]
                radius: 4
                MouseArea {
                    anchors.fill: parent
                    onClicked: colorDialog1.open()
                }
            }

            Label {
                text: "End Color:"
            }
            Rectangle {
                width: 50
                height: 30
                color: gradientColors[1]
                radius: 4
                MouseArea {
                    anchors.fill: parent
                    onClicked: colorDialog2.open()
                }
            }
        }

        // Apply
        Item {
            Layout.fillWidth: true

            Button {
                anchors.centerIn: parent
                text: qsTr("Apply")
                Layout.alignment: Qt.AlignCenter
                Material.background: studioWindow.accentColor

                // onClicked: {
                //     videoController.background = {
                //         "type": "gradient",
                //         "value": {
                //             "colors": gradientColors,
                //             "angle": gradientAngle
                //         }
                //     }
                //     if (!isPlaying) {
                //         videoController.get_current_frame()
                //     }
                // }

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
    }

    ColorDialog {
        id: colorDialog1
        title: "Choose first color"
        onAccepted: {
            gradientColors = [colorToHexString(
                                  selectedColor), gradientColors[1]]
        }
    }

    ColorDialog {
        id: colorDialog2
        title: "Choose second color"
        onAccepted: {
            gradientColors = [gradientColors[0], colorToHexString(
                                  selectedColor)]
        }
    }

    function colorToHexString(color) {
        return "#" + Qt.rgba(color.r, color.g, color.b,
                             1).toString().substr(1, 6)
    }
}
