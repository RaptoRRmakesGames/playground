from flask import Flask, render_template, redirect, request

app = Flask('playground')

@app.route('/')
def index():
    
    return render_template('index.html')