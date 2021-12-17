import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: topBarButton

    property url iconSource: "../../images/icons/icon_minimize.png"
    property color defaultColor: "#21252b"
    property color mouseOverColor: "#282c34"
    property color clickedColor: "#ff79c6"

    QtObject {
        id: internal
        property var dynamicColor: if (topBarButton.down) {
                                       clickedColor
                                   } else if (topBarButton.hovered) {
                                       mouseOverColor
                                   } else {
                                       defaultColor
                                   }
    }


    implicitWidth: 35
    implicitHeight: 35

    background: Rectangle {
        id: buttonBackground
        color: internal.dynamicColor
        radius: 5
    }

    contentItem: Item {
        Image {
            id: buttonIcon
            source: iconSource
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 20
            width: 20
            fillMode: Image.PreserveAspectFit
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true}
}
##^##*/
