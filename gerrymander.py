from collections import deque
import random

class BacktrackingGerrymander:
    TARGET_SIZE = 9   # Target size is the number of voters wanted per district

    def backtrack(self, electorate, party):
        graph = electorate.graph                    #adjacent structure
        voters = electorate.number_of_voters()      #total number of voters
        d = electorate.district_size()              #N/TARGET_size

        def is_connected(group):  # Checks connectivity of a set
            start = next(iter(group))  #iterates through group takes one node from it
            visited = {start}           # tracks nodes visited
            queue = deque([start])      # the nodes to explore next
            while queue:                #Best First Search
                u = queue.popleft()     #take node out of queue
                for w in graph.neighbors(u):#looks at adjacent node
                    if w in group and w not in visited: #only looks at the edges of nodes that are not visited and inside the district(w group)
                        visited.add(w)
                        queue.append(w) #add valid neighbors to visited and queue to then check its neighbors
            return len(visited) == len(group)  #if every node is reached return True

        def score(group):
            votes = sum(electorate.votes[i] == party for i in group)
            opp = self.TARGET_SIZE - votes
            return votes, opp

        def classify(group):
            votes, opp = score(group)
            if votes == 5 and opp == 4: return 0  # BEST: ideal 5–4
            if opp >= 8: return 1  # crack opponent
            if votes > 4: return 2  # normal win
            return 3  # fallback

        def grow(group, used):
            if len(group) == self.TARGET_SIZE: # if group is correct district size
                return [set(group)] if is_connected(group) else None # only accept if is_connected True


            for node in list(group): #for each node in district
                for nbr in random.sample(graph.neighbors(node), len(graph.neighbors(node))): # look at random neighbors (important for different trials)
                    if nbr not in group and nbr not in used: # if not in group or used in another district
                        group.add(nbr)              # try adding to group
                        result = grow(group, used)  # add recursively
                        if result:                  #till a valid complete district
                            return result
                        group.remove(nbr)           #otherwise remove from group

        def build(used, districts):     #tries to create all districts with grow function
            if len(districts) == d:     # if all districts made return the list of districts
                return districts

            for seed in range(voters):  #loop through all voters
                if seed in used:        #skip seeds already in a district
                    continue

                group = {seed}          #have seed in group then try to grow a new distict
                built_group = grow(group, used)
                if not built_group:     #if that doesn't work try another seed(voter)
                    continue

                gset = built_group[0]      #if the built_group works add to list of districts
                districts.append(list(gset))
                used |= gset               #have all voters in district set to used

                result = build(used, districts) #now recursively build a new district
                if result:                  # if it works return result
                    return result

                used -= gset        # if the recursion doesn't work remove the voters from district and remove from used list
                districts.pop()

            return None     # if every voter fails return none


        return build(set(), []) # makes a list starting with no used voters and no districts

    def best_of_trials(self, electorate, party):
        trials = 2 # hard for my computer you can increase for a better result
        best = None
        best_wins = -1

        for _ in range(trials):
            gm = BacktrackingGerrymander()
            districts = gm.backtrack(electorate, party)
            wins = electorate.get_wins(districts, party)

            if wins > best_wins:
                best = districts
                best_wins = wins

                # early exit if  party wins
                if wins > self.TARGET_SIZE // 2:
                    break

        return best
