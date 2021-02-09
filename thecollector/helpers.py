from thecollector import relative, db
from thecollector.models import Data
from time import strftime, gmtime
import json


def data_len():
    return len(Data.query.all())


def data_dump(form="squad"):
    fname = "data_" + strftime("%y%m%d-%H%M%S", gmtime()) + ".json"
    fpath = relative("static/data/" + fname)
    if form == "squad":
        data = data_jsonify_squad()
    else:
        data = data_jsonify()
    with open(fpath, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def data_jsonify():
    val = []
    for title in [i[0] for i in db.session.query(Data.title).distinct().all()]:
        data = Data.query.filter_by(title=title).all()
        context = data[0].__dict__["context"]
        pairs = [i.to_dict(rules=("-context", "-title")) for i in data]
        val.append(
            {
                "title": title,
                "context": context,
                "pairs": pairs,
            }
        )
    return val


def data_jsonify_squad():
    val = []
    for title in [i[0] for i in db.session.query(Data.title).distinct().all()]:
        data = Data.query.filter_by(title=title).all()
        context = data[0].__dict__["context"]
        pairs = [i.to_dict(rules=("-context", "-title")) for i in data]
        # Empty answers if impossible instead of null
        for i in pairs:
            if i["is_impossible"]:
                i["answers"] = []
        val.append(
            {
                "title": title,
                "paragraphs": [
                    {
                        "qas": pairs,
                        "context": context,
                    }
                ]
            }
        )
    return {"data": val}


# read_squad_v2 function
def data_test_custom(path):
    path = relative(path)
    ds = []
    with open(path, encoding="utf-8") as f:
        squad = json.load(f)
        for example in squad["data"]:
            title = example.get("title", "").strip()
            for paragraph in example["paragraphs"]:
                context = paragraph["context"].strip()
                for qa in paragraph["qas"]:
                    question = qa["question"].strip()
                    id_ = qa["id"]
                    answer_starts = [answer["answer_start"] for answer in qa["answers"]]
                    answers = [answer["text"].strip() for answer in qa["answers"]]
                    ds.append(
                        {
                            "title": title,
                            "context": context,
                            "question": question,
                            "id": id_,
                            "answers": {"answer_start": answer_starts, "text": answers},
                        }
                    )
    return ds
