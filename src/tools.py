import re
from tralda.datastructures.Tree import Tree, LCA
from asymmetree.tools.PhyloTreeTools import parse_newick, assign_missing_labels

#.......................................................
# Transform RAxML newick to tralda
#.......................................................
def get_tralda_ML(fname):
    f = open(fname, "r")
    ML_newick = f.read()
    f.close()
    ml_tree = parse_newick(ML_newick)
    for n in ml_tree.postorder():
        if n.is_leaf():
            if not isinstance(n.label, str):
                raise RuntimeError('\t gene tree labels are not strings')
            numbers = re.findall(r'\d+', n.label)
            numbers  = list(map(int, numbers))
            if len(numbers) != 3:
                raise RuntimeError('\t gene tree does not follow name format fam<n>gen<n>spec<n>')
            n.label  = numbers[1]
            n.reconc = int(numbers[2])
        n.event  = 'S'
    assign_missing_labels(ml_tree)
    return(ml_tree)


#......................................................
# Check gt newick species
#......................................................
def assert_species_equal(gtree,stree):
    species = [v.label for v in stree.leaves()]
    species = set(species)
    species_in_genes = [v.reconc for v in gtree.leaves()]

    reply = True
    for s in species_in_genes:
        if s not in species:
            raise RuntimeError('\t genes contain a species not present in species tree')
        reply = False
    return(reply)

#.......................................................
# Calculate duplication cost 
#.......................................................
"""
Let g be an internal node of G. If M(c(g)) = M(g) for
some child c(g) of g, then we say that a duplication occurs at M(g) (or
more exactly in the lineage entering M(g) in S.

The total number of duplications arising in the lca reconciliation is the
duplication cost.
"""
def calculate_dcost(tree):
    def _d_node_cost(node):
        val = 0
        for child in node.children:
            if node.reconc == child.reconc:
                val = 1
                return val
        return val
    d_cost = 0
    for node in tree.preorder():
        if not node.is_leaf():
            d_cost += _d_node_cost(node)
    return d_cost


#.......................................................
# Get least-duplication resolved tree
#.......................................................
def get_least_duplication_resolved_tree(reconciled_gene_tree):
    #get redundant edges
    r = []
    for u,v in reconciled_gene_tree.inner_edges():
        if u.reconc == v.reconc and u.event == "D" and v.event == "D":
            r.append((u,v))

    reconciled_gene_tree.contract(r)
    return(reconciled_gene_tree)
    


#.....................................................
# Output the reconciled gene as a reconciliation newick
#.....................................................
def to_renconc_string(reconciled_gene_tree,format='parle'):
    T = reconciled_gene_tree.copy()
    if format=='parle':
        for v in T.postorder():
            if v.event == 'D':
                rmap = v.reconc
            else:
                rmap = v.reconc
            new_tag = str(v.label) + "_" + v.event + "_" + str(rmap)
            v.label = new_tag
    else:
        for v in T.postorder():
            if not v.is_leaf():
                if v.event == 'D':
                    v.label = 'duplication'
                else:
                    v.label = 'speciation'
    return(T.to_newick())
