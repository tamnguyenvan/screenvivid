import QtQuick

Rectangle {
    id: preview
    property string gradientType
    property var gradientColors
    property real gradientAngle

    Gradient {
        id: linearGradient
        orientation: (gradientAngle / 360 + 1)
        GradientStop { position: 0.0; color: gradientColors[0] }
        GradientStop { position: 1.0; color: gradientColors[1] }
    }
    gradient: gradientType === "LinearGradient" ? linearGradient : null
}