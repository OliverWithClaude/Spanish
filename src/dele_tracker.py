"""
DELE Exam Readiness Tracker for Spanish Learning App
Tracks progress toward DELE A1, A2, B1 certification requirements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from src.database import get_connection


# ============ DELE Topic Definitions ============

# DELE A1 Topics (Basic User - Breakthrough)
DELE_A1_TOPICS = {
    "greetings": {
        "name": "Greetings & Farewells",
        "name_es": "Saludos y despedidas",
        "required_words": 15,
        "keywords": ["hola", "adiós", "buenos", "buenas", "gracias", "por favor",
                    "hasta", "luego", "mañana", "bienvenido", "encantado"]
    },
    "personal_info": {
        "name": "Personal Information",
        "name_es": "Información personal",
        "required_words": 20,
        "keywords": ["nombre", "apellido", "edad", "año", "profesión", "trabajo",
                    "nacionalidad", "país", "ciudad", "dirección", "teléfono"]
    },
    "numbers": {
        "name": "Numbers & Counting",
        "name_es": "Números",
        "required_words": 25,
        "keywords": ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete",
                    "ocho", "nueve", "diez", "veinte", "cien", "número", "primero"]
    },
    "time": {
        "name": "Time & Dates",
        "name_es": "Tiempo y fechas",
        "required_words": 20,
        "keywords": ["hora", "minuto", "día", "semana", "mes", "año", "hoy",
                    "mañana", "ayer", "lunes", "enero", "fecha", "calendario"]
    },
    "family": {
        "name": "Family",
        "name_es": "Familia",
        "required_words": 15,
        "keywords": ["padre", "madre", "hermano", "hermana", "hijo", "hija",
                    "abuelo", "abuela", "familia", "padres", "tío", "primo"]
    },
    "colors": {
        "name": "Colors",
        "name_es": "Colores",
        "required_words": 10,
        "keywords": ["rojo", "azul", "verde", "amarillo", "negro", "blanco",
                    "naranja", "rosa", "color", "marrón"]
    },
    "basic_verbs": {
        "name": "Basic Verbs",
        "name_es": "Verbos básicos",
        "required_words": 20,
        "keywords": ["ser", "estar", "tener", "hacer", "ir", "venir", "poder",
                    "querer", "saber", "decir", "hablar", "comer", "beber",
                    "vivir", "trabajar", "llamar"]
    },
    "food_basic": {
        "name": "Basic Food & Drink",
        "name_es": "Comida y bebida básica",
        "required_words": 15,
        "keywords": ["agua", "café", "pan", "leche", "fruta", "carne", "pescado",
                    "comida", "bebida", "desayuno", "almuerzo", "cena"]
    },
}

# DELE A2 Topics (Basic User - Waystage)
DELE_A2_TOPICS = {
    "work": {
        "name": "Work & Profession",
        "name_es": "Trabajo y profesión",
        "required_words": 25,
        "keywords": ["trabajo", "oficina", "reunión", "jefe", "compañero",
                    "empresa", "proyecto", "cliente", "correo", "ordenador",
                    "horario", "vacaciones", "sueldo"]
    },
    "home": {
        "name": "Home & Housing",
        "name_es": "Casa y vivienda",
        "required_words": 25,
        "keywords": ["casa", "piso", "habitación", "cocina", "baño", "salón",
                    "dormitorio", "mueble", "puerta", "ventana", "escalera"]
    },
    "daily_routine": {
        "name": "Daily Routine",
        "name_es": "Rutina diaria",
        "required_words": 20,
        "keywords": ["levantarse", "acostarse", "ducharse", "vestirse",
                    "desayunar", "almorzar", "cenar", "dormir", "despertar"]
    },
    "shopping": {
        "name": "Shopping",
        "name_es": "Compras",
        "required_words": 20,
        "keywords": ["comprar", "tienda", "precio", "dinero", "euro", "barato",
                    "caro", "pagar", "tarjeta", "efectivo", "recibo"]
    },
    "health": {
        "name": "Health & Body",
        "name_es": "Salud y cuerpo",
        "required_words": 25,
        "keywords": ["médico", "hospital", "enfermo", "dolor", "cabeza",
                    "estómago", "fiebre", "medicina", "cita", "farmacia"]
    },
    "travel": {
        "name": "Travel & Transport",
        "name_es": "Viajes y transporte",
        "required_words": 25,
        "keywords": ["viajar", "viaje", "tren", "avión", "autobús", "coche",
                    "metro", "billete", "estación", "aeropuerto", "hotel"]
    },
    "weather": {
        "name": "Weather",
        "name_es": "El tiempo",
        "required_words": 15,
        "keywords": ["tiempo", "lluvia", "sol", "nube", "viento", "frío",
                    "calor", "temperatura", "llover", "nevar"]
    },
    "leisure": {
        "name": "Hobbies & Leisure",
        "name_es": "Ocio y tiempo libre",
        "required_words": 20,
        "keywords": ["película", "música", "libro", "deporte", "fútbol",
                    "restaurante", "bar", "cine", "teatro", "vacaciones"]
    },
    "describing_people": {
        "name": "Describing People",
        "name_es": "Describir personas",
        "required_words": 20,
        "keywords": ["alto", "bajo", "gordo", "delgado", "joven", "viejo",
                    "guapo", "simpático", "inteligente", "amable"]
    },
    "past_tense": {
        "name": "Past Tense Verbs",
        "name_es": "Verbos en pasado",
        "required_words": 20,
        "keywords": ["fue", "era", "tuvo", "hizo", "dijo", "pudo", "quiso",
                    "vino", "estuvo", "hubo", "fui", "estuve"]
    },
}

# ============ Complete DELE A1 Vocabulary with Translations ============

DELE_A1_VOCABULARY = {
    "greetings": [
        ("hola", "hello"),
        ("adiós", "goodbye"),
        ("buenos días", "good morning"),
        ("buenas tardes", "good afternoon"),
        ("buenas noches", "good evening/night"),
        ("gracias", "thank you"),
        ("por favor", "please"),
        ("de nada", "you're welcome"),
        ("perdón", "sorry/excuse me"),
        ("hasta luego", "see you later"),
        ("hasta mañana", "see you tomorrow"),
        ("bienvenido", "welcome (m)"),
        ("bienvenida", "welcome (f)"),
        ("encantado", "nice to meet you (m)"),
        ("encantada", "nice to meet you (f)"),
        ("mucho gusto", "pleased to meet you"),
        ("¿qué tal?", "how's it going?"),
        ("bien", "well/good"),
        ("mal", "bad"),
        ("regular", "so-so"),
    ],
    "personal_info": [
        ("nombre", "name"),
        ("apellido", "surname"),
        ("edad", "age"),
        ("año", "year"),
        ("profesión", "profession"),
        ("trabajo", "work/job"),
        ("nacionalidad", "nationality"),
        ("país", "country"),
        ("ciudad", "city"),
        ("dirección", "address"),
        ("teléfono", "telephone"),
        ("correo", "email"),
        ("casado", "married (m)"),
        ("casada", "married (f)"),
        ("soltero", "single (m)"),
        ("soltera", "single (f)"),
        ("español", "Spanish (m)"),
        ("española", "Spanish (f)"),
        ("estudiante", "student"),
        ("profesor", "teacher (m)"),
    ],
    "numbers": [
        ("uno", "one"),
        ("dos", "two"),
        ("tres", "three"),
        ("cuatro", "four"),
        ("cinco", "five"),
        ("seis", "six"),
        ("siete", "seven"),
        ("ocho", "eight"),
        ("nueve", "nine"),
        ("diez", "ten"),
        ("once", "eleven"),
        ("doce", "twelve"),
        ("veinte", "twenty"),
        ("treinta", "thirty"),
        ("cuarenta", "forty"),
        ("cincuenta", "fifty"),
        ("cien", "one hundred"),
        ("mil", "one thousand"),
        ("primero", "first"),
        ("segundo", "second"),
        ("número", "number"),
    ],
    "time": [
        ("hora", "hour/time"),
        ("minuto", "minute"),
        ("segundo", "second"),
        ("día", "day"),
        ("semana", "week"),
        ("mes", "month"),
        ("año", "year"),
        ("hoy", "today"),
        ("mañana", "tomorrow"),
        ("ayer", "yesterday"),
        ("ahora", "now"),
        ("después", "after/later"),
        ("antes", "before"),
        ("lunes", "Monday"),
        ("martes", "Tuesday"),
        ("miércoles", "Wednesday"),
        ("jueves", "Thursday"),
        ("viernes", "Friday"),
        ("sábado", "Saturday"),
        ("domingo", "Sunday"),
        ("enero", "January"),
        ("febrero", "February"),
        ("marzo", "March"),
        ("abril", "April"),
        ("mayo", "May"),
        ("junio", "June"),
        ("julio", "July"),
        ("agosto", "August"),
        ("septiembre", "September"),
        ("octubre", "October"),
        ("noviembre", "November"),
        ("diciembre", "December"),
    ],
    "family": [
        ("familia", "family"),
        ("padre", "father"),
        ("madre", "mother"),
        ("padres", "parents"),
        ("hijo", "son"),
        ("hija", "daughter"),
        ("hermano", "brother"),
        ("hermana", "sister"),
        ("abuelo", "grandfather"),
        ("abuela", "grandmother"),
        ("tío", "uncle"),
        ("tía", "aunt"),
        ("primo", "cousin (m)"),
        ("prima", "cousin (f)"),
        ("sobrino", "nephew"),
        ("sobrina", "niece"),
        ("marido", "husband"),
        ("mujer", "wife/woman"),
        ("novio", "boyfriend"),
        ("novia", "girlfriend"),
    ],
    "colors": [
        ("color", "color"),
        ("rojo", "red"),
        ("azul", "blue"),
        ("verde", "green"),
        ("amarillo", "yellow"),
        ("naranja", "orange"),
        ("negro", "black"),
        ("blanco", "white"),
        ("gris", "gray"),
        ("rosa", "pink"),
        ("marrón", "brown"),
        ("morado", "purple"),
        ("claro", "light"),
        ("oscuro", "dark"),
    ],
    "basic_verbs": [
        ("ser", "to be (permanent)"),
        ("estar", "to be (temporary)"),
        ("tener", "to have"),
        ("hacer", "to do/make"),
        ("ir", "to go"),
        ("venir", "to come"),
        ("poder", "to be able"),
        ("querer", "to want"),
        ("saber", "to know (facts)"),
        ("conocer", "to know (people)"),
        ("decir", "to say"),
        ("hablar", "to speak"),
        ("comer", "to eat"),
        ("beber", "to drink"),
        ("vivir", "to live"),
        ("trabajar", "to work"),
        ("llamar", "to call"),
        ("estudiar", "to study"),
        ("gustar", "to like"),
        ("necesitar", "to need"),
        ("comprar", "to buy"),
        ("leer", "to read"),
        ("escribir", "to write"),
        ("escuchar", "to listen"),
        ("ver", "to see"),
    ],
    "food_basic": [
        ("comida", "food"),
        ("bebida", "drink"),
        ("agua", "water"),
        ("café", "coffee"),
        ("té", "tea"),
        ("leche", "milk"),
        ("zumo", "juice"),
        ("pan", "bread"),
        ("fruta", "fruit"),
        ("verdura", "vegetable"),
        ("carne", "meat"),
        ("pescado", "fish"),
        ("pollo", "chicken"),
        ("huevo", "egg"),
        ("arroz", "rice"),
        ("ensalada", "salad"),
        ("sopa", "soup"),
        ("desayuno", "breakfast"),
        ("almuerzo", "lunch"),
        ("cena", "dinner"),
        ("hambre", "hunger"),
        ("sed", "thirst"),
    ],
}

# Core DELE vocabulary lists (essential words for each level)
DELE_A1_CORE_VERBS = [
    ("ser", "to be (permanent)"),
    ("estar", "to be (temporary)"),
    ("tener", "to have"),
    ("hacer", "to do/make"),
    ("ir", "to go"),
    ("venir", "to come"),
    ("poder", "to be able"),
    ("querer", "to want"),
    ("saber", "to know (facts)"),
    ("conocer", "to know (people)"),
    ("decir", "to say"),
    ("hablar", "to speak"),
    ("comer", "to eat"),
    ("beber", "to drink"),
    ("vivir", "to live"),
    ("trabajar", "to work"),
    ("llamar", "to call"),
    ("estudiar", "to study"),
    ("gustar", "to like"),
    ("necesitar", "to need"),
]

DELE_A2_CORE_VERBS = [
    ("levantarse", "to get up"),
    ("acostarse", "to go to bed"),
    ("ducharse", "to shower"),
    ("vestirse", "to get dressed"),
    ("despertarse", "to wake up"),
    ("sentarse", "to sit down"),
    ("quedarse", "to stay"),
    ("encontrar", "to find"),
    ("perder", "to lose"),
    ("buscar", "to look for"),
    ("llegar", "to arrive"),
    ("salir", "to leave/go out"),
    ("volver", "to return"),
    ("empezar", "to start"),
    ("terminar", "to finish"),
    ("creer", "to believe"),
    ("pensar", "to think"),
    ("parecer", "to seem"),
    ("recordar", "to remember"),
    ("olvidar", "to forget"),
]


@dataclass
class TopicCoverage:
    """Coverage data for a single DELE topic."""
    topic_key: str
    topic_name: str
    topic_name_spanish: str
    level: str
    required_words: int
    known_words: int
    coverage_pct: float
    status: str  # 'complete', 'partial', 'missing'
    missing_keywords: List[str] = field(default_factory=list)


@dataclass
class DeleReadiness:
    """Overall DELE readiness for a level."""
    level: str
    overall_pct: float
    vocabulary_coverage_pct: float
    topic_coverage_pct: float
    verbs_coverage_pct: float
    total_topics: int
    complete_topics: int
    partial_topics: int
    missing_topics: int
    topics: List[TopicCoverage] = field(default_factory=list)
    missing_core_verbs: List[Tuple[str, str]] = field(default_factory=list)
    recommendation: str = ""


def get_topics_for_level(level: str) -> Dict:
    """Get topic definitions for a DELE level."""
    if level == "A1":
        return DELE_A1_TOPICS
    elif level == "A2":
        return DELE_A2_TOPICS
    else:
        return {}


def get_core_verbs_for_level(level: str) -> List[Tuple[str, str]]:
    """Get core verbs for a DELE level."""
    if level == "A1":
        return DELE_A1_CORE_VERBS
    elif level == "A2":
        return DELE_A1_CORE_VERBS + DELE_A2_CORE_VERBS
    else:
        return DELE_A1_CORE_VERBS + DELE_A2_CORE_VERBS


def init_dele_topics():
    """Initialize DELE topics in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Add A1 topics
    for topic_key, topic_data in DELE_A1_TOPICS.items():
        cursor.execute("""
            INSERT OR IGNORE INTO dele_topics
            (level, topic_key, topic_name, topic_name_spanish, required_words, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("A1", topic_key, topic_data["name"], topic_data["name_es"],
              topic_data["required_words"], ", ".join(topic_data["keywords"][:5])))

    # Add A2 topics
    for topic_key, topic_data in DELE_A2_TOPICS.items():
        cursor.execute("""
            INSERT OR IGNORE INTO dele_topics
            (level, topic_key, topic_name, topic_name_spanish, required_words, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("A2", topic_key, topic_data["name"], topic_data["name_es"],
              topic_data["required_words"], ", ".join(topic_data["keywords"][:5])))

    # Add core verbs
    for spanish, english in DELE_A1_CORE_VERBS:
        cursor.execute("""
            INSERT OR IGNORE INTO dele_core_vocabulary
            (level, spanish, english, topic_key, is_verb)
            VALUES (?, ?, ?, ?, ?)
        """, ("A1", spanish, english, "basic_verbs", True))

    for spanish, english in DELE_A2_CORE_VERBS:
        cursor.execute("""
            INSERT OR IGNORE INTO dele_core_vocabulary
            (level, spanish, english, topic_key, is_verb)
            VALUES (?, ?, ?, ?, ?)
        """, ("A2", spanish, english, "daily_routine", True))

    conn.commit()
    conn.close()


def get_user_vocabulary() -> set:
    """Get all vocabulary words the user has in their collection."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT LOWER(spanish) FROM vocabulary")
    words = {row[0] for row in cursor.fetchall()}
    conn.close()
    return words


def get_user_known_vocabulary() -> Dict[str, float]:
    """
    Get vocabulary words the user has practiced, with weights.

    Returns:
        Dict mapping word -> weight (1.0 for learned/due, 0.5 for learning)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT LOWER(v.spanish), vp.status FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.status IN ('learning', 'learned', 'due')
    """)
    words = {}
    for row in cursor.fetchall():
        word, status = row[0], row[1]
        # Learning words count 50%, learned/due count 100%
        words[word] = 0.5 if status == 'learning' else 1.0
    conn.close()
    return words


def calculate_topic_coverage(topic_key: str, topic_data: dict, level: str,
                            user_vocab: Dict[str, float]) -> TopicCoverage:
    """Calculate coverage for a single topic with weighted word counts."""
    keywords = [k.lower() for k in topic_data["keywords"]]
    required = topic_data["required_words"]

    # Count weighted coverage (learned=1.0, learning=0.5)
    weighted_count = sum(user_vocab.get(k, 0) for k in keywords)
    known_count = weighted_count  # For display purposes
    missing = [k for k in keywords if k not in user_vocab]

    # Calculate coverage (cap at 100%)
    coverage = min(100.0, (weighted_count / len(keywords)) * 100) if keywords else 0

    # Determine status
    if coverage >= 80:
        status = "complete"
    elif coverage >= 30:
        status = "partial"
    else:
        status = "missing"

    return TopicCoverage(
        topic_key=topic_key,
        topic_name=topic_data["name"],
        topic_name_spanish=topic_data["name_es"],
        level=level,
        required_words=required,
        known_words=known_count,
        coverage_pct=coverage,
        status=status,
        missing_keywords=missing[:5]  # Show top 5 missing
    )


def calculate_dele_readiness(level: str = "A2") -> DeleReadiness:
    """
    Calculate overall DELE readiness for a given level.

    Args:
        level: DELE level (A1, A2)

    Returns:
        DeleReadiness object with detailed coverage information
    """
    topics = get_topics_for_level(level)
    core_verbs = get_core_verbs_for_level(level)
    user_vocab = get_user_known_vocabulary()  # Only count words actually practiced

    # Calculate topic coverage
    topic_coverages = []
    complete = partial = missing = 0

    for topic_key, topic_data in topics.items():
        coverage = calculate_topic_coverage(topic_key, topic_data, level, user_vocab)
        topic_coverages.append(coverage)

        if coverage.status == "complete":
            complete += 1
        elif coverage.status == "partial":
            partial += 1
        else:
            missing += 1

    # Calculate verb coverage (weighted: learned=1.0, learning=0.5)
    missing_verbs = []
    known_verbs = 0.0
    for spanish, english in core_verbs:
        weight = user_vocab.get(spanish.lower(), 0)
        if weight > 0:
            known_verbs += weight
        else:
            missing_verbs.append((spanish, english))

    verbs_pct = (known_verbs / len(core_verbs) * 100) if core_verbs else 0

    # Calculate overall metrics
    total_topics = len(topics)
    topic_pct = (complete / total_topics * 100) if total_topics else 0

    # Vocabulary coverage is average of all topic coverages
    vocab_pct = sum(t.coverage_pct for t in topic_coverages) / len(topic_coverages) if topic_coverages else 0

    # Overall is weighted average: 50% vocab, 30% topics complete, 20% verbs
    overall = (vocab_pct * 0.5) + (topic_pct * 0.3) + (verbs_pct * 0.2)

    # Generate recommendation
    if overall >= 80:
        recommendation = f"Excellent! You're well-prepared for DELE {level}. Focus on practice tests."
    elif overall >= 60:
        recommendation = f"Good progress! Review the partial topics to strengthen your {level} preparation."
    elif overall >= 40:
        recommendation = f"Making progress. Focus on the missing topics to improve your {level} readiness."
    else:
        recommendation = f"Keep learning! Start with basic topics to build your {level} foundation."

    # Sort topics: missing first, then partial, then complete
    topic_coverages.sort(key=lambda t: (
        0 if t.status == "missing" else 1 if t.status == "partial" else 2,
        -t.coverage_pct
    ))

    return DeleReadiness(
        level=level,
        overall_pct=overall,
        vocabulary_coverage_pct=vocab_pct,
        topic_coverage_pct=topic_pct,
        verbs_coverage_pct=verbs_pct,
        total_topics=total_topics,
        complete_topics=complete,
        partial_topics=partial,
        missing_topics=missing,
        topics=topic_coverages,
        missing_core_verbs=missing_verbs[:10],  # Top 10 missing verbs
        recommendation=recommendation
    )


def get_missing_topics(level: str = "A2") -> List[TopicCoverage]:
    """Get topics that need more work for a DELE level."""
    readiness = calculate_dele_readiness(level)
    return [t for t in readiness.topics if t.status in ("missing", "partial")]


def get_topic_vocabulary_suggestions(topic_key: str, level: str = "A2") -> List[Tuple[str, str]]:
    """Get vocabulary suggestions for a specific topic."""
    topics = get_topics_for_level(level)
    if topic_key not in topics:
        return []

    topic = topics[topic_key]
    user_vocab = get_user_vocabulary()

    # Return keywords the user doesn't know yet
    suggestions = []
    for keyword in topic["keywords"]:
        if keyword.lower() not in user_vocab:
            suggestions.append((keyword, ""))  # Translation to be filled

    return suggestions[:10]


def format_readiness_display(level: str = "A2") -> str:
    """Format DELE readiness as a displayable markdown string."""
    readiness = calculate_dele_readiness(level)

    # Progress bar helper
    def progress_bar(pct: float, width: int = 20) -> str:
        filled = int(pct / 100 * width)
        return "█" * filled + "░" * (width - filled)

    # Status emoji helper
    def status_emoji(status: str) -> str:
        return {"complete": "✅", "partial": "⚠️", "missing": "❌"}.get(status, "")

    lines = [
        f"## DELE {level} Readiness",
        "",
        f"### Overall Progress: {readiness.overall_pct:.0f}%",
        f"`{progress_bar(readiness.overall_pct)}`",
        "",
        readiness.recommendation,
        "",
        "---",
        "",
        "### Coverage Breakdown",
        "",
        "| Area | Progress | |",
        "|:-----|:---------|-------:|",
        f"| Vocabulary | {progress_bar(readiness.vocabulary_coverage_pct)} | {readiness.vocabulary_coverage_pct:.0f}% |",
        f"| Topics ({readiness.complete_topics}/{readiness.total_topics}) | {progress_bar(readiness.topic_coverage_pct)} | {readiness.topic_coverage_pct:.0f}% |",
        f"| Core Verbs | {progress_bar(readiness.verbs_coverage_pct)} | {readiness.verbs_coverage_pct:.0f}% |",
        "",
        "---",
        "",
        "### Topic Details",
        "",
    ]

    # Group by status
    for status_name, status_code in [("Needs Work", "missing"), ("In Progress", "partial"), ("Complete", "complete")]:
        status_topics = [t for t in readiness.topics if t.status == status_code]
        if status_topics:
            lines.append(f"**{status_emoji(status_code)} {status_name}:**")
            for topic in status_topics:
                lines.append(f"- {topic.topic_name} ({topic.topic_name_spanish}): {topic.coverage_pct:.0f}%")
                if topic.missing_keywords and status_code != "complete":
                    lines.append(f"  - Missing: {', '.join(topic.missing_keywords)}")
            lines.append("")

    # Missing verbs section
    if readiness.missing_core_verbs:
        lines.extend([
            "---",
            "",
            "### Missing Core Verbs",
            "",
        ])
        for spanish, english in readiness.missing_core_verbs[:5]:
            lines.append(f"- **{spanish}** - {english}")

    return "\n".join(lines)


def get_study_priorities(level: str = "A2", limit: int = 5) -> List[dict]:
    """Get prioritized study recommendations."""
    readiness = calculate_dele_readiness(level)
    priorities = []

    # Add missing topics as priorities
    for topic in readiness.topics:
        if topic.status == "missing":
            priorities.append({
                "type": "topic",
                "name": topic.topic_name,
                "name_es": topic.topic_name_spanish,
                "coverage": topic.coverage_pct,
                "action": f"Learn {topic.topic_name.lower()} vocabulary",
                "keywords": topic.missing_keywords
            })

    # Add missing verbs
    if readiness.missing_core_verbs:
        priorities.append({
            "type": "verbs",
            "name": "Core Verbs",
            "name_es": "Verbos esenciales",
            "coverage": readiness.verbs_coverage_pct,
            "action": "Practice essential verbs",
            "verbs": readiness.missing_core_verbs[:5]
        })

    # Add partial topics
    for topic in readiness.topics:
        if topic.status == "partial" and len(priorities) < limit:
            priorities.append({
                "type": "topic",
                "name": topic.topic_name,
                "name_es": topic.topic_name_spanish,
                "coverage": topic.coverage_pct,
                "action": f"Review {topic.topic_name.lower()} vocabulary",
                "keywords": topic.missing_keywords
            })

    return priorities[:limit]


def get_missing_dele_vocabulary(level: str = "A1") -> List[Tuple[str, str, str]]:
    """
    Get all missing DELE vocabulary for a level with translations.

    Args:
        level: DELE level (A1 or A2)

    Returns:
        List of tuples: (spanish, english, topic_name)
    """
    user_vocab = get_user_vocabulary()
    missing = []

    if level == "A1":
        vocab_dict = DELE_A1_VOCABULARY
    else:
        # For A2, include both A1 and A2 vocabulary
        vocab_dict = DELE_A1_VOCABULARY.copy()
        # Note: Could add DELE_A2_VOCABULARY here when defined

    # Get topic names for display
    topics = get_topics_for_level(level)

    for topic_key, words in vocab_dict.items():
        topic_name = topics.get(topic_key, {}).get("name", topic_key.title())
        for spanish, english in words:
            # Normalize for comparison
            spanish_lower = spanish.lower()
            if spanish_lower not in user_vocab:
                missing.append((spanish, english, topic_name))

    return missing


def add_missing_dele_vocabulary(level: str = "A1") -> Tuple[int, int, List[str]]:
    """
    Add all missing DELE vocabulary to the user's vocabulary database.

    Args:
        level: DELE level (A1 or A2)

    Returns:
        Tuple of (words_added, words_skipped, topics_updated)
    """
    from datetime import datetime

    missing = get_missing_dele_vocabulary(level)

    if not missing:
        return 0, 0, []

    conn = get_connection()
    cursor = conn.cursor()

    added = 0
    skipped = 0
    topics_updated = set()

    for spanish, english, topic_name in missing:
        # Check if word already exists (case-insensitive)
        cursor.execute(
            "SELECT id FROM vocabulary WHERE LOWER(spanish) = LOWER(?)",
            (spanish,)
        )
        existing = cursor.fetchone()

        if existing:
            skipped += 1
            continue

        # Add the word
        cursor.execute("""
            INSERT INTO vocabulary (spanish, english, category, cefr_level)
            VALUES (?, ?, ?, ?)
        """, (spanish, english, topic_name, level))

        vocab_id = cursor.lastrowid

        # Initialize progress tracking
        cursor.execute("""
            INSERT INTO vocabulary_progress (vocabulary_id, next_review, status)
            VALUES (?, ?, 'new')
        """, (vocab_id, datetime.now().isoformat()))

        added += 1
        topics_updated.add(topic_name)

    conn.commit()
    conn.close()

    return added, skipped, list(topics_updated)


def get_dele_vocabulary_summary(level: str = "A1") -> dict:
    """
    Get a summary of DELE vocabulary status for a level.

    Returns:
        dict with total, known, missing counts and topic breakdown
    """
    user_vocab = get_user_vocabulary()

    if level == "A1":
        vocab_dict = DELE_A1_VOCABULARY
    else:
        vocab_dict = DELE_A1_VOCABULARY.copy()

    topics = get_topics_for_level(level)

    summary = {
        "level": level,
        "total_words": 0,
        "known_words": 0,
        "missing_words": 0,
        "topics": []
    }

    for topic_key, words in vocab_dict.items():
        topic_name = topics.get(topic_key, {}).get("name", topic_key.title())
        topic_total = len(words)
        topic_known = sum(1 for s, e in words if s.lower() in user_vocab)
        topic_missing = topic_total - topic_known

        summary["total_words"] += topic_total
        summary["known_words"] += topic_known
        summary["missing_words"] += topic_missing

        summary["topics"].append({
            "key": topic_key,
            "name": topic_name,
            "total": topic_total,
            "known": topic_known,
            "missing": topic_missing,
            "pct": (topic_known / topic_total * 100) if topic_total > 0 else 0
        })

    # Sort topics by missing count (most missing first)
    summary["topics"].sort(key=lambda t: -t["missing"])

    return summary


if __name__ == "__main__":
    # Test the module
    print("Initializing DELE topics...")
    init_dele_topics()

    print("\nCalculating DELE A2 readiness...")
    display = format_readiness_display("A2")
    print(display)

    print("\n\nStudy priorities:")
    priorities = get_study_priorities("A2")
    for p in priorities:
        print(f"- {p['name']}: {p['action']}")
