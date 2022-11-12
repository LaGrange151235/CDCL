import math
def index_of_lit(assignment, lit):
    for i, dic in enumerate(assignment):
        if dic[0] == lit:
            return i

def index_of_clause(sentence, clause):
    for i, c in enumerate(sentence):
        if clause == c:
            return i

def bcp(sentence, assignment, c2l_watch, l2c_watch):
    """Propagate unit clauses with watched literals."""

    """ YOUR CODE HERE """
    assign_list = []
    for dic in assignment:
        assign_list.append(dic[0])

    last_clause = sentence[len(sentence)-1]
    ifunit = 0
    lit_to_assign = 0
    for lit in last_clause:
        if -lit in assign_list:
            ifunit += 1
        else:
            lit_to_assign = lit
    if ifunit == len(last_clause) - 1 and lit_to_assign not in assign_list:
        dic = {}
        dic[0] = lit_to_assign
        dic[1] = last_clause
        assignment.append(dic)
        assign_list.append(lit_to_assign)

    up_idx = len(assignment) - 1 if len(assignment) > 0 else 0

    if len(assignment) == 0:
        for clause in sentence:
            if len(clause) == 1:
                dic = {}
                dic[0] = clause[0]
                dic[1] = clause
                assignment.append(dic)
                assign_list.append(dic[0])

    while up_idx < len(assignment):
        x = assignment[up_idx][0]
        up_idx += 1

        for clause in l2c_watch[-x]:
            if len(clause) == 1:
                return clause
            k = index_of_clause(sentence, clause)
            y = c2l_watch[k][1] if -x == c2l_watch[k][0] else c2l_watch[k][0]
            if y in assign_list:
                continue
            flag = False
            for z in clause:
                if -z not in assign_list and z != -x and z != y:
                    l2c_watch[-x].remove(clause)
                    l2c_watch[z].append(clause)
                    c2l_watch[k].remove(-x)
                    c2l_watch[k].append(z)
                    flag = True
                    break
            if not flag:
                if -y in assign_list:
                    return clause
                else:
                    dic = {}
                    dic[0] = y
                    dic[1] = clause
                    assignment.append(dic)
                    assign_list.append(y)
                    """print(dic)"""

    return None  # indicate no conflict; other return the antecedent of the conflict

def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS."""
    scores = {}

    """ YOUR CODE HERE """
    for i in range(-num_vars, num_vars+1):
        scores[i] = 0

    for clause in sentence:
        for lit in clause:
            scores[lit] += 1

    return scores

def decide_vsids(assignment, vsids_scores):
    """Decide which variable to assign and whether to assign True or False."""
    assigned_lit = None

    """ YOUR CODE HERE """
    assign_list = []
    for dic in assignment:
        assign_list.append(dic[0])
    max = 0
    for lit in vsids_scores:
        if vsids_scores[lit] > max and lit not in assign_list and -lit not in assign_list:
            max = vsids_scores[lit]
            assigned_lit = lit

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

    for i in range(-num_vars, num_vars + 1):
        l2c_watch[i] = []

    for i, clause in enumerate(sentence):
        c2l_watch[i] = []
        for lit in clause:
            if len(c2l_watch[i]) < 2:
                c2l_watch[i].append(lit)
                l2c_watch[lit].append(clause)
            else:
                break

    return c2l_watch, l2c_watch

def analyze_conflict(assignment, decided_idxs, conflict_ante):
    """Analyze the conflict with first-UIP clause learning."""
    backtrack_level, learned_clause = None, []

    """ YOUR CODE HERE """
    if len(decided_idxs) == 0:
        return -1, []
    c = conflict_ante
    latest_decided = decided_idxs[len(decided_idxs)-1]

    while True:
        cnt = 0
        for lit in c:
            if index_of_lit(assignment, -lit) >= latest_decided:
                cnt += 1
        if cnt == 1:
            break
        dic = assignment.pop()
        if -dic[0] in c:
            c.remove(-dic[0])
            tmp = dic[1]
            tmp.remove(dic[0])
            c = list(set(c).union(tmp))

    learned_clause = c
    print(learned_clause)

    idx = []
    for lit in learned_clause:
        idx.append(index_of_lit(assignment, -lit))
    if len(idx) == 1:
        backtrack_level = 0
    else:
        idx.sort(reverse=True)
        max2 = idx[1]
        for i, value in enumerate(decided_idxs):
            if value > max2:
                backtrack_level = i
                break

    return backtrack_level, learned_clause

def backtrack(assignment, decided_idxs, level):
    """Backtrack by deleting assigned variables."""

    """ YOUR CODE HERE """
    length = decided_idxs[level]
    for i in range(length, len(assignment)):
        assignment.pop()
    for i in range(level, len(decided_idxs)):
        decided_idxs.pop()

def add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch):
    """Add learned clause to the sentence and update watch."""

    """ YOUR CODE HERE """
    sentence.append(learned_clause)
    c2l_watch[str(learned_clause)] = []
    for lit in learned_clause:
        if len(c2l_watch[str(learned_clause)]) < 2:
            c2l_watch[str(learned_clause)].append(lit)
            l2c_watch[lit].append(learned_clause)
        else:
            break

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
        assigned_lit = decide_vsids(assignment, vsids_scores)
        decided_idxs.append(len(assignment))
        dic = {}
        dic[0] = assigned_lit
        dic[1] = []
        assignment.append(dic)

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
            print("conflict")
            print(decided_idxs)
            print(conflict_ante)
    assignment_final = []
    for dic in assignment:
        assignment_final.append(dic[0])
    return assignment_final # indicate SAT
