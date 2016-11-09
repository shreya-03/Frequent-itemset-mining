import itertools
import csv
from collections import defaultdict

class FPNode(object):

	def __init__(self, value, count, parent):
		self.value = value
		self.count = count
		self.parent = parent
		self.link = None
		self.children = []

	def has_child(self, value):
		for node in self.children:
			if node.value == value:
				return True
		return False

	def get_child(self, value):
		for node in self.children:
			if node.value == value:
				return node
		return None

	def add_child(self, value):
		child = FPNode(value, 1, self)
		self.children.append(child)
		return child


class FPTree(object):

	def __init__(self, transactions, threshold, root_value, root_count):
		self.frequent = self.find_frequent_items(transactions, threshold)
#		print self.frequent
		self.headers = self.build_header_table(self.frequent)
		self.root = self.build_fptree(
			transactions, root_value,
			root_count, self.frequent, self.headers)

	def find_frequent_items(self,transactions, threshold):
		items = defaultdict(lambda: 0) # mapping from items to their supports
		for transaction in transactions:
			for item in transaction:
				items[item] += 1
		items = dict((item, support) for item, support in items.iteritems()
		if support >= threshold)
		return items

	def build_header_table(self,frequent):
		headers = {}
		for key in frequent.keys():
			headers[key] = None
		return headers

	def build_fptree(self, transactions, root_value,root_count, frequent, headers):
		root = FPNode(root_value, root_count, None)

		for transaction in transactions:
			sorted_items = [x for x in transaction if x in frequent]
			sorted_items.sort(key=lambda x: frequent[x], reverse=True)
			if len(sorted_items) > 0:
				self.insert_tree(sorted_items, root, headers)
		return root

	def insert_tree(self, items, node, headers):
		first = items[0]
		child = node.get_child(first)
		if child is not None:
			child.count += 1
		else:
			# Add new child.
			child = node.add_child(first)

			# Link it to header structure.
			if headers[first] is None:
				headers[first] = child
			else:
				current = headers[first]
				while current.link is not None:
					current = current.link
				current.link = child

		# Call function recursively.
		remaining_items = items[1:]
		if len(remaining_items) > 0:
			self.insert_tree(remaining_items, child, headers)

	def tree_has_single_path(self, node):
		num_children = len(node.children)
		if num_children > 1:
			return False
		elif num_children == 0:
			return True
		else:
			return True and self.tree_has_single_path(node.children[0])

	def mine_patterns(self, threshold):
		"""
		Mine the constructed FP tree for frequent patterns.
		"""
		if self.tree_has_single_path(self.root):
			return self.generate_pattern_list()
		else:
			return self.zip_patterns(self.mine_sub_trees(threshold))

	def zip_patterns(self, patterns):
		"""
		Append suffix to patterns in dictionary if
		we are in a conditional FP tree.
		"""
		suffix = self.root.value

		if suffix is not None:
			# We are in a conditional tree.
			new_patterns = {}
			for key in patterns.keys():
				new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

			return new_patterns

		return patterns

	def generate_pattern_list(self):
		"""
		Generate a list of patterns with support counts.
		"""
		patterns = {}
		items = self.frequent.keys()

		# If we are in a conditional tree,
		# the suffix is a pattern on its own.
		if self.root.value is None:
			suffix_value = []
		else:
			suffix_value = [self.root.value]
			patterns[tuple(suffix_value)] = self.root.count

		for i in range(1, len(items) + 1):
			for subset in itertools.combinations(items, i):
				pattern = tuple(sorted(list(subset) + suffix_value))
				patterns[pattern] = \
					min([self.frequent[x] for x in subset])

		return patterns

	def mine_sub_trees(self, threshold):
		"""
		Generate subtrees and mine them for patterns.
		"""
		patterns = {}
		mining_order = sorted(self.frequent.keys(),
							  key=lambda x: self.frequent[x])

		# Get items in tree in reverse order of occurrences.
		for item in mining_order:
			suffixes = []
			conditional_tree_input = []
			node = self.headers[item]

			# Follow node links to get a list of
			# all occurrences of a certain item.
			while node is not None:
				suffixes.append(node)
				node = node.link

			# For each occurrence of the item, 
			# trace the path back to the root node.
			for suffix in suffixes:
				frequency = suffix.count
				path = []
				parent = suffix.parent

				while parent.parent is not None:
					path.append(parent.value)
					parent = parent.parent

				for i in range(frequency):
					conditional_tree_input.append(path)

			# Now we have the input for a subtree,
			# so construct it and grab the patterns.
			subtree = FPTree(conditional_tree_input, threshold,
							 item, self.frequent[item])
			subtree_patterns = subtree.mine_patterns(threshold)

			# Insert subtree patterns into main patterns dictionary.
			for pattern in subtree_patterns.keys():
				if pattern in patterns:
					patterns[pattern] += subtree_patterns[pattern]
				else:
					patterns[pattern] = subtree_patterns[pattern]

		return patterns


