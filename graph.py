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
            p = commit_dict[psha]
            p['children'].add(csha)


def calc_size(commit_dict, c):
    visited = set()
    to_visit = collections.deque([c['sha']])
    while to_visit:
        nsha = to_visit.pop()
        n = commit_dict[nsha]
        if nsha in visited:
            continue
        visited.add(nsha)
        to_visit.extend(n['parents'])
    return len(visited)


# find all newest commits older than ts (but not their parents)
def find_all_heads(commit_dict, ts):
    visited = set()
    heads = set()
    to_explore = collections.deque()
    for c in commit_dict.values():
        if c['ts'] > ts:
            continue
        if c['sha'] in visited:
            continue
        visited.add(c['sha'])
        heads.add(c['sha'])
        to_explore.extend(c['parents'])
        while to_explore:
            sha = to_explore.popleft()
            if sha in heads:
                heads.remove(sha)
            if sha in visited:
                continue
            visited.add(sha)
            to_explore.extend(commit_dict[sha]['parents'])
    return heads


def count_authors(commit_dict, ts):
    authors = collections.Counter()
    for c in commit_dict.values():
        if c['ts'] > ts:
            continue
        authors[c['author']] += 1
    return authors
