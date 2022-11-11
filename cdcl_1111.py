def bcp(sentence, assignment, c2l_watch, l2c_watch):
    """Propagate unit clauses with watched literals."""

    """ YOUR CODE HERE """
    def add_node(implication_graph, lit, clause):
        assign_node = {
            "var": abs(lit),
            "lit": lit,
            "pre": clause
        }
        implication_graph[abs(lit)] = assign_node

    def assign_lit(assignment, implication_graph, lit, c2l_watch, l2c_watch, unsolved_clauses, unit_clauses):
        if lit not in assignment:
            assignment.append(lit)
        for clause in l2c_watch[lit]:
            if lit in c2l_watch[str(clause)]:
                c2l_watch[str(clause)].remove(lit)
            # remove solved
            while clause in unsolved_clauses:
                unsolved_clauses.remove(clause)
            while clause in unit_clauses:
                unit_clauses.remove(clause)
        
        for clause in l2c_watch[-lit]:
            if -lit in c2l_watch[str(clause)]:
                c2l_watch[str(clause)].remove(-lit)
            # check new unit clauses
            if len(c2l_watch[str(clause)]) == 1 and clause in unsolved_clauses:
                unit_clauses.append(clause)
            # check conflict
            if len(c2l_watch[str(clause)]) == 0 and clause in unit_clauses:
                add_node(implication_graph, 0, clause)
                return False

        return True

    unsolved_clauses = list.copy(sentence)
    implication_graph = {}
    unit_clauses = []

    # make assignment nodes in implication graph
    if assignment == []:
        for clause in unsolved_clauses:
            if len(clause) == 1:
                unsolved_clauses.remove(clause)
                lit = clause[0]
                add_node(implication_graph, lit, [])
                if not assign_lit(assignment, implication_graph, lit, c2l_watch, l2c_watch, unsolved_clauses, unit_clauses):
                    #print(implication_graph)
                    return implication_graph


    for lit in assignment:
        add_node(implication_graph, lit, [])
        if not assign_lit(assignment, implication_graph, lit, c2l_watch, l2c_watch, unsolved_clauses, unit_clauses):
            #print(implication_graph)
            return implication_graph

    #print(assignment)
    #print(unit_clauses)
    while unit_clauses != []:
        clause = unit_clauses.pop()
        print(len(assignment), clause, c2l_watch[str(clause)])
        # assignment for unit clause
        unit_lit = c2l_watch[str(clause)][0]
        add_node(implication_graph, unit_lit, clause)
        if not assign_lit(assignment, implication_graph, unit_lit, c2l_watch, l2c_watch, unsolved_clauses, unit_clauses):
            #print(implication_graph)
            return implication_graph

    #print(implication_graph)
    return None  # indicate no conflict; other return the antecedent of the conflict

