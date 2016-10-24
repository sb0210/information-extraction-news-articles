import csv
from math import *

"""--------------------------------------------------------------------------------------------------------
File Input-Output
--------------------------------------------------------------------------------------------------------"""

f_w=open("final_ouput.txt","w")
f_c=open("countries_id_map.txt","r")
f_c_o=open("countries_id_map_orig.txt","r")
f_t=open("target-relations.tsv","r")
f_k=open("selected_indicators","r")
f_s=open("sentences.tsv","r")
f_f=open("kb-facts-train_SI.tsv","r")

"""--------------------------------------------------------------------------------------------------------
Dictionaries
--------------------------------------------------------------------------------------------------------"""

country_map=dict()
country_map_from_code=dict()
country_facts=dict()
keyword_list=dict()
targets_list=[]

"""--------------------------------------------------------------------------------------------------------
Classes
--------------------------------------------------------------------------------------------------------"""
#Class Country
class Country:
	def __init__(self,c_id) :
		self.lists=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
		self.id=c_id

	def __str__(self):
		return self.name

#Class Keyword
class Keyword:
	def __init__(self,name):
		self.name=name
		self.lists=[]

	def __str__(self):
		return self.name

"""--------------------------------------------------------------------------------------------------------
Functions
--------------------------------------------------------------------------------------------------------"""

#Function - convert string to float
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

#Function - Giving initial confidence to sentences 
def initial_confidence(n,N):
	try:
		if N==0:
			return 0
		if N-n >0:
			d=(N-n)/N
		else: 
			d=(n-N)/N	
		return 0.55*(2.7**(-1*20*d*d))
	except:
		return 0

#Function - Giving the final confidence to the sentences depending on the matchings found in the sentences and target
def matching(sentence_string,keyword_parameter,init):
	try:
		count=0
		for keywords in keyword_list[keyword_parameter].lists:
			if keywords in sentence_string:
				count=count+1
		final_confidence=1-(1-init)*(2**(-1*count))
		if count==0:
			final_confidence=final_confidence/1.5
		return round(final_confidence,2)		
	except:
		return 0

#Function - To check each sentence and allot Relation and confidence to them
def allot(sentence_id,sentence_string,sentence_numbers_array,sentence_countries_array):
	try:
		count=0
		f=0
		coi=0;
		for country in sentence_countries_array:
			for number in sentence_numbers_array:
				if not isfloat(number):
					continue
				number=float(number)
				if number<0:
					number=-1*number
				if number==0:
					continue			
				if number >1:
					digit = ceil(log10(number))
				elif number <=1 and number >= -1:
					digit = 0
				else :
					digit = ceil(log10(-1*number))	 
				targets={k:[0,0] for k in targets_list}
				if digit==0:
					final_list = country_facts[country_map[country]].lists[digit] + country_facts[country_map[country]].lists[digit+1]
				else:
					final_list = country_facts[country_map[country]].lists[digit] + country_facts[country_map[country]].lists[digit+1] + country_facts[country_map[country]].lists[digit-1]
				for tuples in final_list:
					if ((tuples[0]-number)/number) <= 0.3 and ((tuples[0]-number)/number) >= -0.3:
						init=initial_confidence(tuples[0],number)
						final_confidence=matching(sentence_string,tuples[1],init)
						if final_confidence>=0.6:
							coi=1
						if targets[tuples[1]][0]<final_confidence:
							targets[tuples[1]][0]=final_confidence
							targets[tuples[1]][1]=tuples[0]
						count=1

				for targ,confi in targets.items():
					if coi==0:
						if confi[0]>=0.32:
							string=sentence_id+"\t"+country_map_from_code[country_map[country]]+"\t"+targ+"\t"+str(number)+"\t"+str(confi[1])+"\t"+str(confi[0])+"\n"
							f_w.write(string)
							f=2
					else:
						if confi[0]>=0.5:
							string=sentence_id+"\t"+country_map_from_code[country_map[country]]+"\t"+targ+"\t"+str(number)+"\t"+str(confi[1])+"\t"+str(confi[0])+"\n"
							f_w.write(string)
							f=2
										
		if count==0 or f==0:
			string=sentence_id+"\t"+"no country matching found"+"\n"
			f_w.write(string)
		f_w.write("\n")
	except:
		pass

"""--------------------------------------------------------------------------------------------------------
Reading the data and initialising objects
--------------------------------------------------------------------------------------------------------"""

#Reading the country_id_map.txt and relating countries with country code
reader_c = csv.reader(f_c,dialect="excel-tab")
for row in reader_c:
	try:
		country_map[row[1]]=row[0]
		if row[0] not in country_facts:
			country_facts[row[0]]=Country(row[0])
	except:
		pass		
f_c.close()	

#Reading the country_id_map.txt and relating countries with country code
reader_c = csv.reader(f_c_o,dialect="excel-tab")
for row in reader_c:
	country_map_from_code[row[0]]=row[1]
f_c.close()	


#Reading the kb-facts-train.tsv (facts) and adding the facts in the countries
reader_f = csv.reader(f_f,dialect="excel-tab")
for row in reader_f:
	try:
		tup=(float(row[1]),row[2])
		if float(row[1])>1:
			if tup not in country_facts[row[0]].lists[ceil(log10(float(row[1])))]:
				country_facts[row[0]].lists[ceil(log10(float(row[1])))].append(tup)
		elif -1<=float(row[1]) and float(row[1])<=1:
			if tup not in country_facts[row[0]].lists[0]:
				if float(row[1]) < 0:
					tup=(-1*float(row[1]),row[2])				
				country_facts[row[0]].lists[0].append(tup)
		else:
			if tup not in country_facts[row[0]].lists[ceil(log10(-1*float(row[1])))]:		
				if float(row[1]) < 0:
					tup=(-1*float(row[1]),row[2])				
				country_facts[row[0]].lists[ceil(log10(-1*float(row[1])))].append(tup)
	except:
		pass			
f_f.close()		
		 

#Reading targets
reader_t=csv.reader(f_t,dialect="excel-tab")
for row1 in reader_t:
	try:
		keyword_list[row1[0]]=Keyword(row1[0])
		targets_list.append(row1[0])
	except:
		pass	
f_t.close()

#Reading the indicators and pushing in the list of targets
reader_k=csv.reader(f_k,dialect="excel-tab")
for row in reader_k:
	try:
		target=""
		for target,sent in keyword_list.items():
			if target in row:
				break
		for col in row:
			if col != target:
				keyword_list[target].lists.append(col)
	except:
		pass			
f_k.close()			

#Reading the sentence one by one, applying "allot" function writing in the final-output file
reader_s=csv.reader(f_s,dialect="excel-tab")
for row in reader_s:
	try:
		sid=row[0]
		ss=row[1]
		sn=row[2]
		sc=row[3]
		ss=ss.lower()
		snu=sn.replace(" ","")
		scu=sc.replace(" ","")
		sna=snu.split(",")
		sca=scu.split(",")
		snau=[]
		scau=[]

		for country in sca:
			if country_map_from_code[country_map[country]] not in scau:
				scau.append(country_map_from_code[country_map[country]])

		for num in sna:
			if num not in snau:
				snau.append(num)
		allot(sid,ss,snau,scau)
	except:
		pass	
f_s.close()
