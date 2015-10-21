#!/usr/bin/env python

import uuid
import random
import threading
import json
import requests
import time
import sys


__author__ = "David Amies"
__copyright__ = "Copyright 2015, David Amies"
__credits__ = ["David Amies"]
__license__ = "GPL"
__version__ = "1.0.3"
__maintainer__ = "David Amies"
__email__ = "damies13@gmail.com"
__status__ = "Beta"



PrettyName = "KV Bench v"+__version__
finalkey = "All"

# top 100 nouns
nouns = ["time","issue","year","side","people","kind","way","head","day","house","man","service","thing","friend","woman",
		"father","life","power","child","hour","world","game","school","line","state","end","family","member","student","law",
		"group","car","country","city","problem","community","hand","name","part","president","place","team","case","minute",
		"week","idea","company","kid","system","body","program","information","question","back","work","parent","government",
		"face","number","others","night","level","Mr","office","point","door","home","health","water","person","room","art",
		"mother","war","area","history","money","party","storey","result","fact","change","month","morning","lot","reason",
		"right","research","study","girl","book","guy","eye","food","job","moment","word","air","business","teacher"]

threads = []
results = {}
bresults = []
sleephi = 1.0
sleeplo = 0.1

runDataPrime = True
runPhase1 = True
runPhase2 = True
runPhase3 = True


host = "http://127.0.0.1:5984"


sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=5000, pool_maxsize=5000)
sess.mount("http://", adapter)
gTimeout = 1200

urlPrefix = "/kvbench/"
url31SecondsSuffix = '_design/KVB/_view/seconds?reduce=false&startkey="{StartNum}"&endkey="{EndNum}"'
url32SummListSuffix = '_design/KVB/_view/summary?group=true'
url33SummarySuffix = '_design/KVB/_view/summary?reduce=false&startkey="{Summary}"&endkey="{Summary}"'

def saveresult(phase, type, result):
	global results
	if phase not in results:
		results[phase] = {}
	if type not in results[phase]:
		results[phase][type] = []
	if finalkey not in results[phase]:
		results[phase][finalkey] = []
	results[phase][finalkey].append(result)
	results[phase][type].append(result)

def GenerateSummary():
	# >>> random.sample([1, 2, 3, 4, 5],  3)  # Choose 3 elements
	# [4, 1, 5]
	# (1000*50)/100^2=5
	# (1000*50)/100^3=0.05
	# (2000*50)/100^2=10
	# wordcount = random.randint(2, 3)
	wordcount = 2
	summarywords = random.sample(nouns,  wordcount)
	summary = " ".join(summarywords)
	return summary

def GenerateDescription():
	# >>> random.sample([1, 2, 3, 4, 5],  3)  # Choose 3 elements
	# [4, 1, 5]
	paras = []
	paracount = random.randint(0, 5)
	for i in range(paracount):
		wordcount = random.randint(10, 90)
		summarywords = random.sample(nouns,  wordcount)
		summary = " ".join(summarywords)
		paras.append(summary)
	description = "\r\n".join(paras)
	return description



def StoreKV(threadid, phase):
	uu = uuid.uuid4()
	# 	Key: KVB_<ThreadId>_<UUID>
	key = 'KVB_'+str(threadid)+'_'+str(uu)
	val = {}
	val["key"] = key
	val["seconds"] = random.uniform(0, 30)
	val["summary"] = GenerateSummary()
	val["description"] = GenerateDescription()
	# print key
	# print json.dumps(val)
	url = host+urlPrefix+key
	# url = urlPrefix+key
	starttime = time.time()
	# r = requests.put(url, data=json.dumps(val))
	r = sess.put(url, data=json.dumps(val), timeout=gTimeout)
	endtime = time.time()
	saveresult(phase, "Write", endtime-starttime)
	retdata = r.json()


def ReadKV(threadid, phase, key):
	url = host+urlPrefix+key
	# url = urlPrefix+key
	starttime = time.time()
	# r = requests.get(url)
	r = sess.get(url, timeout=gTimeout)
	endtime = time.time()
	saveresult(phase, "Read", endtime-starttime)
	retdata = r.json()


def getSecondsKVs(threadid, phase):
	StartNum = 0
	EndNum = 9
	num0 = random.randint(StartNum, EndNum)
	if num0>3:
		StartNum = num0-1
		EndNum = num0
	else:
		StartNum = num0
		EndNum = num0+1
	# print "url31SecondsSuffix: "+url31SecondsSuffix
	urlSuffix = url31SecondsSuffix
	# print "urlSuffix: "+urlSuffix
	urlSuffix = urlSuffix.replace("{StartNum}", str(StartNum))
	# print "urlSuffix: "+urlSuffix
	urlSuffix = urlSuffix.replace("{EndNum}", str(EndNum))
	# print "urlSuffix: "+urlSuffix
	url = host+urlPrefix+urlSuffix
	# url = urlPrefix+urlSuffix
	# print "url: "+url
	starttime = time.time()
	# r = requests.get(url)
	r = sess.get(url, timeout=gTimeout)
	endtime = time.time()
	saveresult(phase, "Query 3.1", endtime-starttime)
	# print "r.json():"
	# print r.json()
	# print "json.loads(r):"
	# print json.loads(r.json())
	retdata = r.json()
	return retdata

