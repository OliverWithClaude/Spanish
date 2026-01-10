"""
Initial content for Spanish Learning App
Madrid-specific Spanish phrases and vocabulary
"""

from src.database import init_database, add_phrase, add_vocabulary, get_all_vocabulary, get_phrases

# ============ Greetings & Basic Phrases ============
GREETINGS = [
    ("¡Hola!", "Hello!", "Start any conversation"),
    ("Buenos días", "Good morning", "Use until about 2 PM"),
    ("Buenas tardes", "Good afternoon", "Use from 2 PM to 8 PM"),
    ("Buenas noches", "Good evening/night", "Use after 8 PM or when leaving"),
    ("¿Qué tal?", "How's it going?", "Casual greeting"),
    ("¿Cómo estás?", "How are you?", "Informal"),
    ("¿Cómo está usted?", "How are you?", "Formal"),
    ("Muy bien, gracias", "Very well, thanks", "Common response"),
    ("¿Y tú?", "And you?", "Informal follow-up"),
    ("Hasta luego", "See you later", "Common goodbye"),
    ("Hasta mañana", "See you tomorrow", "For work colleagues"),
    ("¡Que tengas un buen día!", "Have a nice day!", "Friendly farewell"),
    ("Encantado/Encantada", "Nice to meet you", "Male/Female form"),
    ("Mucho gusto", "Pleased to meet you", "Also common"),
]

# ============ Workplace Phrases ============
WORKPLACE = [
    ("¿Tienes un momento?", "Do you have a moment?", "To get someone's attention"),
    ("Tengo una pregunta", "I have a question", "Starting a query"),
    ("¿Me puedes ayudar?", "Can you help me?", "Asking for help"),
    ("No entiendo", "I don't understand", "Very useful!"),
    ("¿Puedes repetir, por favor?", "Can you repeat, please?", "Ask for repetition"),
    ("Más despacio, por favor", "Slower, please", "When they speak too fast"),
    ("¿Cómo se dice...?", "How do you say...?", "Learning new words"),
    ("¿Qué significa...?", "What does ... mean?", "Understanding vocabulary"),
    ("Tenemos una reunión", "We have a meeting", "Meeting-related"),
    ("¿A qué hora es la reunión?", "What time is the meeting?", "Asking about time"),
    ("Estoy trabajando en...", "I'm working on...", "Describing your work"),
    ("Ya está", "It's done", "Task completed"),
    ("Necesito más tiempo", "I need more time", "When you need extension"),
    ("¿Quedamos a las tres?", "Shall we meet at three?", "Scheduling"),
    ("Perfecto", "Perfect", "Agreement"),
    ("De acuerdo", "Agreed / OK", "Confirming"),
    ("Vale", "OK", "Very common in Spain"),
]

# ============ Coffee Break / Smalltalk ============
SMALLTALK = [
    ("¿Tomamos un café?", "Shall we have a coffee?", "Coffee break invitation"),
    ("Un café con leche, por favor", "A latte, please", "Common coffee order"),
    ("Un cortado, por favor", "An espresso with milk, please", "Madrid favorite"),
    ("¿Qué tal el fin de semana?", "How was your weekend?", "Monday smalltalk"),
    ("¿Tienes planes para el fin de semana?", "Do you have plans for the weekend?", "Friday smalltalk"),
    ("Hace buen tiempo hoy", "The weather is nice today", "Weather talk"),
    ("Hace mucho calor", "It's very hot", "Summer in Madrid"),
    ("Hace mucho frío", "It's very cold", "Winter comment"),
    ("¿Has visto el partido?", "Did you see the game?", "Sports smalltalk"),
    ("¿Qué vas a hacer esta noche?", "What are you doing tonight?", "Evening plans"),
    ("Voy a salir con amigos", "I'm going out with friends", "Social plans"),
    ("Me quedo en casa", "I'm staying home", "Quiet evening"),
]

# ============ Numbers ============
NUMBERS = [
    ("uno", "one", "1"),
    ("dos", "two", "2"),
    ("tres", "three", "3"),
    ("cuatro", "four", "4"),
    ("cinco", "five", "5"),
    ("seis", "six", "6"),
    ("siete", "seven", "7"),
    ("ocho", "eight", "8"),
    ("nueve", "nine", "9"),
    ("diez", "ten", "10"),
    ("veinte", "twenty", "20"),
    ("treinta", "thirty", "30"),
    ("cien", "one hundred", "100"),
    ("mil", "one thousand", "1000"),
]

