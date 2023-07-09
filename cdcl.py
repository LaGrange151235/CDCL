def bcp(sentence, assignment, c2l_watch, l2c_watch, up_idx=0):
    # NOTE: add parameter up_idx to keep record
    """Propagate unit clauses with watched literals."""

    """ YOUR CODE HERE """
    assigned_lits = []
    for trail in assignment:
        assigned_lits.append(trail[0])
    if len(assignment) == 0:
        up_idx = 0
        for clause_idx in c2l_watch:
            if len(c2l_watch[clause_idx]) == 1:
                if c2l_watch[clause_idx][0] != None:
                    if c2l_watch[clause_idx][0] not in assigned_lits:
                        assignment.append((c2l_watch[clause_idx][0], clause_idx))
                        assigned_lits.append(c2l_watch[clause_idx][0])
                else:
                    if c2l_watch[clause_idx][1] != None:
                        if c2l_watch[clause_idx][1] not in assigned_lits:
                            assignment.append((c2l_watch[clause_idx][1], clause_idx))
                            assigned_lits.append(c2l_watch[clause_idx][1])
    while up_idx < len(assignment):
        x = assignment[up_idx][0]
        up_idx += 1
        y = None
        watched_clause = list.copy(l2c_watch[-x])
        for clause_idx in watched_clause:
            if len(c2l_watch[clause_idx]) == 1:
                return clause_idx
            if c2l_watch[clause_idx][0] != -x:
                y = c2l_watch[clause_idx][0]
            else:
                y = c2l_watch[clause_idx][1]
            if y in assigned_lits:
                continue
            z = None
            for lit in sentence[clause_idx]:
                if lit != -x and lit != y and -lit not in assigned_lits:
                    z = lit
                    break
            if z:
                if c2l_watch[clause_idx][0] == -x:
                    c2l_watch[clause_idx][0] = z
                else:
                    c2l_watch[clause_idx][1] = z
                l2c_watch[-x].remove(clause_idx)
                l2c_watch[z].append(clause_idx)
            else:
                if -y in assigned_lits:
                    return clause_idx
                else:
                    if y not in assigned_lits:
                        assignment.append((y, clause_idx))
                        assigned_lits.append(y)
    return None  # indicate no conflict; other return the antecedent of the conflict

