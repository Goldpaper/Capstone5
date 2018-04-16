from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPalette
import sys, random


class Tetris(QMainWindow):  # 테트리스 게임 창 클래스

   def __init__(self):  # 생성자
       super().__init__()

       self.initUI()  # 생성시 UI 생성

   def initUI(self):  # UI 생성 함수
       '''initiates application UI'''

       self.tboard1 = Board(self)  # Board 클래스 1 생성
       self.tboard2 = Board(self)  # Board 클래스 2 생성
       self.tboard1.setStyleSheet("background-color: gray;")  # 색 지정 후에 아래 주석의 Pallete로 원하는 이미지 삽입 가능
       self.tboard2.setStyleSheet("background-color: gray;")
       self.tboard1.move(40, 80)  # 위치 조절
       self.tboard2.move(300, 80)

       self.tboard1.resize(180, 360)  # 사이즈 조절
       self.tboard2.resize(180, 360)

       self.tboard1.setStyleSheet("background-color: #2F2F2F;")  # 색 조정, 후에 아래 주석에 있는 코드로 이미지 삽입 가능
       self.tboard2.setStyleSheet("background-color: #2F2F2F;")

       self.tboard1.start()  # 각 보드 시작
       self.tboard2.start()

       # palette = QPalette() 팔레트 생성 및 이미지 지정하여 백그라운드로 설정하는 코드. 이미지 이름 원하시는 대로 수정해서 쓰시면 됩니다.
       # palette.setBrush(QPalette.Background,QBrush(QPixmap("anne.jpg")))
       # frame.setPalette(palette)

       self.setStyleSheet("background-color: #38374C;")  # 전체 UI 색 지정
       self.resize(520, 450)  # 사이즈 조절
       self.center()  # center 함수
       self.setWindowTitle('Tetris')  # 프로그램명 변경
       self.show()  # UI 보여주기

   def center(self):
       # 화면 가운데로 창을 띄워주는 함수

       screen = QDesktopWidget().screenGeometry()  # 화면 해상도 구함
       size = self.geometry()  # 현재 창의 크기 및 위치 정보 구함
       self.move((screen.width() - size.width()) / 2,  # 중앙으로 창 이동
                 (screen.height() - size.height()) / 2)


class Board(QFrame):
   BoardWidth = 10  # 보드 너비
   BoardHeight = 22  # 보드 높이

   def __init__(self, parent):  # 생성자
       super().__init__(parent)

       self.initBoard()

   def initBoard(self):  # 보드 생성 함수

       self.curX = 0  # 블럭 현재 위치 x 좌표
       self.curY = 0  # 블럭 현재 위치 y 좌표
       self.board = []  # 위치 정보를 담는 보드를 리스트 형태로 선언

       self.setFocusPolicy(Qt.StrongFocus)  # 키보드 입력 포커싱을 설정해주는 메소드
       self.setboardindex()  # 게임 시작 전 인덱스를 정렬해주는 함수

   def shapeAt(self, x, y):  # 보드 위치

       return self.board[(y * Board.BoardWidth) + x]

   def squareWidth(self):  # 보드의 '한 칸'의 너비 반환

       return self.contentsRect().width() // Board.BoardWidth

   def squareHeight(self):  # 보드의 '한 칸'의 높이 반환

       return self.contentsRect().height() // Board.BoardHeight

   def start(self):  # 게임을 시작하는 함수

       self.setboardindex()  # 보드 인덱스 정렬

       self.newPiece()  # 새로운 조각 생성

   def paintEvent(self, event):
       # 블록을 위치에 색칠하여 표시하는 함수

       painter = QPainter(self)
       rect = self.contentsRect()
       boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()  # 보드 맨 윗 칸의 y 좌표

       for i in range(4):  # 테트리스 조각은 4개이므로 4번 칠해야함

           x = self.curX + self.curPiece.x(i)  # 조각 표시할 x좌표
           y = self.curY - self.curPiece.y(i)  # 조각 표시할 y좌표
           self.drawSquare(painter, rect.left() + x * self.squareWidth(),  # 값들 계산하여 해당 위치에 네모(테트리스 조각 한 칸)를 그림
                           boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                           self.curPiece.shape())

   def setboardindex(self):  # 보드 인덱스 지정

       for i in range(Board.BoardHeight * Board.BoardWidth):  # 모든 칸에 '없음' 속성을 추가해서 22 * 10 리스트를 완성함
           self.board.append(Tetrominoe.NoShape)

   def newPiece(self):  # 새로운 조각 생성

       self.curPiece = Shape()  # shape 구조체 생성
       self.curPiece.setRandomShape()  # 해당 모양을 랜덤 지정
       self.curX = Board.BoardWidth // 2 + 1  # 위치 조정
       self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

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

   def minY(self):  # 모양의 가장 낮은 y 좌표값 반환
       '''returns min y value'''

       m = self.coords[0][1]
       for i in range(4):
           m = min(m, self.coords[i][1])

       return m

   def maxY(self):  # 모양의 가장 높은 y 좌표값 반환
       '''returns max y value'''

       m = self.coords[0][1]
       for i in range(4):
           m = max(m, self.coords[i][1])

       return m


if __name__ == '__main__':
   app = QApplication([])  # 앱 생성
   tetris = Tetris()  # 테트리스 객체 생성
   sys.exit(app.exec_())  #
