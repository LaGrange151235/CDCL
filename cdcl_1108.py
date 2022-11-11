def bcp(sentence, assignment, c2l_watch, l2c_watch):
    """Propagate unit clauses with watched literals."""

    """ YOUR CODE HERE """
    # 维护c2l_watch
    for clause in sentence:
        c2l_watch[str(clause)] = []
        for lit in clause:
            if lit not in assignment:
                c2l_watch[str(clause)].append(lit)

    print("\nbcp")
    #print("bcp initial assignment: ", assignment)
    conflict_ante = []
    unsolved_clauses = list.copy(sentence)
    len_assignment = -1

    # 首先找到未被解决的子句(unsolved_clauses)
    for lit in assignment:
        # 查询每个在assignment中的lit可以解决的子句并删除他们
        for clause in l2c_watch[lit]:
            if clause in unsolved_clauses:
                unsolved_clauses.remove(clause)
        # 顺便维护c2l_watch
        for clause in l2c_watch[-lit]:
            if -lit in c2l_watch[str(clause)]:
                c2l_watch[str(clause)].remove(-lit)
    
    while len_assignment != len(assignment):
        # 一直扩散直到assignment长度不再改变
        len_assignment = len(assignment)
        unit_clauses = []
        for clause in unsolved_clauses:
            cnt_watch = len(c2l_watch[str(clause)])
            if cnt_watch >= 2:
                # 不是unit_clause
                continue
            if cnt_watch == 1:
                # 是unit_clause
                lit = c2l_watch[str(clause)][0]
                unit_clauses.append(clause)
                conflict_ante.append(clause)
                if lit not in assignment:
                    assignment.append(lit)
                    for clause in l2c_watch[lit]:
                        if lit in c2l_watch[str(clause)]:
                            c2l_watch[str(clause)].remove(lit)
                            while clause in unsolved_clauses:
                                unsolved_clauses.remove(clause)
                    for clause in l2c_watch[-lit]:
                        if -lit in c2l_watch[str(clause)]:
                            c2l_watch[str(clause)].remove(-lit)
            if cnt_watch == 0:
                # 是conflict_clause
                # 理由如下：
                # 1. 显然此子句没有被本轮扩散前的assignment解决
                # 2. 在此前的assignment或者本轮扩散过程中被解决，
                #    但是子句中lit已耗尽，说明全部在assignment中并在此为假
                conflict_ante.append(clause)
                print("bcp conflict clause:", clause, "\nconflict_ante:", conflict_ante, "\nassignment:", assignment)
                return conflict_ante
        #print("bcp assignment: ", assignment)
        print("bcp: ", len(assignment))

    #print("unsolved_clauses: ", unsolved_clauses)
    #print("unit_clauses: ", unit_clauses)
    #print("assignment: ", assignment)
    #print("c2l_watch: ", c2l_watch)
    #print("conflict_ante: ", conflict_ante, "\n")

    return None  # indicate no conflict; other return the antecedent of the conflict