def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS."""
    scores = {}

    """ YOUR CODE HERE """
    for i in range(-num_vars, num_vars+1):
        if i == 0:
            continue
        scores[i] = 0
    for clause in sentence:
        for lit in clause:
            scores[lit] += 1
    return scores

def decide_vsids(vsids_scores, assignment): # NOTE: add assignment to avoid assigning same lit twice
    """Decide which variable to assign and whether to assign True or False."""
    assigned_lit = None

    """ YOUR CODE HERE """
    max_score = 0
    for lit, score in vsids_scores.items():
        if score >= max_score and lit not in assignment and -lit not in assignment:
            max_score = score
            assigned_lit = lit
    print("decide:", assigned_lit)
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
    for i in range(-num_vars, num_vars+1):
        if i == 0:
            continue
        l2c_watch[i] = []
    for clause in sentence:
        c2l_watch[str(clause)] = []
        for lit in clause:
            l2c_watch[lit].append(clause)
            c2l_watch[str(clause)].append(lit)
    return c2l_watch, l2c_watch

def analyze_conflict(assignment, decided_idxs, conflict_ante):
    """Analyze the conflict with first-UIP clause learning."""
    backtrack_level, learned_clause = None, []

    """ YOUR CODE HERE """
    def one_lit_at_level(c, d, conflict_ante):
        cnt = 0
        for lit in c:
            if conflict_ante[abs(lit)]["level"] == d:
                cnt += 1
        if cnt > 1:
            return False
        else:
            return True

    def last_assigned_lit_at_level(c, d, assignment, conflict_ante):
        last_lit = c[0]
        last_idx = 0
        for lit in c:
            if conflict_ante[abs(lit)]["level"] == d:
                if lit in assignment:
                    if assignment.index(lit) > last_idx:
                        last_idx = assignment.index(lit)
                        last_lit = lit
                if -lit in assignment:
                    if assignment.index(-lit) > last_idx:
                        last_idx = assignment.index(-lit)
                        last_lit = -lit
        return last_lit
        
    def resolve(ante, c, v):
        resolved = []
        resolved.extend(ante)
        resolved.extend(c)
        resolved = list(set(resolved))
        if v in resolved:
            resolved.remove(v)
        if -v in resolved:
            resolved.remove(-v)
        return resolved

    def asserting_level(c, conflict_ante):
        levels = []
        for lit in c:
            levels.append(conflict_ante[abs(lit)]["level"])
        levels = list(set(levels))
        levels = sorted(levels, reverse=True)
        if len(levels) > 2:
            return levels[1]
        if len(levels) <= 2:
            return levels[0]
        if len(levels) == 0:
            return -1

    level = 0
    if decided_idxs == []:
        for lit in assignment:
            conflict_ante[abs(lit)]["level"] = 0
        conflict_ante[0]["level"] = level
    else:
        upper_bound = decided_idxs[level]
        for i in range(len(assignment)):
            if level < len(decided_idxs):
                upper_bound = decided_idxs[level]
                if i >= upper_bound:
                    level += 1
            conflict_ante[abs(assignment[i])]["level"] = level
        conflict_ante[0]["level"] = level

    print(assignment)
    print(decided_idxs)
    print(conflict_ante)

    d = conflict_ante[0]["level"]
    if d == 0:
        return -1, []
    c = conflict_ante[0]["pre"]

    while not one_lit_at_level(c, d, conflict_ante):
        t = last_assigned_lit_at_level(c, d, assignment, conflict_ante)
        v = conflict_ante[abs(t)]["var"]
        ante = conflict_ante[abs(t)]["pre"]
        c = resolve(ante, c, v)
    backtrack_level = asserting_level(c, conflict_ante)
    learned_clause = c
    if backtrack_level <= 0:
        return -1, []
    return backtrack_level, learned_clause

def backtrack(assignment, decided_idxs, level, c2l_watch, l2c_watch): # NOTE: add c2l and l2c watch list to keep its correctness
    """Backtrack by deleting assigned variables."""

    """ YOUR CODE HERE """
    print(level, decided_idxs)
    while len(assignment) > decided_idxs[level-1]+1:
        lit = assignment.pop()
        for clause in l2c_watch[lit]:
            if lit not in c2l_watch[str(clause)]:
                c2l_watch[str(clause)].append(lit)
        for clause in l2c_watch[-lit]:
            if -lit not in c2l_watch[str(clause)]:
                c2l_watch[str(clause)].append(-lit)
    assignment[-1] *= -1
    while len(decided_idxs) >= level:
        decided_idxs.pop()



def add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch):
    """Add learned clause to the sentence and update watch."""

    """ YOUR CODE HERE """
    sentence.append(learned_clause)
    c2l_watch[str(learned_clause)] = []
    for lit in learned_clause:
        c2l_watch[str(learned_clause)].append(lit)
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
        assigned_lit = decide_vsids(vsids_scores, assignment) # NOTE: add assignment to avoid assigning same lit twice
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

            backtrack(assignment, decided_idxs, backtrack_level, c2l_watch, l2c_watch) # NOTE: add c2l and l2c watch list to keep its correctness

            # Propagate watch.
            conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch)
    return assignment  # indicate SAT
