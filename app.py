import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLineEdit, QListWidgetItem)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QListWidgetItem, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon


class ListItemWidget(QWidget):
    def __init__(self, text, color, list_widget_item, list_widget, parent=None):
        super(ListItemWidget, self).__init__(parent)
        self.list_widget_item = list_widget_item
        self.list_widget = list_widget
        self.layout = QHBoxLayout()

        self.label = QLabel(text)
        self.label.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {color};
                border-radius: 10px;
                background-color: {color};
                color: black;  /* Define a cor do texto para preto */
                font-weight: bold;  /* Torna o texto em negrito */
                padding: 5px;
                margin-right: 5px;
            }}
        """)
        
        self.closeButton = QPushButton("x")
        self.closeButton.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 10px;
                background-color: red;
                color: white;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.closeButton.setFixedSize(20, 20)
        self.closeButton.clicked.connect(self.on_close)

        # Estilo para remover o efeito de hover padrão
        self.setStyleSheet("""
            QListWidget::item:hover {
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
            QListWidget::item:selected:!active {
                background: transparent;
            }
        """)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.closeButton)
        self.layout.addStretch()
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.setLayout(self.layout)
        self.update_color(color)

    
    def update_color(self, color):
        self.label.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {color};
                border-radius: 10px;
                background-color: {color};
                color: black;
                font-weight: bold;
                padding: 5px;
                margin-right: 5px;
            }}
        """)


    def on_close(self):
        row = self.list_widget.row(self.list_widget_item)
        item = self.list_widget.takeItem(row)
        del item  # Remova o item para liberar memória

# Classe personalizada para suportar arrastar e soltar
class DraggableListWidget(QListWidget):
    def __init__(self, type, parent=None):
        super(DraggableListWidget, self).__init__(parent)
        self.type = type  # 'todo', 'in_progress', 'done'
        self.setDragDropMode(QListWidget.InternalMove)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dropEvent(self, event):
        super(DraggableListWidget, self).dropEvent(event)
        # Atualize a cor dos itens após o drop
        for index in range(self.count()):
            item = self.item(index)
            widget = self.itemWidget(item)
            widget.update_color(self.get_color_for_type(self.type))

    def get_color_for_type(self, type):
        colors = {
            'todo': '#fca8a1',
            'in_progress': '#f7d6b3',
            'done': '#abd5aa'
        }
        return colors.get(type, '#ffffff')  # default to white if type not found

# Classe principal do Kanban Board
class KanbanBoard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Kanban Produtividade @Antonio Santos')
        self.setWindowIcon(QIcon('PROJETO PRODUTIVIDADE\icone.ico'))
        
        # Layout principal
        self.main_layout = QHBoxLayout()
        
        # Colunas Kanban
        self.todo_list = DraggableListWidget('todo')
        self.in_progress_list = DraggableListWidget('in_progress')
        self.done_list = DraggableListWidget('done')
        
        # Adiciona as listas ao layout principal
        self.main_layout.addWidget(self.todo_list)
        self.main_layout.addWidget(self.in_progress_list)
        self.main_layout.addWidget(self.done_list)
        
        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        
        # Campo de entrada para o nome da tarefa
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Digite o nome da atividade aqui")
        
        # Botões para adicionar tarefas com estilos CSS
        self.add_buttons_layout = QVBoxLayout()
        self.add_buttons_layout.addWidget(self.task_input)  # Adiciona a QLineEdit no layout

        self.add_task_button_todo = QPushButton('Adicionar em "A Fazer"')
        self.add_task_button_in_progress = QPushButton('Adicionar em "Em Progresso"')
        self.add_task_button_done = QPushButton('Adicionar em "Concluído"')
        self.remove_task_button = QPushButton('Remover Tarefa Selecionada')

        # Definindo os estilos dos botões
        self.add_task_button_todo.setStyleSheet(self.style_for_todo_button())
        self.add_task_button_in_progress.setStyleSheet(self.style_for_in_progress_button())
        self.add_task_button_done.setStyleSheet(self.style_for_done_button())
        self.remove_task_button.setStyleSheet(self.style_for_remove_button())

        self.add_buttons_layout.addWidget(self.add_task_button_todo)
        self.add_buttons_layout.addWidget(self.add_task_button_in_progress)
        self.add_buttons_layout.addWidget(self.add_task_button_done)
        self.add_buttons_layout.addWidget(self.remove_task_button)

        self.main_layout.addLayout(self.add_buttons_layout)

        # Conectar botões a funções
        self.add_task_button_todo.clicked.connect(lambda: self.add_task(self.todo_list))
        self.add_task_button_in_progress.clicked.connect(lambda: self.add_task(self.in_progress_list))
        self.add_task_button_done.clicked.connect(lambda: self.add_task(self.done_list))
        self.remove_task_button.clicked.connect(self.remove_selected_task)

        # Aplicar o estilo para remover o efeito de hover em todos os QListWidgets
        self.todo_list.setStyleSheet(self.style_for_list_widget())
        self.in_progress_list.setStyleSheet(self.style_for_list_widget())
        self.done_list.setStyleSheet(self.style_for_list_widget())
        

    def add_task(self, list_widget):
        task_name = self.task_input.text()
        if task_name:  # Only add if the text is not empty
            item = QListWidgetItem()
            list_widget.addItem(item)
            # The color will be determined by the list type
            color = list_widget.get_color_for_type(list_widget.type)
            task_widget = ListItemWidget(task_name, color, item, list_widget)
            item.setSizeHint(task_widget.sizeHint())
            list_widget.setItemWidget(item, task_widget)
            self.task_input.clear()  # Clear the input field after adding


    def remove_selected_task(self):
        for list_widget in [self.todo_list, self.in_progress_list, self.done_list]:
            selected_items = list_widget.selectedItems()
            if selected_items:
                for item in selected_items:
                    list_widget.takeItem(list_widget.row(item))

    # Funções de estilo para os botões
    def style_for_todo_button(self):
        return """
            QPushButton {
                border: 2px solid #f61f0e;
                background-color: #fca8a1;
                color: black;  /* Cor do texto do botão */
                border-radius: 10px;  /* Cantos arredondados */
                padding: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #f61f0e;
            }
        """

    def style_for_in_progress_button(self):
        return """
            QPushButton {
                border: 2px solid #eb9b48;
                background-color: #f7d6b3;
                color: black;  /* Cor do texto do botão */
                border-radius: 10px;  /* Cantos arredondados */
                padding: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #eb9b48;
            }
        """

    def style_for_done_button(self):
        return """
            QPushButton {
                border: 2px solid #68b465;
                background-color: #abd5aa;
                color: black;  /* Cor do texto do botão */
                border-radius: 10px;  /* Cantos arredondados */
                padding: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #68b465;
            }
        """

    def style_for_remove_button(self):
        return """
            QPushButton {
                border: 2px solid #46a7f5;
                background-color: #86c6f8;
                color: black;  /* Cor do texto do botão */
                border-radius: 10px;  /* Cantos arredondados */
                padding: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #46a7f5;
            }
        """
    
    def style_for_list_widget(self):
        return """
            QListWidget::item:hover {
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
            QListWidget::item:selected:!active {
                background: transparent;
            }
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    kanban_board = KanbanBoard()
    kanban_board.show()
    sys.exit(app.exec_())
