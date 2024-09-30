import QtQuick 6.7
import QtQuick.Effects 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Dialogs 6.7
import QtQuick.Controls.Material 6.7
import "../components"

Item {
    id: root
    width: controlPanelWidth
    height: controlPanelHeight

    readonly property int controlPanelWidth: 480
    readonly property int controlPanelHeight: 80
    readonly property int closeButtonSize: 30
    readonly property int modeButtonSize: 60
    readonly property int toolButtonSize: 40
    readonly property string backgroundColor: "#212121"
    readonly property string borderColor: "#464646"
    readonly property int borderWidth: 1
    readonly property int separatorWidth: 1
    readonly property int verticalMargin: 10
    readonly property int horizontalMargin: 40
    readonly property int layoutSpacing: 14
    property int bottomMargin: 120

    // Control panel
    Rectangle {
        id: controlPanel
        width: controlPanelWidth
        height: controlPanelHeight
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        color: backgroundColor
        radius: 14
        border.width: borderWidth
        border.color: borderColor

        Item {
            anchors.fill: parent
            anchors.leftMargin: 0
            anchors.rightMargin: horizontalMargin
            anchors.topMargin: verticalMargin
            anchors.bottomMargin: verticalMargin

            RowLayout {
                anchors.fill: parent

                // Drag indicator
                Item {
                    Layout.fillHeight: true
                    Layout.preferredWidth: horizontalMargin

                    Rectangle {
                        id: dragIndicator
                        anchors.fill: parent
                        color: "transparent"

                        Column {
                            anchors.centerIn: parent
                            spacing: 4

                            Image {
                                source: "qrc:/resources/icons/drag_indicator.svg"
                                width: 20
                                height: 20
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        drag.target: root
                        drag.axis: Drag.XAndYAxis
                        drag.minimumX: 0
                        drag.minimumY: 0
                    }
                }

                Item {
                    Layout.fillHeight: true
                    Layout.minimumWidth: modeButtonSize * 3 + layoutSpacing * 2

                    Row {
                        anchors.fill: parent
                        spacing: layoutSpacing

                        ModeButton {
                            id: customButton
                            text: "Custom"
                            iconPath: "qrc:/resources/icons/custom.svg"
                            toolTipText: "Area Selection"
                            onClicked: {
                                customButton.activated = true
                                screenButton.activated = false
                                safeAreaButton.activated = false
                                startupWindow.selectedMode = "custom"
                            }
                            width: modeButtonSize
                            height: modeButtonSize
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
                                safeAreaButton.activated = false
                                startupWindow.selectedMode = "screen"
                            }
                            width: modeButtonSize
                            height: modeButtonSize
                        }

                        ModeButton {
                            id: safeAreaButton
                            text: "Safe Area"
                            iconPath: "qrc:/resources/icons/safe_area.svg"
                            toolTipText: "Safe Area Selection"
                            onClicked: {
                                customButton.activated = false
                                screenButton.activated = false
                                safeAreaButton.activated = true
                                startupWindow.selectedMode = "safeArea"
                            }
                            width: modeButtonSize
                            height: modeButtonSize
                        }

                        // MonitorComboBox {
                        //     id: monitorComboBox
                        //     text: "Monitor 1"
                        //     iconPath: "qrc:/resources/icons/monitor.svg"
                        //     toolTipText: "Choose Monitor"
                        //     width: modeButtonSize
                        //     height: modeButtonSize
                        // }
                    }
                }

                // Add a vertical separator
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        anchors.centerIn: parent
                        width: 1
                        height: parent.height - 10
                        color: borderColor
                    }
                }

                Item {
                    Layout.fillHeight: true
                    Layout.minimumWidth: recordButton.width + browseButton.width + layoutSpacing

                    Row {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: layoutSpacing

                        // Record button
                        RecordButton {
                            id: recordButton
                            width: root.toolButtonSize
                            height: root.toolButtonSize
                            icon.width: 28
                            icon.height: 28

                            onClicked: {
                                var region = "screen";
                                if (startupWindow.selectedMode === "custom") {
                                    region = [customSelector.customRegionX, customSelector.customRegionY,
                                            customSelector.customRegionWidth, customSelector.customRegionHeight];
                                } else if (startupWindow.selectedMode === "screen") {
                                    region = [startupWindow.x, startupWindow.y, startupWindow.width, startupWindow.height];
                                } else if (startupWindow.selectedMode === "safeArea") {
                                    region = [windowController.left, windowController.top,
                                            Screen.desktopAvailableWidth, Screen.desktopAvailableHeight];
                                }
                                logger.debug("Selected region:" + region)
                                videoRecorder.region = region;
                                countdownLoader.source = "";
                                countdownLoader.source = "qrc:/qml/countdown/Countdown.qml";
                                startupWindow.hide();
                            }
                        }

                        // Browse button
                        ToolButton {
                            id: browseButton
                            width: root.toolButtonSize
                            height: root.toolButtonSize
                            anchors.verticalCenter: recordButton.verticalCenter
                            icon.source: "qrc:/resources/icons/folder.svg"
                            icon.color: "#e8eaed"
                            icon.width: 24
                            icon.height: 24

                            onClicked: {
                                startupWindow.hide();
                                videoFileDialog.open();
                            }
                            // background: Rectangle {
                            //     radius: 8
                            //     color: browseButton.hovered ? "#242424" : "#212121"
                            // }
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
                color: closeButton.hovered ? Qt.lighter("#393939", 1.2) : "#393939"
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
        source: controlPanel
        anchors.fill: controlPanel
        shadowBlur: 1.0
        shadowEnabled: true
        shadowColor: "black"
        shadowVerticalOffset: 0
        shadowHorizontalOffset: 0
    }
}