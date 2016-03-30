from flask import Flask, render_template, request, redirect
from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import CDN
from bokeh.charts import Bar, Line
from bokeh.io import gridplot,vplot
from bokeh.models import HoverTool
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)

@app.route('/')
def main():
  return redirect("/welcome")

@app.route('/welcome')
def welcome():
  page_title='Choose Healthy'
  pagetext='You can\'t control everything about your health ... Take advantage of what you can control'
  return render_template('welcome.html', page_title=page_title,pagetext=pagetext)

@app.route('/background')
def background():
  page_title = "Background"

  health_se_df = pickle.load(open('fig1data.p','rb'))
  health_se_df['Poverty Rate'] = np.float64(health_se_df['Poverty Rate'])
  plot = figure(plot_width=500, plot_height=400,x_axis_label='Poverty Rate',y_axis_label='Adult Obesity Rate',title='Obesity increases with poverty rate - US counties 2010',title_text_font_size='12pt')
  plot.scatter(health_se_df['Poverty Rate'],health_se_df['Adult Obesity Rate'],marker='+',color='DarkSlateGray')
  plot.xaxis.axis_label_text_font_size='9pt'
  plot.yaxis.axis_label_text_font_size='9pt'
  plot.text(0,50,['A 10% increase in poverty rate corresponds to a 3% increase in obesity rate'],text_font_size='8pt')

  regr = np.polyfit(health_se_df['Poverty Rate'],health_se_df['Adult Obesity Rate'],1)

  mx_X = max(health_se_df['Poverty Rate'])
  vals_X = range(np.int(round(mx_X)))
  vals_Y = regr[0]*np.float64(vals_X) + regr[1]

  plot.line(vals_X,vals_Y,color='red',line_width=1.5)

  plot2 = figure(plot_width=500, plot_height=400,x_axis_label='Poverty Rate', y_axis_label='Adult Diabetes Rate', title='Diabetes increases with poverty rate - US counties 2010', title_text_font_size='12pt')
  plot2.scatter(health_se_df['Poverty Rate'],health_se_df['Adult Diabetes Rate'], marker='+',color='DarkSlateBlue')
  plot2.xaxis.axis_label_text_font_size='9pt'
  plot2.yaxis.axis_label_text_font_size='9pt'
  plot2.text(0,20,['a 10% increase in poverty rate corresponds to a 2% increase in diabetes rate'],text_font_size='8pt')
  
  regr2 = np.polyfit(health_se_df['Poverty Rate'],health_se_df['Adult Diabetes Rate'],1)
  mx_X2 = max(health_se_df['Poverty Rate'])
  vals_X2 = range(np.int(round(mx_X2)))
  vals_Y2 = regr2[0]*np.float64(vals_X2) + regr2[1]
  plot2.line(vals_X2,vals_Y2,color='red',line_width=1.5)
  p0=gridplot([[plot,plot2]])
  script0, div0 = components(p0,CDN)
    
  percentile_means_df = pickle.load(open('fig2data.p','rb'))
    
  p1 = Line(percentile_means_df,  x='percentile',
            y=['Grocery Store',
              # 'Supercenter',
               'Convenience Store',
              # 'Specialty Store',
             # 'SNAPS Authorized Store',
             #  'WIC Authorized Store',
               'Fast Food Restaurant',
               'Full Service Restaurant'],legend='bottom_left',
            xlabel='Poverty Rate by Percentile',
            ylabel='Stores per 1000 People',
            xgrid=False,
color=['Aqua','CornflowerBlue','Coral','Green'],
          plot_width=500, plot_height=600)

  script1,div1 = components(p1,CDN)
    
  scores = np.load('scores_file.npy')
  lowci = np.percentile(scores,2.5,axis=0)
  highci = np.percentile(scores,97.5,axis=0)
  CIs = np.matrix([lowci,highci])
  
  scores_svm = np.load('scores_svm.npy')
  lowci_svm = np.percentile(scores_svm,2.5,axis=0)
  highci_svm = np.percentile(scores_svm,97.5,axis=0)
  CIs_svm = np.matrix([lowci_svm,highci_svm])

  p1 = figure(title='Predicting obesity from poverty, food access, food availability (logistic)',title_text_font_size='12pt',plot_width=550, plot_height=400)
  p1.quad(top=.7,bottom=.5,left=[.55,1.55,2.55,3.55],right=[1.45,2.45,3.45,4.45],alpha=.2,color=['red','blue','blue','blue'])
  p1.multi_line(xs=[[1,1],[2,2],[3,3],[4,4]],ys=[CIs[:,0],CIs[:,1],CIs[:,2],CIs[:,3]],line_width = 4)
  p1.circle(x=[1,2,3,4],y=scores.mean(axis=0),size=10,color='red')
  p1.xgrid.grid_line_color = None
  p1.ygrid.grid_line_color = None
  p1.xaxis.major_label_text_color = None
  p1.yaxis.axis_label = "Classifier accuracy"
  p1.text(.65,.51,['All variables'],text_font_size='10pt')
  p1.text(1.5,.51,['Drop poverty rate'],text_font_size='10pt')
  p1.text(2.65,.51,['Drop access'],text_font_size='10pt')
  p1.text(3.55,.51,['Drop availablity'],text_font_size='10pt')

  p2 = figure(title='Predict obesity from poverty, food access, food availability (SVM)',title_text_font_size = '12pt',plot_width=550,plot_height=400)
  p2.quad(top=.7,bottom=.5,left=[.55,1.55,2.55,3.55],right=[1.45,2.45,3.45,4.45],alpha=.2,color=['red','blue','blue','blue'])
  p2.multi_line(xs=[[1,1],[2,2],[3,3],[4,4]],ys=[CIs_svm[:,0],CIs_svm[:,1],CIs_svm[:,2],CIs_svm[:,3]],line_width=4)
  p2.circle(x=[1,2,3,4],y=scores_svm.mean(axis=0),size=10,color='red')
  p2.xgrid.grid_line_color = None
  p2.ygrid.grid_line_color = None
  p2.xaxis.major_label_text_color = None
  p2.yaxis.axis_label = "Classifier accuracy"
  p2.text(.65,.51,['All variables'],text_font_size='10pt')
  p2.text(1.5,.51,['Drop poverty rate'],text_font_size='10pt')
  p2.text(2.65,.51,['Drop access'],text_font_size='10pt')
  p2.text(3.55,.51,['Drop availability'], text_font_size='10pt')

  p = gridplot([[p1,p2]])
  script2, div2 = components(p,CDN)

  use_data2 = pickle.load(open('fig4bdata.p','rb'))
    
  hover = HoverTool(tooltips = [('State','@state')])
  plot2 = figure(
      title_text_font_size='12pt', 
      x_axis_label = 'Percent of meals "out" at fast food',
      y_axis_label = 'Obesity Rate',tools=[hover],plot_width=500,plot_height=400)
  plot2.scatter('percentFF','obesityRate',size=10,source = use_data2)

  script3,div3 = components(plot2,CDN)
    
  return render_template('backgroundpage.html',page_title=page_title,script0=script0,div0=div0,script1=script1,script2=script2,div1=div1,div2=div2,script3=script3,div3=div3)


@app.route('/grocerylist', methods=['GET','POST'])
def grocerylist():
  page_title = "Let's start a grocery list"
  pagetext = 'Enter an ingredient and we\'ll show you other ingredients you\'ll need to make popular recipes'
  if request.method=='GET':
      return render_template('grocerylist.html', page_title=page_title, pagetext=pagetext)
  else:
      ingred_of_int = request.form['ingred_of_int']
      return redirect('/newlist/'+ingred_of_int)

@app.route('/newlist/<ingred_of_int>', methods=['GET','POST'])
def newlist(ingred_of_int):
  page_title = "Here's your new grocery list"
  pagetext = 'You picked ' + ingred_of_int + ' but I haven\'t finished this page yet so here\'s a picture of my dog!'
  return render_template('newlist.html', page_title=page_title, pagetext=pagetext)

if __name__ == '__main__':
  app.run(port=33507,debug = True)
