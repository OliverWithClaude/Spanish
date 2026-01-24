"""
Initial content for Spanish Learning App
CEFR-aligned Spanish vocabulary and phrases organized by learning units
Target: 500+ words for A1 level
"""

from src.database import (
    init_database, add_phrase, add_vocabulary, add_section, add_unit,
    get_all_vocabulary, get_phrases, get_sections, get_units
)

# ============================================================================
# SECTION 1: A1.1 - Survival Basics (Target: 250 words)
# ============================================================================

# Unit 1: Greetings & Introductions
UNIT_1_GREETINGS = {
    "vocabulary": [
        ("hola", "hello", "Basic greeting"),
        ("adiós", "goodbye", "Farewell"),
        ("buenos días", "good morning", "Until ~2 PM"),
        ("buenas tardes", "good afternoon", "2 PM to 8 PM"),
        ("buenas noches", "good evening/night", "After 8 PM"),
        ("bienvenido", "welcome", "Welcoming someone (m)"),
        ("bienvenida", "welcome", "Welcoming someone (f)"),
        ("encantado", "nice to meet you", "Male speaker"),
        ("encantada", "nice to meet you", "Female speaker"),
        ("mucho gusto", "pleased to meet you", "Formal/neutral"),
        ("hasta luego", "see you later", "Common goodbye"),
        ("hasta pronto", "see you soon", "Expecting to meet soon"),
        ("hasta mañana", "see you tomorrow", "Work goodbye"),
        ("chao", "bye", "Informal"),
        ("saludos", "greetings", "Also used in emails"),
        ("señor", "Mr./sir", "Formal address (m)"),
        ("señora", "Mrs./ma'am", "Formal address (f)"),
        ("señorita", "Miss", "Formal address (young f)"),
        ("amigo", "friend", "Male friend"),
        ("amiga", "friend", "Female friend"),
    ],
    "phrases": [
        ("¡Hola!", "Hello!", "Start any conversation"),
        ("Buenos días", "Good morning", "Formal morning greeting"),
        ("Buenas tardes", "Good afternoon", "Afternoon greeting"),
        ("Buenas noches", "Good evening/night", "Evening greeting"),
        ("¿Qué tal?", "How's it going?", "Casual greeting"),
        ("¿Cómo estás?", "How are you?", "Informal"),
        ("¿Cómo está usted?", "How are you?", "Formal"),
        ("Muy bien, gracias", "Very well, thanks", "Common response"),
        ("¿Y tú?", "And you?", "Informal follow-up"),
        ("¿Y usted?", "And you?", "Formal follow-up"),
        ("Hasta luego", "See you later", "Common goodbye"),
        ("¡Que tengas un buen día!", "Have a nice day!", "Friendly farewell"),
        ("Me llamo...", "My name is...", "Introducing yourself"),
        ("¿Cómo te llamas?", "What's your name?", "Informal"),
        ("Encantado de conocerte", "Nice to meet you", "Male speaker"),
        ("Soy de...", "I'm from...", "Saying where you're from"),
        ("¿De dónde eres?", "Where are you from?", "Asking origin"),
        ("Vivo en Madrid", "I live in Madrid", "Where you live"),
    ],
}

# Unit 2: Numbers 1-100
UNIT_2_NUMBERS = {
    "vocabulary": [
        ("cero", "zero", "0"),
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
        ("once", "eleven", "11"),
        ("doce", "twelve", "12"),
        ("trece", "thirteen", "13"),
        ("catorce", "fourteen", "14"),
        ("quince", "fifteen", "15"),
        ("dieciséis", "sixteen", "16"),
        ("diecisiete", "seventeen", "17"),
        ("dieciocho", "eighteen", "18"),
        ("diecinueve", "nineteen", "19"),
        ("veinte", "twenty", "20"),
        ("veintiuno", "twenty-one", "21"),
        ("veintidós", "twenty-two", "22"),
        ("treinta", "thirty", "30"),
        ("cuarenta", "forty", "40"),
        ("cincuenta", "fifty", "50"),
        ("sesenta", "sixty", "60"),
        ("setenta", "seventy", "70"),
        ("ochenta", "eighty", "80"),
        ("noventa", "ninety", "90"),
        ("cien", "one hundred", "100"),
        ("el número", "number", "The number"),
        ("primero", "first", "1st"),
        ("segundo", "second", "2nd"),
        ("tercero", "third", "3rd"),
    ],
    "phrases": [
        ("¿Cuántos?", "How many?", "Asking quantity"),
        ("¿Cuánto cuesta?", "How much does it cost?", "Asking price"),
        ("Son cinco euros", "It's five euros", "Stating price"),
        ("Tengo veinte años", "I'm twenty years old", "Age"),
        ("¿Cuántos años tienes?", "How old are you?", "Asking age"),
        ("Mi número de teléfono es...", "My phone number is...", "Giving number"),
        ("El primero", "The first one", "Ordinal"),
        ("El segundo piso", "The second floor", "Floor number"),
    ],
}