def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS."""
    scores = {}

    """ YOUR CODE HERE """
    print("\ninit_vsids_scores")

    for i in range(num_vars):
        scores[i+1] = 0
        scores[-i-1] = 0
    for clause in sentence:
        for lit in clause:
            scores[lit] += 1
    return scores

def decide_vsids(vsids_scores, assignment): 
    # NOTE: Here we add another arg 'assignment' 
    #       to avoid choose the same var twice
    """Decide which variable to assign and whether to assign True or False."""
    assigned_lit = None

    """ YOUR CODE HERE """
    max_score = 0
    for lit, score in vsids_scores.items():
        if score >= max_score and lit not in assignment and -lit not in assignment:
            max_score = score
            assigned_lit = -lit
    print("\ndecide_vsids: choose lit: ", assigned_lit, "with score: ", max_score)
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
    print("\ninit_watch")
    for i in range(num_vars):
        l2c_watch[i+1] = []
        l2c_watch[-i-1] = []
    for clause in sentence:
        c2l_watch[str(clause)] = []
        for lit in clause:
            c2l_watch[str(clause)].append(lit)
            l2c_watch[lit].append(clause)

    return c2l_watch, l2c_watch

def analyze_conflict(assignment, decided_idxs, conflict_ante):
    """Analyze the conflict with first-UIP clause learning."""
    backtrack_level, learned_clause = None, []

    """ YOUR CODE HERE """
    def one_lit_at_level(c, d, assignment):
        cnt_lit = 0
        for lit in c:
            if lit in assignment:
                idx = assignment.index(lit)
            if -lit in assignment:
                idx = assignment.index(-lit)
            if idx > d:
                cnt_lit += 1
        if cnt_lit > 1:
            return False
        else:
            return True

    def last_assigned_lit_at_level(c, d, assignment, decided_idxs):
        if d == decided_idxs[-1]:
            for i in range(len(assignment)-1, d-1, -1):
                if assignment[i] in c or -assignment[i] in c:
                    return assignment[i]
        else:
            upper_bound = decided_idxs[decided_idxs.index(d)+1]
            for i in range(upper_bound-1, d-1, -1):
                if assignment[i] in c:
                    return assignment[i]
    
    def var_of_lit(t):
        return abs(t)

    def antecedent(t, d, assignment, conflict_ante):
        for clause in conflict_ante:
            if t in clause:
                #print("\n", t, "\n", conflict_ante, "\n", assignment, "\n", clause)
                return clause

    def resolve(ante, c, v):
        print("\n", ante, "\n", c, "\n", v)
        if ante == None:
            # 有些特殊情况下可能没有 first-UIP 
            # 这种情况下没法resolve到只有一个lit
            return c
        res = []
        res.extend(ante)
        res.extend(c)
        res = list(set(res))
        res.remove(v)
        res.remove(-v)
        return res

    def asserting_level(c, assignment, decided_idxs):
        asserting_level = 0
        highest_level = 0
        second_highest_level = 0
        idx_c = []
        for lit in c:
            if lit in assignment:
                idx_c.append(assignment.index(lit))
            if -lit in assignment:
                idx_c.append(assignment.index(-lit))
        idx_c = sorted(idx_c, reverse=True)
        for i in range(len(decided_idxs)-1, -1, -1):
            if decided_idxs[i] <= idx_c[0]:
                highest_level = decided_idxs[i]
                break
        for idx in idx_c:
            if idx < highest_level:
                for j in range(len(decided_idxs)-1, -1, -1):
                    if decided_idxs[j] <= idx:
                        second_highest_level = decided_idxs[j]
                        break
                if second_highest_level != 0:
                    break
        asserting_level = second_highest_level
        return asserting_level

    d = 0
    if len(decided_idxs) > 0:
        d = decided_idxs[-1]
    if d == -1:
        backtrack_level = -1
        learned_clause = []
        return backtrack_level, learned_clause
    c = conflict_ante[-1]
    conflict_ante.remove(c)

    while not one_lit_at_level(c, d, assignment):
        t = last_assigned_lit_at_level(c, d, assignment, decided_idxs)
        v = var_of_lit(t)
        ante = antecedent(t, d, assignment,conflict_ante)
        c_resolved = resolve(ante, c, v)
        if c != c_resolved:
            c = c_resolved
            continue
        else:
            break
        #print("c: ", c, "d: ", d)
    
    backtrack_level = asserting_level(c, assignment, decided_idxs)
    learned_clause = c
    print("\nanalyze_conflict")
    print("backtrack_level:", backtrack_level, "\nlearned_clause:", learned_clause)
    return backtrack_level, learned_clause

def backtrack(assignment, decided_idxs, level):
    """Backtrack by deleting assigned variables."""

    """ YOUR CODE HERE """
    print("\nbacktrack")
    #print("initial assignment:", assignment, "level:", level)
    while len(assignment) > level+1:
        assignment.remove(assignment[-1])
    assignment[level] *= -1
    while True:
        if decided_idxs == []:
            break
        if decided_idxs[-1] == level:
            decided_idxs.remove(decided_idxs[-1])
            break
        decided_idxs.remove(decided_idxs[-1])
    #print("assignment:", assignment, "\ndecided_idxs:", decided_idxs)


def add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch):
    """Add learned clause to the sentence and update watch."""

    """ YOUR CODE HERE """
    sentence.append(learned_clause)
    c2l_watch[str(learned_clause)] = []
    for lit in learned_clause:
        c2l_watch[str(learned_clause)].append(lit)
        l2c_watch[lit].append(learned_clause)
    print("\nadd_learned_clause")
    #print("sentence:", sentence, "\nlearned_clause:", learned_clause, "\nc2l_watch:", c2l_watch, "\nl2c_watch:", l2c_watch)
    print("learned_clause:", learned_clause)

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
        # NOTE: Here we add another arg 'assignment' 
        #       to avoid choose the same var twice
        decided_idxs.append(-1)
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
