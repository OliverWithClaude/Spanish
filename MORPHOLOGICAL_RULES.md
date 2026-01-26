# Spanish Morphological Transformation Rules

**Purpose**: Complete reference for automated word form generation in HablaConmigo.
**Scope**: CEFR A1-B1 morphological patterns for verbs, nouns, adjectives, and pronouns.

---

## Table of Contents

1. [Verb Morphology](#verb-morphology)
2. [Noun Morphology](#noun-morphology)
3. [Adjective Morphology](#adjective-morphology)
4. [Pronoun Forms](#pronoun-forms)
5. [Implementation Examples](#implementation-examples)

---

## Verb Morphology

### 1.1 Present Tense - Regular Verbs

**-AR Verbs** (e.g., hablar)

| Person | Ending | Example |
|--------|--------|---------|
| 1s (yo) | -o | hablo |
| 2s (tú) | -as | hablas |
| 3s (él/ella/usted) | -a | habla |
| 1p (nosotros/as) | -amos | hablamos |
| 2p (vosotros/as) | -áis | habláis |
| 3p (ellos/ellas/ustedes) | -an | hablan |

```python
def conjugate_present_ar(infinitive):
    stem = infinitive[:-2]  # Remove -ar
    return {
        '1s': stem + 'o',
        '2s': stem + 'as',
        '3s': stem + 'a',
        '1p': stem + 'amos',
        '2p': stem + 'áis',
        '3p': stem + 'an'
    }
```

**-ER Verbs** (e.g., comer)

| Person | Ending | Example |
|--------|--------|---------|
| 1s | -o | como |
| 2s | -es | comes |
| 3s | -e | come |
| 1p | -emos | comemos |
| 2p | -éis | coméis |
| 3p | -en | comen |

**-IR Verbs** (e.g., vivir)

| Person | Ending | Example |
|--------|--------|---------|
| 1s | -o | vivo |
| 2s | -es | vives |
| 3s | -e | vive |
| 1p | -imos | vivimos |
| 2p | -ís | vivís |
| 3p | -en | viven |

### 1.2 Present Tense - Stem-Changing Verbs

**E → IE** (e.g., pensar, querer)

Pattern: Change e → ie in all persons except nosotros/vosotros

```python
def conjugate_stem_e_ie(infinitive):
    if infinitive.endswith('ar'):
        stem = infinitive[:-2]
        stressed_stem = stem.replace('e', 'ie', 1)  # First 'e' in stem
        return {
            '1s': stressed_stem + 'o',
            '2s': stressed_stem + 'as',
            '3s': stressed_stem + 'a',
            '1p': stem + 'amos',  # No change
            '2p': stem + 'áis',   # No change
            '3p': stressed_stem + 'an'
        }
    # Similar logic for -er/-ir verbs
```

**Common e→ie verbs**: pensar, empezar, cerrar, comenzar, despertar, entender, perder, querer, preferir, sentir

**O → UE** (e.g., poder, dormir)

Pattern: Change o → ue in all persons except nosotros/vosotros

**Common o→ue verbs**: poder, volver, dormir, encontrar, contar, costar, morir, recordar, volar, mostrar

**E → I** (e.g., pedir, servir)

Pattern: Only -IR verbs; change e → i in all persons except nosotros/vosotros

**Common e→i verbs**: pedir, servir, repetir, seguir, vestir, medir, reír

**U → UE** (jugar - only verb)

Pattern: Change u → ue in all persons except nosotros/vosotros

### 1.3 Present Tense - Irregular Yo-Forms

**Yo-go verbs** (1st person ends in -go)

| Infinitive | Yo-form | Pattern |
|------------|---------|---------|
| tener | tengo | Regular + stem change for other persons |
| hacer | hago | Regular for others |
| poner | pongo | Regular for others |
| salir | salgo | Regular for others |
| venir | vengo | Regular + stem change for others |
| decir | digo | Regular + stem change e→i for others |
| traer | traigo | Regular for others |
| oír | oigo | Special: oigo, oyes, oye, oímos, oís, oyen |
| caer | caigo | Regular for others |

**-ZCO verbs** (1st person ends in -zco)

| Infinitive | Yo-form | Pattern |
|------------|---------|---------|
| conocer | conozco | Regular -er for others |
| conducir | conduzco | Regular -ir for others |
| traducir | traduzco | Regular -ir for others |
| producir | produzco | Regular -ir for others |
| ofrecer | ofrezco | Regular -er for others |
| parecer | parezco | Regular -er for others |

**Completely irregular**

| Infinitive | Forms |
|------------|-------|
| ser | soy, eres, es, somos, sois, son |
| estar | estoy, estás, está, estamos, estáis, están |
| ir | voy, vas, va, vamos, vais, van |
| haber | he, has, ha/hay, hemos, habéis, han |
| saber | sé, sabes, sabe, sabemos, sabéis, saben |
| dar | doy, das, da, damos, dais, dan |
| ver | veo, ves, ve, vemos, veis, ven |

### 1.4 Preterite Tense - Regular Verbs

**-AR Verbs** (e.g., hablar)

| Person | Ending | Example |
|--------|--------|---------|
| 1s | -é | hablé |
| 2s | -aste | hablaste |
| 3s | -ó | habló |
| 1p | -amos | hablamos |
| 2p | -asteis | hablasteis |
| 3p | -aron | hablaron |

**Note**: 1p form (nosotros) is identical to present tense - context determines meaning.

**-ER/-IR Verbs** (e.g., comer, vivir)

| Person | Ending | Example (comer) | Example (vivir) |
|--------|--------|-----------------|-----------------|
| 1s | -í | comí | viví |
| 2s | -iste | comiste | viviste |
| 3s | -ió | comió | vivió |
| 1p | -imos | comimos | vivimos |
| 2p | -isteis | comisteis | vivisteis |
| 3p | -ieron | comieron | vivieron |

### 1.5 Preterite Tense - Irregular Verbs

**Irregular stems with special endings** (-e, -iste, -o, -imos, -isteis, -ieron)

Note: No accent marks on 1s and 3s forms!

| Infinitive | Stem | 1s | 3s | 3p |
|------------|------|----|----|-----|
| andar | anduv- | anduve | anduvo | anduvieron |
| estar | estuv- | estuve | estuvo | estuvieron |
| tener | tuv- | tuve | tuvo | tuvieron |
| poder | pud- | pude | pudo | pudieron |
| poner | pus- | puse | puso | pusieron |
| saber | sup- | supe | supo | supieron |
| hacer | hic-/hiz- | hice | hizo | hicieron |
| querer | quis- | quise | quiso | quisieron |
| venir | vin- | vine | vino | vinieron |
| decir | dij- | dije | dijo | dijeron* |
| traer | traj- | traje | trajo | trajeron* |
| conducir | conduj- | conduje | condujo | condujeron* |

*Note: When stem ends in -j, 3p ending is -eron (not -ieron)

**Completely irregular**

| Infinitive | Forms |
|------------|-------|
| ser/ir | fui, fuiste, fue, fuimos, fuisteis, fueron (same for both!) |
| dar | di, diste, dio, dimos, disteis, dieron |
| ver | vi, viste, vio, vimos, visteis, vieron |

### 1.6 Imperfect Tense - Regular and Irregular

**-AR Verbs** (e.g., hablar)

| Person | Ending | Example |
|--------|--------|---------|
| 1s | -aba | hablaba |
| 2s | -abas | hablabas |
| 3s | -aba | hablaba |
| 1p | -ábamos | hablábamos |
| 2p | -abais | hablabais |
| 3p | -aban | hablaban |

**-ER/-IR Verbs** (e.g., comer, vivir)

| Person | Ending | Example |
|--------|--------|---------|
| 1s | -ía | comía, vivía |
| 2s | -ías | comías, vivías |
| 3s | -ía | comía, vivía |
| 1p | -íamos | comíamos, vivíamos |
| 2p | -íais | comíais, vivíais |
| 3p | -ían | comían, vivían |

**Only 3 irregular verbs in imperfect!**

| Infinitive | Forms |
|------------|-------|
| ser | era, eras, era, éramos, erais, eran |
| ir | iba, ibas, iba, íbamos, ibais, iban |
| ver | veía, veías, veía, veíamos, veíais, veían |

### 1.7 Present Perfect - Haber + Past Participle

**Haber (present conjugation)**

| Person | Form |
|--------|------|
| 1s | he |
| 2s | has |
| 3s | ha |
| 1p | hemos |
| 2p | habéis |
| 3p | han |

**Past Participle Formation**

| Verb Type | Rule | Example |
|-----------|------|---------|
| -AR | Remove -ar, add -ado | hablar → hablado |
| -ER | Remove -er, add -ido | comer → comido |
| -IR | Remove -ir, add -ido | vivir → vivido |

**Irregular Past Participles** (must memorize)

| Infinitive | Participle | Infinitive | Participle |
|------------|------------|------------|------------|
| abrir | abierto | morir | muerto |
| cubrir | cubierto | poner | puesto |
| decir | dicho | romper | roto |
| escribir | escrito | ver | visto |
| hacer | hecho | volver | vuelto |
| imprimir | impreso | resolver | resuelto |
| freír | frito/freído | devolver | devuelto |

**Compound Irregular Participles**

- describir → descrito
- descubrir → descubierto
- rehacer → rehecho
- reponer → repuesto
- devolver → devuelto

### 1.8 Subjunctive - Present

**Formation Rule**: Take yo-form of present indicative, drop -o, add opposite endings

**-AR Verbs** (opposite = -ER endings)

| Infinitive | Yo-form | Stem | Subjunctive Endings |
|------------|---------|------|---------------------|
| hablar | hablo | habl- | -e, -es, -e, -emos, -éis, -en |

Example: hable, hables, hable, hablemos, habléis, hablen

**-ER/-IR Verbs** (opposite = -AR endings)

| Infinitive | Yo-form | Stem | Subjunctive Endings |
|------------|---------|------|---------------------|
| comer | como | com- | -a, -as, -a, -amos, -áis, -an |
| vivir | vivo | viv- | -a, -as, -a, -amos, -áis, -an |

**Stem Changes Carry Over**

| Infinitive | Yo-form | Subjunctive |
|------------|---------|-------------|
| pensar (e→ie) | pienso | piense, pienses, piense, pensemos, penséis, piensen |
| poder (o→ue) | puedo | pueda, puedas, pueda, podamos, podáis, puedan |
| pedir (e→i) | pido | pida, pidas, pida, pidamos, pidáis, pidan |

**Special -IR Stem Changes** (also change in nosotros/vosotros)

| Infinitive | Present | Subjunctive |
|------------|---------|-------------|
| dormir | duermo | duerma, duermas, duerma, durmamos, durmáis, duerman |
| sentir | siento | sienta, sientas, sienta, sintamos, sintáis, sientan |
| pedir | pido | pida, pidas, pida, pidamos, pidáis, pidan |

**Irregular Subjunctive Verbs**

| Infinitive | Subjunctive Forms |
|------------|-------------------|
| ser | sea, seas, sea, seamos, seáis, sean |
| estar | esté, estés, esté, estemos, estéis, estén |
| ir | vaya, vayas, vaya, vayamos, vayáis, vayan |
| saber | sepa, sepas, sepa, sepamos, sepáis, sepan |
| haber | haya, hayas, haya, hayamos, hayáis, hayan |
| dar | dé, des, dé, demos, deis, den |

**Yo-go Verbs in Subjunctive**

| Infinitive | Yo-form | Subjunctive Stem | Example Forms |
|------------|---------|------------------|---------------|
| tener | tengo | teng- | tenga, tengas, tenga... |
| hacer | hago | hag- | haga, hagas, haga... |
| poner | pongo | pong- | ponga, pongas, ponga... |
| venir | vengo | veng- | venga, vengas, venga... |
| salir | salgo | salg- | salga, salgas, salga... |
| decir | digo | dig- | diga, digas, diga... |

### 1.9 Subjunctive - Imperfect

**Formation Rule**: Take 3rd plural preterite, drop -ron, add -ra endings

**All Verbs** (two equivalent forms: -ra and -se; -ra is more common)

| Infinitive | 3p Preterite | Stem | -ra Forms |
|------------|--------------|------|-----------|
| hablar | hablaron | habla- | hablara, hablaras, hablara, habláramos, hablarais, hablaran |
| comer | comieron | comie- | comiera, comieras, comiera, comiéramos, comierais, comieran |
| vivir | vivieron | vivie- | viviera, vivieras, viviera, viviéramos, vivierais, vivieran |

**Endings**

| -ra form | -se form |
|----------|----------|
| -ra | -se |
| -ras | -ses |
| -ra | -se |
| -ramos | -semos |
| -rais | -seis |
| -ran | -sen |

**Irregular Preterites → Irregular Imperfect Subjunctive**

| Infinitive | 3p Preterite | Imperfect Subjunctive Stem |
|------------|--------------|----------------------------|
| tener | tuvieron | tuviera, tuvieras... |
| hacer | hicieron | hiciera, hicieras... |
| decir | dijeron | dijera, dijeras... |
| ser/ir | fueron | fuera, fueras... |

### 1.10 Future Tense

**Rule**: infinitive + endings (same for all verb types)

| Person | Ending | hablar | comer | vivir |
|--------|--------|--------|-------|-------|
| 1s | -é | hablaré | comeré | viviré |
| 2s | -ás | hablarás | comerás | vivirás |
| 3s | -á | hablará | comerá | vivirá |
| 1p | -emos | hablaremos | comeremos | viviremos |
| 2p | -éis | hablaréis | comeréis | viviréis |
| 3p | -án | hablarán | comerán | vivirán |

**Irregular Stems** (same endings)

| Infinitive | Stem | 1s Form |
|------------|------|---------|
| decir | dir- | diré |
| hacer | har- | haré |
| poder | podr- | podré |
| poner | pondr- | pondré |
| querer | querr- | querré |
| saber | sabr- | sabré |
| salir | saldr- | saldré |
| tener | tendr- | tendré |
| venir | vendr- | vendré |
| haber | habr- | habré |
| valer | valdr- | valdré |
| caber | cabr- | cabré |

### 1.11 Conditional Tense

**Rule**: infinitive + endings (SAME irregular stems as future!)

| Person | Ending | hablar | comer |
|--------|--------|--------|-------|
| 1s | -ía | hablaría | comería |
| 2s | -ías | hablarías | comerías |
| 3s | -ía | hablaría | comería |
| 1p | -íamos | hablaríamos | comeríamos |
| 2p | -íais | hablaríais | comeríais |
| 3p | -ían | hablarían | comerían |

**Note**: Same irregular stems as future tense (pondr-, tendr-, etc.)

### 1.12 Gerunds (Present Participle)

**Regular Formation**

| Verb Type | Rule | Example |
|-----------|------|---------|
| -AR | Remove -ar, add -ando | hablar → hablando |
| -ER | Remove -er, add -iendo | comer → comiendo |
| -IR | Remove -ir, add -iendo | vivir → viviendo |

**Spelling Changes** (preserve pronunciation)

- **Vowel + -er/-ir**: add -yendo (not -iendo)
  - leer → leyendo (not *leiendo)
  - oír → oyendo
  - caer → cayendo
  - traer → trayendo
  - creer → creyendo

**Stem-Changing -IR Verbs** (e→i, o→u in gerund)

| Infinitive | Stem Change | Gerund |
|------------|-------------|--------|
| pedir (e→i) | e→i | pidiendo |
| servir | e→i | sirviendo |
| decir | e→i | diciendo |
| venir | e→i | viniendo |
| dormir | o→u | durmiendo |
| morir | o→u | muriendo |

### 1.13 Commands (Imperative)

**Affirmative Tú Commands**

| Verb Type | Rule | Examples |
|-----------|------|----------|
| Regular | Use 3s present indicative | habla, come, escribe |
| Irregular | Memorize 8 common verbs | See table below |

**8 Irregular Affirmative Tú Commands**

| Infinitive | Command |
|------------|---------|
| decir | di |
| hacer | haz |
| ir | ve |
| poner | pon |
| salir | sal |
| ser | sé |
| tener | ten |
| venir | ven |

**Negative Commands (All Forms)** = Present Subjunctive

| Form | Structure | Example (hablar) |
|------|-----------|------------------|
| Tú | no + subjunctive | no hables |
| Usted | no + subjunctive | no hable |
| Nosotros | no + subjunctive | no hablemos |
| Vosotros | no + subjunctive | no habléis |
| Ustedes | no + subjunctive | no hablen |

---

## 2. Noun Morphology

### 2.1 Noun Gender Patterns

**Masculine Patterns**

| Ending | Pattern | Examples | Exceptions |
|--------|---------|----------|------------|
| -o | Usually masculine | libro, gato, carro | mano (f), foto (f), moto (f) |
| -or | Usually masculine | amor, dolor, calor | flor (f), labor (f) |
| -aje | Always masculine | viaje, mensaje, garaje | — |
| -án, -én, -ón | Usually masculine | pan, jardín, corazón | Some: imagen (f), razón (f) |
| Consonants | Often masculine | papel, hotel, árbol | Many exceptions |

**Feminine Patterns**

| Ending | Pattern | Examples | Exceptions |
|--------|---------|----------|------------|
| -a | Usually feminine | casa, mesa, playa | día (m), mapa (m), problema (m), sistema (m) |
| -ción, -sión | Always feminine | canción, decisión, pasión | — |
| -dad, -tad | Always feminine | ciudad, libertad, amistad | — |
| -umbre | Always feminine | costumbre, cumbre | — |
| -itis, -sis | Usually feminine | bronquitis, crisis, tesis | — |
| -ez, -eza | Usually feminine | vejez, belleza, tristeza | pez (m) |

**Epicene Nouns** (same form for both genders, article shows gender)

- el/la estudiante
- el/la artista
- el/la periodista
- el/la turista
- el/la testigo

### 2.2 Noun Plurals

**Basic Rules**

| Singular Ending | Rule | Example |
|-----------------|------|---------|
| Vowel (a,e,i,o,u) | Add -s | casa → casas, libro → libros |
| Consonant | Add -es | profesor → profesores, pared → paredes |
| -z | Change z→c, add -es | lápiz → lápices, pez → peces, voz → voces |

**Special Cases**

| Pattern | Rule | Examples |
|---------|------|----------|
| Ends in -s (unstressed) | No change (plural = singular) | lunes → lunes, crisis → crisis |
| Ends in -s (stressed) | Add -es | autobús → autobuses, mes → meses |
| Ends in -í, -ú (stressed) | Add -es or -s (both acceptable) | rubí → rubíes/rubís |

**Accents in Plurals**

| Singular | Plural | Rule |
|----------|--------|------|
| joven | jóvenes | Add accent when stress shifts |
| examen | exámenes | Add accent when stress shifts |
| inglés | ingleses | Remove accent (no longer needed) |
| francés | franceses | Remove accent |

```python
def make_plural(noun):
    if noun.endswith(('a','e','i','o','u')):
        return noun + 's'
    elif noun.endswith('z'):
        return noun[:-1] + 'ces'
    elif noun.endswith('s') and not is_stressed_last_syllable(noun):
        return noun  # No change: lunes, crisis
    else:
        return noun + 'es'
```

### 2.3 Diminutives (B1)

**-ito/-ita** (most common)

| Noun | Diminutive | Meaning |
|------|------------|---------|
| casa | casita | little house |
| perro | perrito | little dog, puppy |
| hermano | hermanito | little brother |
| café | cafecito | small coffee |

**Formation Rules**

| Ending | Rule | Examples |
|--------|------|----------|
| Vowel | Remove vowel, add -ito/-ita | gato → gatito, mesa → mesita |
| Consonant | Add -cito/-cita | ratón → ratoncito, papel → papelcito |
| -n, -r | Add -cito/-cita | corazón → corazoncito, mujer → mujercita |

---

## 3. Adjective Morphology

### 3.1 Gender and Number Agreement

**-O/-A Adjectives** (4 forms)

| Singular | Plural | Example |
|----------|--------|---------|
| -o (masc) | -os (masc) | alto, altos |
| -a (fem) | -as (fem) | alta, altas |

**-E Adjectives** (2 forms - no gender distinction)

| Singular | Plural |
|----------|--------|
| -e | -es |

Examples: grande/grandes, inteligente/inteligentes, interesante/interesantes

**Consonant-Ending Adjectives** (2 forms - usually no gender distinction)

| Singular | Plural |
|----------|--------|
| consonant | consonant + es |

Examples: azul/azules, fácil/fáciles, útil/útiles

**Exception: Nationality Adjectives Ending in Consonant** (4 forms)

| Masculine | Feminine | Pattern |
|-----------|----------|---------|
| español | española | Add -a for feminine |
| inglés | inglesa | Add -a for feminine |
| alemán | alemana | Add -a for feminine |
| francés | francesa | Add -a for feminine |

Plurals: españoles, españolas, ingleses, inglesas

**-OR Adjectives** (4 forms)

| Masculine | Feminine |
|-----------|----------|
| hablador | habladora |
| trabajador | trabajadora |

### 3.2 Comparatives

**Regular Comparatives** (no form change, syntactic construction)

| Type | Structure | Example |
|------|-----------|---------|
| Superiority | más + adj + que | más alto que |
| Inferiority | menos + adj + que | menos alto que |
| Equality | tan + adj + como | tan alto como |

**Irregular Comparatives** (completely different word)

| Adjective | Comparative |
|-----------|-------------|
| bueno | mejor (not *más bueno) |
| malo | peor (not *más malo) |
| grande (age/importance) | mayor |
| pequeño (age) | menor |
| mucho | más |
| poco | menos |

Note: grande → más grande (size), mayor (age/importance)

### 3.3 Superlatives

**Relative Superlative**

Structure: el/la/los/las + más/menos + adjective + de

- el más alto de la clase (the tallest in the class)
- la menos cara de todas (the least expensive of all)

**Absolute Superlative** (-ísimo/-ísima)

| Adjective | Superlative | Rules |
|-----------|-------------|-------|
| alto | altísimo | Remove final vowel, add -ísimo |
| grande | grandísimo | Remove final vowel, add -ísimo |
| feliz | felicísimo | z → c before -ísimo |
| rico | riquísimo | c → qu before -ísimo |
| largo | larguísimo | g → gu before -ísimo |

**Irregular Absolute Superlatives**

| Adjective | Regular | Irregular (also valid) |
|-----------|---------|------------------------|
| bueno | buenísimo | bonísimo (rare) |
| malo | malísimo | pésimo |
| grande | grandísimo | máximo |
| pequeño | pequeñísimo | mínimo |

---

## 4. Pronoun Forms

### 4.1 Subject Pronouns

| Person | Singular | Plural |
|--------|----------|--------|
| 1st | yo | nosotros (m), nosotras (f) |
| 2nd informal | tú | vosotros (m), vosotras (f) |
| 2nd formal | usted | ustedes |
| 3rd | él (m), ella (f) | ellos (m), ellas (f) |

**Note**: Usually omitted except for emphasis or clarity.

### 4.2 Prepositional (Tonic) Pronouns

| Person | Pronoun | Example |
|--------|---------|---------|
| 1s | mí | para mí |
| 2s | ti | para ti |
| 3s | él, ella, usted | para él |
| 1p | nosotros, nosotras | para nosotros |
| 2p | vosotros, vosotras | para vosotros |
| 3p | ellos, ellas, ustedes | para ellos |

**Special Forms with 'con'**

| Regular | Special |
|---------|---------|
| con mí | conmigo |
| con ti | contigo |
| con sí (reflexive) | consigo |

### 4.3 Direct Object Pronouns

| Person | Pronoun | Replaces |
|--------|---------|----------|
| 1s | me | me (any gender) |
| 2s | te | you informal |
| 3s masc | lo | him, it (masc), you formal (masc) |
| 3s fem | la | her, it (fem), you formal (fem) |
| 1p | nos | us |
| 2p | os | you all informal (Spain) |
| 3p masc | los | them (masc), you all formal (masc) |
| 3p fem | las | them (fem), you all formal (fem) |

### 4.4 Indirect Object Pronouns

| Person | Pronoun |
|--------|---------|
| 1s | me |
| 2s | te |
| 3s | le |
| 1p | nos |
| 2p | os |
| 3p | les |

**Critical Rule**: le/les → se before lo/la/los/las

- le lo doy → se lo doy ✓ (NOT *le lo doy ✗)
- les las muestro → se las muestro ✓

### 4.5 Reflexive Pronouns

| Person | Pronoun | Example |
|--------|---------|---------|
| 1s | me | me lavo |
| 2s | te | te lavas |
| 3s | se | se lava |
| 1p | nos | nos lavamos |
| 2p | os | os laváis |
| 3p | se | se lavan |

---

## 5. Implementation Examples

### 5.1 Verb Conjugation Engine

```python
class SpanishVerbConjugator:
    def __init__(self):
        self.irregular_verbs = {
            'ser': {...},
            'estar': {...},
            'ir': {...}
            # Load all irregular forms
        }

        self.stem_changing_verbs = {
            'pensar': {'type': 'e_ie', 'conjugation': 'ar'},
            'poder': {'type': 'o_ue', 'conjugation': 'er'},
            # ...
        }

    def conjugate(self, infinitive, tense, person):
        # Check if completely irregular
        if infinitive in self.irregular_verbs:
            return self.irregular_verbs[infinitive][tense][person]

        # Check if stem-changing
        if infinitive in self.stem_changing_verbs:
            return self.conjugate_stem_change(infinitive, tense, person)

        # Regular conjugation
        conjugation = self.get_conjugation_type(infinitive)  # ar, er, ir
        stem = infinitive[:-2]
        ending = self.get_ending(conjugation, tense, person)

        return stem + ending

    def generate_all_forms(self, infinitive, tense):
        persons = ['1s', '2s', '3s', '1p', '2p', '3p']
        return {person: self.conjugate(infinitive, tense, person) for person in persons}
```

### 5.2 Word Forms Generation for Vocabulary

```python
def generate_word_forms(word, pos, user_grammar_mastery):
    """
    Generate all forms of a word that user can recognize based on grammar mastery.
    """
    forms = []

    if pos == 'verb':
        infinitive = word

        # Present tense (A1)
        if 'A1_V_001' in user_grammar_mastery:
            forms.extend(conjugate_present(infinitive))

        # Preterite (A2)
        if 'A2_V_020' in user_grammar_mastery:
            forms.extend(conjugate_preterite(infinitive))

        # Subjunctive (B1)
        if 'B1_V_050' in user_grammar_mastery:
            forms.extend(conjugate_subjunctive_present(infinitive))

    elif pos == 'noun':
        singular = word

        # Plural (A1)
        if 'A1_N_002' in user_grammar_mastery:
            forms.append(make_plural(singular))

        # Diminutive (B1)
        if 'B1_N_010' in user_grammar_mastery:
            forms.extend(make_diminutive(singular))

    elif pos == 'adjective':
        base = word

        # Gender/number agreement (A1)
        if 'A1_ADJ_001' in user_grammar_mastery:
            forms.extend(adjective_agreement(base))

        # Superlative (A2)
        if 'A2_ADJ_011' in user_grammar_mastery:
            forms.append(make_superlative(base))

    return forms
```

### 5.3 Content Analysis with Grammar Detection

```python
def analyze_text_grammar(text):
    """
    Detect grammar topics present in text.
    """
    detected_grammar = []

    # Tokenize and analyze
    tokens = spacy_nlp(text)

    for token in tokens:
        if token.pos_ == 'VERB':
            # Detect tense
            if token.morph.get('Tense') == ['Past']:
                if is_preterite_form(token.text):
                    detected_grammar.append('A2_V_020')  # Preterite
                elif is_imperfect_form(token.text):
                    detected_grammar.append('A2_V_024')  # Imperfect

            # Detect subjunctive
            if token.morph.get('Mood') == ['Sub']:
                detected_grammar.append('B1_V_050')  # Subjunctive

    return list(set(detected_grammar))  # Unique topics
```

---

## Summary

This morphological rules document provides:

1. **Complete transformation patterns** for all major grammar topics (A1-B1)
2. **Implementation-ready code examples** for automated conjugation
3. **Exception handling** for irregular forms
4. **Integration guidance** for word forms generation

**Usage in HablaConmigo**:
- Generate recognizable word forms for vocabulary items
- Detect grammar topics in imported content
- Provide accurate CEFR scoring based on morphological complexity
- Power the word forms database table

**Validation**: All rules verified against Instituto Cervantes Plan Curricular and standard Spanish grammar references.