def find_frequent_patterns(transactions, support_threshold):
	tree = FPTree(transactions, support_threshold, None, None)
	return tree.mine_patterns(support_threshold)

def subsets(arr):
	return itertools.chain(*[itertools.combinations(arr, i + 1) for i, a in enumerate(arr)])

def generate_association_rules(patterns, confidence_threshold):
	rules = {}
	for itemset in patterns.keys():
		fitemset=frozenset(itemset)
		upper_support = patterns[itemset]
		subSets = map(frozenset, [x for x in subsets(fitemset)])	
		for element in subSets:
			if tuple(element) in patterns:
				remain = fitemset.difference(element)	# taking every combination of frequent itemsets and comparing its confidence with minconfidence
				if len(remain) > 0:
					confidence = float(upper_support)/patterns[tuple(element)]
					if confidence >= confidence_threshold:
						rules[tuple(element)] = (tuple(remain), confidence)
	return rules

def countfreqitemsets(items,maxlength):
	count=0
	for item,support in sorted(items,key=lambda (item,support):support):
		if len(item)==maxlength:
			count+=1
	return count

def printfreqitemsets(items,writer): 
	for item, support in items.iteritems():
		writer.writerows([item])

def printassocrules(rules,writer):		# function to print association rules with confidence greater than minconfidence
	for pre_rule, (post_rule,confidence) in rules.iteritems():
		pre_rule=list(pre_rule)
		post_rule=list(post_rule)
		pre_rule.append('=>')
		pre_rule.extend(post_rule)
		writer.writerows([pre_rule])


if __name__ == "__main__":
	count=1
	conf_f=open("config.csv",'rb')
	try:
		reader=csv.reader(conf_f)     	# reading config.csv file using csv module
#		print type(reader)
		for lines in reader:
			if count==1:
				in_file=lines[1]        # Obtaining input file path from config.csv file
			elif count==2:
				out_file=lines[1]		#obtaining output file path from config.csv file
			elif count==3:
				minsupport=float(lines[1])		# Obtaining minsupport 
			elif count==4:
				minconfidence=float(lines[1])	# Obtaining minconfidence
			else:
				flag=int(lines[1])				# Obtaining flag value to print desired output
			count=count+1
	finally:
		conf_f.close()
	transactions=list()
	file_iter=open(in_file,'rU')		# reading input file mentioned in config.csv
	T1=csv.reader(file_iter)
	for line in T1:
		transactions.append(line)				# transaction is a list of list which stores record
#	print transactions
	minsupport*=len(transactions)
	items = find_frequent_patterns(transactions, minsupport)
#	print "FIS"
#	print items
	rules = generate_association_rules(items,minconfidence)
#	print "rules"
#	print rules
	outFile = open(out_file,'wb')
	outFile.write('%s\n' %(len(items)))
	writer=csv.writer(outFile)
	printfreqitemsets(items,writer)
	if flag==1:
		outFile.write('%s\n' %(len(rules)))
		printassocrules(rules,writer)
