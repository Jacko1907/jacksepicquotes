from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests 
import json
import random




# Config 
quotesurl = 'https://type.fit/api/quotes'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'Heroku_Database_URL'
db = SQLAlchemy(app)


class LikedQuote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False)
    index = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return '<Index %r>' % self.index

@app.route('/')
def index():
    # This is the home page
    return render_template('index.html')

@app.route('/motivationalquote')
def motivationalquote():
    # This is the motivational quote page
    
    # Requesting all of the quotes
    quotesrequest = requests.get(quotesurl)
    quotes = json.loads(quotesrequest.content)


    # Selecting random quote and image, then sending them to the page on request.
    quote = random.choice(quotes)
    index = quotes.index(quote)
    return render_template('motivational.html', quote=quote, index=index)

@app.route('/motivationalquote/<int:index>/')
def motivationalquotespecific(index):
    # This is the motivational quote page
    
    # Requesting all of the quotes
    quotesrequest = requests.get(quotesurl)
    quotes = json.loads(quotesrequest.content)


    # Selecting random quote and image, then sending them to the page on request.
    quote = quotes[index]
    return render_template('motivational.html', quote=quote, index=index)

@app.route('/likequote/<int:index>/')
def likequote(index):
    quotesrequest = requests.get(quotesurl)
    quotes = json.loads(quotesrequest.content)
    ip = 0

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
       ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ('HTTP_X_FORWARDED_FOR') # if behind a proxy
    


    if index <= len(quotes):
        exists = db.session.query(db.exists().where(LikedQuote.index == index and LikedQuote.ip == ip)).scalar()
        if exists == True: 
            return redirect('/likedquotes')
        newliked = LikedQuote(ip=ip, index=index)
        try:
            db.session.add(newliked)
            db.session.commit()
            return redirect(f'/motivationalquote/{index}')
        except:
            return 'There was an error'
        
    else: 
        return 'Sorry! This is not a valid quote!'

@app.route('/likedquotes')
def likedquotes():
    ip = 0
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
       ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ('HTTP_X_FORWARDED_FOR') # if behind a proxy
    


    quotes = LikedQuote.query.where(LikedQuote.ip==ip)
    count = quotes.count()
    return render_template('likedquotes.html', quotes=quotes, count=count)

@app.route('/deletelikedquote/<int:id>')
def deletelikedquote(id):
    ip = 0

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
       ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ('HTTP_X_FORWARDED_FOR') # if behind a proxy

    exists = db.session.query(db.exists().where(LikedQuote.id == id and LikedQuote.ip == ip)).scalar()
    if exists == True: 
        todelete = LikedQuote.query.get_or_404(id)
        db.session.delete(todelete)
        db.session.commit()
        return redirect('/likedquotes')
    else: 
        return 'You do not have a liked quote with this index'





if __name__ == '__main__':
    app.run(debug=False)