# Unit 3: Basic Questions
UNIT_3_QUESTIONS = {
    "vocabulary": [
        ("qué", "what", "Question word"),
        ("quién", "who", "Question word"),
        ("cuándo", "when", "Question word"),
        ("dónde", "where", "Question word"),
        ("por qué", "why", "Question word"),
        ("porque", "because", "Answer to why"),
        ("cómo", "how", "Question word"),
        ("cuánto", "how much", "Question word - singular"),
        ("cuántos", "how many", "Question word - plural (m)"),
        ("cuántas", "how many", "Question word - plural (f)"),
        ("cuál", "which", "Question word"),
        ("la pregunta", "question", "Noun"),
        ("la respuesta", "answer", "Noun"),
        ("sí", "yes", "Affirmative"),
        ("no", "no", "Negative"),
        ("quizás", "maybe/perhaps", "Uncertainty"),
        ("tal vez", "perhaps", "Uncertainty"),
        ("claro", "of course/clear", "Agreement"),
        ("cierto", "true/certain", "Confirming"),
        ("falso", "false", "Denying"),
    ],
    "phrases": [
        ("¿Qué es esto?", "What is this?", "Asking about objects"),
        ("¿Quién es?", "Who is it?", "Asking about person"),
        ("¿Cuándo es?", "When is it?", "Asking about time"),
        ("¿Dónde está?", "Where is it?", "Asking location"),
        ("¿Por qué?", "Why?", "Asking reason"),
        ("¿Cómo estás?", "How are you?", "Asking about state"),
        ("¿Cuánto cuesta esto?", "How much does this cost?", "Price question"),
        ("¿Cuál es tu nombre?", "What is your name?", "Name question"),
        ("No lo sé", "I don't know", "Not knowing"),
        ("No entiendo", "I don't understand", "Confusion"),
        ("¿Puedes repetir?", "Can you repeat?", "Asking for repetition"),
        ("¿Qué significa?", "What does it mean?", "Asking meaning"),
        ("Creo que sí", "I think so", "Uncertain yes"),
        ("Creo que no", "I don't think so", "Uncertain no"),
    ],
}

# Unit 4: Family & People
UNIT_4_FAMILY = {
    "vocabulary": [
        ("la familia", "family", "Family unit"),
        ("el padre", "father", "Dad"),
        ("la madre", "mother", "Mom"),
        ("los padres", "parents", "Both parents"),
        ("el hijo", "son", "Male child"),
        ("la hija", "daughter", "Female child"),
        ("los hijos", "children", "Sons/children"),
        ("el hermano", "brother", "Male sibling"),
        ("la hermana", "sister", "Female sibling"),
        ("el abuelo", "grandfather", "Grandpa"),
        ("la abuela", "grandmother", "Grandma"),
        ("los abuelos", "grandparents", "Both grandparents"),
        ("el tío", "uncle", "Parent's brother"),
        ("la tía", "aunt", "Parent's sister"),
        ("el primo", "cousin", "Male cousin"),
        ("la prima", "cousin", "Female cousin"),
        ("el sobrino", "nephew", "Sibling's son"),
        ("la sobrina", "niece", "Sibling's daughter"),
        ("el esposo", "husband", "Spouse (m)"),
        ("la esposa", "wife", "Spouse (f)"),
        ("el marido", "husband", "Informal"),
        ("la mujer", "wife/woman", "Also means woman"),
        ("el novio", "boyfriend", "Partner (m)"),
        ("la novia", "girlfriend", "Partner (f)"),
        ("el bebé", "baby", "Infant"),
        ("el niño", "boy/child", "Male child"),
        ("la niña", "girl", "Female child"),
        ("el hombre", "man", "Adult male"),
        ("la mujer", "woman", "Adult female"),
        ("el joven", "young person", "Youth (m)"),
        ("la persona", "person", "Individual"),
        ("la gente", "people", "People in general"),
    ],
    "phrases": [
        ("Tengo dos hermanos", "I have two brothers", "Describing family"),
        ("¿Tienes hermanos?", "Do you have siblings?", "Asking about family"),
        ("Soy hijo único", "I'm an only child", "Male speaker"),
        ("Soy hija única", "I'm an only child", "Female speaker"),
        ("Mi padre se llama...", "My father's name is...", "Introducing family"),
        ("¿Estás casado?", "Are you married?", "Relationship status (m)"),
        ("¿Estás casada?", "Are you married?", "Relationship status (f)"),
        ("Estoy soltero", "I'm single", "Male speaker"),
        ("Estoy soltera", "I'm single", "Female speaker"),
        ("Tengo una hija", "I have a daughter", "Having children"),
        ("¿Cuántos hijos tienes?", "How many children do you have?", "Asking about kids"),
        ("Esta es mi familia", "This is my family", "Introducing family"),
    ],
}

# Unit 5: Time & Days
UNIT_5_TIME = {
    "vocabulary": [
        ("la hora", "hour/time", "Time"),
        ("el minuto", "minute", "Time unit"),
        ("el segundo", "second", "Time unit"),
        ("el día", "day", "Day"),
        ("la semana", "week", "Week"),
        ("el mes", "month", "Month"),
        ("el año", "year", "Year"),
        ("lunes", "Monday", "Day of week"),
        ("martes", "Tuesday", "Day of week"),
        ("miércoles", "Wednesday", "Day of week"),
        ("jueves", "Thursday", "Day of week"),
        ("viernes", "Friday", "Day of week"),
        ("sábado", "Saturday", "Weekend"),
        ("domingo", "Sunday", "Weekend"),
        ("hoy", "today", "Current day"),
        ("mañana", "tomorrow", "Next day"),
        ("ayer", "yesterday", "Previous day"),
        ("ahora", "now", "Present moment"),
        ("luego", "later", "Future"),
        ("pronto", "soon", "Near future"),
        ("tarde", "late/afternoon", "Time of day"),
        ("temprano", "early", "Before expected"),
        ("siempre", "always", "Frequency"),
        ("nunca", "never", "Frequency"),
        ("a veces", "sometimes", "Frequency"),
        ("la mañana", "morning", "Time of day"),
        ("la tarde", "afternoon/evening", "Time of day"),
        ("la noche", "night", "Time of day"),
        ("el fin de semana", "weekend", "Saturday and Sunday"),
        ("el mediodía", "noon", "12:00 PM"),
        ("la medianoche", "midnight", "12:00 AM"),
    ],
    "phrases": [
        ("¿Qué hora es?", "What time is it?", "Asking time"),
        ("Son las tres", "It's three o'clock", "Telling time"),
        ("Es la una", "It's one o'clock", "Telling time"),
        ("Son las diez y media", "It's half past ten", "Telling time"),
        ("Son las cuatro y cuarto", "It's quarter past four", "Telling time"),
        ("¿Qué día es hoy?", "What day is today?", "Asking day"),
        ("Hoy es lunes", "Today is Monday", "Stating day"),
        ("Nos vemos mañana", "See you tomorrow", "Future meeting"),
        ("La reunión es el viernes", "The meeting is on Friday", "Scheduling"),
        ("¿A qué hora?", "At what time?", "Asking specific time"),
        ("A las nueve de la mañana", "At nine in the morning", "Morning time"),
        ("Por la tarde", "In the afternoon", "Afternoon reference"),
        ("La semana que viene", "Next week", "Future week"),
        ("El mes pasado", "Last month", "Past month"),
    ],
}

