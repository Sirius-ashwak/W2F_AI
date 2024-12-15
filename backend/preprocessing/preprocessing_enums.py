from enum import Enum

class DifficultyLevel(str, Enum):
    """Difficulty level of recipe preparation."""
    EASY = "easy"  # Simple recipes with few steps
    MODERATE = "moderate"  # More complex but still manageable
    CHALLENGING = "challenging"  # Complex recipes requiring skill
    EXPERT = "expert"  # Professional-level recipes

# Mapping of difficulty levels to emojis
DIFFICULTY_MAP = {
    "easy": "Easy - 👶",  # Baby face for easy recipes
    "moderate": "Moderate - 👌",  # OK hand for moderate difficulty
    "challenging": "Challenging - 💪",  # Flexed biceps for challenging recipes  
    "expert": "Expert - 👨‍🍳" # Chef for expert level recipes
}

class CookingMethod(str, Enum):
    """Primary cooking methods."""
    BAKE = "bake"
    BROIL = "broil"
    GRILL = "grill"
    FRY = "fry"
    SAUTE = "saute"
    ROAST = "roast"
    STEAM = "steam"
    BOIL = "boil"
    SIMMER = "simmer"
    SLOW_COOK = "slow_cook"
    PRESSURE_COOK = "pressure_cook"
    NO_COOK = "no_cook"
    SMOKE = "smoke"
    FERMENT = "ferment"

# Mapping of cooking methods to emojis
COOKING_METHOD_MAP = {
    "bake": "Bake - 🥖",  # Bread for baking
    "broil": "Broil - 🔥",  # Fire for broiling
    "grill": "Grill - 🍖",  # Meat on bone for grilling
    "fry": "Fry - 🍳",  # Frying pan for frying
    "saute": "Saute - 🥘",  # Shallow pan for sauteing
    "roast": "Roast - 🦃",  # Turkey for roasting
    "steam": "Steam - ♨️",  # Fondue for boiling
    "boil": "Boil - 🥣",  # Bowl with spoon for simmering
    "simmer": "Simmer - 🍲",  # Pot of food for slow cooking
    "slow_cook": "Slow Cook - 🥘",  # Pan for pressure cooking
    "pressure_cook": "Pressure Cook - 🥘",  # Pan for pressure cooking
    "no_cook": "No Cook - 🥗",  # Green salad for no-cook
    "smoke": "Smoke - 💨",  # Dashing away for smoking
    "ferment": "Ferment - 🧪"  # Test tube for fermenting
}

class Equipment(str, Enum):
    """Common kitchen equipment needed."""
    OVEN = "oven"
    STOVETOP = "stovetop"
    MICROWAVE = "microwave"
    GRILL = "grill"
    SLOW_COOKER = "slow_cooker"
    PRESSURE_COOKER = "pressure_cooker"
    BLENDER = "blender"
    FOOD_PROCESSOR = "food_processor"
    MIXER = "mixer"
    BAKING_DISH = "baking_dish"
    CUTTING_BOARD = "cutting_board"
    KNIFE = "knife"
    POT = "pot"
    PAN = "pan"
    SHEET_PAN = "sheet_pan"

# Mapping of equipment to emojis
EQUIPMENT_MAP = {
    "oven": "Oven - 🔥",  # Fire for oven
    "stovetop": "Stovetop - 🎯",  # Target for stovetop burner
    "microwave": "Microwave - 📡",  # Satellite dish for microwave
    "grill": "Grill - 🔥",  # Fire for grill
    "slow_cooker": "Slow Cooker - 🍲",  # Pot of food for slow cooker
    "pressure_cooker": "Pressure Cooker - ♨️",  # Hot springs for pressure cooker
    "blender": "Blender - 🌪️",  # Tornado for blender
    "food_processor": "Food Processor - ⚙️",  # Gear for food processor
    "mixer": "Mixer - 🔄",  # Arrows in circle for mixer
    "baking_dish": "Baking Dish - 🥘",  # Pan for baking dish
    "cutting_board": "Cutting Board - 🪚",  # Saw for cutting board
    "knife": "Knife - 🔪",  # Kitchen knife
    "pot": "Pot - 🥘",  # Pan for pot
    "pan": "Pan - 🍳",  # Frying pan
    "sheet_pan": "Sheet Pan - 📄"  # Page for sheet pan
}

