"""
Content Analysis Module for HablaConmigo

Provides text analysis and vocabulary gap analysis for Spanish content.
Compares external content against user's learned vocabulary to identify
new words to learn.

Usage:
    from src.content_analysis import analyze_content, ContentAnalysis

    result = analyze_content("Hola, ¿cómo estás?")
    print(f"Known: {result.known_count}, New: {result.new_count}")
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Tuple
from datetime import datetime

from src.frequency_data import (
    get_frequency_rank, estimate_cefr_level, get_translation,
    is_high_frequency, get_frequency_tier, is_in_dele_vocabulary
)
from src.database import get_connection


@dataclass
class WordInfo:
    """Information about a word found in content."""
    spanish: str
    english: Optional[str]
    frequency_rank: int
    cefr_level: str
    frequency_tier: str
    in_dele_a2: bool
    occurrences: int = 1
    context_sentences: List[str] = field(default_factory=list)
    original_forms: List[str] = field(default_factory=list)  # Original forms from text (e.g., conjugated verbs)


@dataclass
class ContentAnalysis:
    """Result of analyzing Spanish content."""
    # Basic stats
    total_words: int
    unique_words: int

    # Vocabulary breakdown
    known_words: Set[str]
    learning_words: Set[str]
    new_words: Set[str]

    # Counts
    known_count: int
    learning_count: int
    new_count: int

    # Comprehension estimate
    comprehension_pct: float

    # Detailed info about new words (sorted by frequency)
    new_words_details: List[WordInfo]

    # Metadata
    source_text: str = ""
    analyzed_at: str = ""

    # Word forms contribution (multiplication effect)
    word_forms_matched: int = 0

    @property
    def is_ready_to_consume(self) -> bool:
        """Check if user knows enough vocabulary to comfortably consume this content."""
        return self.comprehension_pct >= 80.0

    @property
    def difficulty_label(self) -> str:
        """Get a human-readable difficulty label."""
        if self.comprehension_pct >= 95:
            return "Very Easy"
        elif self.comprehension_pct >= 85:
            return "Easy"
        elif self.comprehension_pct >= 70:
            return "Moderate"
        elif self.comprehension_pct >= 50:
            return "Challenging"
        else:
            return "Difficult"

    @property
    def high_value_words(self) -> List[WordInfo]:
        """Get new words that are high frequency (most valuable to learn)."""
        return [w for w in self.new_words_details if w.frequency_rank <= 1500]


# Spanish stop words that are usually known even by beginners
STOP_WORDS = {
    'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con',
    'contra', 'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 'e',
    'el', 'ella', 'ellas', 'ellos', 'en', 'entre', 'era', 'esa', 'esas', 'ese',
    'eso', 'esos', 'esta', 'estado', 'estas', 'este', 'esto', 'estos', 'fue',
    'ha', 'han', 'hay', 'la', 'las', 'le', 'les', 'lo', 'los', 'me', 'mi',
    'muy', 'ni', 'no', 'nos', 'o', 'os', 'para', 'pero', 'por', 'que', 'qué',
    'se', 'si', 'sí', 'sin', 'sobre', 'su', 'sus', 'también', 'tan', 'te',
    'tu', 'tus', 'un', 'una', 'uno', 'unos', 'unas', 'y', 'ya', 'yo',
}

# Common Spanish verb endings for basic lemmatization
VERB_ENDINGS = {
    # Infinitive markers
    'ar', 'er', 'ir',
    # Present tense
    'o', 'as', 'a', 'amos', 'áis', 'an',
    'es', 'e', 'emos', 'éis', 'en',
    'imos', 'ís',
    # Past tense (preterite)
    'é', 'aste', 'ó', 'amos', 'asteis', 'aron',
    'í', 'iste', 'ió', 'imos', 'isteis', 'ieron',
    # Imperfect
    'aba', 'abas', 'ábamos', 'abais', 'aban',
    'ía', 'ías', 'íamos', 'íais', 'ían',
    # Future
    'aré', 'arás', 'ará', 'aremos', 'aréis', 'arán',
    'eré', 'erás', 'erá', 'eremos', 'eréis', 'erán',
    'iré', 'irás', 'irá', 'iremos', 'iréis', 'irán',
    # Gerund
    'ando', 'iendo',
    # Past participle
    'ado', 'ido',
}

# Irregular verb mappings (common forms -> infinitive)
IRREGULAR_VERBS = {
    # ser
    'soy': 'ser', 'eres': 'ser', 'es': 'ser', 'somos': 'ser', 'sois': 'ser', 'son': 'ser',
    'era': 'ser', 'eras': 'ser', 'éramos': 'ser', 'erais': 'ser', 'eran': 'ser',
    'fui': 'ser', 'fuiste': 'ser', 'fue': 'ser', 'fuimos': 'ser', 'fuisteis': 'ser', 'fueron': 'ser',
    'sido': 'ser', 'siendo': 'ser',
    # estar
    'estoy': 'estar', 'estás': 'estar', 'está': 'estar', 'estamos': 'estar', 'estáis': 'estar', 'están': 'estar',
    'estaba': 'estar', 'estabas': 'estar', 'estábamos': 'estar', 'estabais': 'estar', 'estaban': 'estar',
    'estuve': 'estar', 'estuviste': 'estar', 'estuvo': 'estar', 'estuvimos': 'estar', 'estuvieron': 'estar',
    'estado': 'estar', 'estando': 'estar',
    # tener
    'tengo': 'tener', 'tienes': 'tener', 'tiene': 'tener', 'tenemos': 'tener', 'tenéis': 'tener', 'tienen': 'tener',
    'tenía': 'tener', 'tenías': 'tener', 'teníamos': 'tener', 'teníais': 'tener', 'tenían': 'tener',
    'tuve': 'tener', 'tuviste': 'tener', 'tuvo': 'tener', 'tuvimos': 'tener', 'tuvieron': 'tener',
    'tenido': 'tener', 'teniendo': 'tener',
    # hacer
    'hago': 'hacer', 'haces': 'hacer', 'hace': 'hacer', 'hacemos': 'hacer', 'hacéis': 'hacer', 'hacen': 'hacer',
    'hacía': 'hacer', 'hacías': 'hacer', 'hacíamos': 'hacer', 'hacíais': 'hacer', 'hacían': 'hacer',
    'hice': 'hacer', 'hiciste': 'hacer', 'hizo': 'hacer', 'hicimos': 'hacer', 'hicieron': 'hacer',
    'hecho': 'hacer', 'haciendo': 'hacer',
    # ir
    'voy': 'ir', 'vas': 'ir', 'va': 'ir', 'vamos': 'ir', 'vais': 'ir', 'van': 'ir',
    'iba': 'ir', 'ibas': 'ir', 'íbamos': 'ir', 'ibais': 'ir', 'iban': 'ir',
    'yendo': 'ir', 'ido': 'ir',
    # poder
    'puedo': 'poder', 'puedes': 'poder', 'puede': 'poder', 'podemos': 'poder', 'podéis': 'poder', 'pueden': 'poder',
    'podía': 'poder', 'podías': 'poder', 'podíamos': 'poder', 'podíais': 'poder', 'podían': 'poder',
    'pude': 'poder', 'pudiste': 'poder', 'pudo': 'poder', 'pudimos': 'poder', 'pudieron': 'poder',
    'podido': 'poder', 'pudiendo': 'poder',
    # decir
    'digo': 'decir', 'dices': 'decir', 'dice': 'decir', 'decimos': 'decir', 'decís': 'decir', 'dicen': 'decir',
    'decía': 'decir', 'decías': 'decir', 'decíamos': 'decir', 'decíais': 'decir', 'decían': 'decir',
    'dije': 'decir', 'dijiste': 'decir', 'dijo': 'decir', 'dijimos': 'decir', 'dijieron': 'decir',
    'dicho': 'decir', 'diciendo': 'decir',
    # venir
    'vengo': 'venir', 'vienes': 'venir', 'viene': 'venir', 'venimos': 'venir', 'venís': 'venir', 'vienen': 'venir',
    'venía': 'venir', 'venías': 'venir', 'veníamos': 'venir', 'veníais': 'venir', 'venían': 'venir',
    'vine': 'venir', 'viniste': 'venir', 'vino': 'venir', 'vinimos': 'venir', 'vinieron': 'venir',
    'venido': 'venir', 'viniendo': 'venir',
    # querer
    'quiero': 'querer', 'quieres': 'querer', 'quiere': 'querer', 'queremos': 'querer', 'queréis': 'querer', 'quieren': 'querer',
    'quería': 'querer', 'querías': 'querer', 'queríamos': 'querer', 'queríais': 'querer', 'querían': 'querer',
    'quise': 'querer', 'quisiste': 'querer', 'quiso': 'querer', 'quisimos': 'querer', 'quisieron': 'querer',
    'querido': 'querer', 'queriendo': 'querer',
    # saber
    'sé': 'saber', 'sabes': 'saber', 'sabe': 'saber', 'sabemos': 'saber', 'sabéis': 'saber', 'saben': 'saber',
    'sabía': 'saber', 'sabías': 'saber', 'sabíamos': 'saber', 'sabíais': 'saber', 'sabían': 'saber',
    'supe': 'saber', 'supiste': 'saber', 'supo': 'saber', 'supimos': 'saber', 'supieron': 'saber',
    'sabido': 'saber', 'sabiendo': 'saber',
    # dar
    'doy': 'dar', 'das': 'dar', 'da': 'dar', 'damos': 'dar', 'dais': 'dar', 'dan': 'dar',
    'daba': 'dar', 'dabas': 'dar', 'dábamos': 'dar', 'dabais': 'dar', 'daban': 'dar',
    'di': 'dar', 'diste': 'dar', 'dio': 'dar', 'dimos': 'dar', 'dieron': 'dar',
    'dado': 'dar', 'dando': 'dar',
    # ver
    'veo': 'ver', 'ves': 'ver', 've': 'ver', 'vemos': 'ver', 'veis': 'ver', 'ven': 'ver',
    'veía': 'ver', 'veías': 'ver', 'veíamos': 'ver', 'veíais': 'ver', 'veían': 'ver',
    'vi': 'ver', 'viste': 'ver', 'vio': 'ver', 'vimos': 'ver', 'vieron': 'ver',
    'visto': 'ver', 'viendo': 'ver',
    # sentir (e→ie stem change) - to feel
    'siento': 'sentir', 'sientes': 'sentir', 'siente': 'sentir', 'sentimos': 'sentir', 'sentís': 'sentir', 'sienten': 'sentir',
    'sentía': 'sentir', 'sentías': 'sentir', 'sentíamos': 'sentir', 'sentíais': 'sentir', 'sentían': 'sentir',
    'sentí': 'sentir', 'sentiste': 'sentir', 'sintió': 'sentir', 'sentimos': 'sentir', 'sintieron': 'sentir',
    'sentido': 'sentir', 'sintiendo': 'sentir',
    'sienta': 'sentir', 'sientas': 'sentir', 'sintamos': 'sentir', 'sintáis': 'sentir', 'sientan': 'sentir',
    # sentar (e→ie stem change) - to sit/seat
    'siento': 'sentar', 'sientas': 'sentar', 'sienta': 'sentar', 'sentamos': 'sentar', 'sentáis': 'sentar', 'sientan': 'sentar',
    # Note: sienta/siento could be sentir or sentar - defaulting to sentir as more common
    # pensar (e→ie) - to think
    'pienso': 'pensar', 'piensas': 'pensar', 'piensa': 'pensar', 'pensamos': 'pensar', 'pensáis': 'pensar', 'piensan': 'pensar',
    'pensaba': 'pensar', 'pensabas': 'pensar', 'pensábamos': 'pensar', 'pensabais': 'pensar', 'pensaban': 'pensar',
    'pensé': 'pensar', 'pensaste': 'pensar', 'pensó': 'pensar', 'pensamos': 'pensar', 'pensaron': 'pensar',
    'pensado': 'pensar', 'pensando': 'pensar',
    # entender (e→ie) - to understand
    'entiendo': 'entender', 'entiendes': 'entender', 'entiende': 'entender', 'entendemos': 'entender', 'entendéis': 'entender', 'entienden': 'entender',
    'entendía': 'entender', 'entendías': 'entender', 'entendíamos': 'entender', 'entendíais': 'entender', 'entendían': 'entender',
    'entendí': 'entender', 'entendiste': 'entender', 'entendió': 'entender', 'entendimos': 'entender', 'entendieron': 'entender',
    'entendido': 'entender', 'entendiendo': 'entender',
    # dormir (o→ue) - to sleep
    'duermo': 'dormir', 'duermes': 'dormir', 'duerme': 'dormir', 'dormimos': 'dormir', 'dormís': 'dormir', 'duermen': 'dormir',
    'dormía': 'dormir', 'dormías': 'dormir', 'dormíamos': 'dormir', 'dormíais': 'dormir', 'dormían': 'dormir',
    'dormí': 'dormir', 'dormiste': 'dormir', 'durmió': 'dormir', 'dormimos': 'dormir', 'durmieron': 'dormir',
    'dormido': 'dormir', 'durmiendo': 'dormir',
    # volver (o→ue) - to return
    'vuelvo': 'volver', 'vuelves': 'volver', 'vuelve': 'volver', 'volvemos': 'volver', 'volvéis': 'volver', 'vuelven': 'volver',
    'volvía': 'volver', 'volvías': 'volver', 'volvíamos': 'volver', 'volvíais': 'volver', 'volvían': 'volver',
    'volví': 'volver', 'volviste': 'volver', 'volvió': 'volver', 'volvimos': 'volver', 'volvieron': 'volver',
    'vuelto': 'volver', 'volviendo': 'volver',
    # encontrar (o→ue) - to find
    'encuentro': 'encontrar', 'encuentras': 'encontrar', 'encuentra': 'encontrar', 'encontramos': 'encontrar', 'encontráis': 'encontrar', 'encuentran': 'encontrar',
    'encontraba': 'encontrar', 'encontrabas': 'encontrar', 'encontrábamos': 'encontrar', 'encontrabais': 'encontrar', 'encontraban': 'encontrar',
    'encontré': 'encontrar', 'encontraste': 'encontrar', 'encontró': 'encontrar', 'encontramos': 'encontrar', 'encontraron': 'encontrar',
    'encontrado': 'encontrar', 'encontrando': 'encontrar',
    # pedir (e→i) - to ask for
    'pido': 'pedir', 'pides': 'pedir', 'pide': 'pedir', 'pedimos': 'pedir', 'pedís': 'pedir', 'piden': 'pedir',
    'pedía': 'pedir', 'pedías': 'pedir', 'pedíamos': 'pedir', 'pedíais': 'pedir', 'pedían': 'pedir',
    'pedí': 'pedir', 'pediste': 'pedir', 'pidió': 'pedir', 'pedimos': 'pedir', 'pidieron': 'pedir',
    'pedido': 'pedir', 'pidiendo': 'pedir',
    # seguir (e→i) - to follow/continue
    'sigo': 'seguir', 'sigues': 'seguir', 'sigue': 'seguir', 'seguimos': 'seguir', 'seguís': 'seguir', 'siguen': 'seguir',
    'seguía': 'seguir', 'seguías': 'seguir', 'seguíamos': 'seguir', 'seguíais': 'seguir', 'seguían': 'seguir',
    'seguí': 'seguir', 'seguiste': 'seguir', 'siguió': 'seguir', 'seguimos': 'seguir', 'siguieron': 'seguir',
    'seguido': 'seguir', 'siguiendo': 'seguir',
}

# Common noun/adjective endings for basic lemmatization
NOUN_ADJ_MAPPINGS = {
    # Plural -> singular
    'es': '',      # ciudades -> ciudad
    's': '',       # casas -> casa
    # Feminine -> masculine (for adjectives)
    'a': 'o',      # bonita -> bonito (approximate)
    'as': 'os',    # bonitas -> bonitos
}


def normalize_text(text: str) -> str:
    """
    Normalize Spanish text for analysis.

    - Converts to lowercase
    - Preserves Spanish accents
    - Removes punctuation except apostrophes
    """
    text = text.lower()
    # Remove punctuation but keep letters and spaces
    text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize_spanish(text: str) -> List[str]:
    """
    Tokenize Spanish text into words.

    Args:
        text: Spanish text to tokenize

    Returns:
        List of word tokens (lowercase, with accents preserved)
    """
    normalized = normalize_text(text)
    # Split on whitespace
    tokens = normalized.split()
    # Filter out very short tokens and numbers
    tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
    return tokens


def lemmatize_spanish(word: str) -> str:
    """
    Basic Spanish lemmatization (word -> base form).

    This is a simplified rule-based approach. For production,
    consider using spaCy with Spanish model.

    Args:
        word: Spanish word to lemmatize

    Returns:
        Base form of the word (best guess)
    """
    word = word.lower().strip()

    # Check irregular verbs first
    if word in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[word]

    # Try to identify verb conjugations and return infinitive
    # This is simplified and won't catch everything

    # Common -ar verb patterns
    if word.endswith('ando'):  # gerund
        return word[:-4] + 'ar'
    if word.endswith('ado'):   # past participle
        return word[:-3] + 'ar'

    # -ar verb present tense: -o, -as, -a, -amos, -áis, -an
    if word.endswith('amos') and len(word) > 4:
        return word[:-4] + 'ar'
    if word.endswith('áis') and len(word) > 3:
        return word[:-3] + 'ar'
    if word.endswith('an') and len(word) > 3:
        # Check if it looks like an -ar verb (not words like "pan")
        potential_stem = word[:-2]
        if len(potential_stem) >= 2:
            return potential_stem + 'ar'
    if word.endswith('as') and len(word) > 3:
        # Could be verb form (hablas -> hablar) or plural adjective (bajas -> bajo)
        from src.frequency_data import get_word_data

        # Try plural adjective: bajas -> bajo (via baja)
        singular_fem = word[:-1]  # Remove 's'
        singular_masc = word[:-2] + 'o'  # Change 'as' to 'o'
        adj_data = get_word_data(singular_masc)

        # Try verb: hablas -> hablar
        verb_form = word[:-2] + 'ar'
        verb_data = get_word_data(verb_form)

        # If adjective exists and is an adjective, use it
        if adj_data and adj_data.pos in ('adj', 'adv'):
            return singular_masc
        # If only verb exists, use it
        elif verb_data:
            return verb_form
        # If neither, default to verb form (original behavior)
        else:
            return verb_form
    if word.endswith('a') and len(word) > 3 and not word.endswith(('ía', 'ea', 'oa')):
        # Could be feminine adjective (baja -> bajo) or verb form (habla -> hablar)
        # Check adjective form first (more common for words ending in -a)
        from src.frequency_data import get_frequency_rank, get_word_data

        # Try adjective: change 'a' to 'o' (e.g., baja -> bajo)
        adj_form = word[:-1] + 'o'
        adj_data = get_word_data(adj_form)

        # Try verb: change 'a' to 'ar' (e.g., habla -> hablar)
        verb_form = word[:-1] + 'ar'
        verb_data = get_word_data(verb_form)

        # If both exist, prefer the more common one
        if adj_data and verb_data:
            # Lower rank = more common
            if adj_data.rank < verb_data.rank:
                return adj_form
            else:
                return verb_form
        # If only adjective exists, use it
        elif adj_data and adj_data.pos in ('adj', 'adv'):
            return adj_form
        # If only verb exists, use it
        elif verb_data:
            return verb_form
        # If neither exists in our data, keep the word as-is
        # (likely a noun ending in 'a')

    # Common -er/-ir verb patterns
    if word.endswith('iendo'):  # gerund
        base = word[:-5]
        # Could be -er or -ir, default to -er
        return base + 'er'
    if word.endswith('ido'):    # past participle
        base = word[:-3]
        return base + 'ir'

    # -er verb present tense: -o, -es, -e, -emos, -éis, -en
    if word.endswith('emos') and len(word) > 4:
        return word[:-4] + 'er'
    if word.endswith('éis') and len(word) > 3:
        return word[:-3] + 'er'
    if word.endswith('en') and len(word) > 3:
        potential_stem = word[:-2]
        if len(potential_stem) >= 2:
            # Check if -er or -ir verb
            from src.frequency_data import get_frequency_rank
            if get_frequency_rank(potential_stem + 'er') < 99999:
                return potential_stem + 'er'
            if get_frequency_rank(potential_stem + 'ir') < 99999:
                return potential_stem + 'ir'

    # -ir verb present tense: -imos, -ís
    if word.endswith('imos') and len(word) > 4:
        return word[:-4] + 'ir'
    if word.endswith('ís') and len(word) > 2:
        return word[:-2] + 'ir'

    # Common Spanish names to exclude from lemmatization
    SPANISH_NAMES = {
        'carlos', 'maría', 'maria', 'josé', 'jose', 'juan', 'pedro', 'luis',
        'miguel', 'antonio', 'francisco', 'manuel', 'javier', 'david', 'pablo',
        'ana', 'carmen', 'isabel', 'rosa', 'elena', 'laura', 'marta', 'lucía',
        'lucia', 'sara', 'paula', 'andrea', 'sofía', 'sofia', 'marcos', 'diego',
        'andrés', 'andres', 'fernando', 'rafael', 'alberto', 'alejandro', 'roberto',
        'ricardo', 'daniel', 'sergio', 'jorge', 'ramón', 'ramon', 'ángel', 'angel',
        'mercedes', 'pilar', 'teresa', 'dolores', 'cristina', 'beatriz', 'silvia'
    }

    # Don't lemmatize names
    if word in SPANISH_NAMES:
        return word

    # For nouns/adjectives, try to get singular form
    if word.endswith('es') and len(word) > 3:
        # Could be plural of word ending in consonant
        singular = word[:-2]
        if singular.endswith(('d', 'n', 'r', 'l', 's', 'z')):
            # Verify the singular form exists in our data
            from src.frequency_data import get_frequency_rank
            if get_frequency_rank(singular) < 99999:
                return singular

    if word.endswith('s') and len(word) > 2 and not word.endswith('es'):
        # Simple plural - only strip if singular exists in frequency data
        potential_singular = word[:-1]
        from src.frequency_data import get_frequency_rank
        if get_frequency_rank(potential_singular) < 99999:
            return potential_singular

    # Return word as-is if no rules match
    return word


def get_user_vocabulary(status: Optional[str] = None) -> Set[str]:
    """
    Get user's vocabulary from the database.

    Args:
        status: Filter by status ('learned', 'learning', 'new', etc.)
                If None, returns all vocabulary.

    Returns:
        Set of Spanish words (lowercase)
    """
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("""
            SELECT LOWER(v.spanish) as word
            FROM vocabulary v
            JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
            WHERE vp.status = ?
        """, (status,))
    else:
        cursor.execute("""
            SELECT LOWER(v.spanish) as word
            FROM vocabulary v
        """)

    words = {row['word'] for row in cursor.fetchall()}
    conn.close()
    return words


def get_learned_vocabulary() -> Set[str]:
    """Get words the user has mastered (status='learned')."""
    return get_user_vocabulary('learned')


def get_learning_vocabulary() -> Set[str]:
    """Get words the user is currently learning (status='learning')."""
    return get_user_vocabulary('learning')


def get_all_known_vocabulary() -> Set[str]:
    """Get all words the user knows or is learning."""
    learned = get_learned_vocabulary()
    learning = get_learning_vocabulary()
    return learned | learning


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text for context examples."""
    # Split on sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    # Clean up and filter
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    return sentences