# ============================================================================
# SECTION 2: A1.2 - Daily Life (Target: 500 words total)
# ============================================================================

# Unit 6: Food & Drinks
UNIT_6_FOOD = {
    "vocabulary": [
        ("el agua", "water", "Drink - feminine!"),
        ("el café", "coffee", "Drink"),
        ("el té", "tea", "Drink"),
        ("la leche", "milk", "Drink"),
        ("el zumo", "juice", "Spain: zumo"),
        ("la cerveza", "beer", "Alcoholic drink"),
        ("el vino", "wine", "Alcoholic drink"),
        ("el pan", "bread", "Food staple"),
        ("el arroz", "rice", "Food staple"),
        ("la pasta", "pasta", "Food"),
        ("la carne", "meat", "Protein"),
        ("el pollo", "chicken", "Protein"),
        ("el pescado", "fish", "Protein"),
        ("el huevo", "egg", "Protein"),
        ("la verdura", "vegetable", "Produce"),
        ("la fruta", "fruit", "Produce"),
        ("la manzana", "apple", "Fruit"),
        ("la naranja", "orange", "Fruit"),
        ("el plátano", "banana", "Fruit"),
        ("el tomate", "tomato", "Vegetable"),
        ("la lechuga", "lettuce", "Vegetable"),
        ("la patata", "potato", "Spain: patata"),
        ("la ensalada", "salad", "Dish"),
        ("la sopa", "soup", "Dish"),
        ("el bocadillo", "sandwich", "Spain style"),
        ("el queso", "cheese", "Dairy"),
        ("el jamón", "ham", "Spanish specialty"),
        ("la tortilla", "omelette", "Spanish tortilla"),
        ("las tapas", "tapas", "Spanish appetizers"),
        ("el postre", "dessert", "Sweet course"),
        ("el helado", "ice cream", "Dessert"),
        ("el azúcar", "sugar", "Sweetener"),
        ("la sal", "salt", "Seasoning"),
        ("el aceite", "oil", "Cooking"),
    ],
    "phrases": [
        ("Tengo hambre", "I'm hungry", "Physical need"),
        ("Tengo sed", "I'm thirsty", "Physical need"),
        ("¿Qué quieres comer?", "What do you want to eat?", "Offering food"),
        ("¿Qué quieres beber?", "What do you want to drink?", "Offering drink"),
        ("Un café, por favor", "A coffee, please", "Ordering"),
        ("Un café con leche", "A latte", "Coffee with milk"),
        ("Un vaso de agua", "A glass of water", "Ordering water"),
        ("Una cerveza, por favor", "A beer, please", "Ordering"),
        ("¿Tiene leche de avena?", "Do you have oat milk?", "Dietary preference"),
        ("Soy vegetariano", "I'm vegetarian", "Male speaker"),
        ("Soy vegetariana", "I'm vegetarian", "Female speaker"),
        ("¿Qué recomiendas?", "What do you recommend?", "Asking for suggestion"),
        ("Está delicioso", "It's delicious", "Compliment"),
        ("Está muy rico", "It's very tasty", "Compliment"),
    ],
}

# Unit 7: At the Restaurant
UNIT_7_RESTAURANT = {
    "vocabulary": [
        ("el restaurante", "restaurant", "Dining place"),
        ("el bar", "bar", "Also serves food in Spain"),
        ("la cafetería", "cafeteria/café", "Coffee shop"),
        ("la mesa", "table", "Furniture"),
        ("la silla", "chair", "Furniture"),
        ("el menú", "menu", "Also 'la carta'"),
        ("la carta", "menu", "Spanish term"),
        ("el camarero", "waiter", "Server (m)"),
        ("la camarera", "waitress", "Server (f)"),
        ("el plato", "plate/dish", "Dishware/course"),
        ("el vaso", "glass", "For water"),
        ("la copa", "wine glass", "For wine"),
        ("la taza", "cup", "For coffee/tea"),
        ("el cuchillo", "knife", "Utensil"),
        ("el tenedor", "fork", "Utensil"),
        ("la cuchara", "spoon", "Utensil"),
        ("la servilleta", "napkin", "Table item"),
        ("la cuenta", "bill/check", "Payment"),
        ("la propina", "tip", "Gratuity"),
        ("el precio", "price", "Cost"),
        ("el primer plato", "first course", "Appetizer"),
        ("el segundo plato", "main course", "Entree"),
        ("la bebida", "drink", "Beverage"),
        ("el entrante", "starter/appetizer", "First course"),
        ("la especialidad", "specialty", "House special"),
    ],
    "phrases": [
        ("Una mesa para dos, por favor", "A table for two, please", "Requesting seating"),
        ("¿Tienen mesa libre?", "Do you have a free table?", "Checking availability"),
        ("La carta, por favor", "The menu, please", "Requesting menu"),
        ("¿Qué tiene el menú del día?", "What's on the daily menu?", "Special menu"),
        ("Quiero...", "I want...", "Ordering"),
        ("Para mí...", "For me...", "Ordering"),
        ("De primero...", "For the first course...", "Ordering appetizer"),
        ("De segundo...", "For the main course...", "Ordering entree"),
        ("¿Algo más?", "Anything else?", "Waiter asking"),
        ("Nada más, gracias", "Nothing else, thanks", "Finishing order"),
        ("La cuenta, por favor", "The bill, please", "Requesting check"),
        ("¿Puedo pagar con tarjeta?", "Can I pay by card?", "Payment method"),
        ("¿Está incluido el IVA?", "Is tax included?", "About price"),
        ("Quédese con el cambio", "Keep the change", "Tipping"),
    ],
}

