from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPalette
import sys, random


class Tetris(QMainWindow):  # 테트리스 게임 창 클래스

    def __init__(self):  # 생성자
        super().__init__()

        self.initUI()  # 생성시 UI 생성

    def initUI(self):  # UI 생성 함수

        self.tboard1 = Board(self)  # Board 클래스 생성
        self.tboard2 = Board(self)
        self.tboard1.move(40, 80)
        self.tboard2.move(300, 80)

        self.tboard1.resize(180, 360)
        self.tboard2.resize(180, 360)

        self.tboard1.setStyleSheet("background-color: #2F2F2F;")  # 색 조정, 후에 아래 주석에 있는 코드로 이미지 삽입 가능
        self.tboard2.setStyleSheet("background-color: #2F2F2F;")

        self.statusbar = self.statusBar()
        self.tboard1.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.statusbar.setStyleSheet("background-color: #FFFFFF;")

        self.tboard1.start()  # 보드 시작
        self.tboard2.start()

        self.setStyleSheet("background-color: #38374C;")
        self.resize(520, 500)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

    def center(self):
        # 화면 가운데로 창을 띄워주는 함수

        screen = QDesktopWidget().screenGeometry()  # 화면 해상도 구함
        size = self.geometry()  # 현재 창의 크기 및 위치 정보 구함
        self.move((screen.width() - size.width()) / 2,  # 중앙으로 창 이동
                  (screen.height() - size.height()) / 2)


class Board(QFrame):
    msg2Statusbar = pyqtSignal(str)

    BoardWidth = 10  # 보드 너비
    BoardHeight = 22  # 보드 높이
    Speed = 300

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()

    def initBoard(self):  # 보드 생성 함수

        self.timer = QBasicTimer()  # 타이머 생성
        self.isWaitingAfterLine = False

        # 블럭 현재 위치 정보
        self.curX = 0
        self.curY = 0

        self.numLinesRemoved = 0
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()

    def shapeAt(self, x, y):  # 보드 위치 반환

        return self.board[(y * Board.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):  # 보드 위치 설정

        self.board[(y * Board.BoardWidth) + x] = shape

    def squareWidth(self):  # 보드 한칸 너비 반환

        return self.contentsRect().width() // Board.BoardWidth

    def squareHeight(self):  # 보드 한칸 높이 반환
        '''returns the height of one square'''

        return self.contentsRect().height() // Board.BoardHeight

    def start(self):  # 게임 시작 함수

        if self.isPaused:  # 게임이 정지 상태일 경우 시작하지 않음
            return

        self.isStarted = True  # 게임 시작 여부 설정
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0  # 삭제한 라인 수 초기화
        self.clearBoard()  # 보드 초기화

        self.msg2Statusbar.emit(str(self.numLinesRemoved))  # 상태바 숫자 초기화

        self.newPiece()  # 새 블럭 생성
        self.timer.start(Board.Speed, self)  # 타이머 시작

    def pause(self):  # 정지상태 전환 함수

        if not self.isStarted:  # 게임 진행 중일 경우 함수 실행 안함
            return

        self.isPaused = not self.isPaused  # pause를 not 연산

        if self.isPaused:  # 게임이 정지 상태일 경우
            self.timer.stop()  # 타이머를 멈추고
            self.msg2Statusbar.emit("paused")  # 상태바에 일시정지 메시지 출력

        else:  # 그 외의 경우
            self.timer.start(Board.Speed, self)  # 게임재시작 후 상태바 업데이트
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.update()  # 바뀐 내용 토대로 보드 업데이트

    def paintEvent(self, event):  # paintEvent 재정의

        painter = QPainter(self)
        rect = self.contentsRect()

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()

        for i in range(Board.BoardHeight):  # 떨어진 블록을 보드에 그리는 함수. shapeAt()을 통해 블록 정보를 얻어온다.
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

                if shape != Tetrominoe.NoShape:  # 정상적인 블록인 경우 주어진 모양에 맞게 그린다.
                    self.drawSquare(painter,
                                    rect.left() + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != Tetrominoe.NoShape:  # 떨어지는 블록을 그리는 함수

            for i in range(4):  # 총 4칸을 떨어지는 궤도에 그린다.

                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                                boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                                self.curPiece.shape())

    def keyPressEvent(self, event):  # 키 입력 이벤트 재정의

        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_Down:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key_Space:
            self.dropDown()

        elif key == Qt.Key_D:
            self.oneLineDown()

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):  # 타이머 이벤트 재정의

        if event.timerId() == self.timer.timerId():

            if self.isWaitingAfterLine:  # 떨어지는 블록이 없을 경우 블록 생성
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()  # 그 외의 경우 떨어지는 블록 위치를 옮김

        else:
            super(Board, self).timerEvent(event)

    def clearBoard(self):  # 보드를 초기화함과 동시에 알맞은 크기의 배열로 만들어줌

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

    def dropDown(self):  # 블록을 바로 떨어뜨리는 함수

        newY = self.curY

        while newY > 0:

            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1

        self.pieceDropped()

    def oneLineDown(self):  # 한 칸씩 블록을 떨어뜨리는 함수

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):  # 블록이 바로 떨어진 후 채워진 라인 삭제 및 새 블록 생성

        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):  # 채워진 라인을 삭제하는 함수

        numFullLines = 0
        rowsToRemove = []

        # 10개의 조각이 있는 라인(채워진 라인)을 위에서부터 찾아 rowsToRemove 리스트에 추가함

        for i in range(Board.BoardHeight):

            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        # 아래부터 라인을 제거해야 정상적으로 작동하므로 순서를 바꿔줌
        rowsToRemove.reverse()

        # 제거해야하는 라인을 윗 줄로 덮어씌움
        for m in rowsToRemove:

            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines  # 없앤 라인 수 누적
            self.msg2Statusbar.emit(str(self.numLinesRemoved))  # 없앤 라인 수는 스코어로 계산되어 상태바에 바로 반영

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)  # 그릴 조각의 모양 초기화
            self.update()  # 변경 내용 보드에 업데이트

    def newPiece(self):  # 새로운 블록 생성

        self.curPiece = Shape()  # shape 구조체 생성
        self.curPiece.setRandomShape()  # 해당 모양을 랜덤 지정
        self.curX = Board.BoardWidth // 2 + 1  # 위치 조정
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):  # 블록이 안 움직여질 경우 게임오버

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")

    def tryMove(self, newPiece, newX, newY):  # 블록을 움직이는 함수

        for i in range(4):  # 블록 위치를 주어진 XY 좌표값에 새로 그림

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def drawSquare(self, painter, x, y, shape):  # 모양에 맞게 색을 지정해 입혀주는 함수

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,  # 컬러 테이블 담은 리스트
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])  # qt에서 color 속성을 담는 Qcolor, 주어진 모양에 맞게 색을 지정한다.
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)  # 설정된 펜으로 칸 칠함

        painter.setPen(color.lighter())  # 조각의 바깥 쪽을 옅은 색으로 칠해 경계 표시
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())  # 조각의 가장 바깥 쪽을 검은 색으로 칠해 경계 표시
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)


