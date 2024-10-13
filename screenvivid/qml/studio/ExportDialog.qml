import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls.Material 6.7

Dialog {
    id: root
    title: "Export"
    width: Screen.width * 0.4
    height: Screen.height * 0.5

    x: (parent.width - width) / 2
    y: (parent.height - height) / 2

    modal: false
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property color accentColor: "#545EEE"
    property color backgroundColor: "#808080"
    property var outputSize
    property string currentSize: determineCurrentSize()
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
        '2K': {
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

    property string exportFormat: "MP4"
    property string codec: "MPEG4"
    property int exportFps: 30
    property string exportCompression: "Studio"

    property int estimatedExportTime: -1

    signal exportProgress(real progress)
    signal exportFinished

    function determineCurrentSize() {
        var screenWidth = Screen.width * Screen.devicePixelRatio
        var screenHeight = Screen.height * Screen.devicePixelRatio

        if (screenWidth >= 3840 || screenHeight >= 2160) {
            return "4K"
        } else if (screenWidth >= 2560 || screenHeight >= 1440) {
            return "2k"
        } else if (screenWidth >= 1920 || screenHeight >= 1080) {
            return "1080p"
        } else {
            return "720p"
        }
    }

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

    function formatTime(seconds) {
        var h = Math.floor(seconds / 3600);
        var m = Math.floor((seconds % 3600) / 60);
        var s = Math.floor(seconds % 60);

        var timeString = "";
        if (h > 0) {
            timeString += h + "h ";
        }
        if (m > 0) {
            timeString += m + "m ";
        }
        timeString += s + "s";

        return timeString.trim();
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
                            model: ["MP4"]
                            currentIndex: 0
                            onCurrentTextChanged: exportFormat = currentText
                            width: 120
                            height: 30

                            background: Rectangle {
                                color: formatComboBox.pressed ? "#2c313c" : "#1e2228"
                                border.color: formatComboBox.pressed ? "#3d4450" : "#2c313c"
                                border.width: 1
                                implicitWidth: 120
                                radius: 5
                            }

                            contentItem: Text {
                                text: formatComboBox.displayText
                                color: "#ecf0f1"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 10
                            }

                            delegate: ItemDelegate {
                                width: formatComboBox.width
                                contentItem: Text {
                                    text: modelData
                                    color: "#e8eaed"
                                    font: formatComboBox.font
                                    elide: Text.ElideNone
                                    verticalAlignment: Text.AlignVCenter
                                    width: parent.width
                                    clip: true
                                }
                                highlighted: formatComboBox.highlightedIndex === index
                                background: Rectangle {
                                    color: highlighted ? "#3d4450" : "#1e2228"
                                }
                            }

                            popup: Popup {
                                y: formatComboBox.height
                                width: formatComboBox.width
                                implicitHeight: contentItem.implicitHeight
                                padding: 1

                                contentItem: ListView {
                                    clip: true
                                    implicitHeight: contentHeight
                                    model: formatComboBox.popup.visible ? formatComboBox.delegateModel : null
                                    currentIndex: formatComboBox.highlightedIndex

                                    ScrollIndicator.vertical: ScrollIndicator { }
                                }

                                background: Rectangle {
                                    border.color: "#3d4450"
                                    color: "#1e2228"
                                    radius: 4
                                }
                            }
                        }
                    }

                    RowLayout {
                        Text {
                            text: "Codec"
                            color: "white"
                        }
                        ComboBox {
                            id: codecComboBox
                            model: ["H264", "MPEG4"]
                            currentIndex: 0
                            onCurrentTextChanged: codec = currentText
                            width: 120
                            height: 30

                            background: Rectangle {
                                color: codecComboBox.pressed ? "#2c313c" : "#1e2228"
                                border.color: codecComboBox.pressed ? "#3d4450" : "#2c313c"
                                border.width: 1
                                implicitWidth: 120
                                radius: 5
                            }

                            contentItem: Text {
                                text: codecComboBox.displayText
                                color: "#ecf0f1"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 10
                            }

                            delegate: ItemDelegate {
                                width: codecComboBox.width
                                contentItem: Text {
                                    text: modelData
                                    color: "#e8eaed"
                                    font: codecComboBox.font
                                    elide: Text.ElideNone
                                    verticalAlignment: Text.AlignVCenter
                                    width: parent.width
                                    clip: true
                                }
                                highlighted: codecComboBox.highlightedIndex === index
                                background: Rectangle {
                                    color: highlighted ? "#3d4450" : "#1e2228"
                                }
                            }

                            popup: Popup {
                                y: codecComboBox.height
                                width: codecComboBox.width
                                implicitHeight: contentItem.implicitHeight
                                padding: 1

                                contentItem: ListView {
                                    clip: true
                                    implicitHeight: contentHeight
                                    model: codecComboBox.popup.visible ? codecComboBox.delegateModel : null
                                    currentIndex: codecComboBox.highlightedIndex

                                    ScrollIndicator.vertical: ScrollIndicator { }
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

                RowLayout {
                    Text {
                        text: "Output Size"
                        color: "white"
                    }

                    RadioButton {
                        text: "720p"
                        checked: currentSize == "720p"
                        onCheckedChanged: if (checked)
                                              currentSize = "720p"
                    }
                    RadioButton {
                        text: "1080p"
                        checked: currentSize == "1080p"
                        onCheckedChanged: if (checked)
                                              currentSize = "1080p"
                    }
                    RadioButton {
                        text: "2K"
                        checked: currentSize == "2K"
                        onCheckedChanged: if (checked)
                                              currentSize = "2K"
                    }
                    RadioButton {
                        text: "4K"
                        checked: currentSize == "4K"
                        onCheckedChanged: if (checked)
                                              currentSize = "4K"
                    }
                }

                Text {
                    text: outputSize ? outputSize[0] + "px x " + outputSize[1] + "px" : ""
                    color: "gray"
                }

                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    Button {
                        text: "Export to file"
                        highlighted: true
                        enabled: !isExporting

                        background: Rectangle {
                            color: parent.pressed ? Qt.darker(root.accentColor, 1.2) :
                                parent.hovered ? Qt.lighter(root.accentColor, 1.1) : root.accentColor
                            radius: 8
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "#FFFFFF"
                            Layout.alignment: Qt.AlignVCenter
                        }

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
                                "output_path": outputPath,
                                "icc_profile": screenRecorder.icc_profile,
                                "codec": codec.toLowerCase(),
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

                    Button {
                        text: "Cancel"

                        background: Rectangle {
                            color: parent.pressed ? Qt.darker(root.backgroundColor, 1.2) :
                                parent.hovered ? Qt.lighter(root.backgroundColor, 1.1) : root.backgroundColor
                            radius: 8
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                        onClicked: {
                            videoController.cancel_export()
                            root.close()
                        }
                    }
                }

                Text {
                    id: estimatedTimeText
                    text: {
                        var estimatedTimeText = ""
                        if (estimatedExportTime < 0) estimatedTimeText = "Calculating..."
                        else estimatedTimeText = formatTime(estimatedExportTime)
                        "Estimated export time: " + estimatedTimeText
                    }
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

                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(root.backgroundColor, 1.2) :
                            parent.hovered ? Qt.lighter(root.backgroundColor, 1.1) : root.backgroundColor
                        radius: 8
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }

                    onClicked: {
                        videoController.cancel_export()
                        exportProgressBar.visible = false
                        cancelExportButton.visible = false
                        root.close()
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
                    text: {
                        var basePath = (Qt.platform.os === "osx") ? "~/Movies" : "~/Videos";
                        return `${basePath}/ScreenVivid/${outputPath}.${exportFormat.toLowerCase()}`;
                    }
                    color: "white"
                    font.pixelSize: 14
                    Layout.alignment: Qt.AlignHCenter
                }

                Button {
                    text: "Close"
                    Layout.alignment: Qt.AlignHCenter

                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(root.backgroundColor, 1.2) :
                            parent.hovered ? Qt.lighter(root.backgroundColor, 1.1) : root.backgroundColor
                        radius: 8
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }

                    onClicked: root.close()
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
        estimatedExportTime = -1
    }
}
