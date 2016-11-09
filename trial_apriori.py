import sys
import csv
from itertools import chain, combinations
from collections import defaultdict


def subsets(arr):
	""" Returns non empty subsets of arr"""
	return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnfrequentitemsets(itemSet, transactionList, minSupport, freqSet):
		"""calculates the support for items in the itemSet and returns a subset
	   of the itemSet each of whose elements satisfies the minimum support"""
		_itemSet = set()
		localSet = defaultdict(int)

		for item in itemSet:
			for transaction in transactionList:
				if item.issubset(transaction):
					freqSet[item] += 1
					localSet[item] += 1

		for item, count in localSet.items():
				support = float(count)/len(transactionList)

				if support >= minSupport:
						_itemSet.add(item)

		return _itemSet


def joinSet(itemSet, length):
		"""Join a set with itself and returns the n-element itemsets"""
		return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getSupport(transactionList,freqSet,item):
	return float(freqSet[item])/len(transactionList)

def runApriori(data_iter, minSupport, minConfidence):

	transactionList=list()
	itemSet=set()
	for record in data_iter:
		transaction=frozenset(record)
		transactionList.append(transaction)
		for item in transaction:
			itemSet.add(frozenset([item]))             # generate 1-itemset
#	print type(itemSet)
	freqSet = defaultdict(int)
	largeSet = dict()
	assocRules = dict()
	# Dictionary which stores Association Rules

	oneCSet = returnfrequentitemsets(itemSet,transactionList,minSupport,freqSet)  # obtaining frequent 1-itemset          

	currentLSet = oneCSet
	k = 2
	while(currentLSet != set([])):
		""" while loop generates 2 or more itemsets that are frequent and the result is stored in 
			largeSet dictionary"""      
		largeSet[k-1] = currentLSet
		currentLSet = joinSet(currentLSet, k)		# joining frequent itemset to obtain k length itemset
		currentCSet = returnfrequentitemsets(currentLSet,transactionList,minSupport,freqSet)	# from the set obtained by joining select the itemsets that satisfy minsupport
		currentLSet = currentCSet
		k = k + 1
	RetrieveItems = []
	""" RetrieveItems store itemset which are frequent with their support"""
	for key, value in largeSet.items():
		for item in value:
			RetrieveItems.append((tuple(item),getSupport(transactionList,freqSet,item))) 
#		RetrieveItems.extend([(tuple(item), getSupport(transactionList,freqSet,item))
#						   for item in value])
	"""RetrieveRules store the asociation rule"""
	RetrieveRules = []
	print largeSet
	for key, value in largeSet.items():		# Items in associated rules are from frequent itemset
		for item in value:
			print "type :",type(item)
			_subsets = map(frozenset, [x for x in subsets(item)])	# converting list to set to perform set operation
			for element in _subsets:
				remain = item.difference(element)	# taking every combination of frequent itemsets and comparing its confidence with minconfidence
				if len(remain) > 0:
					confidence = getSupport(transactionList,freqSet,item)/getSupport(transactionList,freqSet,element)
					if confidence >= minConfidence:
						RetrieveRules.append(((tuple(element), tuple(remain)),
										   confidence))
	length=k-2
	return RetrieveItems, RetrieveRules,length

def countfreqitemsets(items,maxlength):
	count=0
	for item,support in sorted(items,key=lambda (item,support):support):
		if len(item)==maxlength:
			count+=1
	return count

def printfreqitemsets(items,maxlength,writer): 
	count=countfreqitemsets(items,maxlength)
#	count=list(count)
#	writer.write('%d' %count)
	for item, support in sorted(items, key=lambda (item, support): support):
#	print type(item)
		if len(item)==maxlength:	# printing frequent itemsets with max length
			itemlist=list(item)
#			print type(itemlist)
#			freq_item=str(",".join([str(s) for s in itemlist]))
#			freq_itemList=freq_item.split(' ')
#			print freq_itemList
			writer.writerows([itemlist])
#			print "%s" % str(item)

def countrules(rules):
	return len(rules)

def printassocrules(rules,writer):		# function to print association rules with confidence greater than minconfidence
#	print len(rules)
	for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
		pre, post = rule
		pre_list=list(pre)
		post_list=list(post)
		pre_list.append('=>')
		pre_list.extend(post_list)
#		string_pre=str(",".join([str(s) for s in list(pre)]))
#		string_post=str(",".join([str(s) for s in list(post)]))
#		print "%s" %(string_post)
#		rules=str("%s => %s" %(string_pre,string_post))
#		rulesList=rules.split(' ')
#		print rulesList
		writer.writerows([pre_list])
#		print ",".join([str(s) for s in list(pre)])",".join([str(s) for s in list(post)])
#		print "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)


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
	for line in file_iter:
		line=line.strip().rstrip(',')			 
		record=frozenset(line.split(','))		# record stores a transaction and is of type list
		transactions.append(record)				# transaction is a list of list which stores record
#	print transactions
	items, rules, maxlength = runApriori(transactions, minsupport, minconfidence)
#	print type(items)
	with open(out_file,'wb') as outFile:
		outFile.write('%s\n' %(str(countfreqitemsets(items,maxlength))))
		writer=csv.writer(outFile)
		printfreqitemsets(items,maxlength,writer)
		if flag==1:
			outFile.write('%s\n' %(str(countrules(rules))))
			printassocrules(rules,writer)