# Unit 8: Shopping Basics
UNIT_8_SHOPPING = {
    "vocabulary": [
        ("la tienda", "store/shop", "Retail"),
        ("el supermercado", "supermarket", "Grocery"),
        ("el mercado", "market", "Outdoor market"),
        ("el centro comercial", "shopping center", "Mall"),
        ("la farmacia", "pharmacy", "Drug store"),
        ("la panadería", "bakery", "Bread shop"),
        ("la carnicería", "butcher shop", "Meat shop"),
        ("la pescadería", "fish shop", "Seafood"),
        ("la frutería", "fruit shop", "Produce"),
        ("el dependiente", "shop assistant", "Employee (m)"),
        ("la dependienta", "shop assistant", "Employee (f)"),
        ("el cliente", "customer", "Buyer (m)"),
        ("la clienta", "customer", "Buyer (f)"),
        ("el euro", "euro", "Currency"),
        ("el céntimo", "cent", "Currency"),
        ("el dinero", "money", "Cash"),
        ("la tarjeta", "card", "Credit/debit"),
        ("el efectivo", "cash", "Physical money"),
        ("el recibo", "receipt", "Proof of purchase"),
        ("la bolsa", "bag", "Shopping bag"),
        ("barato", "cheap", "Price adjective"),
        ("caro", "expensive", "Price adjective"),
        ("gratis", "free", "No cost"),
        ("la oferta", "offer/sale", "Discount"),
        ("el descuento", "discount", "Price reduction"),
    ],
    "phrases": [
        ("¿Cuánto cuesta?", "How much does it cost?", "Asking price"),
        ("¿Cuánto es?", "How much is it?", "Asking total"),
        ("Son diez euros", "It's ten euros", "Stating price"),
        ("Es muy caro", "It's very expensive", "Price complaint"),
        ("¿Tiene algo más barato?", "Do you have something cheaper?", "Negotiating"),
        ("¿Puedo ver esto?", "Can I see this?", "Examining item"),
        ("¿Dónde está...?", "Where is...?", "Finding products"),
        ("¿Tienen...?", "Do you have...?", "Asking for item"),
        ("Busco...", "I'm looking for...", "Shopping"),
        ("Me lo llevo", "I'll take it", "Buying decision"),
        ("¿Aceptan tarjeta?", "Do you accept card?", "Payment"),
        ("En efectivo", "In cash", "Payment method"),
        ("¿Puedo devolver esto?", "Can I return this?", "Return policy"),
        ("Necesito una bolsa", "I need a bag", "Requesting bag"),
    ],
}

# Unit 9: Colors & Adjectives
UNIT_9_COLORS = {
    "vocabulary": [
        ("rojo", "red", "Color"),
        ("azul", "blue", "Color"),
        ("verde", "green", "Color"),
        ("amarillo", "yellow", "Color"),
        ("naranja", "orange", "Color"),
        ("morado", "purple", "Color"),
        ("rosa", "pink", "Color"),
        ("negro", "black", "Color"),
        ("blanco", "white", "Color"),
        ("gris", "gray", "Color"),
        ("marrón", "brown", "Color"),
        ("grande", "big/large", "Size"),
        ("pequeño", "small", "Size"),
        ("mediano", "medium", "Size"),
        ("largo", "long", "Dimension"),
        ("corto", "short", "Dimension"),
        ("alto", "tall/high", "Height"),
        ("bajo", "short/low", "Height"),
        ("nuevo", "new", "Condition"),
        ("viejo", "old", "Condition"),
        ("bueno", "good", "Quality"),
        ("malo", "bad", "Quality"),
        ("bonito", "pretty", "Appearance"),
        ("feo", "ugly", "Appearance"),
        ("limpio", "clean", "Condition"),
        ("sucio", "dirty", "Condition"),
        ("caliente", "hot", "Temperature"),
        ("frío", "cold", "Temperature"),
        ("rápido", "fast", "Speed"),
        ("lento", "slow", "Speed"),
        ("fácil", "easy", "Difficulty"),
        ("difícil", "difficult", "Difficulty"),
    ],
    "phrases": [
        ("¿De qué color es?", "What color is it?", "Asking color"),
        ("Es rojo", "It's red", "Describing color"),
        ("¿Tiene en azul?", "Do you have it in blue?", "Shopping for color"),
        ("Me gusta el color verde", "I like the color green", "Preference"),
        ("Es muy grande", "It's very big", "Describing size"),
        ("Es demasiado pequeño", "It's too small", "Size complaint"),
        ("¿Tiene una talla más grande?", "Do you have a larger size?", "Shopping"),
        ("El coche nuevo", "The new car", "Describing objects"),
        ("La casa vieja", "The old house", "Describing objects"),
        ("Hace frío", "It's cold", "Weather/temperature"),
        ("Está caliente", "It's hot", "Temperature of object"),
    ],
}

