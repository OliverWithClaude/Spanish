# Spanish Grammar Dependency Graph

This document visualizes the prerequisite relationships between Spanish grammar topics for CEFR levels A1-B1, showing the natural progression and dependencies for optimal learning.

---

## Overview

```mermaid
graph TD
    A1[A1 Foundation] --> A2[A2 Expansion]
    A2 --> B1[B1 Complex Structures]

    style A1 fill:#90EE90
    style A2 fill:#FFD700
    style B1 fill:#FFA07A
```

**Learning Path Summary**:
- **A1**: Present tense mastery, basic noun/adjective agreement, fundamental pronouns
- **A2**: Past tenses (preterite/imperfect), object pronouns, commands
- **B1**: Subjunctive mood, future/conditional, complex subordination

---

## A1 Level: Foundation (Entry Points)

### Parallel Entry Points (No Prerequisites)

These topics can be learned simultaneously as they don't depend on each other:

```mermaid
graph LR
    ENTRY[Start A1]
    ENTRY --> V001[Regular -ar Verbs]
    ENTRY --> V002[Regular -er Verbs]
    ENTRY --> V003[Regular -ir Verbs]
    ENTRY --> V010[Irregular: ser]
    ENTRY --> V011[Irregular: estar]
    ENTRY --> V012[Irregular: ir]
    ENTRY --> V013[Irregular: tener]
    ENTRY --> V014[Irregular: hacer]
    ENTRY --> N001[Noun Gender]
    ENTRY --> PRO001[Subject Pronouns]

    style ENTRY fill:#FFE4E1
    style V001 fill:#90EE90
    style V002 fill:#90EE90
    style V003 fill:#90EE90
    style V010 fill:#FFB6C1
    style V011 fill:#FFB6C1
    style V012 fill:#FFB6C1
    style V013 fill:#FFB6C1
    style V014 fill:#FFB6C1
```

**Legend**:
- Green: Regular patterns (easier)
- Pink: Irregular verbs (harder but high-frequency)

---

## A1 Verbal System Dependencies

### Present Tense Progression

```mermaid
graph TD
    V001[Regular -ar: hablar] --> V004[Stem e→ie: pensar]
    V002[Regular -er: comer] --> V004
    V003[Regular -ir: vivir] --> V004

    V001 --> V005[Stem o→ue: poder]
    V002 --> V005
    V003 --> V005

    V003 --> V006[Stem e→i: pedir]

    V004 --> STEM[All Stem Changes Mastered]
    V005 --> STEM
    V006 --> STEM

    style V001 fill:#90EE90
    style V002 fill:#90EE90
    style V003 fill:#90EE90
    style V004 fill:#FFD700
    style V005 fill:#FFD700
    style V006 fill:#FFD700
    style STEM fill:#87CEEB
```

**Rationale**: Stem-changing verbs require understanding of regular conjugation patterns first. Learners must recognize the base pattern before understanding stem changes.

### Progressive and Periphrastic Constructions

```mermaid
graph TD
    V011[estar present] --> V007[Present Progressive<br/>estar + gerund]

    V012[ir present] --> V008[Near Future<br/>ir a + infinitive]

    V013[tener present] --> I005[Obligation<br/>tener que + inf]

    style V011 fill:#FFB6C1
    style V012 fill:#FFB6C1
    style V013 fill:#FFB6C1
    style V007 fill:#87CEEB
    style V008 fill:#87CEEB
    style I005 fill:#87CEEB
```

**Rationale**: Periphrastic constructions depend on mastering the auxiliary verb first.

---

## A1 Nominal System Dependencies

### Noun-Adjective-Article Agreement Chain

