import os
from flask import Flask, render_template, request


class MorhAnalyzer:
    def analyze(self, word):
        form = '"' + word.lower() + '"'
        analysis = os.popen(f'echo {form} | hfst-lookup ruu-analyzer.hfst').read()

        variants = []
        for v in analysis.split('\n')[:-2]:
            splitted = v.split('\t')
            if v == '' or splitted[2] == 'inf':
                continue
            row = splitted[1]
            deep_search = os.popen(f'echo "{row}" | hfst-lookup ruu-deepgenerator.hfst').read()
            for s in deep_search.split('\n')[:-2]:
                if s == '':
                    continue
                query = s.split('\t')[1]
                outputs = [line.split('\t')[1] if line != '' else None for line in
                           os.popen(f'echo "{query}" | hfst-lookup ruu.twol.hfst').read().split('\n')[:-2]]
                if word in outputs:
                    an = row.strip('><').split('><')
                    if 'cop' in an:
                        pos = 'cop'
                    else:
                        pos = {'n', 'v', 'adj', 'adv', 'pro', 'dem', 'intj', 'part', 'prep', 'conj', 'ideo'}.intersection(set(an)).pop()
                        an.remove(pos)
                    variants.append((('-'.join(an), pos), query.replace('>', '-')))

        if len(variants) == 0:
            return [(('', 'NA'), 'Not found')]

        return variants


m = MorhAnalyzer()
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['get'])
def results():
    input_string = request.args.get("wordform")
    search_result = m.analyze(input_string)
    return render_template("results.html", results=search_result, wordform=input_string.lower())

if __name__ == '__main__':
    app.run(debug=False)