class Tetrominoe(object):  # 테트리스 모양 정보를 담은 클래스. 각 모양에 해당하는 정수를 지정해준다.

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):  # 모양의 좌표 관련 정보를 담은 클래스.

    # 각 조각에 맞는 위치 정보를 coordsTable로 정리해둠
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):  # 클래스 생성자. 맨 처음에는 NoShape로 지정해둔 후, setShape를 호출한다.

        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)

    def shape(self):  # 모양 정보를 반환하는 함수

        return self.pieceShape

    def setShape(self, shape):  # 모양의 좌표 정보를 담아주는 함수

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):  # 무작위 도형을 뽑는 함수

        self.setShape(random.randint(1, 7))

    def x(self, index):  # x 좌표 반환

        return self.coords[index][0]

    def y(self, index):  # y 좌표 반환

        return self.coords[index][1]

    def setX(self, index, x):  # x 좌표 지정

        self.coords[index][0] = x

    def setY(self, index, y):  # y 좌표 지정

        self.coords[index][1] = y

    def minX(self):  # 모양의 가장 낮은 x 좌표값 반환

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def maxX(self):  # 모양의 가장 높은 x 좌표값 반환

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def minY(self):  # 모양의 가장 낮은 y 좌표값 반환

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def maxY(self):  # 모양의 가장 높은 y 좌표값 반환

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotateLeft(self):  # 좌로 회전

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotateRight(self):  # 우로 회전

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result


if __name__ == '__main__':
    app = QApplication([])  # 앱 생성
    tetris = Tetris()  # 테트리스 객체 생성
    sys.exit(app.exec_())  # 앱 실행