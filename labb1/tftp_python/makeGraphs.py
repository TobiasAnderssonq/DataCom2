import json
import ast
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import subprocess
import os
import time

plotly.tools.set_credentials_file(username='sambakalle', api_key='5w9vb7wh65')
py.sign_in('sambakalle', '5w9vb7wh65')

fileSize = ['Small', 'Medium', 'Large']

#GRAPHS SCENARIO 1 - SSH INTO SCHOOL FROM HOME WIFI
SSH6969DL = [0.232141039371, 0.279837489128, 0.305791189671]
SSH6969UL = [0.0328373289108, 0.0477843213081, 0.10544271946]

SSH11069DL = [0.344007897377, 2.8003895998, 13.0062170029]
SSH11069UL = [0.594337701797, 3.25572628975, 12.6210705042]

SSH12069DL = [0.795105290413, 6.10716099739, 24.0575241804]
SSH12069UL = [0.995596790314, 5.42042789459, 24.8823272943]

SSH13069DL = [0.827843809128, 9.43416190147, 39.3842238903]
SSH13069UL = [1.65301389694, 8.4744893074, 41.0700582027]

# Edit the layout
layout = dict(title = 'SSH from home to school - WiFi',
              xaxis = dict(title = 'FileSize'),
              yaxis = dict(title = 'Average time'),
              )

trace1 = go.Scatter(
    x = fileSize,
    y = SSH6969DL,
    name = '6969 Download',
    line = dict(
        color = ('rgb(255, 255, 0)'),
        width = 4,)
)

trace2 = go.Scatter(
    x = fileSize,
    y = SSH6969UL,
    name = '6969 Upload',
    line = dict(
        color = ('rgb(210, 210, 0)'),
        width = 4,)
)
data = [trace1, trace2]

#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='SSH6969')


trace3 = go.Scatter(
    x = fileSize,
    y = SSH11069DL,
    name = '11069 Download',
    line = dict(
        color = ('rgb(0, 0, 255)'),
        width = 4,)
)

trace4 = go.Scatter(
    x = fileSize,
    y = SSH11069UL,
    name = '11069 Upload',
    line = dict(
        color = ('rgb(0, 0, 210)'),
        width = 4,)
)
data = [trace3, trace4]


# Plot and embed in ipython notebook!
#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='SSH11069')

trace5 = go.Scatter(
    x = fileSize,
    y = SSH12069DL,
    name = '12069 Download',
    line = dict(
        color = ('rgb(0, 255, 0)'),
        width = 4,)
)

trace6 = go.Scatter(
    x = fileSize,
    y = SSH12069UL,
    name = '12069 Upload',
    line = dict(
        color = ('rgb(0, 210, 0)'),
        width = 4,)
)
data = [trace5, trace6]


# Plot and embed in ipython notebook!
#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='SSH12069')

trace7 = go.Scatter(
    x = fileSize,
    y = SSH13069DL,
    name = '13069 Download',
    line = dict(
        color = ('rgb(255, 0, 0)'),
        width = 4,)
)

trace8 = go.Scatter(
    x = fileSize,
    y = SSH13069UL,
    name = '13069 Upload',
    line = dict(
        color = ('rgb(210, 0, 0)'),
        width = 4,)
)
data = [trace7, trace8]


# Plot and embed in ipython notebook!
#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='SSH13069')

data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
fig = dict(data=data, layout=layout)
py.iplot(fig, filename='AllSSH')

#GRAPHS SCENARIO 2 - HOME CABLE NETWORK
SSH6969DL = [0.122399902344, 0.559082317352, 1.27906601429]
SSH6969UL = [0.124615812302, 0.577993988991, 1.56394741535]

SSH11069DL = [0.209110713005, 2.71592831612, 14.9982268095]
SSH11069UL = [0.862228393555, 2.22237920761, 16.1688059092]

SSH12069DL = [0.299993896484, 5.26800639629, 27.4504888058]
SSH12069UL = [0.70143737793, 5.8363699913, 28.5755963087]

SSH13069DL = [1.02115738392, 8.25715308189, 41.2207322121]
SSH13069UL = [0.945095610619, 8.41062729359, 40.4742142916]

# Edit the layout
layout = dict(title = 'Home network - cable',
              xaxis = dict(title = 'FileSize'),
              yaxis = dict(title = 'Average time'),
              )

trace1 = go.Scatter(
    x = fileSize,
    y = SSH6969DL,
    name = '6969 Download',
    line = dict(
        color = ('rgb(255, 255, 0)'),
        width = 4,)
)

trace2 = go.Scatter(
    x = fileSize,
    y = SSH6969UL,
    name = '6969 Upload',
    line = dict(
        color = ('rgb(210, 210, 0)'),
        width = 4,)
)
data = [trace1, trace2]

#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='CABLE6969')


trace3 = go.Scatter(
    x = fileSize,
    y = SSH11069DL,
    name = '11069 Download',
    line = dict(
        color = ('rgb(0, 0, 255)'),
        width = 4,)
)

trace4 = go.Scatter(
    x = fileSize,
    y = SSH11069UL,
    name = '11069 Upload',
    line = dict(
        color = ('rgb(0, 0, 210)'),
        width = 4,)
)
data = [trace3, trace4]


# Plot and embed in ipython notebook!
#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='CABLE11069')

trace5 = go.Scatter(
    x = fileSize,
    y = SSH12069DL,
    name = '12069 Download',
    line = dict(
        color = ('rgb(0, 255, 0)'),
        width = 4,)
)

trace6 = go.Scatter(
    x = fileSize,
    y = SSH12069UL,
    name = '12069 Upload',
    line = dict(
        color = ('rgb(0, 210, 0)'),
        width = 4,)
)
data = [trace5, trace6]


# Plot and embed in ipython notebook!
#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='SSH12069')

trace7 = go.Scatter(
    x = fileSize,
    y = SSH13069DL,
    name = '13069 Download',
    line = dict(
        color = ('rgb(255, 0, 0)'),
        width = 4,)
)

trace8 = go.Scatter(
    x = fileSize,
    y = SSH13069UL,
    name = '13069 Upload',
    line = dict(
        color = ('rgb(210, 0, 0)'),
        width = 4,)
)
data = [trace7, trace8]


# Plot and embed in ipython notebook!
#fig = dict(data=data, layout=layout)
#py.iplot(fig, filename='CABLE13069')

data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
fig = dict(data=data, layout=layout)
py.iplot(fig, filename='AllCABLE')



#GRAPHS SCENARIO 3 - SCHOOL WIFI