def find_word_context(word: str, sentences: List[str], max_contexts: int = 2) -> List[str]:
    """Find sentences containing a word for context."""
    contexts = []
    word_lower = word.lower()
    for sentence in sentences:
        if word_lower in sentence.lower():
            contexts.append(sentence)
            if len(contexts) >= max_contexts:
                break
    return contexts


def analyze_content(text: str, include_stop_words: bool = False) -> ContentAnalysis:
    """
    Analyze Spanish text and compare against user's vocabulary.

    This is the main analysis function that:
    1. Tokenizes and lemmatizes the text
    2. Compares against user's learned/learning vocabulary
    3. Identifies new words with frequency data
    4. Calculates comprehension percentage

    Args:
        text: Spanish text to analyze
        include_stop_words: If True, include common stop words in analysis

    Returns:
        ContentAnalysis object with detailed breakdown
    """
    # Tokenize
    tokens = tokenize_spanish(text)
    total_words = len(tokens)

    # Lemmatize and get unique words
    lemmas = [lemmatize_spanish(token) for token in tokens]
    unique_lemmas = set(lemmas)

    # Optionally filter out stop words
    if not include_stop_words:
        unique_lemmas = {w for w in unique_lemmas if w not in STOP_WORDS}

    unique_count = len(unique_lemmas)

    # Get user's vocabulary
    learned = get_learned_vocabulary()
    learning = get_learning_vocabulary()
    all_known = learned | learning

    # Also consider words in the database as "known" even if not learned yet
    # This helps with words the user has seen but hasn't fully mastered
    all_vocab = get_user_vocabulary(None)

    # ENHANCEMENT: Include generated word forms in matching
    # This implements the multiplication effect: base vocabulary × grammar = word forms
    try:
        from src.word_forms import get_all_word_forms
        word_forms = get_all_word_forms()
        all_known_with_forms = all_known | word_forms
    except Exception as e:
        print(f"Note: Word forms not available: {e}")
        all_known_with_forms = all_known
        word_forms = set()

    # Categorize words
    # First check against base vocabulary (lemmas)
    known_words = unique_lemmas & learned
    learning_words = unique_lemmas & learning

    # Then check against word forms (non-lemmatized tokens)
    # This catches conjugated verbs, plurals, etc. that the user can recognize
    unique_tokens = set(tokens)
    known_word_forms = unique_tokens & word_forms

    # Combine: words matched via lemma + words matched via forms
    total_known_unique = known_words | known_word_forms

    # New words are lemmas not in user's vocabulary
    # We only use lemmas to ensure we store base forms (infinitives, singular nouns)
    new_words = unique_lemmas - all_vocab

    # Filter out very short words and stop words from new words
    new_words = {w for w in new_words
                 if len(w) > 2 and w not in STOP_WORDS}

    # Extract sentences for context
    sentences = extract_sentences(text)

    # Build detailed info for new words
    word_counts = {}
    for token in tokens:
        lemma = lemmatize_spanish(token)
        word_counts[lemma] = word_counts.get(lemma, 0) + 1

    # Build a map from lemma to original tokens for context finding
    lemma_to_tokens = {}
    for token in tokens:
        lemma = lemmatize_spanish(token)
        if lemma not in lemma_to_tokens:
            lemma_to_tokens[lemma] = set()
        lemma_to_tokens[lemma].add(token.lower())

    new_words_details = []
    for lemma in new_words:
        # Look up translation and metadata using the lemma (base form)
        translation = get_translation(lemma)
        freq_rank = get_frequency_rank(lemma)
        cefr = estimate_cefr_level(lemma)
        in_dele = is_in_dele_vocabulary(lemma, 'A2')

        # Find context sentences using original token forms
        context = []
        original_forms = lemma_to_tokens.get(lemma, {lemma})
        for form in original_forms:
            context.extend(find_word_context(form, sentences))
        # Deduplicate context sentences
        context = list(dict.fromkeys(context))[:3]

        info = WordInfo(
            spanish=lemma,  # Store the base form (infinitive for verbs)
            english=translation,
            frequency_rank=freq_rank,
            cefr_level=cefr,
            frequency_tier=get_frequency_tier(lemma),
            in_dele_a2=in_dele,
            occurrences=word_counts.get(lemma, 1),
            context_sentences=context,
            original_forms=list(original_forms)  # Keep track of original forms from text
        )
        new_words_details.append(info)

    # Sort by frequency (most common/valuable words first)
    new_words_details.sort(key=lambda w: w.frequency_rank)

    # Calculate comprehension percentage
    # Based on unique words the user knows vs total unique words
    # ENHANCED: Now includes word forms recognition
    if unique_count > 0:
        # Count known + learning + word_forms + stop words as "comprehensible"
        # This reflects the multiplication effect: base vocab × grammar = comprehension
        comprehensible = len(total_known_unique) + len(learning_words)
        if not include_stop_words:
            # Add back stop words that were in the text
            stop_in_text = len({lemmatize_spanish(t) for t in tokens} & STOP_WORDS)
            comprehensible += stop_in_text
            total_unique_with_stops = unique_count + stop_in_text
            comprehension_pct = (comprehensible / total_unique_with_stops) * 100
        else:
            comprehension_pct = (comprehensible / unique_count) * 100
    else:
        comprehension_pct = 100.0

    # Calculate word forms contribution to comprehension
    word_forms_matched = len(known_word_forms) if 'known_word_forms' in locals() else 0

    return ContentAnalysis(
        total_words=total_words,
        unique_words=unique_count,
        known_words=known_words,
        learning_words=learning_words,
        new_words=new_words,
        known_count=len(known_words),
        learning_count=len(learning_words),
        new_count=len(new_words),
        comprehension_pct=min(100.0, comprehension_pct),
        new_words_details=new_words_details,
        source_text=text[:500] + "..." if len(text) > 500 else text,
        word_forms_matched=word_forms_matched,  # NEW: Track word forms contribution
        analyzed_at=datetime.now().isoformat()
    )


