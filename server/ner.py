import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.util import filter_spans
from pprint import pprint
from intent import *
import datetime, dateparser
import pdb

if not spacy.util.is_package("en_core_web_lg"):
    spacy.cli.download("en_core_web_lg")
NLP = spacy.load("en_core_web_lg")
PATTERN = [{'POS': 'VERB', 'OP': '?'},
           {'POS': 'ADV', 'OP': '*'},
           {'POS': 'AUX', 'OP': '*'},
           {'POS': 'VERB', 'OP': '+'}]
MATCHER = Matcher(NLP.vocab)
MATCHER.add("Verb Phrase", [PATTERN])
LABELS = [
    "study",
    "shopping",
    "laundry",
    "workout",
    "travel",
    "booking",
    "apply",
    "pay"
]
DURATION_CACHE = {}
LOCATION_CACHE = {}

# example = "Go shopping for 2 hours at Giant Eagle on Wednesday."

class Task(object):
    def __init__(self, text, task_str, duration, location, start_time=None, deadline=None, status="incomplete"):
        self.text = text
        self.task_str = task_str
        self.duration = duration
        self.location = location
        self.start_time = start_time
        self.deadline = deadline
        self.status = status
        if start_time is not None:
            self.start_time = dateparser.parse(start_time)
        if deadline is not None:
            self.deadline = dateparser.parse(deadline)
        if duration is not None:
            t1 = dateparser.parse(duration)
            t2 = datetime.datetime.now()
            if (t1 - t2).days < 0:
                # t1 later than t2
                seconds = (t2-t1).seconds
            else:
                seconds = (t1-t2).seconds
            self.duration = str(datetime.timedelta(seconds=seconds))
            # self.duration = float(seconds) / 3600

    def __str__(self):
        s = ''
        s += f"[{self.task_str}] at [{'NA' if self.location is None else self.location}] for "
        s += f"[{self.duration}] from "
        s += f"[{'NA' if self.start_time is None else self.start_time}] before "
        s += f"[{'NA' if self.deadline is None else self.deadline}]"
        return s

def extract_entity(text):
    doc = NLP(text)
    time = [ent for ent in doc.ents if ent.label_ == "TIME"]
    duration, location, start_time, deadline = None, None, None, None
    matches = MATCHER(doc)
    cand_spans = [doc[start:end] for _, start, end in matches]
    # task_str = get_intent(text, [s.text for s in filter_spans(cand_spans) if not any([t.is_stop for t in s])])
    task_str = get_intent(text, LABELS)
    if len(time) == 0:
        # request for time duration
        duration = request_keyword("duration", ["TIME"])
    else:
        for t in time:
            idx = doc.text.split().index(t.text.split()[0])
            if idx >= 1:
                if doc[idx-1].text in ["at", "on", "from", "in"]:
                    # start time
                    start_time = t.text
                elif doc[idx-1].text == "for":
                    # duration
                    duration = t.text
                else:
                    # deadline
                    deadline = t.text
    loc = [ent for ent in doc.ents if ent.label_ in ["GPE", "ORG"]]
    if len(loc) == 0:
        # request for location
        location = request_keyword("location", ["GPE", "ORG"])
    else:
        location = ', '.join([l.text for l in loc])
    # special keywords that requires specification
    if set(task_str.split()).intersection(set(["exam", "bill", "submit", "complete", "apply", "close", "open", "start"])):
        # request for deadline
        deadline = request_keyword("deadline", ["TIME"])
    task = Task(
        text=text, task_str=task_str, duration=duration, location=location,
        start_time=start_time, deadline=deadline
    )
    return task

def parse_task(text):
    doc = NLP(text)
    time = [ent for ent in doc.ents if ent.label_ == "TIME"]
    duration, location, start_time, deadline = None, None, None, None
    matches = MATCHER(doc)
    cand_spans = [doc[start:end] for _, start, end in matches]
    # task_str = get_intent(text, [s.text for s in filter_spans(cand_spans) if not any([t.is_stop for t in s])])
    task_str = get_intent(text, LABELS)
    missing_info = []
    has_duration = False
    
    for t in time:
        idx = doc.text.split().index(t.text.split()[0])
        if idx >= 1:
            if doc[idx-1].text in ["at", "on", "from", "in"]:
                # start time
                start_time = t.text
            elif doc[idx-1].text == "for":
                # duration
                has_duration = True
                duration = t.text
                DURATION_CACHE[task_str] = duration
            else:
                # deadline
                deadline = t.text

    if has_duration == False:
        if task_str in DURATION_CACHE:
            duration = DURATION_CACHE[task_str]
        else:
            # request for time duration
            print("[INFO] Missing duration.")
            missing_info.append("duration")

    loc = [ent for ent in doc.ents if ent.label_ in ["GPE", "ORG"]]
    if len(loc) == 0:
        if task_str in LOCATION_CACHE:
            location = LOCATION_CACHE[task_str]
        else:
            # request for location
            print("[INFO] Missing location.")
            missing_info.append("location")
    else:
        location = ', '.join([l.text for l in loc])
        LOCATION_CACHE[task_str] = location
    # special keywords that requires specification
    if set(task_str.split()).intersection(set(["exam", "bill", "submit", "complete", "apply", "close", "open", "start"])):
        # request for deadline
        print("[INFO] Missing deadline")
        missing_info.append("deadline")
    task = Task(
        text=text, task_str=task_str, duration=duration, location=location,
        start_time=start_time, deadline=deadline, status="complete" if len(missing_info) == 0 else "incomplete"
    )
    print("[INFO] OK.")
    return task, missing_info

def add_info(task_dict, info):
    missing_info = []
    key2label = {
        "duration": ["TIME"],
        "location": ["GPE", "ORG"],
        "deadline": ["TIME"]
    }
    for k,v in info.items():
        ans = NLP(v)
        loc = [ent.text for ent in ans.ents if ent.label_ in key2label[k]]
        if len(loc) > 0:
            task_dict[k] = ', '.join(loc)
        else:
            task_dict[k] = ans.text
    for k in key2label.keys():
        if k not in task_dict:
            missing_info.append(k)
            task_dict[k] = None
    if len(missing_info) == 0:
        task_dict["status"] = "complete"
    task = Task(**task_dict)
    return task, missing_info

def request_keyword(keyword, labels):
    ans = NLP(input(f"What is the {keyword}? "))
    loc = [ent.text for ent in ans.ents if ent.label_ in labels]
    if len(loc) > 0:
        return ', '.join(loc)
    else:
        return ans


if __name__ == "__main__":
    while True:
        text = input("> ")
        if text in ["quit", 'q']:
            break
        task = extract_entity(text)
        pprint(task.__dict__)


