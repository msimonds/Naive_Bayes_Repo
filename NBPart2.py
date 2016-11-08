#Homework 2 Part 2
#Rachel Katz & Michael Simonds
import string
import math
from StemmingUtil import *

'''
	things to improve upon:
	
	stopWordsList gets parseTokened weirdly
'''
class Instance:
	
	def __init__(self, author, title=""):
		self.author = author
		self.title = title
		#frequency of unique words in text
		self.freqs ={}
		#probabilities for each value, same mapping as freqs
		self.probs = {}
		self.wordCount = 0
		
	def addProb(self, key, val):
		self.probs[key] = val
	
	def addFreq(self, key, val):
		self.freqs[key] = val

#create stopwords list from external .txt file and parses tokens on them returning a string
def createStopWords(fileName):
	stopWordsList = []
	
	file = open(fileName, "r")
	for line in file:
		line = line.replace("\n", "")		
		stopWordsList.append(line)
		

	print (stopWordsList)
	return stopWordsList

#ignores punctuation and 
def clean(word):
	
	translator = str.maketrans({key: None for key in string.punctuation})
	word = str(word).translate(translator)	
	#removing stop words and empty strings
	if(word!=""):
		return word
		
	return " "
		
#takes in a list of words and returns dictionary of frequency of each word
def count(wordList):
	freq = {}
	for word in wordList:
		if word in freq:
			freq[word] = freq[word]+1
		else:
			freq[word] = 1
	return freq

#takes in instance object and fills out probabilities table, returns updated object instance
def probabilities(objectInstance, allBooksWordCount):
	tempProbDict = {}
	for key in objectInstance.freqs:
		tempProbDict[key] = (objectInstance.freqs[key]+1)/(objectInstance.wordCount + allBooksWordCount)
	objectInstance.probs = tempProbDict
	return objectInstance

#takes in array with author and word list
#returns predicted label for that word list
def predictLabel(testSet, trainingList, totalWords):
	P_l = 1/10
	hiProb = -10000
	hiLabel = ""
	for instance in trainingList:
		sumProbs = 0
		for word in testSet:
			if (word in instance.probs):
				sumProbs = sumProbs + math.log(instance.probs[word])
			else:
				sumProbs = sumProbs + math.log(1/totalWords)
		curProb = math.log(P_l) + sumProbs
		if curProb > hiProb:
			hiProb = curProb
			hiLabel = instance.author
	return hiLabel
	
#takes in test tuple array and predictionsDict which is key actual, value predicted
def confuseMatrix(trainingList, predictionsList):
	matrix = []
	for i in range(0, len(trainingList)):
		matrix.append([0]*len(trainingList))
	labelsList = []
	#create labelsList to have proper indexing into matrix
	for object in trainingList:
		labelsList.append(object.author)
	#go through dictionary
	for tuple in predictionsList:
		actualIndex = labelsList.index(tuple[0])
		predIndex = labelsList.index(tuple[1])
		matrix[actualIndex][predIndex] += 1
	return (labelsList, matrix)
	
def testInstance(path, stops, set):
	file = open(path, "r", encoding="utf-8")
	fileList = file.read().splitlines()
	testDirectory = []
	tempEntry = ""
	curAuthor = ""
	count=0
	for i in range(0, len(fileList)):
		curLine = fileList[i]
		if (curLine!="" and curLine[0]=="#"):			
			curAuthor = fileList[i+1]			
			nextLine = " "			
			while (nextLine!="" and nextLine[0] != "#"):				
				tempEntry = tempEntry + nextLine + " "
				if (2+i+count)<len(fileList):
					nextLine = fileList[2+i+count]
				else:
					break
				count+=1			
			testDirectory.append([curAuthor, tempEntry])
			tempEntry=" "	
			count=0
	for passage in testDirectory:
		passageStr=" "
		for word in passage[1].split():
			word = clean(word.lower())
			
			if(word not in stops):
				passageStr = passageStr+" " +word
				set.add(word)
				
		passageStr = parseTokens(passageStr)
		#print("line 128, parseing/cleaning passageStr")
		#print("passageStr should be a list")
		#print("passageStr is: ", passageStr)
		
		
		#print("after cleaning: ", passageStr)
		passage[1] = createStems(passageStr)
	return testDirectory
		
		
		
		
def main():	
	
	#list of file names for books (in folder "Books") along with author
	books = [["PrideAndPrejudice", "Austen"], ["AliceInWonderland", "Carroll"], ["AnnaKarenina", "Tolstoy"], ["SherlockHolmes", "Doyle"], 
			["TheRepublic", "Plato"], ["TheTrial", "Kafka"], ["Dracula", "Stoker"], ["WarOfTheWorlds", "Wells"], ["GreatExpectations", "Dickens"], ["Odyssey", "Homer"]]
	#our test file is in "Books/test.txt"
	
	testFile = input("Enter the name of test file: ")
	
	#key is author and the value 
	attDict = {}
	#1. create stopWords list	
	stops = createStopWords("stopWords.txt")
	print(stops)
	#newStops = parseTokens(stops)
	#print(newStops)
	#each index is an instance of class Instance
	trainingList = []
	#2. read in each book and turn into string
	totalWordSet = set()
	testTuples = testInstance("Books/test.txt", stops,totalWordSet)	
	
	for book in books:
		print(book[0])
		fileName = "Books/" + book[0] + ".txt"
		file = open(fileName, "r", encoding="utf-8")
		author = book[1]
		title = book[0]
		bookString=" "
		instanceObject = Instance(author, title)
		f = file.read()
		
		for word in f.split():
			word= clean(word.lower())
			if(word not in stops):
				
				bookString = bookString +" "+ word
				totalWordSet.add(word)
		
		#print("bookString to pass into parseTokens is: \n", bookString)
		
		#Need to count unique words so add them all to a set 
			
		wordList = parseTokens(bookString)
		wordList = createStems(wordList)
		instanceObject.wordCount = len(wordList)
		
		instanceObject.freqs = count(wordList)
		trainingList.append(instanceObject)
		
	allBooksWordCount = len(totalWordSet)
	
	for i in range(0, len(trainingList)):
		trainingList[i] = probabilities(trainingList[i], allBooksWordCount)
		#instanceObject = probabilities(instanceObject)
		#print("adding instanceObject ", trainingList[i].author)
		
	#getting predictions for each test set and outputting matrix	
	
	#predictions dictionary: tuple where tuple[0] is actual and tuple[1] is predicted
	predictionsList = []
	for test in testTuples:
		predictionsList.append((test[0], predictLabel(test[1], trainingList, allBooksWordCount)))

	labelsList, matrix = confuseMatrix(trainingList, predictionsList)
	
	sumDiag = 0
	total = 0
	counter = 0
	
	for row in range(0, len(matrix)):
		for col in range(0, len(matrix[row])):
			total = total = matrix[row][col]
			if(row==col):
				sumDiag = sumDiag + matrix[row][col]
	print("done ")	
		
	list = []
	for label in labelsList:
		list.append(label)
	matrix.insert(0, list)
	for r in range(0, len(matrix)):
		for c in range (0, len(matrix[r])):
			if(c==0 and r!=0):
				matrix[r].append(labelsList[r-1])
				
	fname = "NaiveBayes"+".csv"
	print(fname)
	file = open(fname, "w")
	for rowss in matrix:
		st = ""
		for obj in rowss:
			st=st+str(obj)+","
		file.write(st[0:-1])
		file.write("\n")
        		
	
		
		
main()


		
	