# Unit 10: Weather & Seasons
UNIT_10_WEATHER = {
    "vocabulary": [
        ("el tiempo", "weather/time", "Context dependent"),
        ("el sol", "sun", "Weather"),
        ("la lluvia", "rain", "Weather"),
        ("la nieve", "snow", "Weather"),
        ("el viento", "wind", "Weather"),
        ("la nube", "cloud", "Weather"),
        ("la tormenta", "storm", "Weather"),
        ("el cielo", "sky", "Nature"),
        ("la temperatura", "temperature", "Measurement"),
        ("el grado", "degree", "Measurement"),
        ("la primavera", "spring", "Season"),
        ("el verano", "summer", "Season"),
        ("el otoño", "autumn/fall", "Season"),
        ("el invierno", "winter", "Season"),
        ("soleado", "sunny", "Weather condition"),
        ("nublado", "cloudy", "Weather condition"),
        ("lluvioso", "rainy", "Weather condition"),
        ("ventoso", "windy", "Weather condition"),
        ("húmedo", "humid", "Weather condition"),
        ("seco", "dry", "Weather condition"),
        ("el paraguas", "umbrella", "Item"),
        ("el abrigo", "coat", "Clothing"),
        ("las gafas de sol", "sunglasses", "Item"),
        ("el clima", "climate", "Long-term weather"),
    ],
    "phrases": [
        ("¿Qué tiempo hace?", "What's the weather like?", "Asking about weather"),
        ("Hace sol", "It's sunny", "Weather description"),
        ("Hace calor", "It's hot", "Weather description"),
        ("Hace frío", "It's cold", "Weather description"),
        ("Hace viento", "It's windy", "Weather description"),
        ("Está lloviendo", "It's raining", "Current weather"),
        ("Está nevando", "It's snowing", "Current weather"),
        ("Hay nubes", "There are clouds", "Weather description"),
        ("El cielo está despejado", "The sky is clear", "Weather"),
        ("Va a llover", "It's going to rain", "Weather forecast"),
        ("Hace buen tiempo", "The weather is good", "General comment"),
        ("Hace mal tiempo", "The weather is bad", "General comment"),
        ("¿Necesito un paraguas?", "Do I need an umbrella?", "Practical"),
        ("En verano hace mucho calor en Madrid", "In summer it's very hot in Madrid", "Seasonal"),
    ],
}

# ============================================================================
# SECTION 3: A2.1 - Workplace Basics (Target: 750 words total)
# ============================================================================

# Unit 11: Office Vocabulary
UNIT_11_OFFICE = {
    "vocabulary": [
        ("la oficina", "office", "Workplace"),
        ("el trabajo", "work/job", "Employment"),
        ("el escritorio", "desk", "Furniture"),
        ("la silla", "chair", "Furniture"),
        ("el ordenador", "computer", "Spain term"),
        ("el portátil", "laptop", "Portable computer"),
        ("la pantalla", "screen", "Display"),
        ("el teclado", "keyboard", "Input device"),
        ("el ratón", "mouse", "Input device"),
        ("la impresora", "printer", "Office equipment"),
        ("el teléfono", "telephone", "Communication"),
        ("el móvil", "cell phone", "Mobile"),
        ("el correo", "email/mail", "Communication"),
        ("el documento", "document", "File"),
        ("el archivo", "file", "Digital or physical"),
        ("la carpeta", "folder", "Organization"),
        ("el papel", "paper", "Material"),
        ("el bolígrafo", "pen", "Writing tool"),
        ("el lápiz", "pencil", "Writing tool"),
        ("la grapadora", "stapler", "Office supply"),
        ("las tijeras", "scissors", "Tool"),
        ("el calendario", "calendar", "Scheduling"),
        ("la agenda", "planner/diary", "Scheduling"),
        ("la empresa", "company", "Business"),
        ("el departamento", "department", "Division"),
        ("el despacho", "office (private)", "Private office"),
        ("la sala de reuniones", "meeting room", "Space"),
        ("el ascensor", "elevator", "Building"),
        ("las escaleras", "stairs", "Building"),
        ("la recepción", "reception", "Building area"),
    ],
    "phrases": [
        ("¿Dónde está la sala de reuniones?", "Where is the meeting room?", "Finding places"),
        ("Estoy en mi despacho", "I'm in my office", "Location"),
        ("¿Puedo usar tu ordenador?", "Can I use your computer?", "Permission"),
        ("No funciona la impresora", "The printer doesn't work", "Problem"),
        ("¿Tienes un bolígrafo?", "Do you have a pen?", "Borrowing"),
        ("Voy a enviar un correo", "I'm going to send an email", "Action"),
        ("¿Has recibido mi mensaje?", "Did you receive my message?", "Confirming"),
        ("El documento está en la carpeta", "The document is in the folder", "Location"),
        ("Trabajo en el departamento de marketing", "I work in the marketing department", "Job"),
        ("La empresa tiene cien empleados", "The company has 100 employees", "Company info"),
    ],
}

