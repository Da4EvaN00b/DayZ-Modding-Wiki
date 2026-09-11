import json
from pathlib import Path
base=Path('graphify-out')
parts=[json.loads((base/name).read_text(encoding='utf-8-sig')) for name in ['.graphify_chunk_05_tutorial.json','.graphify_chunk_05_admin.json']]
nodes={}; edges=[]; hyperedges=[]
for part in parts:
    for n in part['nodes']:
        if n['id'] not in nodes:nodes[n['id']]=n
        else:
            old=nodes[n['id']]
            refs=old.setdefault('source_references',[{k:old.get(k) for k in ['source_file','source_location']}])
            ref={k:n.get(k) for k in ['source_file','source_location']}
            if ref not in refs:refs.append(ref)
            if n.get('rationale') and n.get('rationale') != old.get('rationale'):old['rationale']=' '.join(filter(None,[old.get('rationale'),n['rationale']]))
    edges.extend(part['edges']);hyperedges.extend(part.get('hyperedges',[]))
assert len(hyperedges)<=3
assert all(e['source'] in nodes and e['target'] in nodes for e in edges)
assert all(n in nodes for h in hyperedges for n in h['nodes'])
assert all(e['confidence_score']==1 for e in edges if e['confidence']=='EXTRACTED')
assert all(.6<=e['confidence_score']<=.9 for e in edges if e['confidence']=='INFERRED')
assert all(.1<=e['confidence_score']<=.3 for e in edges if e['confidence']=='AMBIGUOUS')
docs=[n for n in nodes.values() if n['file_type']=='document']
expected={Path(p).relative_to(Path.cwd()).as_posix() for p in json.loads((base/'.files_05.json').read_text())}
assert {n['source_file'] for n in docs}==expected
assert all(Path(n['source_file']).is_file() for n in nodes.values())
out=dict(nodes=list(nodes.values()),edges=edges,hyperedges=hyperedges,input_tokens=0,output_tokens=0)
(base/'.graphify_chunk_05.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(dict(nodes=len(nodes),edges=len(edges),hyperedges=len(hyperedges),documents=len(docs),ambiguous=sum(e['confidence']=='AMBIGUOUS' for e in edges))))
