from app import app


# Keep debug to false in production 
if __name__ == '__main__':
    app.run(debug=False)