def analyze_for_dele(text: str, level: str = 'A2') -> Dict:
    """
    Analyze text specifically for DELE exam preparation.

    Args:
        text: Spanish text to analyze
        level: DELE level (A1, A2, B1, B2, C1, C2)

    Returns:
        Dict with DELE-specific analysis
    """
    analysis = analyze_content(text)

    # Count words that are in DELE vocabulary for the target level
    dele_words = [w for w in analysis.new_words_details
                  if is_in_dele_vocabulary(w.spanish, level)]
    non_dele_words = [w for w in analysis.new_words_details
                      if not is_in_dele_vocabulary(w.spanish, level)]

    return {
        'analysis': analysis,
        'dele_level': level,
        'dele_relevant_words': dele_words,
        'beyond_level_words': non_dele_words,
        'dele_word_count': len(dele_words),
        'recommendation': f"Learn the {len(dele_words)} DELE {level} words first"
                          if dele_words else f"This content is above DELE {level} level"
    }


def get_comprehension_recommendation(analysis: ContentAnalysis) -> str:
    """
    Get a recommendation based on the analysis.

    Args:
        analysis: ContentAnalysis result

    Returns:
        Human-readable recommendation
    """
    pct = analysis.comprehension_pct
    new_count = analysis.new_count
    high_value = len(analysis.high_value_words)

    if pct >= 95:
        return "Perfect for your level! You know almost all the vocabulary."
    elif pct >= 85:
        return f"Great match! Learn {new_count} new words to fully understand this content."
    elif pct >= 70:
        return f"Moderate challenge. Consider learning the {high_value} high-frequency words first."
    elif pct >= 50:
        return f"Challenging content. Focus on the {high_value} most common new words to improve comprehension."
    else:
        return f"This content may be too advanced. Consider easier material or learn {high_value} essential words first."