# Unit 12: Meetings & Schedules
UNIT_12_MEETINGS = {
    "vocabulary": [
        ("la reunión", "meeting", "Event"),
        ("la cita", "appointment", "Scheduled meeting"),
        ("el horario", "schedule", "Timetable"),
        ("la fecha", "date", "Calendar"),
        ("el plazo", "deadline", "Time limit"),
        ("la hora", "time/hour", "Scheduling"),
        ("el jefe", "boss", "Manager (m)"),
        ("la jefa", "boss", "Manager (f)"),
        ("el director", "director", "Leadership (m)"),
        ("la directora", "director", "Leadership (f)"),
        ("el gerente", "manager", "Management (m)"),
        ("la gerente", "manager", "Management (f)"),
        ("el empleado", "employee", "Worker (m)"),
        ("la empleada", "employee", "Worker (f)"),
        ("el compañero", "colleague", "Coworker (m)"),
        ("la compañera", "colleague", "Coworker (f)"),
        ("el equipo", "team", "Group"),
        ("el proyecto", "project", "Work project"),
        ("la tarea", "task", "Assignment"),
        ("el objetivo", "objective/goal", "Target"),
        ("el progreso", "progress", "Advancement"),
        ("el resultado", "result", "Outcome"),
        ("el informe", "report", "Document"),
        ("la presentación", "presentation", "Slides/talk"),
        ("la agenda", "agenda", "Meeting topics"),
        ("el punto", "point/item", "Agenda item"),
        ("libre", "free/available", "Schedule"),
        ("ocupado", "busy", "Schedule"),
    ],
    "phrases": [
        ("¿Tienes un momento?", "Do you have a moment?", "Getting attention"),
        ("Tenemos una reunión a las tres", "We have a meeting at three", "Scheduling"),
        ("¿A qué hora es la reunión?", "What time is the meeting?", "Asking"),
        ("La reunión se cancela", "The meeting is cancelled", "Changes"),
        ("¿Quedamos mañana?", "Shall we meet tomorrow?", "Scheduling"),
        ("Estoy ocupado ahora", "I'm busy now", "Declining"),
        ("¿Cuándo estás libre?", "When are you free?", "Scheduling"),
        ("El plazo es el viernes", "The deadline is Friday", "Deadline"),
        ("Vamos a discutir el proyecto", "We're going to discuss the project", "Agenda"),
        ("¿Cuál es el orden del día?", "What's on the agenda?", "Meeting"),
        ("Tengo una cita con el cliente", "I have an appointment with the client", "Business"),
        ("Necesito terminar este informe", "I need to finish this report", "Task"),
        ("¿Has terminado la tarea?", "Have you finished the task?", "Checking"),
        ("Buen trabajo", "Good job", "Praise"),
    ],
}

# Unit 13: Communication & Email
UNIT_13_COMMUNICATION = {
    "vocabulary": [
        ("el mensaje", "message", "Communication"),
        ("el correo electrónico", "email", "Full term"),
        ("el asunto", "subject", "Email field"),
        ("el adjunto", "attachment", "Email file"),
        ("el destinatario", "recipient", "Email field"),
        ("el remitente", "sender", "Email field"),
        ("la respuesta", "reply/answer", "Communication"),
        ("la llamada", "call", "Phone"),
        ("la conversación", "conversation", "Dialogue"),
        ("la pregunta", "question", "Query"),
        ("la explicación", "explanation", "Clarification"),
        ("el problema", "problem", "Issue"),
        ("la solución", "solution", "Fix"),
        ("la ayuda", "help", "Assistance"),
        ("la información", "information", "Data"),
        ("los datos", "data", "Information"),
        ("urgente", "urgent", "Priority"),
        ("importante", "important", "Priority"),
        ("disponible", "available", "Status"),
        ("pendiente", "pending", "Status"),
        ("enviado", "sent", "Status"),
        ("recibido", "received", "Status"),
        ("confirmar", "to confirm", "Action"),
        ("responder", "to reply", "Action"),
        ("reenviar", "to forward", "Action"),
    ],
    "phrases": [
        ("Acabo de enviar un correo", "I just sent an email", "Notification"),
        ("¿Has visto mi mensaje?", "Have you seen my message?", "Checking"),
        ("Te llamo luego", "I'll call you later", "Promise"),
        ("¿Puedes enviarme el documento?", "Can you send me the document?", "Request"),
        ("Gracias por tu respuesta", "Thanks for your reply", "Appreciation"),
        ("Por favor, confirma la reunión", "Please confirm the meeting", "Request"),
        ("Adjunto el informe", "I'm attaching the report", "Email"),
        ("¿Tienes alguna pregunta?", "Do you have any questions?", "Offering help"),
        ("No he recibido el correo", "I haven't received the email", "Issue"),
        ("El asunto del mensaje", "The subject of the message", "Email reference"),
        ("Es urgente", "It's urgent", "Priority"),
        ("Necesito más información", "I need more information", "Request"),
        ("Te lo explico", "I'll explain it to you", "Offering explanation"),
        ("¿Puedes repetir eso?", "Can you repeat that?", "Clarification"),
    ],
}

# Unit 14: Asking for Help
UNIT_14_HELP = {
    "vocabulary": [
        ("ayudar", "to help", "Verb"),
        ("necesitar", "to need", "Verb"),
        ("querer", "to want", "Verb"),
        ("poder", "to be able to", "Verb"),
        ("entender", "to understand", "Verb"),
        ("explicar", "to explain", "Verb"),
        ("preguntar", "to ask", "Verb"),
        ("pedir", "to request/ask for", "Verb"),
        ("repetir", "to repeat", "Verb"),
        ("traducir", "to translate", "Verb"),
        ("aprender", "to learn", "Verb"),
        ("practicar", "to practice", "Verb"),
        ("mejorar", "to improve", "Verb"),
        ("intentar", "to try", "Verb"),
        ("el error", "error/mistake", "Noun"),
        ("el favor", "favor", "Noun"),
        ("despacio", "slowly", "Adverb"),
        ("otra vez", "again", "Adverb phrase"),
        ("por favor", "please", "Courtesy"),
        ("lo siento", "I'm sorry", "Apology"),
        ("perdón", "excuse me/sorry", "Apology"),
        ("disculpa", "excuse me", "Getting attention"),
        ("gracias", "thank you", "Courtesy"),
        ("de nada", "you're welcome", "Courtesy"),
    ],
    "phrases": [
        ("¿Me puedes ayudar?", "Can you help me?", "Asking for help"),
        ("Necesito ayuda", "I need help", "Requesting assistance"),
        ("No entiendo", "I don't understand", "Confusion"),
        ("¿Puedes repetir, por favor?", "Can you repeat, please?", "Clarification"),
        ("Más despacio, por favor", "More slowly, please", "Slowing down"),
        ("¿Cómo se dice...?", "How do you say...?", "Learning words"),
        ("¿Qué significa eso?", "What does that mean?", "Understanding"),
        ("¿Puedes explicarlo otra vez?", "Can you explain it again?", "Clarification"),
        ("Estoy aprendiendo español", "I'm learning Spanish", "Context"),
        ("¿Está bien así?", "Is it OK like this?", "Checking"),
        ("Lo siento, no sé", "Sorry, I don't know", "Admitting"),
        ("¿Hay alguien que hable inglés?", "Is there someone who speaks English?", "Emergency"),
        ("Perdona, ¿puedes ayudarme?", "Excuse me, can you help me?", "Polite request"),
        ("Gracias por tu paciencia", "Thank you for your patience", "Appreciation"),
    ],
}

