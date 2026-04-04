import kivy
kivy.require('2.1.0')

from app.shopping_app import ShoppingApp

if __name__ == '__main__':
    shopping_app = ShoppingApp()
    shopping_app.run()
