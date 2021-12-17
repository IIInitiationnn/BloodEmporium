import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: toggleButton

    property url iconSource: "../../images/icons/icon_menu.png"
    property color defaultColor: "#21252b"
    property color mouseOverColor: "#282c34"
    property color clickedColor: "#bd93f9"

    QtObject {
        id: internal
        property var dynamicColor: if (toggleButton.down) {
                                       clickedColor
                                   } else if (toggleButton.hovered) {
                                       mouseOverColor
                                   } else {
                                       defaultColor
                                   }
    }


    implicitWidth: 70
    implicitHeight: 60

    background: Rectangle {
        id: buttonBackground
        color: internal.dynamicColor
    }

    contentItem: Item {
        Image {
            id: buttonIcon
            source: iconSource
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 30
            width: 30
            fillMode: Image.PreserveAspectFit
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:8}
}
##^##*/