# ============ Days & Time ============
DAYS_TIME = [
    ("lunes", "Monday", "First day of work week"),
    ("martes", "Tuesday", ""),
    ("miércoles", "Wednesday", ""),
    ("jueves", "Thursday", ""),
    ("viernes", "Friday", "End of work week"),
    ("sábado", "Saturday", "Weekend"),
    ("domingo", "Sunday", "Weekend"),
    ("hoy", "today", "Time reference"),
    ("mañana", "tomorrow", "Also means 'morning'"),
    ("ayer", "yesterday", "Past reference"),
    ("ahora", "now", "Present"),
    ("luego", "later", "Future"),
    ("la semana que viene", "next week", "Planning"),
]

# ============ Madrid Slang & Expressions ============
MADRID_SLANG = [
    ("¡Mola!", "Cool! / Awesome!", "Very common in Spain"),
    ("¡Qué guay!", "How cool!", "Informal expression"),
    ("Tío/Tía", "Dude / Mate", "Informal address for friends"),
    ("¿Quedamos?", "Shall we meet up?", "Making plans"),
    ("Ir de cañas", "Go for beers", "Social activity"),
    ("Currar", "To work", "Slang for trabajar"),
    ("Flipar", "To be amazed/shocked", "¡Estoy flipando!"),
    ("Molar", "To be cool", "Eso mola mucho"),
    ("Pasta", "Money", "Slang for dinero"),
    ("Mogollón", "A lot", "Hay mogollón de gente"),
]

# ============ Essential Vocabulary ============
VOCABULARY = [
    # Basic
    ("sí", "yes", "basic"),
    ("no", "no", "basic"),
    ("por favor", "please", "basic"),
    ("gracias", "thank you", "basic"),
    ("de nada", "you're welcome", "basic"),
    ("perdón", "sorry/excuse me", "basic"),
    ("lo siento", "I'm sorry", "basic"),

    # Questions
    ("qué", "what", "questions"),
    ("quién", "who", "questions"),
    ("cuándo", "when", "questions"),
    ("dónde", "where", "questions"),
    ("por qué", "why", "questions"),
    ("cómo", "how", "questions"),
    ("cuánto", "how much", "questions"),

    # Work
    ("el trabajo", "work/job", "work"),
    ("la oficina", "office", "work"),
    ("el ordenador", "computer", "work - Spain uses 'ordenador'"),
    ("el correo", "email", "work"),
    ("la reunión", "meeting", "work"),
    ("el proyecto", "project", "work"),
    ("el jefe", "boss", "work"),
    ("el compañero", "colleague", "work"),

    # Food & Drink
    ("el agua", "water", "food"),
    ("el café", "coffee", "food"),
    ("la cerveza", "beer", "food"),
    ("el vino", "wine", "food"),
    ("el pan", "bread", "food"),
    ("la comida", "food/lunch", "food"),
    ("el desayuno", "breakfast", "food"),
    ("la cena", "dinner", "food"),

    # Places
    ("la calle", "street", "places"),
    ("el metro", "metro/subway", "places"),
    ("el restaurante", "restaurant", "places"),
    ("el supermercado", "supermarket", "places"),
    ("el banco", "bank", "places"),
]


def populate_database():
    """Populate the database with initial content"""
    init_database()

    # Check if already populated
    if len(get_phrases()) > 0:
        print("Database already has content. Skipping population.")
        return

    print("Populating database with initial content...")

    # Add greetings
    for spanish, english, notes in GREETINGS:
        add_phrase(spanish, english, "greetings", 1, notes)

    # Add workplace phrases
    for spanish, english, notes in WORKPLACE:
        add_phrase(spanish, english, "workplace", 1, notes)

    # Add smalltalk
    for spanish, english, notes in SMALLTALK:
        add_phrase(spanish, english, "smalltalk", 1, notes)

    # Add numbers
    for spanish, english, notes in NUMBERS:
        add_phrase(spanish, english, "numbers", 1, notes)

    # Add days/time
    for spanish, english, notes in DAYS_TIME:
        add_phrase(spanish, english, "time", 1, notes)

    # Add Madrid slang
    for spanish, english, notes in MADRID_SLANG:
        add_phrase(spanish, english, "slang", 2, notes)

    # Add vocabulary
    for spanish, english, category in VOCABULARY:
        add_vocabulary(spanish, english, category)

    print("Database populated successfully!")
    print(f"  - {len(GREETINGS)} greetings")
    print(f"  - {len(WORKPLACE)} workplace phrases")
    print(f"  - {len(SMALLTALK)} smalltalk phrases")
    print(f"  - {len(NUMBERS)} numbers")
    print(f"  - {len(DAYS_TIME)} days/time phrases")
    print(f"  - {len(MADRID_SLANG)} Madrid slang phrases")
    print(f"  - {len(VOCABULARY)} vocabulary words")


if __name__ == "__main__":
    populate_database()