def process_words_with_llm(words_details: List[WordInfo], text: str, progress_callback=None) -> List[WordInfo]:
    """
    Process a list of WordInfo through LLM to:
    - Filter out names and stop words
    - Get correct base forms
    - Get accurate translations

    Args:
        words_details: List of WordInfo from analyze_content
        text: Original text (for context in finding sentences)
        progress_callback: Optional callback(current, total, message) for progress updates

    Returns:
        Cleaned list of WordInfo with LLM-verified data
    """
    from src.llm import analyze_words_with_llm

    if not words_details:
        return []

    # Extract just the Spanish words
    words_to_analyze = [w.spanish for w in words_details]

    # Get LLM analysis
    print(f"Analyzing {len(words_to_analyze)} words with LLM...")
    llm_results = analyze_words_with_llm(words_to_analyze, progress_callback=progress_callback)

    # Build a map of LLM results using BOTH string matching and positional matching
    # This handles encoding corruption where accented characters may not match
    llm_map = {}
    for i, result in enumerate(llm_results):
        spanish = result.get('spanish', '').lower()
        llm_map[spanish] = result
        # Also store by position for fallback matching
        llm_map[f'_pos_{i}'] = result

    # Process and filter words
    cleaned_words = []
    sentences = extract_sentences(text)

    for i, word_info in enumerate(words_details):
        spanish_lower = word_info.spanish.lower()

        # Try to get LLM data by string match first
        llm_data = llm_map.get(spanish_lower)

        # If not found (possibly due to encoding issues), try positional match
        if not llm_data and i < len(llm_results):
            llm_data = llm_map.get(f'_pos_{i}', {})

        # If still no data, use empty dict
        if not llm_data:
            llm_data = {}

        # Skip if LLM says to skip (names, stop words, etc.)
        if llm_data.get('skip', False):
            reason = llm_data.get('reason', 'filtered by LLM')
            print(f"  Skipping '{word_info.spanish}': {reason}")
            continue

        # Get base form from LLM (or keep original)
        base_form = llm_data.get('base_form', word_info.spanish)
        if base_form:
            base_form = base_form.lower().strip()
        else:
            base_form = word_info.spanish

        # Get translation from LLM (or keep original from frequency data)
        translation = llm_data.get('english') or word_info.english

        # Get part of speech
        pos = llm_data.get('pos', 'unknown')

        # Find context sentences using original forms from the text
        # This ensures we find sentences with conjugated verbs even when storing infinitive
        context = []
        original_forms = word_info.original_forms if word_info.original_forms else [word_info.spanish]
        for form in original_forms:
            context.extend(find_word_context(form, sentences))
        # Also try the base form if no context found
        if not context:
            context = find_word_context(base_form, sentences)
        # Deduplicate and limit
        context = list(dict.fromkeys(context))[:3]

        # Look up frequency data for the base form
        freq_rank = get_frequency_rank(base_form)
        if freq_rank == 99999:
            freq_rank = word_info.frequency_rank

        cefr = estimate_cefr_level(base_form)
        if cefr == 'B1':  # Default/unknown
            cefr = word_info.cefr_level

        in_dele = is_in_dele_vocabulary(base_form, 'A2')
        if not in_dele:
            in_dele = word_info.in_dele_a2

        # Create cleaned WordInfo
        cleaned = WordInfo(
            spanish=base_form,
            english=translation,
            frequency_rank=freq_rank,
            cefr_level=cefr,
            frequency_tier=get_frequency_tier(base_form),
            in_dele_a2=in_dele,
            occurrences=word_info.occurrences,
            context_sentences=context,
            original_forms=original_forms  # Keep original forms for reference
        )
        cleaned_words.append(cleaned)

    # Remove duplicates (same base form)
    seen = set()
    unique_words = []
    for word in cleaned_words:
        if word.spanish not in seen:
            seen.add(word.spanish)
            unique_words.append(word)

    # Sort by frequency
    unique_words.sort(key=lambda w: w.frequency_rank)

    print(f"  Kept {len(unique_words)} words after LLM processing")
    return unique_words


