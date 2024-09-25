import QtQuick 6.7
import QtQuick.Effects 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Dialogs 6.7
import QtQuick.Controls.Material 6.7
import "../components"

Item {
    id: root
    width: homeWidth
    height: homeHeight
    anchors.bottom: parent.bottom
    anchors.bottomMargin: bottomMargin
    anchors.horizontalCenter: parent.horizontalCenter

    readonly property int homeWidth: 420
    readonly property int homeHeight: 80
    readonly property int closeButtonSize: 30
    readonly property int modeButtonSize: 60
    readonly property int toolButtonSize: 50
    readonly property string backgroundColor: "#1c1c1c"
    readonly property string borderColor: "#464646"
    readonly property int borderWidth: 1
    property int bottomMargin: 40

    // Control panel
    Rectangle {
        id: home
        width: parent.homeWidth
        height: parent.homeHeight
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        color: backgroundColor
        radius: 14
        border.width: borderWidth
        border.color: borderColor

        Item {
            anchors.fill: parent
            anchors.leftMargin: 30
            anchors.rightMargin: 30
            anchors.topMargin: 10
            anchors.bottomMargin: 10

            RowLayout {
                anchors.fill: parent
                spacing: 2

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    RowLayout {
                        anchors.fill: parent
                        spacing: 10
                        ModeButton {
                            id: customButton
                            text: "Custom"
                            iconPath: "qrc:/resources/icons/custom.svg"
                            toolTipText: "Area Selection"
                            onClicked: {
                                customButton.activated = true
                                screenButton.activated = false
                                windowButton.activated = false
                                startupWindow.selectedMode = "custom"
                            }
                            Layout.preferredWidth: modeButtonSize
                            Layout.preferredHeight: modeButtonSize
                        }

                        ModeButton {
                            id: screenButton
                            text: "Screen"
                            iconPath: "qrc:/resources/icons/screen.svg"
                            toolTipText: "Screen Selection"
                            activated: true
                            onClicked: {
                                customButton.activated = false
                                screenButton.activated = true
                                windowButton.activated = false
                                startupWindow.selectedMode = "screen"
                            }
                            Layout.preferredWidth: modeButtonSize
                            Layout.preferredHeight: modeButtonSize
                        }

                        ModeButton {
                            id: windowButton
                            text: "Safe Area"
                            iconPath: "qrc:/resources/icons/window.svg"
                            toolTipText: "Safe Area Selection"
                            onClicked: {
                                customButton.activated = false
                                screenButton.activated = false
                                windowButton.activated = true
                                startupWindow.selectedMode = "window"
                            }
                            Layout.preferredWidth: modeButtonSize
                            Layout.preferredHeight: modeButtonSize
                        }
                    }
                }

                // Record button
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    RowLayout {
                        anchors.fill: parent
                        spacing: 20

                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                        }

                        RecordButton {
                            id: recordButton
                            Layout.preferredWidth: root.toolButtonSize
                            Layout.preferredHeight: root.toolButtonSize
                            Layout.alignment: Qt.AlignCenter

                            onClicked: {
                                var region;
                                if (startupWindow.selectedMode === "custom") {
                                    region = [customSelector.customRegionX, customSelector.customRegionY,
                                            customSelector.customRegionWidth, customSelector.customRegionHeight];
                                } else if (startupWindow.selectedMode === "screen") {
                                    region = [startupWindow.x, startupWindow.y, startupWindow.width, startupWindow.height];
                                } else if (startupWindow.selectedMode === "window") {
                                    region = [windowController.left, windowController.top,
                                            Screen.desktopAvailableWidth, Screen.desktopAvailableHeight];
                                }
                                videoRecorder.region = region;
                                countdownLoader.source = "";
                                countdownLoader.source = "qrc:/qml/countdown/Countdown.qml";
                                startupWindow.hide();
                            }
                        }

                        // Browse button
                        ToolButton {
                            id: browseButton
                            Layout.preferredWidth: root.toolButtonSize
                            Layout.preferredHeight: root.toolButtonSize
                            Layout.alignment: Qt.AlignCenter
                            icon.source: "qrc:/resources/icons/folder.svg"
                            icon.color: "#e8eaed"
                            icon.width: 26
                            icon.height: 26

                            background: Rectangle {
                                radius: width / 2
                                color: browseButton.hovered ? "#242424" : "#212121"
                            }

                            onClicked: {
                                startupWindow.hide();
                                videoFileDialog.open();
                            }
                        }
                    }
                }
            }
        }
    }

    Button {
        id: closeButton
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.leftMargin: -width / 2
        anchors.topMargin: -height / 2
        width: root.closeButtonSize
        height: root.closeButtonSize
        z: 1

        background: Item {
            anchors.fill: parent
            Rectangle {
                anchors.fill: parent
                radius: root.closeButtonSize / 2
                color: closeButton.hovered ? Qt.lighter("#393939",
                                                        1.2) : "#393939"
                border.width: 1
                border.color: "#404040"
            }
            Image {
                anchors.centerIn: parent
                source: "qrc:/resources/icons/close.svg"
                width: parent.width / 2
                height: parent.height / 2
            }
        }

        onClicked: Qt.quit()
    }

    MultiEffect {
        source: home
        anchors.fill: home
        shadowBlur: 1.0
        shadowEnabled: true
        shadowColor: "black"
        shadowVerticalOffset: 0
        shadowHorizontalOffset: 0
    }
}