"""
Pipe-O-meter
Version: 1.0
Date : 06/10/18
Autor: Pablo Derendinger 
pyrevit: 4.5
"""

__title__ = 'Pipe-O-meter'


from pyrevit import script
from pyrevit.extensions import extensionmgr
from os import path

logger = script.get_logger()
logger.set_quiet_mode()

import sqlite3
import os
from os import path
from datetime import datetime
import math






#region defining window
output = script.get_output()
output.window.Height= 700
output.window.Width = 300
#enregion

def getDateFromUnix(unixDate):

    date = datetime.fromtimestamp(int(unixDate))
    return date
    


def createGraphic():
    
    """Put here something """
    
    DBpath = os.path.expanduser(r'~\log.sqlite')
    conn = sqlite3.connect(DBpath)

    #Define labes, data , average and maximum
    labelsQuery = conn.execute("SELECT date FROM elements WHERE category LIKE '%s'" %('Pipes') )
    dataQuery = conn.execute("SELECT length FROM elements WHERE category LIKE '%s'" %('Pipes'))
    
    rows=[getDateFromUnix(x[0]) for x in labelsQuery] 
    data = [row[0] for row in dataQuery]
    
    conn.close()

    today = datetime.today().date() 
    istoday = [x.date() == today for x in rows]

    todayRow, todayData = [],[]
    
    count = 0

    for i in istoday:
        if i:
            todayRow.append(str(rows[count]))
            todayData.append(data[count])
        count = count +1

    average = TodayAaverage = 0

    try:
        average = sum(data)/len(data)
        TodayAaverage = sum(todayData)/len(todayData)
    except:
        pass

    optLinearChart = {
            
            'scales': {
            'xAxes': [{
               'type': 'time',
               'time': {
                  'parser': 'YYYY-MM-DD HH:mm:ss',
                  'unit': 'day',
                  'displayFormats': {
                     'day': 'ddd'
                  },
               },
               'ticks': {
                  'source': 'data'
               }
            }]
         }}

    optTodayLineChart = {
            
            'scales': {
            'xAxes': [{
               'type': 'time',
               'time': {
                  'parser': 'YYYY-MM-DD HH:mm:ss',
                  'unit': 'hour',
                  'displayFormats': {
                     'hour': 'hh:mm'
                  },
               },
               'ticks': {
                  'source': 'data'
               }
            }]
         }}
    
    #region History Chart
    LineChart = output.make_line_chart()
    LineChart.options = optLinearChart
    LineChart.data.labels= [str(x) for x in rows] 
    
    set_a = LineChart.data.new_dataset('Historic')
    averageData = LineChart.data.new_dataset('Average')
    [averageData.data.append(average) for x in data] 
    set_a.data = data
    set_a.tension = 0
    
    averageData.backgroundColor = 'transparent'
    
    #endregion
    
    #region Today History Chart

    TodayLineChart = output.make_line_chart()
    TodayLineChart.data.labels= todayRow
    
    Todayset_a = TodayLineChart.data.new_dataset('Today')
    Todayset_a.data = todayData
    Todayset_a.tension = 0
    TodayaverageData = TodayLineChart.data.new_dataset('Average')
    [TodayaverageData.data.append(TodayAaverage) for x in todayData]
    
    TodayLineChart.randomize_colors()
    TodayaverageData.backgroundColor = 'transparent'
    
    TodayLineChart.options = optTodayLineChart
    #endregion

    #region Doughnut Chart
    donutChart = output.make_doughnut_chart()
    donutChart.options.rotation = 1 * math.pi
    donutChart.options.circumference = 1 * math.pi
    donutChart.data.labels = ["average",""]
    speed = donutChart.data.new_dataset('speed')
    speed.backgroundColor = ["red", "grey"]
    speed.data = [round(average), 100-round(average)]
    #endregion

    
    donutChart.draw()

    TodayLineChart.draw()
    
    LineChart.draw()
    
#calcular vleocidad de modelado de pipe
#cuantos metros se modelo en 10 minutos proyectado a 1 hora (x*6)    

    

# def lengthLatHour(dates, lengths):

#     lastHourDateTime = datetime.datetime.now() - datetime.timedelta(hours = 1)
    
#      lengthfor date, length in zip(dates,lengths) if date > lastHourDateTime


createGraphic()



logger.reset_level()
