def bcp(sentence, assignment, c2l_watch, l2c_watch):
    """Propagate unit clauses with watched literals."""

    """ YOUR CODE HERE """
    def update(clause, x, y):
        for lit in clause:
            if -lit not in assignment and lit != x and lit != y:
                if -x == c2l_watch[str(clause)][0]:
                    c2l_watch[str(clause)][0] = lit
                if -x == c2l_watch[str(clause)][1]:
                    c2l_watch[str(clause)][1] = lit
                return True
        return False

    trail = []
    unit_clauses = []
    up_idx = 0

    for clause in sentence:
        if len(clause) == 1:
            unit_clauses.append(clause)
            continue

        x = c2l_watch[str(clause)][0]
        y = c2l_watch[str(clause)][1]
        if -x in assignment:
            if y in assignment:
                continue
            else:
                for lit in clause:
                    if -lit not in assignment and lit != x and lit != y:
                        c2l_watch[str(clause)][0] = lit
                        x = lit
                        break
        if -y in assignment:
            if x in assignment:
                continue
            else:
                for lit in clause:
                    if -lit not in assignment and lit != x and lit != y:
                        c2l_watch[str(clause)][1] = lit
                        y = lit
                        break
        if -x in assignment or -y in assignment:
            unit_clauses.append(clause)

    #print(unit_clauses)
    if len(trail) == 0:
        for clause in unit_clauses:
            if len(clause) == 1:
                assignment.append(c2l_watch[str(clause)][0])
                trail.append([c2l_watch[str(clause)][0], clause])
                continue
            if -c2l_watch[str(clause)][0] in assignment:
                if c2l_watch[str(clause)][1] not in assignment:
                    assignment.append(c2l_watch[str(clause)][1])
                    trail.append([c2l_watch[str(clause)][1], clause])
            if -c2l_watch[str(clause)][1] in assignment:
                if c2l_watch[str(clause)][0] not in assignment:
                    assignment.append(c2l_watch[str(clause)][0])
                    trail.append([c2l_watch[str(clause)][0], clause])
    
    while up_idx < len(trail):
        x = trail[up_idx][0]
        up_idx += 1
        for clause in l2c_watch[-x]:
            if -x not in c2l_watch[str(clause)]:
                continue
            if -x == c2l_watch[str(clause)][0]:
                y = c2l_watch[str(clause)][1]
            if -x == c2l_watch[str(clause)][1]:
                y = c2l_watch[str(clause)][0]
            
            if y in assignment:
                continue
            else:
                if update(clause, x, y):
                    continue
                elif -y in assignment:
                    trail.append([0, clause])
                    print(len(assignment))
                    return trail
                else:
                    assignment.append(y)
                    trail.append([y, clause])
                
    print(len(assignment))
    return None  # indicate no conflict; other return the antecedent of the conflict

