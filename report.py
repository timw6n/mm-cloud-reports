from google.appengine.ext import ndb
import difflib
import jinja2
import time

with open('resources/template.html') as template_file:
    TEMPLATE = jinja2.Template(template_file.read())

class Report(ndb.Model):
    contents = ndb.JsonProperty(compressed=True)

    def to_html(self):
        results = self.contents['results']
        formatted_time = time.strftime("%H:%M on %Y-%m-%d", time.gmtime(self.contents['timestamp']))
        ci_build = ('ci' in self.contents) and self.contents['ci']
        diffs = [_generate_diff(r['original'], r['mutant']) for r in results]
        return TEMPLATE.render(
            total_mutants=self.contents['total_mutants'],
            killed_mutants=self.contents['killed_mutants'],
            percentage_score=self.contents['percentage_score'],
            results=results,
            diffs=diffs,
            time=formatted_time,
            ci_passed=self.contents['ci']['passed'] if ci_build else None,
            ci_threshold=self.contents['ci']['threshold'] if ci_build else None
        )

def _generate_diff(a, b):
    return '\n'.join(list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=''))[2:])