# Unit 15: Common Verbs (Present Tense)
UNIT_15_VERBS = {
    "vocabulary": [
        ("ser", "to be (permanent)", "Essential verb"),
        ("estar", "to be (temporary)", "Essential verb"),
        ("tener", "to have", "Essential verb"),
        ("hacer", "to do/make", "Essential verb"),
        ("ir", "to go", "Essential verb"),
        ("venir", "to come", "Essential verb"),
        ("ver", "to see", "Essential verb"),
        ("dar", "to give", "Essential verb"),
        ("saber", "to know (facts)", "Essential verb"),
        ("conocer", "to know (people/places)", "Essential verb"),
        ("hablar", "to speak", "Regular -ar"),
        ("trabajar", "to work", "Regular -ar"),
        ("estudiar", "to study", "Regular -ar"),
        ("llamar", "to call", "Regular -ar"),
        ("comer", "to eat", "Regular -er"),
        ("beber", "to drink", "Regular -er"),
        ("leer", "to read", "Regular -er"),
        ("vivir", "to live", "Regular -ir"),
        ("escribir", "to write", "Regular -ir"),
        ("abrir", "to open", "Regular -ir"),
        ("cerrar", "to close", "Stem-changing"),
        ("empezar", "to start", "Stem-changing"),
        ("terminar", "to finish", "Regular -ar"),
        ("llegar", "to arrive", "Regular -ar"),
        ("salir", "to leave/go out", "Irregular"),
        ("volver", "to return", "Stem-changing"),
        ("dormir", "to sleep", "Stem-changing"),
        ("pensar", "to think", "Stem-changing"),
        ("creer", "to believe", "Regular -er"),
        ("esperar", "to wait/hope", "Regular -ar"),
    ],
    "phrases": [
        ("Soy español", "I am Spanish", "ser - nationality"),
        ("Estoy cansado", "I am tired", "estar - condition"),
        ("Tengo una pregunta", "I have a question", "tener"),
        ("Voy a la oficina", "I'm going to the office", "ir"),
        ("¿Qué haces?", "What are you doing?", "hacer"),
        ("Hablo español un poco", "I speak Spanish a little", "hablar"),
        ("Trabajo aquí", "I work here", "trabajar"),
        ("Como a las dos", "I eat at two", "comer"),
        ("Vivo en Madrid", "I live in Madrid", "vivir"),
        ("¿Sabes dónde está?", "Do you know where it is?", "saber"),
        ("Conozco a María", "I know María", "conocer"),
        ("La reunión empieza a las diez", "The meeting starts at ten", "empezar"),
        ("Termino a las seis", "I finish at six", "terminar"),
        ("Salgo del trabajo a las siete", "I leave work at seven", "salir"),
    ],
}

# ============================================================================
# MADRID SLANG & EXPRESSIONS (Bonus content)
# ============================================================================

MADRID_SLANG = {
    "vocabulary": [
        ("mola", "it's cool", "From molar"),
        ("guay", "cool", "Very common"),
        ("tío", "dude/guy", "Informal address (m)"),
        ("tía", "chick/girl", "Informal address (f)"),
        ("curro", "job/work", "Slang"),
        ("pasta", "money", "Slang for dinero"),
        ("mogollón", "a lot", "Informal quantity"),
        ("quedada", "meetup", "Getting together"),
        ("caña", "small beer", "Spanish beer serving"),
        ("tapear", "to eat tapas", "Spanish activity"),
        ("trasnochar", "to stay up late", "Night owl behavior"),
        ("resaca", "hangover", "After drinking"),
        ("majo", "nice/cute", "Friendly person"),
        ("maja", "nice/cute", "Friendly person (f)"),
        ("flipar", "to be amazed", "Informal"),
        ("molar", "to be cool", "Verb form"),
        ("enrollarse", "to make out", "Informal"),
        ("pillar", "to catch/get", "Informal for coger"),
        ("currar", "to work", "Slang for trabajar"),
        ("quedar", "to meet up", "Making plans"),
    ],
    "phrases": [
        ("¡Mola mucho!", "That's really cool!", "Enthusiasm"),
        ("¡Qué guay!", "How cool!", "Excitement"),
        ("¡Vamos de cañas!", "Let's go for beers!", "Social invitation"),
        ("¿Quedamos el sábado?", "Shall we meet on Saturday?", "Making plans"),
        ("Estoy flipando", "I'm amazed", "Surprise"),
        ("Tío, ¿qué tal?", "Dude, how's it going?", "Casual greeting"),
        ("Tengo mogollón de trabajo", "I have tons of work", "Lots of work"),
        ("Es muy majo", "He's really nice", "Compliment"),
        ("Vamos a tapear", "Let's go have tapas", "Social activity"),
        ("Tengo una resaca horrible", "I have a horrible hangover", "After partying"),
    ],
}

# ============================================================================
# DATABASE POPULATION FUNCTIONS
# ============================================================================

