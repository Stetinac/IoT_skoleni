"""
soubor slouzi pouze pro Gunicorn
"""
from app import app

if __name__ == '__main__':
    app.rum()