def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS."""
    scores = {}

    """ YOUR CODE HERE """
    for i in range(num_vars):
        scores[i+1] = 0
        scores[-i-1] = 0
    for clause in sentence:
        for lit in clause:
            scores[lit] += 1
    return scores

def decide_vsids(vsids_scores, assignment):
    """Decide which variable to assign and whether to assign True or False."""
    assigned_lit = None

    """ YOUR CODE HERE """
    max_score = 0
    for lit, score in vsids_scores.items():
        if score >= max_score and lit not in assignment and -lit not in assignment:
            max_score = score
            assigned_lit = lit
    #print("decide:", assigned_lit)
    return assigned_lit

def update_vsids_scores(vsids_scores, learned_clause, decay=0.95):
    """Update VSIDS scores."""
    for lit in learned_clause:
        vsids_scores[lit] += 1

    for lit in vsids_scores:
        vsids_scores[lit] = vsids_scores[lit] * decay

def init_watch(sentence, num_vars):
    """Initialize the watched literal data structure."""
    c2l_watch = {}  # clause -> literal
    l2c_watch = {}  # literal -> watch

    """ YOUR CODE HERE """
    for i in range(num_vars):
        l2c_watch[i+1] = []
        l2c_watch[-i-1] = []
    for clause in sentence:
        c2l_watch[str(clause)] = []
        c2l_watch[str(clause)].append(clause[0])
        if len(clause) >= 2:
            c2l_watch[str(clause)].append(clause[1])
        for lit in clause:
            l2c_watch[lit].append(clause)

    #print("c2l_watch:", c2l_watch)
    #print("l2c_watch:", l2c_watch)
    return c2l_watch, l2c_watch

def analyze_conflict(assignment, decided_idxs, conflict_ante):
    """Analyze the conflict with first-UIP clause learning."""
    backtrack_level, learned_clause = None, []

    """ YOUR CODE HERE """
    def resolve(clause, c, lit):
        resolved = clause+c
        resolved = list(set(resolved))
        resolved.remove(lit)
        resolved.remove(-lit)
        return resolved
    def one_lit_at_level(c, d, assignment):
        cnt = 0
        for lit in c:
            if lit in assignment:
                if assignment.index(lit) >= d:
                    cnt += 1
            if -lit in assignment:
                if assignment.index(-lit) >= d:
                    cnt += 1
        if cnt > 1:
            return False
        if cnt <= 1:
            return True
    def idx2level(idx, decided_idxs):
        level = decided_idxs[-1]
        for level_idx in decided_idxs:
            if idx >= level_idx:
                level = level_idx
            if idx < level_idx:
                break
        return level
    def second_highest_decision_level(c, assignment, decided_idxs):
        idx_list = []
        level_list = []
        for lit in c:
            if lit in assignment:
                idx_list.append(assignment.index(lit))
                level_list.append(idx2level(assignment.index(lit), decided_idxs))
                continue
            if -lit in assignment:
                idx_list.append(assignment.index(-lit))
                level_list.append(idx2level(assignment.index(-lit), decided_idxs))
        level_list = list(set(level_list))
        level_list = sorted(level_list, reverse=True)
        if len(level_list) == 1:
            return level_list[0]
        if len(level_list) >= 2:
            return level_list[1]     

    #print("analyze assignment:", assignment)
    #print("analyze decided idxs:", decided_idxs)
    #print("analyze conflict ante:", conflict_ante)
    if decided_idxs == []:
        return -1, []
    c = conflict_ante.pop()[1]
    d = decided_idxs[-1]
    while not one_lit_at_level(c, d, assignment) and conflict_ante != []:
        lit, clause = conflict_ante.pop()
        if -lit in c:
            c = resolve(clause, c, lit)
            #print(c)
    backtrack_level = second_highest_decision_level(c, assignment, decided_idxs)
    learned_clause = c
    #print("analyze result => backtrack level:", backtrack_level, "learned clause:", learned_clause)
    return backtrack_level, learned_clause

def backtrack(assignment, decided_idxs, level):
    """Backtrack by deleting assigned variables."""

    """ YOUR CODE HERE """
    #print("backtrack assignment:", assignment)
    ##print("backtrack decided idxs:", decided_idxs)
    #print("backtrack level:", level)
    while len(assignment) > level+1:
        assignment.pop()
    while decided_idxs[-1] != level:
        decided_idxs.pop()
    decided_idxs.pop()
    assignment[-1] *= -1
    #print("backtrack assignment:", assignment)
    #print("backtrack decided idxs:", decided_idxs)

def add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch):
    """Add learned clause to the sentence and update watch."""

    """ YOUR CODE HERE """
    sentence.append(learned_clause)
    if len(learned_clause) >= 2:
        c2l_watch[str(learned_clause)] = [learned_clause[0], learned_clause[1]]
    if len(learned_clause) == 1:
        c2l_watch[str(learned_clause)] = [learned_clause[0]]
    for lit in learned_clause:
        l2c_watch[lit].append(learned_clause)

def cdcl(sentence, num_vars):
    """Run a CDCL solver for the SAT problem.

    To simplify the use of data structures, `sentence` is a list of lists where each list
    is a clause. Each clause is a list of literals, where a literal is a signed integer.
    `assignment` is also a list of literals in the order of their assignment.
    """
    # Initialize some data structures.
    vsids_scores = init_vsids_scores(sentence, num_vars)
    c2l_watch, l2c_watch = init_watch(sentence, num_vars)
    assignment, decided_idxs = [], []

    # Run BCP.
    if bcp(sentence, assignment, c2l_watch, l2c_watch) is not None:
        return None  # indicate UNSAT

    # Main loop.
    while len(assignment) < num_vars:
        assigned_lit = decide_vsids(vsids_scores, assignment)
        decided_idxs.append(len(assignment))
        assignment.append(assigned_lit)

        # Run BCP.
        conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch)
        while conflict_ante is not None:
            # Learn conflict.
            backtrack_level, learned_clause = analyze_conflict(assignment, decided_idxs, conflict_ante)
            add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch)

            # Update VSIDS scores.
            update_vsids_scores(vsids_scores, learned_clause)

            # Backtrack.
            if backtrack_level < 0:
                return None

            backtrack(assignment, decided_idxs, backtrack_level)

            # Propagate watch.
            conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch)

    return assignment  # indicate SAT
