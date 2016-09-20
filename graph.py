import collections


def calc_depths(commit_dict):
    to_visit = collections.deque(commit_dict.keys())
    while to_visit:
        csha = to_visit[-1]
        c = commit_dict[csha]
        if 'depth' in c:
            to_visit.pop()
            continue
        all_present = True
        parents = [commit_dict[psha] for psha in c['parents']]
        for p in parents:
            if 'depth' not in p:
                all_present = False
                to_visit.append(p['sha'])

        if all_present:
            c['depth'] = 1 + max(p['depth'] for p in parents) if parents else 0
            to_visit.pop()


def calc_children(commit_dict):
    for c in commit_dict.values():
        c['children'] = set()
    for csha, c in commit_dict.items():
        for psha in c['parents']:
            p = commit_dict[p]
            p['children'].add(csha)


def cd2graph(commit_dict):
	# Use numeric lookup
	TODO

def calc_sizes_cd(commit_dict):
	g = cd2graph(commit_dict)


def calc_sizes(g):
	TODO