class MealType(str, Enum):
    """Types of meals throughout the day."""
    
    BREAKFAST = "breakfast"  # First meal of the day, typically eaten in the morning
    BRUNCH = "brunch"  # Combination of breakfast and lunch, eaten mid-morning to early afternoon
    LUNCH = "lunch"  # Midday meal, often lighter than dinner
    AFTERNOON_TEA = "afternoon_tea"  # Light meal between lunch and dinner with tea, pastries, sandwiches
    DINNER = "dinner"  # Main meal of the day, typically eaten in the evening
    SUPPER = "supper"  # Lighter evening meal, often eaten later than dinner
    SNACK = "snack"  # Small portion of food consumed between meals
    MIDNIGHT_SNACK = "midnight_snack"  # Late-night meal or snack eaten before bed

# Mapping of meal types to emojis
MEAL_TYPE_MAP = {
    "breakfast": "Breakfast - 🍳",  # Frying pan with egg for breakfast
    "brunch": "Brunch - 🥞",  # Pancakes for brunch
    "lunch": "Lunch - 🥪",  # Sandwich for lunch
    "afternoon_tea": "Afternoon Tea - ☕",  # Hot beverage for afternoon tea
    "dinner": "Dinner - 🍽️",  # Plate with utensils for dinner
    "supper": "Supper - 🥘",  # Pan of food for supper
    "snack": "Snack - 🍿",  # Popcorn for snack
    "midnight_snack": "Midnight Snack - 🌙"  # Crescent moon for midnight snack
}

class CourseType(str, Enum):
    """Types of courses in a meal."""
    
    APPETIZER = "appetizer"  # Small dish served at the beginning, like soup, salad, or finger foods
    MAIN_COURSE = "main_course"  # Central and most substantial dish, often protein with sides
    SIDE_DISH = "side_dish"  # Accompaniments to the main course, like vegetables, rice, potatoes
    DESSERT = "dessert"  # Sweet dish to conclude the meal, like cake, ice cream, pie
    BEVERAGE = "beverage"  # Drinks served throughout the meal, including water, wine, coffee

# Mapping of course types to emojis
COURSE_TYPE_MAP = {
    "appetizer": "Appetizer - 🥗",  # Green salad for appetizer
    "main_course": "Main Course - 🍖",  # Meat on bone for main course
    "side_dish": "Side Dish - 🥔",  # Potato for side dish
    "dessert": "Dessert - 🍰",  # Shortcake for dessert
    "beverage": "Beverage - 🥤"  # Cup with straw for beverage
}

