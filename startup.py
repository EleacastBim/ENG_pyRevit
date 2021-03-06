"""Example of IronPython script to be executed by pyRevit on extension load

The script filename must end in startup.py

To Test:
- rename file to startup.py
- reload pyRevit: pyRevit will run this script after successfully
  created the DLL for the extension.

pyRevit runs the startup script in a dedicated IronPython engine and output
window. Thus the startup script is isolated and can not hurt the load process.
All errors will be printed to the dedicated output window similar to the way
errors are printed from pyRevit commands.
"""

# with open(r'C:\Temp\test.txt', 'w') as f:
#     f.write('test')



from pyrevit.framework import clr

import time
import sqlite3
import os
from os import path

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('AdWindows')
clr.AddReference('UIFramework')
clr.AddReference('UIFrameworkServices')
clr.AddReference('Newtonsoft.Json')

import Autodesk.Revit.DB.Events as Event

import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI

app = __revit__.Application



def getElementsProperties(AddedElementsIds, connection):
    ''' '''
    output= []
    date = int(time.time())
    doc = __revit__.ActiveUIDocument.Document
    docName = doc.Title  or ""
    userName = app.Username  or ""
    action = "Added"
    
    uniqueIds = list(set(AddedElementsIds))

    for id in uniqueIds:
        test = "SELECT EXISTS(SELECT 1 FROM elements WHERE id='%s' LIMIT 1);" % (id)
        if not connection.execute(test):
            element= doc.GetElement(id)
            category = element.Category
            categoryName = ''
            try:
                categoryName = category.Name
                if "Pipes" in categoryName or "Ducts" in categoryName :
                    length = element.LookupParameter('Length').AsDouble()
                    comment  = ""
                    s ="INSERT INTO elements VALUES ('%s','%s','%s','%s',%s,'%s',%s,'%s')" % (date, userName, docName, action, id, categoryName, length, comment)
                    output.append(s)
                if "Pipe Fitting" in categoryName or "Duct Fitting" in categoryName:
                    length = 0
                    comment  = element.LookupParameter('Size').AsString()
                    s ="INSERT INTO elements VALUES ('%s','%s','%s','%s',%s,'%s',%s,'%s')" % (date, userName, docName, action, id, categoryName, length, comment)
                    output.append(s)
            except Exception as ex:
                erroLog = os.path.expanduser(r'~\error.log')
                with open(erroLog, 'a') as file:
                    file.write(str(ex)+'\n')
            
    return output




def SaveChangeJournal(sender, event):
    '''Save journal of elements changed during document edition'''
    DBpath = os.path.expanduser(r'~\log.sqlite')
    conn = sqlite3.connect(DBpath)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS elements
                (date text, username text, document text, action text, id INTEGER, category text, length real, comment text )''')
    try:
        #Look for elements created in last event and cleaning from duplicated values
        AddedElementsIds  = list(set(event.GetAddedElementIds()))

        queries = getElementsProperties(AddedElementsIds,c)
        for q in queries:
            
            c.execute(q)
            conn.commit()

    except Exception as ex:

        erroLog = os.path.expanduser(r'~\error.log')
        with open(erroLog, 'a') as file:
            file.write(str(ex)+'\n')
    
    #Closing the connections in case something fails
    conn.close()       
        
app.DocumentChanged += SaveChangeJournal
