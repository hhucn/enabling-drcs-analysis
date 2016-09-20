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


def calc_sizes_dumb(commit_dict):
    for c in commit_dict.values():
        visited = set()
        to_visit = collections.deque([c['sha']])
        while to_visit:
            nsha = to_visit.pop()
            n = commit_dict[nsha]
            if nsha in visited:
                continue
            visited.add(nsha)
            to_visit.extend(n['parents'])
        c['size'] = len(visited)


calc_sizes = calc_sizes_dumb


# Implementation from http://stackoverflow.com/a/35831759/35070
def calc_sizes(commit_dict):
    # Use numeric lookup
    commit_list = list(commit_dict.values())
    sha2num = {c['sha']: i for i, c in enumerate(commit_list)}
    parents = [
        [sha2num[p] for p in c['parents']]
        for c in commit_list]
    children = [
        [sha2num[p] for p in c['children']]
        for c in commit_list]

    Vcount = len(commit_list)

    def countReachable(cnum):
        if ignored[cnum]:
            return 0
        visited = [False] * Vcount

        stack = collections.deque([cnum])
        count = 0
        while stack:
            nnum = stack.pop()
            if visited[nnum]:
                continue

            count += 1
            visited[nnum] = True
            for pnum in parents[nnum]:
                if not visited[pnum]:
                    stack.append(pnum)

        if count * 2 >= Vcount:
            return markAndCountAncestors(cnum, visited)
        else:
            return markSuccessors(visited)

    def markAndCountAncestors(root, visited):
        stack = [root]
        visited[root] = False

        count = 0
        while stack:
            nnum = stack.pop()
            if visited[nnum] or ignored[nnum]:
                continue

            count += 1
            visited[nnum] = True
            ignored[nnum] = True

            for cnum in children[nnum]:
                if not visited[cnum] and not ignored[cnum]:
                    stack.append(cnum)

        return count

    def markSuccessors(visited):
        for i in range(Vcount):
            if visited[i]:
                ignored[i] = True

        return 0

    ignored = [False] * Vcount
    for cnum, c in enumerate(commit_list):
        c['size'] = countReachable(cnum)
