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
import itertools

app = Flask(__name__)

@app.route('/')
def main():
  return redirect("/welcome")

@app.route('/welcome')
def welcome():
  page_title='Choose Healthy'
  pagetext='You can\'t control everything about your health. Take advantage of something you can control: the food you eat.'
  return render_template('welcome.html', page_title=page_title,pagetext=pagetext)

@app.route('/background')
def background():
  page_title = "Background"
  script0 = pickle.load(open('script_0.p','rb'))
  div0 = pickle.load(open('div_0.p','rb'))
  
  script1a = pickle.load(open('script_1a.p','rb'))
  div1a = pickle.load(open('div_1a.p','rb'))

  script1b = pickle.load(open('script_1b.p','rb'))
  div1b = pickle.load(open('div_1b.p','rb'))

  script2a = pickle.load(open('script_2a.p','rb'))
  div2a = pickle.load(open('div_2a.p','rb'))
  script2b = pickle.load(open('script_2b.p','rb'))
  div2b = pickle.load(open('div_2b.p','rb'))

  script3 = pickle.load(open('script_3.p','rb'))
  div3 = pickle.load(open('div_3.p','rb'))
    
  return render_template('backgroundpage.html',page_title=page_title,script0=script0,div0=div0,script1a=script1a,script2a=script2a,div1a=div1a,div2a=div2a,script3=script3,div3=div3,script1b=script1b,div1b=div1b,script2b=script2b, div2b=div2b)


@app.route('/grocerylist', methods=['GET','POST'])
def grocerylist():
  page_title = "Let's start a grocery list"
  pagetext = 'Enter an ingredient and we\'ll show you other ingredients you\'ll need to make popular recipes'
  pagetext2 = 'These are good to have on hand:'
  top_ingreds = pickle.load(open('top_ingreds.p','rb'))
  top_ingreds = [x[0] for x in top_ingreds]
  if request.method=='GET':
      return render_template('grocerylist.html', page_title=page_title, pagetext=pagetext,top_ingreds=top_ingreds,pagetext2=pagetext2)
  else:
      ingred_of_int = request.form['ingred_of_int']
      return redirect('/newlist/'+ingred_of_int)

@app.route('/newlist/<ingred_of_int>', methods=['GET','POST'])
def newlist(ingred_of_int):
  page_title = "Here's your new grocery list"
  pagetext = 'Here are some ingredients that go well with ' + ingred_of_int + ':'
  ingred_pairs = pickle.load(open('ingred_pairs.p','rb'))
  top_ingreds = pickle.load(open('top_ingreds.p','rb'))
  prices = pickle.load(open('prices.p','rb'))
  pick_pairs = list(itertools.ifilter(lambda x: ingred_of_int in x, ingred_pairs))
  grocery_list = [pick_pairs[x][0] if pick_pairs[x][0] != ingred_of_int else pick_pairs[x][1] for x in range(len(pick_pairs))]
  top_ingreds = [x[0] for x in top_ingreds]
  grocery_list = [x for x in grocery_list if x not in top_ingreds][:50]
  price_list = []
  total_cost = 0
  for item in grocery_list:
      if prices[item][0] == 'sorry no price':
          price_list.append(item + '...................' + 'not listed')
      elif len(prices[item]) == 1:
          price_list.append(item + '...................' + prices[item][0])
          total_cost += float(prices[item][0].split()[1])
      elif len(prices[item]) == 2:
          price_list.append(item + '....................' + prices[item][0] + '*')
          total_cost += float(prices[item][0].split()[1])
  price_list1 = price_list[:15]
  price_list2 = price_list[15:]
  return render_template('newlist.html', page_title=page_title, pagetext=pagetext, price_list1=price_list1,price_list2=price_list2)

        

if __name__ == '__main__':
  app.run(port=33507, debug=True)