def getSummaryKVs(threadid, phase, summary):
	urlSuffix = url33SummarySuffix
	urlSuffix = urlSuffix.replace("{Summary}", summary)
	url = host+urlPrefix+urlSuffix
	# url = urlPrefix+urlSuffix
	# print "url: "+url
	starttime = time.time()
	# r = requests.get(url)
	r = sess.get(url, timeout=gTimeout)
	endtime = time.time()
	saveresult(phase, "Query 3.3", endtime-starttime)
	retdata = r.json()
	return retdata


def getSummaryList(threadid, phase):
	url = host+urlPrefix+url32SummListSuffix
	# url = urlPrefix+url32SummListSuffix
	# print "url: "+url
	starttime = time.time()
	# r = requests.get(url)
	r = sess.get(url, timeout=gTimeout)
	endtime = time.time()
	saveresult(phase, "Query 3.2", endtime-starttime)
	retdata = r.json()
	return retdata



def DataPrimeThread(threadid):
	for i in range(2000):
		StoreKV(threadid, "DataPrime")
		# time.sleep(random.uniform(0.5, 1.5))

def DataPrime(threadcount):
	starttime = time.time()
	print "Started DataPrime("+str(threadcount)+") "+time.strftime("%x %X %Z")
	for i in range(threadcount):
		t = threading.Thread(target=DataPrimeThread, args=([i]))
		t.start()
		threads.append(t)
		# print "Started thread :"+str(i)

	for t in threads:
		if t.isAlive():
			t.join()
	print "Finished DataPrime("+str(threadcount)+") "+time.strftime("%x %X %Z")
	endtime = time.time()
	print "DataPrime took "+str(endtime-starttime)+" Seconds"

def Phase1Thread(threadid):
	phase = "Phase 1"
	for i in range(10):
		# 			1. Write 3 new Key Value pairs.
		for j in range(3):
			time.sleep(random.uniform(sleeplo, sleephi))
			StoreKV(threadid, phase)

		# 			2. Quety a list of documents based on seconds is between 2 values (3.1)
		# print "sleep"
		time.sleep(random.uniform(sleeplo, sleephi))
		# print "getSecondsKVs"
		ret = getSecondsKVs(threadid, phase)

		# 			3. Select 2 documents at random from list and retreive them
		if "rows" not in ret:
			print ret
		randret = random.sample(ret["rows"],  1)
		# print randret
		# print randret[0]['id']
		time.sleep(random.uniform(sleeplo, sleephi))
		ReadKV(threadid, phase, randret[0]['id'])

		# 			4. Write 3 new Key Value pairs.
		for j in range(3):
			time.sleep(random.uniform(sleeplo, sleephi))
			StoreKV(threadid, phase)

		# 			5. Quety a list of valid values for summary (3.2)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryList(threadid, phase)
		if "rows" not in ret:
			print ret
		# 			6. Write 3 new Key Value pairs.
		for j in range(3):
			time.sleep(random.uniform(sleeplo, sleephi))
			StoreKV(threadid, phase)

		# 			7. Quety a list of documents based on summary selected at random from previous list (3.3)
		randret = random.sample(ret["rows"],  1)
		# print randret
		# print randret[0]['key']
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryKVs(threadid, phase, randret[0]['key'])
		if "rows" not in ret:
			print ret
		# 			8. Select 2 documents at random from list and retreive them
		randret = random.sample(ret["rows"],  2)
		# print randret
		# print randret[0]['id']
		for j in range(2):
			time.sleep(random.uniform(sleeplo, sleephi))
			ReadKV(threadid, phase, randret[j]['id'])
		# 			9. Write 3 new Key Value pairs.
		for j in range(3):
			time.sleep(random.uniform(sleeplo, sleephi))
			StoreKV(threadid, phase)

		# print "Phase1Thread("+str(threadid)+") completed i: "+str(i)+"	"++time.strftime("%x %X %Z")
		sys.stdout.write(".")


def Phase1(threadcount):
	starttime = time.time()
	print "Started Phase 1("+str(threadcount)+") "+time.strftime("%x %X %Z")
	for i in range(threadcount):
		t = threading.Thread(target=Phase1Thread, args=([i]))
		t.start()
		threads.append(t)
		time.sleep(1)
		# print "Started thread :"+str(i)
	for t in threads:
		if t.isAlive():
			t.join()
	print "."
	print "Finished Phase 1("+str(threadcount)+") "+time.strftime("%x %X %Z")
	endtime = time.time()
	print "Phase 1 took "+str(endtime-starttime)+" Seconds"