```mermaid
graph TD
    N001[Noun Gender<br/>Recognition] --> N002[Noun Plurals]
    N001 --> ART001[Definite Articles<br/>el, la, los, las]
    N001 --> ADJ001[Adjective Gender<br/>Agreement]

    N002 --> ART002[Indefinite Articles<br/>un, una, unos, unas]
    N002 --> ADJ002[Adjective Number<br/>Agreement]

    N001 --> ADJ001
    ADJ001 --> ADJ002

    ART001 --> ARTICLES[Article Mastery]
    ART002 --> ARTICLES

    ADJ001 --> ADJECTIVES[Adjective Agreement<br/>Mastery]
    ADJ002 --> ADJECTIVES

    style N001 fill:#FFE4E1
    style N002 fill:#90EE90
    style ART001 fill:#FFD700
    style ART002 fill:#90EE90
    style ADJ001 fill:#FFD700
    style ADJ002 fill:#90EE90
    style ARTICLES fill:#87CEEB
    style ADJECTIVES fill:#87CEEB
```

**Rationale**:
- Gender must be learned before number (singular forms establish gender patterns)
- Articles and adjectives both depend on recognizing noun gender
- Number agreement builds on gender agreement

**Research Note**: Definite articles are acquired late despite early introduction (Natural Order Hypothesis)

---

## A1 Pronominal System Dependencies

```mermaid
graph TD
    PRO001[Subject Pronouns<br/>yo, tú, él...] --> PRO002[Prepositional Pronouns<br/>mí, ti, él...]

    PRO001 --> A2_PRO[A2 Object Pronouns]

    style PRO001 fill:#90EE90
    style PRO002 fill:#FFD700
    style A2_PRO fill:#FFA07A
```

**Rationale**: Subject pronouns are foundational for all other pronoun systems.

---

## A1 Idiomatic Constructions

### Ser vs Estar

```mermaid
graph TD
    V010[ser conjugation] --> I001[Ser vs Estar<br/>Basic Distinctions]
    V011[estar conjugation] --> I001

    I001 --> A2_I010[A2: Ser vs Estar<br/>Advanced Contexts]

    style V010 fill:#FFB6C1
    style V011 fill:#FFB6C1
    style I001 fill:#FF6347
    style A2_I010 fill:#FFA07A
```

**Difficulty Note**: Ser vs estar is conceptually difficult for English speakers. Requires extensive contextualized practice across both A1 and A2 levels.

---

## A1 → A2 Transition Requirements

### Gating Topics (Must Master to Progress)

```mermaid
graph TD
    A1_GATE[A1 Completion Gates] --> PRESENT[All Present Tense<br/>Patterns Mastered]
    A1_GATE --> AGREEMENT[Noun-Adjective<br/>Agreement Solid]
    A1_GATE --> BASICS[Basic Pronouns &<br/>Articles Known]

    PRESENT --> A2_START[Begin A2]
    AGREEMENT --> A2_START
    BASICS --> A2_START

    A2_START --> PAST[Past Tenses<br/>Preterite & Imperfect]

    style A1_GATE fill:#FFE4E1
    style PRESENT fill:#90EE90
    style AGREEMENT fill:#90EE90
    style BASICS fill:#90EE90
    style A2_START fill:#FFD700
    style PAST fill:#FFA07A
```

**Rationale**: Present tense forms the conceptual and morphological foundation for all other tenses. Cannot understand past tense without present tense mastery.

---

## A2 Level: Expansion

### Past Tense Dependencies

```mermaid
graph TD
    V001[A1: Regular -ar] --> V020[Preterite Regular<br/>-ar verbs]
    V002[A1: Regular -er] --> V020
    V003[A1: Regular -ir] --> V020

    V001 --> V024[Imperfect Regular<br/>-ar verbs]
    V002 --> V024
    V003 --> V024

    V020 --> V023[Preterite Irregular]
    V024 --> V025[Imperfect Irregular<br/>only 3 verbs!]

    V020 --> V027[Preterite vs<br/>Imperfect Usage]
    V024 --> V027

    style V020 fill:#FFD700
    style V024 fill:#90EE90
    style V023 fill:#FF6347
    style V025 fill:#90EE90
    style V027 fill:#FFA07A
```

