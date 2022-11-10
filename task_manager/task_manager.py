from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QDate
from PyQt5.uic import loadUi
import sys
import os
import json
from datetime  import datetime
import pandas as pd
import traceback

class TaskManager(QMainWindow):
    
    def __init__(self):

        # variables
        self.qt_date_format = 'dd-MM-yyyy'
        self.py_date_format = '%d-%m-%Y'
        self.all_task_details = {'data':[]} # store data from database file
        self.data_file_path = 'task_details.csv'

        self.column_names = ['UNIQUE TASK NUMBER', 'TASK NAME', 'DESCRIPTION', 'CREATION DATE', 'STARTED DATE', 'COMPLETION DATE', 'STATUS', 'DAYS LEFT']
        
        self.status_list = ['All', 'Not Started', 'In Progress', 'Pending', 'Completed', 'Blocked']
        self.status_color_mapping = {
                                'Not Started' : {'color' : QtGui.QColor(190,190,190), 'index' : 0},
                                'In Progress' : {'color' : QtGui.QColor(247,247,0), 'index' : 1},
                                'Pending' : {'color' : QtGui.QColor(255,0,0), 'index' : 2},
                                'Completed' : {'color' : QtGui.QColor(0,255,0), 'index' : 3},
                                'Blocked' : {'color' : QtGui.QColor(196,118,67), 'index' : 4}
                            }

        # create data file if not present
        if not os.path.isfile(self.data_file_path): #create file if not exist
            with open(self.data_file_path,'w') as fo:
                fo.write(','.join(self.column_names)+"\n")

        # Load UI screen
        super(TaskManager,self).__init__()
        loadUi("task_manager_home_page.ui",self)
        
        # prepare interface            
        self.taskStatusComboBox.addItems(self.status_list) # add status to filter combobox
        self.taskStatusComboBox.setCurrentIndex(2) # Set status as "In progress" by default

        self.taskFilterComboBox.addItems(self.column_names) # set column names to sort combobox
        self.taskFilterComboBox.setCurrentIndex(7) # set "DAYS LEFT" column as defualt sort
        

        # show data first time
        self.show_tasks()
        
        # # create events for widgets
        self.tabWidget.currentChanged.connect(self.onTabChange) #changed the tab

        self.createTaskBtn.clicked.connect(self.create_task)
        self.taskStatusComboBox.activated.connect(self.show_tasks)
        self.taskFilterComboBox.activated.connect(self.show_tasks)

        self.actionAbout.triggered.connect(lambda : self.show_msg('Developer : Mukesh Singh Negi'))
        
        self.updateTaskBtn.clicked.connect(self.update_task)
        self.taskNum2ComboBox.activated.connect(self.show_data_on_update_page)


    def onTabChange(self):
        # read database file
        self.all_task_details = pd.read_csv(self.data_file_path ,na_filter=False)

        current_tab_index = self.tabWidget.currentIndex()

        if (current_tab_index == 0): # show task tab
            self.show_tasks()
        elif(current_tab_index == 1): # create task tab
            # find maximum task number and show to create task page
            if len(self.all_task_details) == 0:
                max_task_num = 0
            else:
                max_task_num = int(self.all_task_details['UNIQUE TASK NUMBER'].max())

            # clear the content
            self.taskNumLabel.setText(str(max_task_num+1))
            self.taskNameEditText.setText('')
            self.descriptionEditText.setText('')
            self.targetDate.setDate(QDate(2000, 1, 1))

        elif(current_tab_index == 2): # update task tab
            self.taskNum2ComboBox.clear()
            task_num_str = list(map(str,list(self.all_task_details['UNIQUE TASK NUMBER'])))
            self.taskNum2ComboBox.addItems(task_num_str)

            self.taskStatus2ComboBox.clear()
            self.taskStatus2ComboBox.addItems(self.status_list[1:])

            self.startDate2DateField.setDate(QDate(2000, 1, 1))
            self.targetDate2DateField.setDate(QDate(2000, 1, 1))


    def show_msg(self,msg):
        messageBox = QMessageBox()
        messageBox.setText(msg)
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()


    def show_tasks(self):
        '''
        This function shows will show the data in table widget whenever a filter will be selected.
        '''

        try:

            
            self.taskTableWidget.setColumnCount(len(self.column_names))
            self.taskTableWidget.setHorizontalHeaderLabels(self.column_names) # set table column names

            # read data file
            self.all_task_details = pd.read_csv(self.data_file_path ,na_filter=False) #read data file

            
            # clear content
            self.taskTableWidget.setRowCount(0)

            # get current filter status
            current_status = self.taskStatusComboBox.currentText()

            # get current filter column name
            filter_col_name = self.taskFilterComboBox.currentText()

             # evaluate days left 
            for i in range(len(self.all_task_details)):
                self.all_task_details.at[i,'DAYS LEFT'] = int((datetime.strptime(self.all_task_details['COMPLETION DATE'][i],'%d-%m-%Y') - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days)

            # filter data if status is not "All" 
            if current_status != 'All':
                filter_data = self.all_task_details[self.all_task_details['STATUS'] == current_status]
            else:
                filter_data = self.all_task_details

            # reset index after filtering out the data on the basis of status
            filter_data.reset_index(drop=True,inplace=True)

            sorted_filter_data = filter_data.sort_values(by=filter_col_name)
            
            # reset index after filtering out the data on the basis of status
            sorted_filter_data.reset_index(drop=True,inplace=True)

            # set maximum row
            self.taskTableWidget.setRowCount(len(sorted_filter_data))

            # show data in table
            for row_index, row_data in sorted_filter_data.iterrows():

                col_index = 0
                for col_name,value in row_data.items():
                    
                    self.taskTableWidget.setItem(row_index,col_index, QTableWidgetItem(str(value)))
                    
                    # set color of status column
                    if col_name == 'STATUS':
                        self.taskTableWidget.item(row_index, col_index).setBackground(self.status_color_mapping[value]['color'])

                    col_index += 1
        
        except Exception as e:
            self.show_msg(f'Exception in method "show_tasks" - {e}')
            print(e)


    def create_task(self):
        
        try:
            
            data = f"{self.taskNumLabel.text()},{self.taskNameEditText.toPlainText()},{self.descriptionEditText.toPlainText()},{datetime.now().strftime(self.py_date_format)},,{self.targetDate.date().toString(self.qt_date_format)},Not Started,\n"
            
            with open(self.data_file_path,'a') as fo:
                fo.write(data)
                self.show_msg(f'Task created successfully')
            
            # clear the content
            self.taskNumLabel.setText(str(int(self.taskNumLabel.text())+1))
            self.taskNameEditText.setText('')
            self.descriptionEditText.setText('')
            self.targetDate.setDate(QDate(2000, 1, 1))

        except Exception as e:
            self.show_msg(f'Exception in method "create_task" - {e}')


    def update_task(self):
        
        try:
            # read database file
            self.all_task_details = pd.read_csv(self.data_file_path ,na_filter=False)

            selected_unique_task_num = self.taskNum2ComboBox.currentText()
            updated_task_name = self.taskName2EditText.toPlainText()
            updated_description = self.description2EditText.toPlainText()
            updated_start_date = self.startDate2DateField.date().toString(self.qt_date_format)
            updated_target_date = self.targetDate2DateField.date().toString(self.qt_date_format)
            updated_task_status = self.taskStatus2ComboBox.currentText()

            # find the index in dataframe
            row_index =  self.all_task_details[self.all_task_details['UNIQUE TASK NUMBER']==int(selected_unique_task_num)].index[0]

            self.all_task_details.loc[row_index,['TASK NAME', 'DESCRIPTION', 'STARTED DATE', 'COMPLETION DATE', 'STATUS']] = [updated_task_name, updated_description, updated_start_date, updated_target_date, updated_task_status]

            # update task
            self.all_task_details.to_csv(self.data_file_path, index=False)

            self.show_msg('Task updated successfully')
            
            # set values
            self.taskName2EditText.setText('')
            self.description2EditText.setText('')
            self.startDate2DateField.setDate(QDate(2000, 1, 1))
            self.targetDate2DateField.setDate(QDate(2000, 1, 1))

        except Exception as e:
            self.show_msg(str(e))
            print(f'Exception in method "update_task" - {e}')
            traceback.print_exc()


    def show_data_on_update_page(self):
        
        selected_unique_task_num = self.taskNum2ComboBox.currentText()

        for row in self.all_task_details[self.all_task_details['UNIQUE TASK NUMBER'] == int(selected_unique_task_num)].iterrows():
            data = dict(row[1])

        # set values
        self.taskName2EditText.setText(str(data['TASK NAME']))
        self.description2EditText.setText(str(data['DESCRIPTION']))
        
        date = []
        if not data['STARTED DATE']:
            self.startDate2DateField.setDate(QDate(2000,1,1))
        else:
            date = list(map(int,data['STARTED DATE'].split('-')))
            date.reverse()
            self.startDate2DateField.setDate(QDate(date[0],date[1],date[2]))
            
        date1 = []
        date1 = list(map(int,data['COMPLETION DATE'].split('-')))
        date1.reverse()
        self.targetDate2DateField.setDate(QDate(date1[0],date1[1],date1[2]))

        self.taskStatus2ComboBox.setCurrentIndex(self.status_color_mapping[data['STATUS']]['index']) # Set status as "In progress" by default


if __name__ == '__main__':
    app = QApplication(sys.argv)
    task_manager_obj = TaskManager()
    task_manager_obj.show()
    
    sys.exit(app.exec())