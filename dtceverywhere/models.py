import peewee as pw
import re

import sys as _sys
import os as _os

db_filename = _os.path.dirname(_os.path.abspath(__file__)) + "/dtceverywhere.db"
db = pw.SqliteDatabase(db_filename)

class Quote(pw.Model):
    text = pw.TextField()
    pk = pw.IntegerField(unique=True, index=True)
    votes_plus = pw.SmallIntegerField()
    votes_minus = pw.SmallIntegerField()
    
    class Meta:
        database = db
    
    def score(self):
        return self.votes_plus + self.votes_minus
    
    def has_positive_score(self):
        return self.score() > 0
    
    def count_lines(self):
        return len(self.text.splitlines())
    
    def parse(self):
        PATTERNS = (
            "^(<[^>]+>)( .*)$",
            "^([^:]+ ?:)( .*)$"
        )
        
        lines = []
        for line in self.text.splitlines():
            for pattern in PATTERNS:
                if re.match(pattern, line):
                    split = re.findall(pattern, line)[0]
                    lines.append((split[0], split[1] + '\n'))
                    break
            else:
                lines.append((line + '\n', ''))
        return lines
    
    def __str__(self):
        return "<Quote #{} ({}/{})>".format(
            self.pk, self.votes_plus, self.votes_minus
        )

def create_table():
    try:
        db.create_tables([Quote])
    except pw.OperationalError:
        print("*** Table already exists.")
    return

def flush_db():
    Quote.delete().execute()
    cursor = db.execute_sql("VACUUM;")
    return