**Teaching Note**:
- Some educators prefer teaching imperfect before preterite (easier conjugation)
- Instituto Cervantes and most textbooks teach preterite first
- Both approaches valid; our system supports either order

### Compound Past Tenses

```mermaid
graph TD
    V013[A1: tener present] --> V040[Present Perfect<br/>haber + participle]

    V040 --> PARTICIPLES[Master Irregular<br/>Participles]

    V024[Imperfect tense] --> V063[B1: Pluperfect<br/>había + participle]
    V040 --> V063

    style V040 fill:#FFD700
    style PARTICIPLES fill:#87CEEB
    style V063 fill:#FFA07A
```

**Morphological Note**: Present perfect introduces past participle formation, which is reused in all perfect tenses.

---

## A2 Object Pronouns System

### Sequential Introduction

```mermaid
graph TD
    PRO001[A1: Subject Pronouns] --> PRO010[Direct Object<br/>Pronouns]

    PRO001 --> PRO011[Indirect Object<br/>Pronouns]

    PRO010 --> PRO012[Double Object<br/>Pronouns]
    PRO011 --> PRO012

    PRO012 --> PLACEMENT[Pronoun Placement<br/>with Commands]

    style PRO001 fill:#90EE90
    style PRO010 fill:#FFD700
    style PRO011 fill:#FFD700
    style PRO012 fill:#FF6347
    style PLACEMENT fill:#FFA07A
```

**Difficulty Progression**:
- Direct object pronouns (medium difficulty)
- Indirect object pronouns (medium difficulty)
- Double pronouns (hard - requires both systems + le→se transformation)

---

## A2 Commands (Imperative)

```mermaid
graph TD
    V001[A1: Present -ar] --> V050[Affirmative tú<br/>Commands]
    V002[A1: Present -er] --> V050
    V003[A1: Present -ir] --> V050

    V050 --> V051[Irregular Commands<br/>8 common verbs]

    V051 --> PRONOUNS[Commands with<br/>Object Pronouns]

    V050 --> B1_V080[B1: Negative Commands<br/>uses subjunctive!]

    style V050 fill:#FFD700
    style V051 fill:#FF6347
    style PRONOUNS fill:#FFA07A
    style B1_V080 fill:#FFA07A
```

**Critical Connection**: Negative commands require subjunctive mood (B1 topic), creating a dependency bridge from A2 to B1.

---

## A2 Comparison System

```mermaid
graph TD
    ADJ001[A1: Adjective Agreement] --> ADJ010[Comparatives<br/>más/menos/tan + que]

    ADJ010 --> ADJ011[Superlatives<br/>Relative & Absolute]

    ADJ010 --> IRREGULAR[Irregular Comparatives<br/>mejor, peor, mayor, menor]

    style ADJ001 fill:#90EE90
    style ADJ010 fill:#FFD700
    style ADJ011 fill:#FFD700
    style IRREGULAR fill:#FF6347
```

---

## A2 → B1 Transition Requirements

### Gating Topics (Must Master to Progress)

```mermaid
graph TD
    A2_GATE[A2 Completion Gates] --> PAST[Past Tenses Mastered<br/>Preterite + Imperfect]
    A2_GATE --> PRONOUNS[Object Pronouns<br/>Direct + Indirect]
    A2_GATE --> PRESENT[Solid Present Tense<br/>Including Irregulars]

    PAST --> B1_START[Begin B1]
    PRONOUNS --> B1_START
    PRESENT --> B1_START

    B1_START --> SUBJUNCTIVE[Subjunctive Mood<br/>MAJOR LEAP]

    style A2_GATE fill:#FFE4E1
    style PAST fill:#FFD700
    style PRONOUNS fill:#FFD700
    style PRESENT fill:#90EE90
    style B1_START fill:#FFA07A
    style SUBJUNCTIVE fill:#FF6347
```

**Critical Requirement**: Present tense mastery is essential for subjunctive formation (uses yo-form stem).

---

## B1 Level: Complex Structures

### Subjunctive System (The B1 Bottleneck)

