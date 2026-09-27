"""Export the curated comparison without losing uncertainty or source qualifiers."""
import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def tables(data):
    def refs(ids):
        return ' ; '.join(data['sources'][id]['url'] for id in dict.fromkeys(ids))
    matrix=[]
    for o in data['observations']:
        for h in data['hypotheses']:
            c=o['cells'][h['id']]
            matrix.append(dict(observation_id=o['id'],observation=o['observation'],family=o['family'],
                observation_kind=o['kind'],epoch=o['epoch'],uncertainty=o['uncertainty'],
                shared_inputs=' ; '.join(o['shared_inputs']),hypothesis=h['label'],status=c['status'],
                status_meaning=data['statuses'][c['status']]['meaning'],assessment=c['summary'],
                requirement=c['requirement'],next_test=c['next_test'],
                sources=refs(o['sources']+c['sources']),assessment_date=data['as_of']))
    events=[]
    for e in data['events']:
        events.append(dict(event_id=e['id'],event=e['label'],sample=e['sample'],event_type=e['event_type'],
            age_unit=data['age_unit'],**e['age'],method=e['method'],caveat=e['caveat'],
            sources=refs(e['sources']),assessment_date=data['as_of']))
    return {'matrix.csv':matrix,'events.csv':events}


def render(rows):
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue()


if __name__=='__main__':
    directory=ROOT/'research/comparison'
    for name,rows in tables(json.loads((directory/'evidence.json').read_text())).items():
        (directory/name).write_text(render(rows))
        print(f'{name}: {len(rows)} rows')