def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS."""
    scores = {}

    """ YOUR CODE HERE """
    for lit in range(1, num_vars+1):
        scores[lit] = 0
        scores[-lit] = 0
    for clause in sentence:
        for lit in clause:
            scores[lit] += 1
    return scores

def decide_vsids(vsids_scores, assignment):
    # NOTE: add parameter assignment to avoid assign same literal twice
    """Decide which variable to assign and whether to assign True or False."""
    assigned_lit = None

    """ YOUR CODE HERE """
    assigned_lits = []
    for lit in assignment:
        assigned_lits.append(lit[0])
        assigned_lits.append(-lit[0])
    lits = set(vsids_scores)
    assigned_lits = set(assigned_lits)
    unassigned_lits = lits - assigned_lits
    max_value = -1
    for lit in unassigned_lits:
        if vsids_scores[lit] > max_value:
            max_value = vsids_scores[lit]
            assigned_lit = (lit, None)
    return assigned_lit

def update_vsids_scores(vsids_scores, learned_clause, decay=0.95):
    """Update VSIDS scores."""
    for lit in learned_clause:
        vsids_scores[lit] += 1

    for lit in vsids_scores:
        vsids_scores[lit] = vsids_scores[lit] * decay

def init_watch(sentence, num_vars):
    """Initialize the watched lit data structure."""
    c2l_watch = {}  # clause -> literal
    l2c_watch = {}  # literal -> watch

    """ YOUR CODE HERE """
    for lit in range(1, num_vars+1):
        l2c_watch[lit] = []
        l2c_watch[-lit] = []
    for clause_idx, clause in enumerate(sentence):
        c2l_watch[clause_idx] = clause[:2]
        for lit in clause[:2]:
            l2c_watch[lit].append(clause_idx)
    return c2l_watch, l2c_watch

def analyze_conflict(assignment, decided_idxs, conflict_ante, sentence):
    # NOTE: add parameter sentence for analyze conflict
    """Analyze the conflict with first-UIP clause learning."""
    backtrack_level, learned_clause = None, []

    """ YOUR CODE HERE """
    def one_lit_at_level(clause, assigned_lits, decided_idxs):
        cnt = 0
        for lit in clause:
            if -lit in assigned_lits:
                if assigned_lits.index(-lit) >= decided_idxs[-1]:
                    cnt += 1
                    if cnt > 1:
                        return False
        return True

    def get_level(lit, assigned_lits, decided_idxs):
        index = assigned_lits.index(lit)
        for i in range(len(decided_idxs)):
            if index < decided_idxs[i]:
                return i
        return len(decided_idxs)

    def get_backtrack_level(c, assigned_lits, decided_idxs):
        backtrack_level = -1
        for lit in c:
            l = get_level(-lit, assigned_lits, decided_idxs)
            if l > backtrack_level and l < d:
                backtrack_level = l
        return backtrack_level

    assigned_lits = []
    for trail in assignment:
        assigned_lits.append(trail[0])
    if len(decided_idxs) == 0:
        return -1, []
    c = sentence[conflict_ante][:]
    d = len(decided_idxs)
    while not one_lit_at_level(c, assigned_lits, decided_idxs):
        (l, clause_idx) = assignment.pop()
        if -l in c:
            c.remove(-l)
            tmp = sentence[clause_idx][:]
            while l in tmp: 
                tmp.remove(l)
            c = list(set(c + tmp))
    if len(c) == 1:
        return 0, c
    backtrack_level = get_backtrack_level(c, assigned_lits, decided_idxs)    
    learned_clause = c
    return backtrack_level, learned_clause

def backtrack(assignment, decided_idxs, level, sentence):
    # NOTE: add parameter sentence for backtrack
    """Backtrack by deleting assigned variables."""

    """ YOUR CODE HERE """
    if level == 0:
        assignment, decided_idxs, up_idx = [], [], 0
    else:
        decided_idxs = decided_idxs[:level+1]
        assignment = assignment[:decided_idxs[-1]]
        decided_idxs = decided_idxs[:level]
        up_idx = decided_idxs[-1]
        learned_clause = sentence[-1]
        cnt, unassigned_lit = 0,None
        assigned_lits = []
        for trail in assignment:
            assigned_lits.append(trail[0])
        for lit in learned_clause:
            if -lit not in assigned_lits:
                cnt+=1
                unassigned_lit = lit
        if cnt == 1 and unassigned_lit not in assigned_lits:
            assignment.append((unassigned_lit, sentence.index(learned_clause)))
            assigned_lits.append(unassigned_lit)
    # NOTE: return assignment decided_idxs and up_idx to update changes
    return assignment, decided_idxs, up_idx

def add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch):
    """Add learned clause to the sentence and update watch."""

    """ YOUR CODE HERE """
    sentence.append(learned_clause)
    c2l_watch[len(sentence) - 1] = learned_clause[-2:]
    for lit in learned_clause[-2:]:
        l2c_watch[lit].append(len(sentence) - 1)

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
    up_idx = 0 # NOTE: add a record of up_idx for bcp

    # Run BCP.
    if bcp(sentence, assignment, c2l_watch, l2c_watch) is not None:
        # NOTE: add parameter up_idx to keep record
        return None  # indicate UNSAT

    # Main loop.
    while len(assignment) < num_vars:
        assigned_lit = decide_vsids(vsids_scores, assignment)
        # NOTE: add parameter assignment to avoid assign same literal twice
        decided_idxs.append(len(assignment))
        assignment.append(assigned_lit)

        # Run BCP.
        conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch, up_idx)
        # NOTE: add parameter up_idx to keep record
        while conflict_ante is not None:
            # Learn conflict.
            backtrack_level, learned_clause = analyze_conflict(assignment, decided_idxs, conflict_ante, sentence)
            # NOTE: add parameter sentence for analyze conflict
            add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch)

            # Update VSIDS scores.
            update_vsids_scores(vsids_scores, learned_clause)

            # Backtrack.
            if backtrack_level < 0:
                return None

            assignment, decided_idxs, up_idx = backtrack(assignment, decided_idxs, backtrack_level, sentence)
            # NOTE: add parameter sentence for backtrack
            # NOTE: return assignment decided_idxs and up_idx to update changes

            # Propagate watch.
            conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch, up_idx)
    # NOTE: get literals list in the final assignment
    tmp = assignment
    assignment = []
    for trail in tmp:
        assignment.append(trail[0])
    return assignment  # indicate SAT
