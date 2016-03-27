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
  return redirect("/poverty_health")

@app.route('/poverty_health')
def poverty_health():
  page_title = "Poverty and health"

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

  p=gridplot([[plot],[plot2]])
  script, div = components(p,CDN)
  script=script.strip()
  return render_template('myplot.html', page_title=page_title, script=script, div=div)

@app.route('/vendor_availability')
def vendor_availability():
  page_title = "Vendor availability"
  percentile_means_df = pickle.load(open('fig2data.p','rb'))
    
  p = Line(percentile_means_df,  x='percentile',
            y=['Grocery Store',
               'Supercenter',
               'Convenience Store',
               'Specialty Store',
              'SNAPS Authorized Store',
               'WIC Authorized Store',
               'Fast Food Restaurant',
               'Full Service Restaurant'],legend='top_left',
            xlabel='Poverty Rate by Percentile',
            ylabel='Stores per 1000 People',
            xgrid=False,title='Change in food vendors as poverty rate increases - US counties, 2012',
color=['Aqua','CornflowerBlue','Blue','BlueViolet','Coral','Crimson','Green','HotPink'])

  script, div = components(p,CDN)
  return render_template('myplot.html', page_title=page_title, script=script, div=div)


@app.route('/predict_obesity')
def predict_obesity():
  page_title = "Predict Obesity"
  scores = np.load('scores_file.npy')
  lowci = np.percentile(scores,2.5,axis=0)
  highci = np.percentile(scores,97.5,axis=0)
  CIs = np.matrix([lowci,highci])
  
  scores_svm = np.load('scores_svm.npy')
  lowci_svm = np.percentile(scores_svm,2.5,axis=0)
  highci_svm = np.percentile(scores_svm,97.5,axis=0)
  CIs_svm = np.matrix([lowci_svm,highci_svm])

  p1 = figure(title='Predicting obesity from poverty, food access, food availability (logistic)',title_text_font_size='12pt')
  p1.quad(top=.7,bottom=.5,left=[.55,1.55,2.55,3.55],right=[1.45,2.45,3.45,4.45],alpha=.2,color=['red','blue','blue','blue'])
  p1.multi_line(xs=[[1,1],[2,2],[3,3],[4,4]],ys=[CIs[:,0],CIs[:,1],CIs[:,2],CIs[:,3]],line_width = 4)
  p1.circle(x=[1,2,3,4],y=scores.mean(axis=0),size=10,color='red')
  p1.xgrid.grid_line_color = None
  p1.ygrid.grid_line_color = None
  p1.xaxis.major_label_text_color = None
  p1.yaxis.axis_label = "Classifier accuracy"
  p1.text(.7,.51,['All variables'],text_font_size='10pt')
  p1.text(1.55,.51,['Drop poverty rate'],text_font_size='10pt')
  p1.text(2.7,.51,['Drop access'],text_font_size='10pt')
  p1.text(3.6,.51,['Drop availablity'],text_font_size='10pt')

  p2 = figure(title='Predict obesity from poverty, food access, food availability (SVM)',title_text_font_size = '12pt')
  p2.quad(top=.7,bottom=.5,left=[.55,1.55,2.55,3.55],right=[1.45,2.45,3.45,4.45],alpha=.2,color=['red','blue','blue','blue'])
  p2.multi_line(xs=[[1,1],[2,2],[3,3],[4,4]],ys=[CIs_svm[:,0],CIs_svm[:,1],CIs_svm[:,2],CIs_svm[:,3]],line_width=4)
  p2.circle(x=[1,2,3,4],y=scores_svm.mean(axis=0),size=10,color='red')
  p2.xgrid.grid_line_color = None
  p2.ygrid.grid_line_color = None
  p2.xaxis.major_label_text_color = None
  p2.yaxis.axis_label = "Classifier accuracy"
  p2.text(.7,.51,['All variables'],text_font_size='10pt')
  p2.text(1.55,.51,['Drop poverty rate'],text_font_size='10pt')
  p2.text(2.7,.51,['Drop access'],text_font_size='10pt')
  p2.text(3.6,.51,['Drop availability'], text_font_size='10pt')

  p = gridplot([[p1],[p2]])
  script, div = components(p,CDN)
  return render_template('myplot.html', page_title=page_title, script=script, div=div)


@app.route('/food_choice')
def food_choice():
  page_title = "Food choice"
#  xl_file = 'DataDownload.xls'
#  data = pd.ExcelFile(xl_file)
#  sheet_names = data.sheet_names
#  all_dfs = {sheet: data.parse(sheet) for sheet in sheet_names}

#  restaurants_df = all_dfs['RESTAURANTS']
#  restaurants_df = restaurants_df[['State','County','PC_FFRSALES07','PC_FSRSALES07']]
#  restaurants_df.columns = ['State','County','Per Capita Fast Food','Per Capita Full Service']
  
#  socioec_df = all_dfs['SOCIOECONOMIC']
#  socioec_df = socioec_df[['State','County','POVRATE10']]
#  health_df = all_dfs['HEALTH']
#  health_df = health_df[['State','County','PCT_OBESE_ADULTS10']]
#  health_se_df = pd.merge(socioec_df,health_df,on=['State','County'])
#  health_se_df.columns = ['State','County','Poverty Rate','Adult Obesity Rate']

#  insec_df = all_dfs['INSECURITY']
#  insec_df = insec_df[['State','County','FOODINSEC_10_12']]
#  insec_df.columns = ['State','County','PercInsecure']

#  insecRes_df = pd.merge(insec_df,restaurants_df, on=['State','County'])
#  meals_df = pd.merge(health_se_df,insecRes_df,on = ['State','County'])
#  meals_df['Meals FF'] = meals_df['Per Capita Fast Food']/6.0
#  meals_df['Meals FS'] = meals_df['Per Capita Full Service']/12.0

#  meals_df['Poverty Rate']=[x  if any([type(x) == int,type(x)==float]) else np.nan for x in meals_df['Poverty Rate']]
#  meals_df['Poverty Rate'] = np.float64(meals_df['Poverty Rate'])

#  stateMeans = meals_df.groupby('State').mean()
#  stateMeans['percentFF'] = 100*stateMeans['Meals FF']/(stateMeans['Meals FF'] + stateMeans['Meals FS'])

#  data = ColumnDataSource(data=dict(percentFF = stateMeans['percentFF'],povRate = stateMeans['Poverty Rate'],state = stateMeans.index))
  use_data2 = pickle.load(open('fig4bdata.p','rb'))
    
  hover = HoverTool(tooltips = [('State','@state')])
  plot2 = figure(
      title = 'More meals "out" at fast food restaurants correlates with higher obesity',
      title_text_font_size='12pt', 
      x_axis_label = 'Percent of meals "out" at fast food',
      y_axis_label = 'Obesity Rate',tools=[hover])
  plot2.scatter('percentFF','obesityRate',size=10,source = use_data2)

  script, div = components(plot2,CDN)
  return render_template('myplot.html', page_title=page_title, script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507)