```mermaid
graph TD
    V001[A1: Present Tense<br/>ALL forms] --> V050[Present Subjunctive<br/>Formation Rule]

    V050 --> V051[Subjunctive<br/>Stem Changes]
    V050 --> V052[Subjunctive<br/>Spelling Changes]
    V050 --> V053[Subjunctive<br/>Irregular Verbs]

    V051 --> TRIGGERS[Subjunctive Triggers<br/>WEIRDO verbs]
    V052 --> TRIGGERS
    V053 --> TRIGGERS

    TRIGGERS --> V054[Subjunctive in<br/>Noun Clauses]
    TRIGGERS --> V055[Subjunctive in<br/>Adverbial Clauses]
    TRIGGERS --> V056[Subjunctive in<br/>Adjective Clauses]

    V023[A2: Preterite] --> V060[Imperfect Subjunctive<br/>Formation]
    V050 --> V060

    V060 --> V061[Past Subjunctive<br/>Contexts]

    style V001 fill:#90EE90
    style V050 fill:#FF6347
    style V051 fill:#FF6347
    style V052 fill:#FF6347
    style V053 fill:#FF6347
    style TRIGGERS fill:#FFA07A
    style V054 fill:#FFA07A
    style V055 fill:#FFA07A
    style V056 fill:#FFA07A
    style V060 fill:#FF6347
    style V061 fill:#FFA07A
```

**Subjunctive Formation Dependencies**:
1. **Present subjunctive**: Requires mastery of yo-form in present indicative
2. **Imperfect subjunctive**: Requires 3rd plural preterite stem
3. **Conceptual prerequisite**: Understanding indicative vs subjunctive mood distinction
4. **Syntactic prerequisite**: Complex syntax knowledge (subordination)

**Research Finding**: "Some syntactic knowledge is a prerequisite for the processing, and so development of, verbal morphology" (subjunctive acquisition studies)

### Subjunctive Granularity (Kwiziq Approach)

Rather than teaching "subjunctive" as monolithic topic, break into contexts:

```mermaid
graph TD
    V050[Present Subjunctive<br/>Formation] --> DESIRE[WEIRDO: Desire<br/>querer que]
    V050 --> EMOTION[WEIRDO: Emotion<br/>me alegra que]
    V050 --> DOUBT[WEIRDO: Doubt<br/>dudo que]
    V050 --> IMPERSONAL[Impersonal Expressions<br/>es importante que]
    V050 --> TEMPORAL[Temporal Clauses<br/>cuando future]
    V050 --> UNKNOWN[Unknown Antecedent<br/>busco una casa que]

    style V050 fill:#FF6347
    style DESIRE fill:#FFA07A
    style EMOTION fill:#FFA07A
    style DOUBT fill:#FFA07A
    style IMPERSONAL fill:#FFA07A
    style TEMPORAL fill:#FFA07A
    style UNKNOWN fill:#FFA07A
```

**Pedagogical Benefit**: Learners master one trigger context at a time, reducing cognitive load.

---

## B1 Future and Conditional

```mermaid
graph TD
    BASE[Any Level] --> V070[Simple Future<br/>infinitive + endings]

    V070 --> V071[Conditional<br/>same stems, different endings]

    V070 --> IRREGULAR[Future Irregular Stems<br/>10 common verbs]
    IRREGULAR --> V071

    V071 --> POLITE[Polite Requests<br/>querría, podría]
    V071 --> HYPO[Hypotheticals<br/>si clauses]

    style V070 fill:#FFD700
    style V071 fill:#FFD700
    style IRREGULAR fill:#FF6347
    style POLITE fill:#87CEEB
    style HYPO fill:#FFA07A
```

**Note**: Future and conditional don't require other tense prerequisites (formed from infinitive). Can be taught earlier than B1 in some approaches.

**Shared Irregularity**: Future and conditional use identical irregular stems (pondr-, tendr-, etc.), making them efficient to teach together.

---

## B1 Perfect Tenses