def Phase2Thread(threadid):
	phase = "Phase 2"
	for i in range(10):
		# 			1. Write a new Key Value pair.
		StoreKV(threadid, phase)

		# 			2. Quety a list of documents based on seconds is between 2 values (3.1) x2
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSecondsKVs(threadid, phase)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSecondsKVs(threadid, phase)

		# 			3. Select a document at random from list and retreive it
		if "rows" not in ret:
			print ret
		randret = random.sample(ret["rows"],  1)
		time.sleep(random.uniform(sleeplo, sleephi))
		ReadKV(threadid, phase, randret[0]['id'])

		# 			4. Quety a list of valid values for summary (3.2) x3
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryList(threadid, phase)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryList(threadid, phase)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryList(threadid, phase)

		if "rows" not in ret:
			print ret

		# 			5. Quety a list of documents based on summary selected at random from previous list (3.3)
		randret = random.sample(ret["rows"],  1)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryKVs(threadid, phase, randret[0]['key'])
		if "rows" not in ret:
			print ret

		# 			6. Select a document at random from list and retreive it
		randret = random.sample(ret["rows"],  1)
		time.sleep(random.uniform(sleeplo, sleephi))
		ReadKV(threadid, phase, randret[0]['id'])
		sys.stdout.write(".")


def Phase2(threadcount):
	starttime = time.time()
	print "Started Phase 2("+str(threadcount)+") "+time.strftime("%x %X %Z")
	for i in range(threadcount):
		t = threading.Thread(target=Phase2Thread, args=([i]))
		t.start()
		threads.append(t)
		time.sleep(1)
		# print "Started thread :"+str(i)
	for t in threads:
		if t.isAlive():
			t.join()
	print "."
	print "Finished Phase 2("+str(threadcount)+") "+time.strftime("%x %X %Z")
	endtime = time.time()
	print "Phase 2 took "+str(endtime-starttime)+" Seconds"


def Phase3Thread(threadid):
	phase = "Phase 3"
	for i in range(10):
		# 			1. Write a new Key Value pair.
		StoreKV(threadid, phase)

		# 			2. Quety a list of documents based on seconds is between 2 values (3.1)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSecondsKVs(threadid, phase)

		# 			3. Select 5 documents at random from list and retreive them
		if "rows" not in ret:
			print ret
		randret = random.sample(ret["rows"],  5)
		for j in range(5):
			time.sleep(random.uniform(sleeplo, sleephi))
			ReadKV(threadid, phase, randret[j]['id'])

		# 			5. Quety a list of valid values for summary (3.2)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryList(threadid, phase)
		if "rows" not in ret:
			print ret

		# 			5. Quety a list of documents based on summary selected at random from previous list (3.3)
		randret = random.sample(ret["rows"],  1)
		time.sleep(random.uniform(sleeplo, sleephi))
		ret = getSummaryKVs(threadid, phase, randret[0]['key'])
		if "rows" not in ret:
			print ret

		# 			6. Select 5 documents at random from list and retreive them
		randret = random.sample(ret["rows"],  5)
		for j in range(5):
			time.sleep(random.uniform(sleeplo, sleephi))
			ReadKV(threadid, phase, randret[j]['id'])
		sys.stdout.write(".")


def Phase3(threadcount):
	starttime = time.time()
	print "Started Phase 3("+str(threadcount)+") "+time.strftime("%x %X %Z")
	for i in range(threadcount):
		t = threading.Thread(target=Phase3Thread, args=([i]))
		t.start()
		threads.append(t)
		time.sleep(1)
		# print "Started thread :"+str(i)
	for t in threads:
		if t.isAlive():
			t.join()
	print "."
	print "Finished Phase 3("+str(threadcount)+") "+time.strftime("%x %X %Z")
	endtime = time.time()
	print "Phase 3 took "+str(endtime-starttime)+" Seconds"




if runDataPrime:
	DataPrime(100)
if runPhase1:
	Phase1(50)
if runPhase2:
	Phase2(50)
if runPhase3:
	Phase3(50)

if "DataPrime" in results:
	del results["DataPrime"]

# print results
skeys1 = results.keys()
skeys1.sort()
for k1 in skeys1:
	print k1
	if finalkey in results[k1]:
		bresults.append(sum(results[k1][finalkey])/float(len(results[k1][finalkey])))

	skeys2 = results[k1].keys()
	skeys2.sort()
	for k2 in skeys2:
		print "	"+k2 +" : "+ str(sum(results[k1][k2])/float(len(results[k1][k2])))


print PrettyName+" score: "+str(sum(bresults)/float(len(bresults)))
