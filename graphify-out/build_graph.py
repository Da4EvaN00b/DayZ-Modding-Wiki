import json
import re
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html
from graphify.cache import save_semantic_cache

OUT = Path('graphify-out')
def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))
def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def merge():
    nodes, edges, hyperedges = {}, [], []
    aliases = {'dayz_addonbuilder': 'dayz_addon_builder'}
    for i in range(1, 6):
        data = read(f'.graphify_chunk_{i:02}.json')
        assert isinstance(data['nodes'], list) and isinstance(data['edges'], list)
        for record in data['nodes'] + data['edges'] + data.get('hyperedges', []):
            path = Path(record['source_file'])
            record['source_file'] = path.relative_to(Path.cwd()).as_posix() if path.is_absolute() else path.as_posix()
        for node in data['nodes']:
            node['id'] = aliases.get(node['id'], node['id'])
            if node['id'] == 'dayz_servermod':
                node['label'] = '-serverMod launch option'
        for edge in data['edges']:
            for endpoint in ('source', 'target'):
                edge[endpoint] = aliases.get(edge[endpoint], edge[endpoint])
        for hyperedge in data.get('hyperedges', []):
            hyperedge['nodes'] = list(dict.fromkeys(aliases.get(n, n) for n in hyperedge['nodes']))
        for node in data['nodes']:
            nid = node['id']
            evidence = {'source_file': node['source_file'], 'source_location': node.get('source_location')}
            if nid not in nodes:
                nodes[nid] = dict(node, sources=[])
            if evidence not in nodes[nid]['sources']:
                nodes[nid]['sources'].append(evidence)
            for additional in node.get('sources', []) + node.get('source_references', []):
                if additional not in nodes[nid]['sources']:
                    nodes[nid]['sources'].append(additional)
        for edge in data['edges']:
            assert edge['confidence'] in ('EXTRACTED', 'INFERRED', 'AMBIGUOUS')
            assert 0 <= edge['confidence_score'] <= 1
            assert edge['confidence'] != 'EXTRACTED' or edge['confidence_score'] == 1
            edges.append(edge)
        hyperedges.extend(data.get('hyperedges', []))
        save_semantic_cache(data['nodes'], data['edges'], data.get('hyperedges', []))
    assert all(e['source'] in nodes and e['target'] in nodes for e in edges), 'Dangling edge'
    expected = {Path(f).resolve() for f in read('.graphify_detect.json')['files']['document']}
    covered = {Path(s['source_file']).resolve() for n in nodes.values() for s in n['sources']}
    assert expected <= covered, f'Missing documents: {expected-covered}'
    result = dict(nodes=list(nodes.values()), edges=edges, hyperedges=hyperedges,
                  input_tokens=0, output_tokens=0, token_usage_status='unavailable: agent tools do not expose usage')
    write('extraction.json', result)
    print(f'Validated all {len(expected)} documents; {len(nodes)} nodes, {len(edges)} evidence records')

def graph():
    extraction = read('extraction.json')
    G = build_from_json(extraction)
    assert G.number_of_nodes() > 0
    # Preserve every source relation even when Graphify collapses a pair of nodes.
    for edge in extraction['edges']:
        G[edge['source']][edge['target']].setdefault('evidence', []).append(edge)
    G.graph['token_usage_status'] = extraction['token_usage_status']
    G.graph['corpus'] = 'en/'
    return G

def analyze():
    G = graph()
    communities = cluster(G)
    data = dict(communities=communities, cohesion=score_all(G, communities),
                gods=god_nodes(G), surprises=surprising_connections(G, communities))
    write('.graphify_analysis.json', data)
    for cid, members in communities.items():
        top = sorted(members, key=lambda n: G.degree(n), reverse=True)[:12]
        print(cid, len(members), ':', ', '.join(G.nodes[n]['label'] for n in top))

def export():
    G = graph()
    a = read('.graphify_analysis.json')
    communities = {int(k): v for k,v in a['communities'].items()}
    cohesion = {int(k): v for k,v in a['cohesion'].items()}
    labels = {int(k): v for k,v in read('.graphify_labels.json').items()}
    questions = suggest_questions(G, communities, labels)
    report = generate(G, communities, cohesion, labels, a['gods'], a['surprises'],
                      read('.graphify_detect.json'), {'input':0,'output':0},
                      str(Path('en').resolve()), suggested_questions=questions)
    report = report.replace('- Token cost: 0 input · 0 output',
                            '- Token cost: unavailable; agent tools do not expose token usage. This does not mean zero cost.')
    report = re.sub(r'## Community Hubs \(Navigation\).*?(?=\n## )', '', report, flags=re.S)
    report += '\n\n---\n\n## Audit Notes\n\n- Scope: all 105 English documents; semantic extraction summarizes major concepts, not every statement.\n- Shared entities retain all source locations in `sources`.\n- Graphify uses an undirected graph for navigation. Each edge retains original directions and relation evidence in `evidence`; `extraction.json` preserves all extracted records.\n- Suggested connections and benchmark figures describe the extracted graph, not independent verification of DayZ behavior.\n'
    ambiguous = [e for e in read('extraction.json')['edges'] if e['confidence'] == 'AMBIGUOUS']
    if ambiguous:
        report += '\n### Source Claims Requiring Review\n\n'
        for edge in ambiguous:
            detail = edge.get('description') or edge.get('rationale') or edge.get('note') or edge['relation']
            report += f"- `{edge['source_file']}` ({edge.get('source_location', 'unspecified location')}): {detail}\n"
    (OUT/'GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    to_json(G, communities, str(OUT/'graph.json'))
    if len(G) <= 5000:
        to_html(G, communities, str(OUT/'graph.html'), community_labels=labels)
    print(f'Graph: {len(G)} nodes, {G.number_of_edges()} edges, {len(communities)} communities')

if __name__ == '__main__':
    import sys
    for command in sys.argv[1:]:
        {'merge':merge, 'analyze':analyze, 'export':export}[command]()