# Export for convenience
__all__ = [
    'analyze_content',
    'analyze_for_dele',
    'ContentAnalysis',
    'WordInfo',
    'get_learned_vocabulary',
    'get_learning_vocabulary',
    'get_all_known_vocabulary',
    'get_comprehension_recommendation',
    'tokenize_spanish',
    'lemmatize_spanish',
    'process_words_with_llm',
]


if __name__ == "__main__":
    # Test the module
    test_text = """
    Hola, me llamo María. Trabajo en una oficina en Madrid.
    Todos los días me levanto temprano y tomo el metro para ir al trabajo.
    Mi jefe es muy simpático. Tenemos reuniones los lunes y viernes.
    Me gusta mucho mi trabajo porque aprendo cosas nuevas cada día.
    """

    print("Testing Content Analysis Module")
    print("=" * 50)
    print(f"\nTest text:\n{test_text}\n")

    result = analyze_content(test_text)

    print(f"Total words: {result.total_words}")
    print(f"Unique words: {result.unique_words}")
    print(f"Known words: {result.known_count}")
    print(f"Learning: {result.learning_count}")
    print(f"New words: {result.new_count}")
    print(f"Comprehension: {result.comprehension_pct:.1f}%")
    print(f"Difficulty: {result.difficulty_label}")
    print(f"Ready to consume: {result.is_ready_to_consume}")

    print(f"\nNew words to learn ({len(result.new_words_details)}):")
    for word in result.new_words_details[:10]:
        dele_marker = "⭐" if word.in_dele_a2 else ""
        print(f"  {word.spanish} ({word.english}) - {word.cefr_level}, rank {word.frequency_rank} {dele_marker}")

    print(f"\nRecommendation: {get_comprehension_recommendation(result)}")
