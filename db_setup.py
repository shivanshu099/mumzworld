import sqlite3
import os

def init_db():
    db_path = 'gifts.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price_aed REAL NOT NULL,
            age_group TEXT NOT NULL,
            rating REAL
        )
    ''')
    
    sample_gifts = [
        ("Baby Monitor 3000", "High-res video baby monitor with night vision and two-way audio.", "Electronics", 350.0, "0-1 year", 4.8),
        ("Soft Spout Sippy Cup", "Spill-proof sippy cup, perfect for transitioning from bottle.", "Feeding", 45.0, "6-12 months", 4.5),
        ("Ergonomic Baby Carrier", "Comfortable, multi-position baby carrier for newborns to toddlers.", "Travel", 250.0, "0-2 years", 4.7),
        ("Organic Cotton Sleepsuit", "Pack of 3 soft, breathable organic cotton sleepsuits.", "Clothing", 120.0, "0-6 months", 4.9),
        ("Sensory Play Gym", "Interactive play mat with hanging toys to develop motor skills.", "Toys", 180.0, "0-6 months", 4.6),
        ("Teething Relief Set", "Silicone teething rings with textured surfaces.", "Health", 60.0, "3-12 months", 4.5),
        ("Smart Bottle Warmer", "Quickly warms breast milk or formula to the perfect temperature.", "Feeding", 150.0, "0-1 year", 4.4),
        ("Musical Night Light", "Projects stars and plays soothing lullabies.", "Nursery", 90.0, "0-3 years", 4.6),
        ("Stroller Organizer", "Universal fit organizer for diapers, bottles, and keys.", "Accessories", 85.0, "Any", 4.7),
        ("Diaper Backpack", "Stylish and spacious diaper bag with insulated pockets.", "Bags", 190.0, "Any", 4.8),
        ("Wooden Activity Cube", "5-in-1 educational toy with bead maze and shape sorter.", "Toys", 130.0, "1-3 years", 4.8),
        ("Bath Time Gift Set", "Includes hooded towel, gentle wash, and bath toys.", "Bath", 110.0, "0-2 years", 4.7),
        ("Maternity Pillow", "Full body pregnancy pillow for back and belly support.", "Maternity", 160.0, "Pregnancy", 4.9),
        ("First Year Memory Book", "Beautifully illustrated baby record book.", "Gifts", 75.0, "0-1 year", 4.6),
        ("Soothing White Noise Machine", "Portable sound machine for better baby sleep.", "Nursery", 100.0, "0-2 years", 4.5),
        ("Silicone Bib Set", "Set of 3 adjustable, easy-to-clean silicone bibs.", "Feeding", 55.0, "6-24 months", 4.7),
    ]
    
    cursor.executemany('''
        INSERT INTO gifts (name, description, category, price_aed, age_group, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_gifts)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with sample gifts.")

if __name__ == "__main__":
    init_db()
