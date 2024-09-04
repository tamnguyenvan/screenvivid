import QtQuick
import QtQuick.Controls

Item {
    id: customSelector
    anchors.fill: parent

    property int customRegionX: (Screen.width - customRegionWidth) / 2
    property int customRegionY: (Screen.height - customRegionHeight) / 2
    property int customRegionWidth: Screen.width / 2
    property int customRegionHeight: Screen.height / 2

    readonly property int minSize: 50
    readonly property int rulerSize: 20
    readonly property int borderWidth: 2
    readonly property string color: "#e85c0d"

    Rectangle {
        id: background
        x: Screen.width * 0.25
        y: Screen.height * 0.25
        width: Screen.width / 2
        height: Screen.height / 2
        // color: "transparent"
        color: Qt.rgba(0.91, 0.36, 0.05, 0.3)
        border.width: customSelector.borderWidth
        border.color: customSelector.color

        // Drag area
        MouseArea {     // drag mouse area
            anchors.fill: parent
            drag {
                target: parent
                minimumX: 0
                minimumY: 0
                maximumX: customSelector.width - parent.width
                maximumY: customSelector.height - parent.height
                smoothed: true
            }

            onPositionChanged: {
                if (background.x < 0) background.x = 0
                if (background.y < 0) background.y = 0
                if (background.x + background.width > customSelector.width) background.x = customSelector.width - background.width
                if (background.y + background.height > customSelector.height) background.y = customSelector.height - background.height

                customRegionX = background.x
                customRegionY = background.y
            }
        }

        // Top left anchor
        Rectangle {
            id: customRegionLeftTop
            width: customSelector.rulerSize
            height: customSelector.rulerSize
            color: customSelector.color
            anchors.left: parent.left
            anchors.top: parent.top
            // radius: width / 2

            MouseArea {
                anchors.fill: parent
                cursorShape: drag.active ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                drag {
                    target: parent
                    smoothed: true
                }
                onMouseXChanged: {
                    if(drag.active){
                        background.width = background.width - mouseX
                        background.height = background.height - mouseY
                        background.x = background.x + mouseX
                        background.y = background.y + mouseY

                        if (background.width < customSelector.minSize)
                            background.width = customSelector.minSize

                        if (background.height < customSelector.minSize)
                            background.height = customSelector.minSize

                        if (background.x < 0) background.x = 0
                        if (background.y < 0) background.y = 0

                        if (background.x + background.width > customSelector.width) background.width = customSelector.width - background.x
                        if (background.y + background.height > customSelector.height) background.height = customSelector.height - background.y

                        customRegionX = background.x
                        customRegionY = background.y
                        customRegionWidth = background.width
                        customRegionHeight = background.height
                    }
                }
            }
        }

        // Top right anchor
        Rectangle {
            id: customRegionRightTop
            width: customSelector.rulerSize
            height: customSelector.rulerSize
            color: customSelector.color
            // radius: width / 2
            anchors.right: parent.right
            anchors.top: parent.top

            MouseArea {
                anchors.fill: parent
                cursorShape: drag.active ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                drag {
                    target: parent
                    smoothed: true
                }
                onMouseXChanged: {
                    if(drag.active){
                        background.width = background.width + mouseX
                        background.y = background.y + mouseY
                        background.height = background.height - mouseY

                        if (background.width < customSelector.minSize)
                            background.width = customSelector.minSize

                        if (background.height < customSelector.minSize)
                            background.height = customSelector.minSize

                        if (background.x < 0) background.x = 0
                        if (background.y < 0) background.y = 0
                        if (background.x + background.width > customSelector.width) background.width = customSelector.width - background.x
                        if (background.y + background.height > customSelector.height) background.height = customSelector.height - background.y

                        customRegionX = background.x
                        customRegionY = background.y
                        customRegionWidth = background.width
                        customRegionHeight = background.height
                    }
                }
            }
        }

        // Right bottom anhcor
        Rectangle {
            id: customRegionRightBottom
            width: customSelector.rulerSize
            height: customSelector.rulerSize
            color: customSelector.color
            // radius: width / 2
            anchors.right: parent.right
            anchors.bottom: parent.bottom

            MouseArea {
                anchors.fill: parent
                cursorShape: drag.active ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                drag {
                    target: parent
                    smoothed: true
                }
                onMouseXChanged: {
                    if(drag.active){
                        background.width = background.width + mouseX
                        background.height = background.height + mouseY

                        if (background.width < customSelector.minSize)
                            background.width = customSelector.minSize

                        if (background.height < customSelector.minSize)
                            background.height = customSelector.minSize

                        if (background.x < 0) background.x = 0
                        if (background.y < 0) background.y = 0
                        if (background.x + background.width > customSelector.width) background.width = customSelector.width - background.x
                        if (background.y + background.height > customSelector.height) background.height = customSelector.height - background.y

                        customRegionX = background.x
                        customRegionY = background.y
                        customRegionWidth = background.width
                        customRegionHeight = background.height
                    }
                }
            }
        }

        // Left bottom anchor
        Rectangle {
            id: customRegionLeftBottom
            width: customSelector.rulerSize
            height: customSelector.rulerSize
            color: customSelector.color
            // radius: width / 2
            anchors.left: parent.left
            anchors.bottom: parent.bottom

            MouseArea {
                anchors.fill: parent
                cursorShape: drag.active ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                drag {
                    target: parent
                    smoothed: true
                }
                onMouseXChanged: {
                    if(drag.active){
                        background.width = background.width - mouseX
                        background.x = background.x + mouseX
                        background.height = background.height + mouseY

                        if (background.width < customSelector.minSize)
                            background.width = customSelector.minSize

                        if (background.height < customSelector.minSize)
                            background.height = customSelector.minSize

                        if (background.x + background.width > customSelector.width) background.width = customSelector.width - background.x
                        if (background.y + background.height > customSelector.height) background.height = customSelector.height - background.y

                        customRegionX = background.x
                        customRegionY = background.y
                        customRegionWidth = background.width
                        customRegionHeight = background.height
                    }
                }
            }
        }
    }
}