def create_learning_path():
    """Create sections and units for the learning path"""
    print("Creating learning path structure...")

    # Check if sections already exist
    existing = get_sections()
    if existing:
        print("Learning path already exists. Skipping creation.")
        return

    # Section 1: A1.1 - Survival Basics
    s1 = add_section(
        name="A1.1 - Survival Basics",
        cefr_level="A1",
        description="Essential words and phrases to start communicating",
        order_num=1,
        xp_required=0,
        word_target=250
    )
    add_unit(s1, "Greetings & Introductions", "Hello, goodbye, and meeting people", 1, 100)
    add_unit(s1, "Numbers 1-100", "Counting and basic math", 2, 100)
    add_unit(s1, "Basic Questions", "What, where, when, why, how", 3, 100)
    add_unit(s1, "Family & People", "Family members and relationships", 4, 100)
    add_unit(s1, "Time & Days", "Days of the week, time expressions", 5, 100)

    # Section 2: A1.2 - Daily Life
    s2 = add_section(
        name="A1.2 - Daily Life",
        cefr_level="A1",
        description="Everyday vocabulary for daily situations",
        order_num=2,
        xp_required=1000,
        word_target=250
    )
    add_unit(s2, "Food & Drinks", "Eating and drinking vocabulary", 1, 100)
    add_unit(s2, "At the Restaurant", "Ordering food and paying", 2, 100)
    add_unit(s2, "Shopping Basics", "Buying things and money", 3, 100)
    add_unit(s2, "Colors & Adjectives", "Describing things", 4, 100)
    add_unit(s2, "Weather & Seasons", "Talking about the weather", 5, 100)

    # Section 3: A2.1 - Workplace Basics
    s3 = add_section(
        name="A2.1 - Workplace Basics",
        cefr_level="A2",
        description="Vocabulary for the office environment",
        order_num=3,
        xp_required=3000,
        word_target=250
    )
    add_unit(s3, "Office Vocabulary", "Office equipment and spaces", 1, 100)
    add_unit(s3, "Meetings & Schedules", "Planning and organizing work", 2, 100)
    add_unit(s3, "Communication & Email", "Professional communication", 3, 100)
    add_unit(s3, "Asking for Help", "Getting assistance and clarification", 4, 100)
    add_unit(s3, "Common Verbs", "Essential verbs in present tense", 5, 100)

    print("Learning path created successfully!")


def populate_unit_content(unit_id: int, content: dict, unit_name: str = None, cefr_level: str = 'A1'):
    """Populate a unit with vocabulary and phrases"""
    # Add vocabulary
    for spanish, english, example in content.get("vocabulary", []):
        add_vocabulary(
            spanish=spanish,
            english=english,
            category=unit_name,  # Use unit name as category for better image matching
            example_sentence=example,
            unit_id=unit_id,
            cefr_level=cefr_level
        )

    # Add phrases
    for spanish, english, notes in content.get("phrases", []):
        add_phrase(
            spanish=spanish,
            english=english,
            category=unit_name,  # Use unit name as category
            notes=notes,
            unit_id=unit_id,
            cefr_level=cefr_level
        )


def populate_database():
    """Populate the database with initial content"""
    init_database()

    # Check if already populated
    existing_vocab = get_all_vocabulary()
    if len(existing_vocab) > 50:
        print(f"Database already has {len(existing_vocab)} vocabulary items. Skipping population.")
        return

    print("Populating database with CEFR-aligned content...")

    # Create learning path structure
    create_learning_path()

    # Get all units
    units = get_units()

    # Map content to units
    content_mapping = {
        "Greetings & Introductions": (UNIT_1_GREETINGS, 'A1'),
        "Numbers 1-100": (UNIT_2_NUMBERS, 'A1'),
        "Basic Questions": (UNIT_3_QUESTIONS, 'A1'),
        "Family & People": (UNIT_4_FAMILY, 'A1'),
        "Time & Days": (UNIT_5_TIME, 'A1'),
        "Food & Drinks": (UNIT_6_FOOD, 'A1'),
        "At the Restaurant": (UNIT_7_RESTAURANT, 'A1'),
        "Shopping Basics": (UNIT_8_SHOPPING, 'A1'),
        "Colors & Adjectives": (UNIT_9_COLORS, 'A1'),
        "Weather & Seasons": (UNIT_10_WEATHER, 'A1'),
        "Office Vocabulary": (UNIT_11_OFFICE, 'A2'),
        "Meetings & Schedules": (UNIT_12_MEETINGS, 'A2'),
        "Communication & Email": (UNIT_13_COMMUNICATION, 'A2'),
        "Asking for Help": (UNIT_14_HELP, 'A2'),
        "Common Verbs": (UNIT_15_VERBS, 'A2'),
    }

    # Populate each unit
    for unit in units:
        unit_name = unit['name']
        if unit_name in content_mapping:
            content, cefr = content_mapping[unit_name]
            populate_unit_content(unit['id'], content, unit_name, cefr)
            vocab_count = len(content.get('vocabulary', []))
            phrase_count = len(content.get('phrases', []))
            print(f"  - {unit_name}: {vocab_count} words, {phrase_count} phrases")

    # Add Madrid slang as bonus content (no specific unit)
    print("Adding Madrid slang...")
    for spanish, english, example in MADRID_SLANG.get("vocabulary", []):
        add_vocabulary(spanish, english, "slang", example, cefr_level='A2')
    for spanish, english, notes in MADRID_SLANG.get("phrases", []):
        add_phrase(spanish, english, "slang", notes=notes, cefr_level='A2')

    # Print summary
    total_vocab = len(get_all_vocabulary())
    total_phrases = len(get_phrases())
    print(f"\nDatabase populated successfully!")
    print(f"  Total vocabulary: {total_vocab} words")
    print(f"  Total phrases: {total_phrases}")


if __name__ == "__main__":
    populate_database()