```mermaid
graph TD
    V040[A2: Present Perfect] --> V063[Pluperfect<br/>había + participle]

    V063 --> NARRATIVE[Past Perfect in<br/>Narrative Context]

    V050[Present Subjunctive] --> V064[Present Perfect<br/>Subjunctive]

    V060[Imperfect Subjunctive] --> V065[Pluperfect<br/>Subjunctive]

    style V040 fill:#FFD700
    style V063 fill:#FFA07A
    style NARRATIVE fill:#87CEEB
    style V064 fill:#FF6347
    style V065 fill:#FF6347
```

**Efficiency**: Once participle formation is mastered (A2), all perfect tenses follow same pattern with different auxiliary conjugations.

---

## B1 Commands (All Forms)

```mermaid
graph TD
    V050[Present Subjunctive] --> V080[Negative Commands<br/>ALL forms]

    V051[A2: Affirmative tú] --> V080

    V080 --> USTED[Usted/ustedes Commands<br/>use subjunctive]

    V080 --> NOSOTROS[Nosotros Commands<br/>let's... form]

    PRO012[A2: Double Pronouns] --> V081[Commands with<br/>Pronouns All Forms]

    V080 --> V081

    style V050 fill:#FF6347
    style V051 fill:#FFD700
    style V080 fill:#FFA07A
    style USTED fill:#FFA07A
    style NOSOTROS fill:#FFA07A
    style V081 fill:#FFA07A
```

**Critical Connection**: Subjunctive mastery unlocks negative commands and formal commands (usted/ustedes forms).

---

## B1 Complex Syntax Dependencies

### Subordination System

```mermaid
graph TD
    BASIC[A2: Basic Sentence<br/>Structure] --> SYN010[Relative Clauses<br/>que, quien, donde]

    SYN010 --> IND_REL[Relative + Indicative<br/>known antecedent]
    V050[Present Subjunctive] --> SUBJ_REL[Relative + Subjunctive<br/>unknown antecedent]

    BASIC --> SYN015[Temporal Clauses<br/>cuando, mientras]
    V050 --> SYN015

    BASIC --> SYN020[Conditional Clauses<br/>si + indicative]
    V060[Imperfect Subjunctive] --> SYN021[Conditional Contrary<br/>si + imperfect subj]

    SYN015 --> MOOD[Mood Selection<br/>Indicative vs Subjunctive]
    SYN010 --> MOOD

    style BASIC fill:#FFD700
    style SYN010 fill:#FFA07A
    style SYN015 fill:#FFA07A
    style SYN020 fill:#FFA07A
    style V050 fill:#FF6347
    style V060 fill:#FF6347
    style MOOD fill:#FF6347
```

**Mood Selection Rule**:
- **Indicative**: Known, factual, habitual
- **Subjunctive**: Unknown, future, hypothetical, subjective

---

## B1 Passive Voice

```mermaid
graph TD
    BASIC[A2: Sentence Structure] --> SYN030[Passive se<br/>se vende]

    SYN030 --> AGREEMENT[Se Agreement<br/>with Subject]

    V063[Pluperfect] --> SYN031[Passive ser + participle<br/>fue vendido]

    style BASIC fill:#FFD700
    style SYN030 fill:#FFA07A
    style AGREEMENT fill:#87CEEB
    style SYN031 fill:#FFA07A
```

---

## Complete Dependency Map: A1 → A2 → B1

### High-Level Progression

