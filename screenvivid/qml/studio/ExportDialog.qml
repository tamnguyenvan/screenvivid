import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Dialog {
    id: exportDialog
    title: "Export"
    width: Screen.width * 0.4
    height: Screen.height * 0.5

    x: (parent.width - width) / 2
    y: (parent.height - height) / 2

    modal: false
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property var outputSize
    property string currentSize: "1080p"
    property var sizeMap: {
        '720p': {
            '16:9': [1280, 720],
            '4:3': [960, 720],
            '1:1': [720, 720],
            '9:16': [720, 1280],
            '3:4': [720, 960]
        },
        '1080p': {
            '16:9': [1920, 1080],
            '4:3': [1440, 1080],
            '1:1': [1080, 1080],
            '9:16': [1080, 1920],
            '3:4': [1080, 1440]
        },
        '2k': {
            '16:9': [2560, 1440],
            '4:3': [1920, 1440],
            '1:1': [1440, 1440],
            '9:16': [1440, 2560],
            '3:4': [1440, 1920]
        },
        '4K': {
            '16:9': [3840, 2160],
            '4:3': [2880, 2160],
            '1:1': [2160, 2160],
            '9:16': [2160, 3840],
            '3:4': [2160, 2880]
        }
    }
    property string outputPath: ""

    // property string currentCompression: "Studio"
    // property var compressionInfo: {
    //     "Studio": {
    //         "description": "Highest quality, best for further editing. Compression is almost impossible to notice.",
    //         "impact": "Quality setting does not impact export speed."
    //     },
    //     "Social Media": {
    //         "description": "High quality, optimized for social media platforms. Slight compression, barely noticeable.",
    //         "impact": "Quality setting may slightly reduce export time."
    //     },
    //     "Web": {
    //         "description": "Good quality, balanced for web viewing. Moderate compression, some loss in detail.",
    //         "impact": "Quality setting reduces export time and file size."
    //     },
    //     "Web (Low)": {
    //         "description": "Lower quality, optimized for fast loading. Higher compression, noticeable loss in quality.",
    //         "impact": "Quality setting significantly reduces export time and file size."
    //     }
    // }

    property string exportFormat: "MP4"
    property int exportFps: 30
    property string exportCompression: "Studio"

    property int estimatedExportTime: -1

    signal exportProgress(real progress)
    signal exportFinished

    function gcd(a, b) {
        while (b !== 0) {
            let temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    function resolutionToAspectRatio(width, height) {
        const divisor = gcd(width, height);
        const aspectWidth = width / divisor;
        const aspectHeight = height / divisor;
        return `${aspectWidth}:${aspectHeight}`;
    }

    function updateOutputSize() {
        var aspectRatio = videoController.aspect_ratio ? videoController.aspect_ratio : "auto";

        if (aspectRatio === "auto") {
            outputSize = videoController.output_size
            aspectRatio = resolutionToAspectRatio(outputSize[0], outputSize[1])
        }

        var size = sizeMap[currentSize] && sizeMap[currentSize][aspectRatio];
        if (size) {
            outputSize = size
        }
    }

    function updateEstimatedTime(progress) {
        if (progress > 0) {
            var elapsedTime = (new Date().getTime() - startTime) / 1000;
            estimatedExportTime = Math.round((elapsedTime / progress) * (100 - progress));
        }
    }

    onCurrentSizeChanged: updateOutputSize()

    Connections {
        target: videoController
        function onAspectRatioChanged() { updateOutputSize() }
    }

    background: Rectangle {
        color: "#1E1E1E"
        radius: 10
        border.color: "#3E3E3E"
        border.width: 1
    }

    property bool isExporting: false

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 10

        Item {
            id: exportContainer
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: true

            ColumnLayout {

                anchors.fill: parent
                spacing: 10

                RowLayout {
                    spacing: 50
                    RowLayout {
                        Text {
                            text: "Export as"
                            color: "white"
                        }
                        ComboBox {
                            id: formatComboBox
                            model: ["MP4", "GIF"]
                            currentIndex: 0
                            onCurrentTextChanged: exportFormat = currentText
                        }
                    }

                    // RowLayout {
                    //     Text {
                    //         text: "Frame rate"
                    //         color: "white"
                    //     }
                    //     ComboBox {
                    //         id: fpsComboBox
                    //         model: ["25 FPS", "60 FPS", "120 FPS"]
                    //         currentIndex: 0
                    //         onCurrentTextChanged: exportFps = parseInt(
                    //                                   currentText.split(" ")[0])
                    //     }
                    // }
                }

                RowLayout {
                    Text {
                        text: "Output Size"
                        color: "white"
                    }

                    RadioButton {
                        text: "720p"
                        onCheckedChanged: if (checked)
                                              currentSize = "720p"
                    }
                    RadioButton {
                        text: "1080p"
                        checked: true
                        onCheckedChanged: if (checked)
                                              currentSize = "1080p"
                    }
                    RadioButton {
                        text: "2k"
                        onCheckedChanged: if (checked)
                                              currentSize = "2k"
                    }
                    RadioButton {
                        text: "4K"
                        onCheckedChanged: if (checked)
                                              currentSize = "4K"
                    }
                }

                Text {
                    text: outputSize ? outputSize[0] + "px x " + outputSize[1] + "px" : ""
                    color: "gray"
                }

                // RowLayout {
                //     Text {
                //         text: "Quality (Compression level)"
                //         color: "white"
                //     }
                //     ComboBox {
                //         id: compressionComboBox
                //         model: ["Studio", "Social Media", "Web", "Web (Low)"]
                //         currentIndex: 0
                //         onCurrentTextChanged: {
                //             currentCompression = currentText
                //             exportCompression = currentText
                //         }
                //     }
                // }
                // Text {
                //     text: compressionInfo[currentCompression].description
                //     color: "gray"
                //     wrapMode: Text.WordWrap
                //     Layout.fillWidth: true
                // }
                // Text {
                //     text: compressionInfo[currentCompression].impact
                //     color: "gray"
                // }

                // Item {
                //     Layout.fillHeight: true
                // }

                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    Button {
                        text: "Export to file"
                        highlighted: true
                        enabled: !isExporting
                        onClicked: {
                            isExporting = true
                            startTime = new Date().getTime()

                            function getFormattedTimestamp() {
                                var now = new Date();
                                var year = now.getFullYear();
                                var month = ('0' + (now.getMonth() + 1)).slice(-2);
                                var day = ('0' + now.getDate()).slice(-2);
                                var hours = ('0' + now.getHours()).slice(-2);
                                var minutes = ('0' + now.getMinutes()).slice(-2);
                                var seconds = ('0' + now.getSeconds()).slice(-2);

                                return year + month + day + '-' + hours + minutes + seconds;
                            }
                            outputPath = 'ScreenVivid-' + getFormattedTimestamp()

                            var exportParams = {
                                "format": exportFormat.toLowerCase(),
                                "fps": exportFps,
                                "output_size": outputSize,
                                "aspect_ratio": videoController.aspect_ratio,
                                "compression_level": exportCompression,
                                "output_path": outputPath
                            }

                            if (sizeMap[currentSize][videoController.aspect_ratio]) {
                                exportParams['output_size'] = sizeMap[currentSize][videoController.aspect_ratio]
                            }
                            videoController.export_video(exportParams)
                            estimatedExportTime = 0
                            exportProgressBar.visible = true
                            cancelExportButton.visible = true
                            estimatedTimeText.visible = true
                        }
                    }
                    // Button {
                    //     text: "Copy to clipboard"
                    //     onClicked: {

                    //         // Handle copy logic
                    //     }
                    // }
                    Button {
                        text: "Cancel"
                        onClicked: {
                            videoController.cancel_export()
                            exportDialog.close()
                        }
                    }
                }

                Text {
                    // text: "Estimated export time — 6 seconds"
                    id: estimatedTimeText
                    text: "Estimated export time: " + (estimatedExportTime >= 0 ? estimatedExportTime + " seconds" : "Calculating...")
                    color: "gray"
                    visible: isExporting
                }

                ProgressBar {
                    id: exportProgressBar
                    visible: false
                    width: parent.width
                    from: 0
                    to: 100
                    value: 0
                }

                Button {
                    id: cancelExportButton
                    text: "Cancel Export"
                    visible: isExporting
                    onClicked: {
                        videoController.cancel_export()
                        exportProgressBar.visible = false
                        cancelExportButton.visible = false
                        exportDialog.close()
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
            }
        }

        Item {
            id: successContainer
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: false

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20

                Text {
                    text: 'Export Completed Successfully!'
                    color: "white"
                    font.pixelSize: 24
                    Layout.alignment: Qt.AlignHCenter
                }
                Text {
                    text: `~/Videos/ScreenVivid/${outputPath}.${exportFormat.toLowerCase()}`
                    color: "white"
                    font.pixelSize: 14
                    Layout.alignment: Qt.AlignHCenter
                }

                Button {
                    text: "Close"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: exportDialog.close()
                }
            }
        }

        Connections {
            target: videoController
            function onExportProgress(progress) {
                exportProgressBar.value = progress
                updateEstimatedTime(progress)
            }
            function onExportFinished() {
                isExporting = false
                exportContainer.visible = false
                exportProgressBar.visible = false
                cancelExportButton.visible = false
                estimatedTimeText.visible = false
                successContainer.visible = true
            }
        }
    }

    property real startTime: 0

    onClosed: {
        // Reset the dialog to its initial state
        exportContainer.visible = true
        successContainer.visible = false
        exportProgressBar.visible = false
        cancelExportButton.visible = false
        exportProgressBar.value = 0

        estimatedTimeText.visible = false
        estimatedExportTime = 0
    }
}
