import QtQuick 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls 6.7

ColumnLayout {
    Layout.fillWidth: true
    Layout.fillHeight: true
    Layout.minimumHeight: 400
    Layout.minimumWidth: 400

    VideoPreview {
        Layout.fillWidth: true
        Layout.fillHeight: true
    }

    ControlButtons {
        Layout.fillWidth: true
        Layout.preferredHeight: 50
    }
}
