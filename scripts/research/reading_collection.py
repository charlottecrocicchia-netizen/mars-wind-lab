"""One editorial index for the five dossiers and their preserved source notes."""
from html import escape

COLLECTION_DATE = '28 September 2026'
DOSSIERS = {
    'science': ('Scientific context', 'What the interior, rocks and measurements can tell us.', {
        'SYNTHESIS': 'Origins of the dichotomy',
        'HYPOTHESES': 'The working archive hypothesis',
        'DICHOTOMY_REVIEW': 'Earlier review of origin scenarios',
        'COMPARISON': 'Comparison and chronology',
        'DICHOTOMY_PHYSICS': 'Composition, amplification and deformation',
        'PALEOMAGNETISM_FOUNDATIONS': 'Paleomagnetism foundations',
        'METEORITES': 'Meteorites and rock magnetism',
        'RECORDING': 'Primary and secondary remanence',
        'WATER': 'Water and alteration',
        'MISSIONS': 'Missions and public archives',
    }),
    'literature': ('Literature method', 'Trace a claim to its source and to what was actually read.', {
        'METHOD': 'Search and reading method',
        'COMMUNITY': 'Community leads and source checks',
        'README': 'Research guide and current reading routes',
        'RESEARCH_PLAN': 'Earlier research programme',
    }),
    'experiments': ('Earlier experiments', 'The controls and exploratory studies behind the six tests.', {
        'EXECUTED_EXPERIMENTS': 'Recording, transfer and laboratory controls',
        'DYNAMO_TESTS': 'Earlier dynamo proposals and source assessment',
        'THERMAL_EXPERIMENT': 'Thermal history experiment',
        'PILOT_STUDY': 'Regional pilot study',
        'FIRST_RESULTS': 'First dataset diagnostics',
        'TEST_PROTOCOL': 'First physical test protocol',
    }),
    'interdisciplinary': ('Interdisciplinary review', 'Connect observations without confusing their clocks or scales.', {
        'INTERDISCIPLINARY_SYNTHESIS': 'Mars as one evolving system',
        'INTERDISCIPLINARY_CHRONOLOGY': 'What each clock dates',
        'INTERDISCIPLINARY_MAGNETISM': 'Paleomagnetism across disciplines',
        'INTERDISCIPLINARY_TESTS': 'Earlier joint-test proposals',
        'INTERDISCIPLINARY_SOURCES': 'Annotated sources and reading depth',
    }),
    'audit': ('Audit and current evidence', 'Follow the corrections, remaining limits and current report.', {
        'DISCRIMINATING_TESTS': 'Current six-test technical report',
        'DISCRIMINATING_AUDIT': 'Implementation audit and follow-up',
        'ARABIA_PREFLIGHT': 'Arabia Terra: geometry and support preflight',
        'BOUNDARY_WALK': 'Boundary transects and the 23 northern cells',
        'DEPTH_AGE': 'Source depth against surface age',
        'RAPID_BODIES': 'Rapidly cooled bodies under a reversing dynamo',
        'REVERSAL_IDENTIFIABILITY': 'Reversal histories and acquisition clocks',
        'STATE_OF_EVIDENCE': 'Where the evidence stands',
        'DENSITY_REMANENCE': 'Density and remanence in one material model',
    }),
}
PAGES = {stem: label for _, _, notes in DOSSIERS.values() for stem, label in notes.items()}
CURRENT_NOTES = {'README', 'DISCRIMINATING_TESTS', 'DISCRIMINATING_AUDIT', 'ARABIA_PREFLIGHT', 'BOUNDARY_WALK', 'DEPTH_AGE', 'DENSITY_REMANENCE', 'RAPID_BODIES', 'REVERSAL_IDENTIFIABILITY', 'STATE_OF_EVIDENCE'}


def dossier_for(stem):
    return next(key for key, (_, _, notes) in DOSSIERS.items() if stem in notes)


def dossier_navigation(active=''):
    return ''.join(f'<a href="/research/dossiers/{key}"'+
                   (' aria-current="page"' if key == active else '')+
                   f'>{escape(title)}</a>' for key, (title, _, _) in DOSSIERS.items())


def note_context(stem):
    key = dossier_for(stem)
    status = ('Current technical reference' if stem in CURRENT_NOTES else
              'Archive collection · ' + COLLECTION_DATE)
    return f'<div class="collection-context"><p>{status}</p><a href="/research/dossiers/{key}">← {escape(DOSSIERS[key][0])}</a><span> · </span><a href="/research/tests">Current results →</a></div>'