class Cuisine(str, Enum):
    """World cuisines and their key characteristics."""
    
    ITALIAN = "italian"  # Pasta, pizza, risotto, olive oil, garlic, tomatoes, herbs
    FRENCH = "french"  # Refined sauces, breads, pastries, coq au vin, croissants
    MEXICAN = "mexican"  # Corn, beans, chili peppers, tacos, enchiladas, guacamole
    CHINESE = "chinese"  # Regional styles, Sichuan spicy dishes, Cantonese dim sum, rice, noodles
    JAPANESE = "japanese"  # Sushi, sashimi, ramen, tempura, emphasis on fresh ingredients
    INDIAN = "indian"  # Bold spices, curries, tandoori dishes, regional variations
    THAI = "thai"  # Balance of sweet, sour, salty, spicy; pad Thai, green curry, tom yum
    GREEK = "greek"  # Olive oil, fresh vegetables, herbs, lamb, seafood, moussaka
    MIDDLE_EASTERN = "middle_eastern"  # Hummus, falafel, kebabs, pita bread, cumin, sumac
    AMERICAN = "american"  # BBQ, burgers, clam chowder, Southern fried chicken
    SPANISH = "spanish"  # Tapas, paella, jamón, churros, saffron
    KOREAN = "korean"  # Fermented foods, kimchi, bulgogi, spicy stews
    VIETNAMESE = "vietnamese"  # Fresh herbs, rice noodles, light broths, pho, banh mi
    CARIBBEAN = "caribbean"  # Jerk chicken, plantains, rice and peas
    AFRICAN = "african"  # Diverse regional cuisines, tagines, injera, jollof rice
    TURKISH = "turkish"  # Kebabs, baklava, meze, Mediterranean influences
    BRAZILIAN = "brazilian"  # Churrasco, feijoada, pão de queijo
    ARGENTINIAN = "argentinian"  # Beef, empanadas, chimichurri sauce
    GERMAN = "german"  # Sausages, schnitzel, pretzels, sauerkraut
    RUSSIAN = "russian"  # Borscht, pelmeni, blini
    ETHIOPIAN = "ethiopian"  # Injera, spiced stews, lentils
    CAJUN_CREOLE = "cajun_creole"  # Gumbo, jambalaya, crawfish étouffée
    LEBANESE = "lebanese"  # Tabbouleh, fattoush, shawarma
    FILIPINO = "filipino"  # Adobo, sinigang, lechon
    PERUVIAN = "peruvian"  # Ceviche, lomo saltado, quinoa
    MOROCCAN = "moroccan"  # Tagines, couscous, preserved lemons
    CUBAN = "cuban"  # Ropa vieja, black beans, plantains
    SWEDISH = "swedish"  # Meatballs, gravlax, lingonberry sauce
    HAWAIIAN = "hawaiian"  # Poke, loco moco, kalua pork
    PORTUGUESE = "portuguese"  # Seafood, bacalhau, pastel de nata
    POLISH = "polish"  # Pierogi, kielbasa, borscht
    MALAYSIAN = "malaysian"  # Nasi lemak, laksa, fusion influences
    INDONESIAN = "indonesian"  # Satay, nasi goreng, rendang
    SINGAPOREAN = "singaporean"  # Chili crab, Hainanese chicken rice
    PAKISTANI = "pakistani"  # Kebabs, biryani, nihari

class DietaryRestriction(str, Enum):
    """Dietary restrictions and their descriptions."""
    
    VEGETARIAN = "vegetarian"  # Avoids meat, poultry, and seafood. May include dairy and eggs
    VEGAN = "vegan"  # Avoids all animal-derived products
    PESCATARIAN = "pescatarian"  # Avoids meat and poultry but includes fish and seafood
    GLUTEN_FREE = "gluten_free"  # Avoids gluten (wheat, barley, rye, some oats)
    LACTOSE_FREE = "lactose_free"  # Avoids dairy products containing lactose
    DAIRY_FREE = "dairy_free"  # Avoids all dairy products
    NUT_FREE = "nut_free"  # Avoids all tree nuts and peanuts
    SOY_FREE = "soy_free"  # Avoids all soy products
    SHELLFISH_FREE = "shellfish_free"  # Avoids shellfish
    EGG_FREE = "egg_free"  # Avoids eggs and products containing eggs

class CleanupEffort(str, Enum):
    """Indicates the cleanup effort required after cooking."""
    
    EASY = "easy"  # Minimal dishes, simple cleanup (e.g., one-pot meals, sheet pan dinners)
    INTENSIVE = "intensive"  # Many dishes, complex cleanup (e.g., multiple pots/pans, special equipment)

# Emoji map for cleanup effort levels
CLEANUP_EFFORT_MAP = {
    "easy": "Easy - 🧹",  # Broom emoji for easy cleanup
    "intensive": "Intensive - 🧽🧼"  # Sponge and soap emoji for intensive cleanup
}