```mermaid
graph TD
    START[Begin Spanish] --> A1_PRESENT[A1: Present Tense<br/>Regular + Irregular]
    START --> A1_NOUNS[A1: Noun-Adjective<br/>Agreement]

    A1_PRESENT --> A1_PROG[A1: Progressive<br/>& Periphrastic]
    A1_NOUNS --> A1_ARTICLES[A1: Articles &<br/>Basic Pronouns]

    A1_PRESENT --> A2_PAST[A2: Past Tenses<br/>Preterite & Imperfect]
    A1_PRESENT --> A2_PERFECT[A2: Present Perfect]

    A1_ARTICLES --> A2_OBJECT[A2: Object Pronouns<br/>Direct & Indirect]

    A2_PAST --> A2_USAGE[A2: Preterite vs<br/>Imperfect Usage]

    A1_PRESENT --> A2_COMMANDS[A2: Commands<br/>Affirmative tú]

    A2_PAST --> B1_PLUPERFECT[B1: Pluperfect]
    A2_PERFECT --> B1_PLUPERFECT

    A1_PRESENT --> B1_SUBJUNCTIVE[B1: Subjunctive<br/>BOTTLENECK]
    A2_PAST --> B1_SUBJUNCTIVE

    B1_SUBJUNCTIVE --> B1_COMPLEX[B1: Complex Syntax<br/>Subordination]
    B1_SUBJUNCTIVE --> B1_COMMANDS_NEG[B1: Negative Commands]

    A1_PRESENT --> B1_FUTURE[B1: Future &<br/>Conditional]

    style START fill:#FFE4E1
    style A1_PRESENT fill:#90EE90
    style A1_NOUNS fill:#90EE90
    style A2_PAST fill:#FFD700
    style A2_OBJECT fill:#FFD700
    style B1_SUBJUNCTIVE fill:#FF6347
    style B1_COMPLEX fill:#FFA07A
```

---

## Bottleneck Topics (High Dependency)

These topics unlock many subsequent topics:

### 1. Present Tense (All Forms) - A1
**Unlocks**:
- All stem-changing verbs (A1)
- Progressive tenses (A1)
- Present subjunctive (B1) ← Major unlock
- Near future (A1)

### 2. Preterite Tense - A2
**Unlocks**:
- Preterite vs imperfect usage (A2)
- Imperfect subjunctive formation (B1)
- Narrative skills (B1)

### 3. Present Subjunctive - B1
**Unlocks**:
- All subordinate clauses with subjunctive (B1)
- Negative commands (B1)
- Formal commands (B1)
- Impersonal expressions (B1)
- Advanced temporal clauses (B1)

### 4. Noun Gender - A1
**Unlocks**:
- Noun plurals (A1)
- Definite articles (A1)
- Indefinite articles (A1)
- Adjective gender agreement (A1)
- Adjective number agreement (A1)

### 5. Subject Pronouns - A1
**Unlocks**:
- Prepositional pronouns (A1)
- Direct object pronouns (A2)
- Indirect object pronouns (A2)
- Double object pronouns (A2)

---

## Learning Path Recommendations

### Sequential Path (Traditional)

```
A1.1: Regular present tense (-ar, -er, -ir) + high-frequency irregulars (ser, estar, ir, tener, hacer)
      Noun gender + plurals + definite articles
      Subject pronouns

A1.2: Stem-changing verbs (e→ie, o→ue, e→i)
      Present progressive (estar + gerund)
      Near future (ir a + infinitive)
      Adjective agreement
      Ser vs estar (basic contexts)

A2.1: Preterite regular and irregular
      Imperfect regular and irregular
      Direct object pronouns
      Indirect object pronouns
      Comparatives

A2.2: Present perfect
      Preterite vs imperfect usage
      Double object pronouns
      Affirmative tú commands
      Superlatives

B1.1: Present subjunctive (formation + common triggers)
      Simple future
      Conditional
      Relative clauses
      Real conditional clauses (si + indicative)

B1.2: Imperfect subjunctive
      Subjunctive in all contexts (noun, adjective, adverbial clauses)
      Pluperfect
      Negative commands
      Passive voice
      Complex subordination
```

### Parallel Path (Modern Approach)

Allow multiple grammar topics to be studied simultaneously when they don't depend on each other:

**Tracks that can run in parallel**:
- **Verbal track**: Present → Past → Future → Subjunctive
- **Nominal track**: Nouns → Articles → Adjectives
- **Pronominal track**: Subject → Object → Reflexive
- **Syntactic track**: Simple sentences → Coordination → Subordination

