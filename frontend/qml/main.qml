import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import "controls"

Window {
    property var isMaximized: false
    property var isMinimized: false
    property int windowMargin: isMaximized ? 0 : 10

    id: main
    /* visibility: {
        if (isMaximized) {
            return Window.Maximized
        } else if (isMinimized) {
            return Window.Minimized
        } else {
            return Window.Windowed
        }
    } */
    width: 1000
    height: 580
    minimumWidth: 800
    minimumHeight: 500
    visible: true
    color: "#00000000"

    flags: Qt.Window | Qt.FramelessWindowHint

    // TODO the below two shortcuts - check WindowManager to see if life can be made easier
    Shortcut {
        sequence: "Meta+Up"
        onActivated: internalFunctions.maximize()
    }

    Shortcut {
        sequence: "Meta+Down"
        onActivated: {
            if (isMaximized) {
                internalFunctions.restore()
            } else {
                internalFunctions.minimize()
            }
        }
    }

    QtObject {
        id: internalFunctions

        function minimize() {
            main.showMinimized()
            isMinimized = true
        }

        function restore() {
            main.showNormal()
            isMaximized = false
        }

        function maximize() {
            main.showMaximized()
            isMaximized = true
        }

        function maximizeRestore() {
            if (isMaximized) {
                restore()
            } else {
                maximize()
            }
        }

        function resizeTop(mouseY, previousY) {
            var dy = mouseY - previousY
            if (main.height - dy >= minimumHeight) {
                main.setY(main.y + dy)
                main.setHeight(main.height - dy)
            }
        }

        function resizeBottom(mouseY, previousY) {
            var dy = mouseY - previousY
            if (main.height + dy >= minimumHeight) {
                main.setHeight(main.height + dy)
            }
        }

        function resizeLeft(mouseX, previousX) {
            var dx = mouseX - previousX
            if (main.width - dx >= minimumWidth) {
                main.setX(main.x + dx)
                main.setWidth(main.width - dx)
            }
        }


        function resizeRight(mouseX, previousX) {
            var dx = mouseX - previousX
            if (main.width + dx >= minimumWidth) {
                main.setWidth(main.width + dx)
            }
        }

    }

    DropShadow {
        anchors.fill: background
        horizontalOffset: 0
        verticalOffset: 0
        z: 0
        radius: 10
        samples: 16
        color: "#80000000"
        source: background
    }

    Rectangle {
        id: background
        color: "#282c34"
        border.color: "#3a404c"
        border.width: 1
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.rightMargin: windowMargin
        anchors.leftMargin: windowMargin
        anchors.bottomMargin: windowMargin
        anchors.topMargin: windowMargin

        Rectangle {
            id: appContainer
            color: "#00000000"
            border.color: "#00000000"
            border.width: 0
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.rightMargin: 1
            anchors.leftMargin: 1
            anchors.bottomMargin: 1
            anchors.topMargin: 1

            Rectangle {
                id: topBar
                height: 60
                color: "#21252b"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.rightMargin: 0
                anchors.leftMargin: 0
                anchors.topMargin: 0

                Rectangle {
                    id: titleDescriptionBar
                    color: "#00000000"
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 105
                    anchors.leftMargin: 80
                    anchors.topMargin: 0

                    DragHandler {
                        onActiveChanged: if (active) {
                                             internalFunctions.restore()
                                             main.startSystemMove()
                                         }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onDoubleClicked: internalFunctions.maximize()
                    }

                    Label {
                        id: titleDescriptionLabel
                        color: "#ffffff"
                        text: qsTr("Blood Emporium")
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        font.family: "Segoe UI"
                        font.pointSize: 10
                    }
                }

                Image {
                    id: icon
                    width: 60
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    source: "../../references/inspo1.png"
                    anchors.bottomMargin: 0
                    anchors.leftMargin: 5
                    anchors.topMargin: 0
                    fillMode: Image.PreserveAspectFit
                }

                Row {
                    id: windowButtons
                    width: 105
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 10
                    anchors.topMargin: 0

                    TopBarButton {
                        id: minimizeButton
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: internalFunctions.minimize()
                    }

                    TopBarButton {
                        id: maximizeButton
                        anchors.verticalCenter: parent.verticalCenter
                        iconSource: isMaximized ? "../images/icons/icon_restore.png" : "../images/icons/icon_maximize.png"
                        onClicked: internalFunctions.maximizeRestore()
                    }

                    TopBarButton {
                        id: closeButton
                        anchors.verticalCenter: parent.verticalCenter
                        clickedColor: "#a63737"
                        mouseOverColor: "#ff5555"
                        iconSource: "../images/icons/icon_close.png"
                        onClicked: main.close() // TODO save and exit
                    }
                }
            }

            Rectangle {
                id: content
                color: "#00000000"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: topBar.bottom
                anchors.bottom: parent.bottom
                anchors.topMargin: 0

                Rectangle {
                    id: leftMenu
                    width: 70
                    color: "#21252b"
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.leftMargin: 0
                    anchors.topMargin: 0

                    PropertyAnimation {
                        id: menuAnimation
                        target: leftMenu
                        property: "width"
                        to: leftMenu.width == 70 ? 250 : 70
                        duration: 500
                        easing.type: Easing.InOutQuint
                    }

                    Column {
                        id: menuColumn
                        height: 400
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.rightMargin: 0
                        anchors.leftMargin: 0
                        anchors.topMargin: 0


                        LeftMenuButton {
                            id: toggleButton
                            width: leftMenu.width
                            text: qsTr("Hide")
                            textColor: "#7d7d7d"
                            iconSource: "../images/icons/icon_menu.png"
                            onClicked: menuAnimation.running = true
                        }


                        LeftMenuButton {
                            id: homeButton
                            width: leftMenu.width
                            text: qsTr("Home")
                        }

                        LeftMenuButton {
                            id: preferencesButton
                            width: leftMenu.width
                            text: qsTr("Preference Profiles")
                            iconSource: "../images/icons/icon_preferences.png"
                        }
                    }

                    LeftMenuButton {
                        id: settingsButton
                        width: leftMenu.width
                        text: qsTr("Settings")
                        anchors.bottom: parent.bottom
                        clip: true
                        anchors.bottomMargin: 25
                        iconSource: "../images/icons/icon_settings.png"
                    }
                }

                Rectangle {
                    id: contentPage
                    color: "#282c34"
                    anchors.left: leftMenu.right
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: 0
                }

                Rectangle {
                    id: bottomBar
                    y: 252
                    height: 25
                    color: "#2f343d"
                    anchors.left: leftMenu.right
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0
                    anchors.bottomMargin: 0

                    Label {
                        id: authorLabel
                        color: "#cecece"
                        text: qsTr("Made by IIInitiationnn")
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        anchors.leftMargin: 10
                        anchors.rightMargin: 105
                        font.family: "Segoe UI"
                        font.pointSize: 8
                    }

                    Label {
                        id: versionLabel
                        color: "#cecece"
                        text: qsTr("v0.1.1")
                        anchors.left: authorLabel.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        anchors.leftMargin: 0
                        font.family: "Segoe UI"
                        anchors.rightMargin: 30
                        font.pointSize: 8
                    }
                }
            }
        }
    }

    MouseArea {
        id: topResizeArea
        height: 10
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: 0
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        cursorShape: Qt.SizeVerCursor

        property int previousY
        x: -2
        y: -12
        onPressed: previousY = mouseY
        onMouseYChanged: internalFunctions.resizeTop(mouseY, previousY)

        visible: !isMaximized
    }

    MouseArea {
        id: bottomResizeArea
        height: 10
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottomMargin: 0
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        cursorShape: Qt.SizeVerCursor

        property int previousY
        x: -2
        y: 558
        onPressed: previousY = mouseY
        onMouseYChanged: internalFunctions.resizeBottom(mouseY, previousY)

        visible: !isMaximized
    }

    MouseArea {
        id: leftResizeArea
        width: 10
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 0
        anchors.bottomMargin: 10
        anchors.topMargin: 10
        cursorShape: Qt.SizeHorCursor

        property int previousX
        x: -12
        y: -2
        onPressed: previousX = mouseX
        onMouseXChanged: internalFunctions.resizeLeft(mouseX, previousX)
    }

    MouseArea {
        id: rightResizeArea
        width: 10
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.rightMargin: 0
        anchors.bottomMargin: 10
        anchors.topMargin: 10
        cursorShape: Qt.SizeHorCursor

        property int previousX
        x: 978
        y: -2
        onPressed: previousX = mouseX
        onMouseXChanged: internalFunctions.resizeRight(mouseX, previousX)

        visible: !isMaximized
    }

    MouseArea {
        id: topLeftResizeArea
        width: 25
        height: 25
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: 0
        anchors.topMargin: 0
        cursorShape: Qt.SizeFDiagCursor

        property int previousX
        property int previousY
        onPressed: {
            previousX = mouseX
            previousY = mouseY
        }
        onMouseXChanged: internalFunctions.resizeLeft(mouseX, previousX)
        onMouseYChanged: internalFunctions.resizeTop(mouseY, previousY)

        visible: !isMaximized
    }

    MouseArea {
        id: topRightResizeArea
        width: 25
        height: 25
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 0
        anchors.topMargin: 0
        cursorShape: Qt.SizeBDiagCursor

        property int previousX
        property int previousY
        x: 963
        y: -12
        onPressed: {
            previousX = mouseX
            previousY = mouseY
        }
        onMouseXChanged: internalFunctions.resizeRight(mouseX, previousX)
        onMouseYChanged: internalFunctions.resizeTop(mouseY, previousY)

        visible: !isMaximized
    }

    MouseArea {
        id: bottomLeftResizeArea
        x: -12
        y: 543
        width: 25
        height: 25
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: 0
        anchors.bottomMargin: 0
        cursorShape: Qt.SizeBDiagCursor

        property int previousX
        property int previousY
        onPressed: {
            previousX = mouseX
            previousY = mouseY
        }
        onMouseXChanged: internalFunctions.resizeLeft(mouseX, previousX)
        onMouseYChanged: internalFunctions.resizeBottom(mouseY, previousY)

        visible: !isMaximized
    }

    MouseArea {
        id: bottomRightResizeArea
        x: 963
        y: 543
        width: 25
        height: 25
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 0
        anchors.bottomMargin: 0
        cursorShape: Qt.SizeFDiagCursor

        property int previousX
        property int previousY
        onPressed: {
            previousX = mouseX
            previousY = mouseY
        }
        onMouseXChanged: internalFunctions.resizeRight(mouseX, previousX)
        onMouseYChanged: internalFunctions.resizeBottom(mouseY, previousY)

        visible: !isMaximized
    }





}





/*##^##
Designer {
    D{i:0;formeditorZoom:1.1}
}
##^##*/
