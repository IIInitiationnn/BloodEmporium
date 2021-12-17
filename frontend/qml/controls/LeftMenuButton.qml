import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: leftMenuButton
    text: qsTr("Text")

    property color textColor: "#ffffff"
    property url iconSource: "../../images/icons/icon_home.png"
    property color defaultColor: "#21252b"
    property color mouseOverColor: "#282c34"
    property color clickedColor: "#ff79c6"
    property int iconWidth: 30
    property int iconHeight: 30
    property bool menuIsActive: false

    QtObject {
        id: internal
        property var dynamicColor: if (leftMenuButton.down) {
                                       clickedColor
                                   } else if (leftMenuButton.hovered) {
                                       mouseOverColor
                                   } else {
                                       defaultColor
                                   }
    }


    implicitWidth: 250
    implicitHeight: 60

    background: Rectangle {
        id: buttonBackground
        color: internal.dynamicColor
    }

    contentItem: Item {
        anchors.fill: parent
        id: content

        Rectangle {
            width: 3
            color: "#ff79c6"
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 0
            anchors.bottomMargin: 0
            anchors.topMargin: 0
            visible: menuIsActive
        }

        Rectangle {
            width: 5
            color: "#282a36"
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 0
            anchors.bottomMargin: 0
            anchors.topMargin: 0
            visible: menuIsActive
        }

        Image {
            id: buttonIcon
            source: iconSource
            anchors.leftMargin: (70 - iconWidth) / 2
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            sourceSize.width: iconWidth
            sourceSize.height: iconHeight
            width: iconWidth
            height: iconHeight
            fillMode: Image.PreserveAspectFit
            antialiasing: true
        }

        Text {
            color: textColor
            text: leftMenuButton.text
            font.family: "Segoe UI"
            font.pointSize: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 75
        }

    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:3}
}
##^##*/