### Communicative Path (Task-Based)

Introduce grammar as needed for communicative tasks:
- **Introducing yourself**: ser present + subject pronouns + noun gender
- **Describing location**: estar present + prepositions + demonstratives
- **Talking about habits**: present tense + frequency adverbs
- **Narrating past events**: preterite + imperfect + temporal markers
- **Expressing desires**: present subjunctive + querer que
- **Making plans**: future tense / ir a + infinitive

---

## Implementation Notes for HablaConmigo

### Database Representation

```sql
-- Store dependencies
CREATE TABLE grammar_dependencies (
    topic_id TEXT NOT NULL,
    prerequisite_id TEXT NOT NULL,
    dependency_type TEXT CHECK(dependency_type IN ('required', 'recommended', 'related')),
    PRIMARY KEY (topic_id, prerequisite_id)
);

-- Example entries:
INSERT INTO grammar_dependencies VALUES
    ('A1_V_004', 'A1_V_001', 'required'),  -- Stem changes require regular -ar
    ('A1_V_004', 'A1_V_002', 'required'),  -- Stem changes require regular -er
    ('B1_V_050', 'A1_V_001', 'required'),  -- Subjunctive requires present tense
    ('B1_V_080', 'B1_V_050', 'required'),  -- Negative commands require subjunctive
    ('A2_V_027', 'A2_V_020', 'recommended'), -- Usage requires both tenses
    ('A2_V_027', 'A2_V_024', 'recommended');
```

### Unlock Algorithm

```python
def get_unlockable_topics(user_id):
    """Return topics where all required prerequisites are mastered."""
    mastered = get_mastered_grammar(user_id)
    all_topics = get_all_topics_for_target_level(user_id)

    unlockable = []
    for topic in all_topics:
        if topic in mastered:
            continue  # Already mastered

        prereqs = get_prerequisites(topic, type='required')

        if all(prereq in mastered for prereq in prereqs):
            unlockable.append(topic)

    return unlockable


def get_next_recommended_topic(user_id):
    """Suggest best next topic considering multiple factors."""
    unlockable = get_unlockable_topics(user_id)

    # Score each unlockable topic
    scored = []
    for topic in unlockable:
        score = 0

        # Factor 1: Natural acquisition order (from research)
        score += get_acquisition_order_score(topic)

        # Factor 2: Frequency in content (how often it appears)
        score += get_frequency_score(topic)

        # Factor 3: Unlocking power (how many topics depend on this)
        enables = get_enabled_topics(topic)
        score += len(enables) * 10

        # Factor 4: Difficulty (prefer easier when equal utility)
        difficulty = get_difficulty(topic)
        score -= {'easy': 0, 'medium': 5, 'hard': 10}[difficulty]

        scored.append((topic, score))

    # Return highest scoring
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0] if scored else None
```

### User Interface: Dependency Visualization

Show dependency graph like Kwiziq brain map:
- **Locked topics** (gray): Prerequisites not met
- **Unlocked topics** (yellow): Ready to learn
- **Learning topics** (orange): Currently practicing
- **Mastered topics** (green): Achieved proficiency

---

## Summary

This dependency graph provides:

1. **Clear prerequisites**: Know exactly what to learn before each topic
2. **Multiple valid paths**: Sequential, parallel, or communicative approaches
3. **Bottleneck identification**: Focus on high-leverage topics (present tense, subjunctive)
4. **Research-validated**: Based on Natural Order Hypothesis and Processability Theory
5. **Implementation-ready**: SQL schema and algorithms provided

**Key Insight**: The subjunctive mood at B1 is the major conceptual leap in Spanish grammar, requiring both formational prerequisites (present tense mastery) and conceptual prerequisites (understanding mood distinctions and complex syntax).

---

**Next Steps**:
1. Implement dependency tracking in database
2. Build unlock algorithm
3. Create visual dependency browser in UI
4. Validate with pilot users
5. Adjust based on learner outcomes
