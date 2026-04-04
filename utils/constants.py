from enum import Enum

class AppConstants:
    APP_NAME = "Shopping List Pro"
    VERSION = "1.0.0"
    
    class Status(Enum):
        ACTIVE = 'active'
        INACTIVE = 'inactive'
        PENDING = 'pending'
        COMPLETED = 'completed'
        
    class Categories(Enum):
        GROCERIES = 'groceries'
        HOUSEHOLD = 'household'
        ELECTRONICS = 'electronics'
        CLOTHING = 'clothing'
        
    class Priority(Enum):
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'
        
    CURRENCIES = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
