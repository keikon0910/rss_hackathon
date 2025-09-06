from app.routes import create_app   

app = create_app()

app.secret_key = 'your_secret_key_here'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
