# !/usr/bin/env python
## ABOUT -----
# o simulates NServers servers , plus a queue of Job s waiting to use them .
# o usage : python MBk.py NServers NCostumers ArrRate ServRate Policy  SimTime SetupOFFtime ServiceDistribution (the last two arguments are optional)
# o expansion of the MMk.py from the ' Introduction to Discrete Event and and SimPy Language', Norm Matloff, February 2008.
#
# Date : 28/4/2013
# Lykourgos Kekempanos
# University of Patras, Computer Engneering & Informatics
## ENDABOUT ---

from SimPy.Simulation import *
from random import Random, expovariate 

# globals
class G:
 	Rnd = Random(12345)
 	# server distribution - default value
	ServerDistribution = 'exponential'
	# setup time  for offstate - default value
	setup_OFFtime = 1.0
	# power consumption for busy, idle and offstates
	pBusy = 240.0
	pIdle = 160.0
	pOff = 0.0

class ServerClass(Process):
	SrvRate = None # r e c i p r o c a l of mean service time
	Busy = [] # busy servers
	NonBusy = [] # NonBusy servers
	Queue = [] # queue for the costumers
	TotWait = 0.0 # total wait time of all jobs done so far , including both queuing and service times
	QueueWait = 0.0 # queuing wait time
	NDone = 0 # number of Jobs done so far
	WaitMon = Monitor()
	
	def __init__(self,sPolicy,ServerID):
		Process.__init__(self)
		if (sPolicy == "BUSYIDLE"):
		 	self.state = "IDLE"
		elif (sPolicy == "BUSYOFF"):
		 	self.state = "OFF"
		self.name = "Server%02d" % (ServerID)
		self.power = 0.0
		self.time = 0.0
		ServerClass.NonBusy.append(self) # starts NonBusy
		
	def Run(self, modelPolicy):
		while 1:
			# "sleep" until this machine awakened
			yield passivate, self
			ServerClass.NonBusy.remove(self)
			ServerClass.Busy.append(self)
			# take Job s from the queue as long as there are some there
			while ServerClass.Queue != []:
				if (self.state == "OFF") :
					# setup time
					yield hold, self, G.setup_OFFtime
					# power penalty
					self.power += G.pBusy*G.setup_OFFtime
					# empty costumers queue ?
					if ServerClass.Queue == []:
						break;
				elif (self.state == "IDLE"):
					self.time = now() - self.time
					self.power += G.pIdle*self.time
				# get the job
				J = ServerClass.Queue.pop(0)
				# monitor the costumers queue size
				ServerClass.QueueWait += now() - J.ArrivalTime
				ServerClass.WaitMon.observe(y=len(ServerClass.Queue))
				# change serverstate
				self.state = "BUSY"
				# do the work
				if (G.ServerDistribution == 'exponential'):
					ServiceTime = G.Rnd.expovariate(ServerClass.SrvRate)
				elif (G.ServerDistribution == 'constant'):
					ServiceTime = ServerClass.SrvRate
				yield hold,self,ServiceTime
				# power consumption during busy state
				self.power += G.pBusy*ServiceTime
				# total time
				ServerClass.NDone += 1
				ServerClass.TotWait += now() - J.ArrivalTime
				self.time = now()
			if(modelPolicy == "BUSYIDLE"):
				self.state = "IDLE"
				self.time = now()
			elif ( modelPolicy == "BUSYOFF"):
				self.state = "OFF"
			ServerClass.Busy.remove(self)
			ServerClass.NonBusy.append(self)
		
class Jobclass:

	def __init__(self):
		self.ArrivalTime = now()
	
class ArrivalClass(Process):
	ArvRate = None

	def __init__(self):
		Process.__init__(self)

	def Run(self, NumCostumers, STime):
		if (STime == 'EndSimulation'):
			# user determines the number of costumers
			for _ in range(NumCostumers):
				# wait for arrival of next job
				yield hold, self, G.Rnd.expovariate(ArrivalClass.ArvRate)
				J = Jobclass()
				ServerClass.Queue.append(J)
				# any machine ready ?
				if ServerClass.NonBusy != []:
					reactivate (ServerClass.NonBusy[0])
				else:
					# create costumers determined by the simulation time
					while 1:
					# wait for a r r i v a l of next job
						yield hold,self,G.Rnd.expovariate(ArrivalClass.ArvRate)
						J = Jobclass()
						ServerClass.Queue.append(J)
						# any machine ready ?
						if ServerClass.NonBusy != []:
							reactivate(ServerClass.NonBusy[0])

def model(NServers,NCostumers,ArrRate,ServRate,Policy,SimTime,*ArgSetup):
	# arguments validation
	if NServers <= 0:
		sys.exit('ERROR\n\n NServers options :\n The number of servers must be >= 1')
	
	if NCostumers <= 0:
	 	sys.exit('ERROR\n\n NCostumers options :\n The number of costumers must be >= 1')
	
	if ArrRate <= 0:
	 	sys.exit('ERROR\n\n ArrRate options :\n The arrival rate must be > 0')

	if ServRate <= 0:
	 	sys.exit('ERROR\n\n ServRate options :\n The service rate must be > 0')
	
	if ( Policy != 'BUSYIDLE' and Policy != 'BUSYOFF' ) :
		sys.exit('ERROR\n\n Policy options :\n 1) BUSYIDLE or \n 2) BUSYOFF')
	
	if SimTime != 'EndSimulation':
	 	try:
	 		SimTime = int(SimTime)
	 	except ValueError:
	 		sys.exit('ERROR\n\nSimTime options :\n 1) EndSimulation or \n 2) Positive number')
	 	if ( SimTime < 0) :
	 		sys.exit('ERROR\n\nSimTime options :\n 1) EndSimulation or \n 2) Positive number')
	
	 	if (len(ArgSetup) > 2):
	 		sys.exit('ERROR \n \nHow to c a l l model ( ) : \nmodel ( NServers, NCostumers, ArrRate, ServRate, Policy, SimTime, SetupOFFtime, ServiceDistribution )\nThe last 2 arguments are optional')
	
	 	if (len(ArgSetup) > 0):
	 		try:
	 			G.setup_OFFtime = int(ArgSetup[0])
	 		except ValueError :
	 			sys.exit( 'ERROR\n\nSetup time for BUSY/OFF Policy must be a non negative number\n')
	 		if (G. setup_OFFtime < 0) :
	 			sys.exit( 'ERROR\n\nSetup time for BUSY/OFF Policy must be a non negative number\n')
	 		if (len(ArgSetup) > 1):
				if ( ArgSetup[1] != 'constant' and ArgSetup[1] != 'exponential'):
	 				sys.exit( 'ERROR\n\nAvailable ServiceDistribution s are :\n 1) exponential \n 2) constant \n ' )
			G.ServerDistribution = ArgSetup[1]
	
	# initialization
	G.Rnd.seed (12345)
	ArrivalClass.ArvRate = ArrRate
	ServerClass.SrvRate = ServRate
	ServerClass.TotWait = 0.0
	ServerClass.QueueWait = 0.0
	ServerClass.NDone = 0
	ServerClass.Queue = []
	ServerClass.Busy = []
	ServerClass.NonBusy = []
	ServerClass.WaitMon = Monitor()
	maxTime = SimTime
	
	# start simulation
	initialize()
	for i in range(NServers):
		M = ServerClass(Policy,i)
		activate(M,M.Run(Policy))
	A = ArrivalClass()
	activate(A,A.Run(NCostumers,SimTime))
	simulate(maxTime)
	
	# metrics

	# number of servers served
	NCostumers = ServerClass.NDone
	# utilization
	utilization = round(ArrRate/float(NServers*ServRate),4)
	# mean queuing time
	meanQT = round(ServerClass.QueueWait/ServerClass.NDone,4)
	# mean response time
	meanRT = round(ServerClass.TotWait/ServerClass.NDone,4)
	# mean power consumption
	powerCons = 0
	if (maxTime == "EndSimulation"):
		for i in range (NServers):
			powerCons += ServerClass.NonBusy[i].power
	else:
		mergedList = ServerClass.Busy+ServerClass.NonBusy
		for i in range (NServers):
			powerCons += mergedList[i].power
	meanPC = round (powerCons/float(NServers),4)
	# Energy Response time Product
	ERP = round (meanPC*meanRT,4)

	# simulation results
	print "Simulation Results \n"
	print "Policy : ", Policy
	print "Number of servers : ", NServers
	print "Number of Costumers : ", NCostumers
	print "Arrival Rate : ", ArrRate
	print "service Rate : ", ServRate
	print "utilization : ", utilization
	print "Mean Response Time : ", meanRT
	print "Mean Queuing Time : ", meanQT
	print "Mean Power Consumption : ", meanPC
	print "ERP : ", ERP
	print "\n---\n"

	# recorded data values  queue length
	QueueMonitorValues = ServerClass.WaitMon.yseries()
	
	return meanRT,meanPC,ERP,ArrRate,QueueMonitorValues		   

def main():
	if (len(sys.argv)==7):
		uServers = int(sys.argv[1])
		uCostumers = int(sys.argv[2])
		uArrivalRate = float(sys.argv[3])
		uServiceRate = float(sys.argv[4])
		uPolicy = str(sys.argv[5]) #BUSYIDLE or BUSYOFF
		uSimTime = str(sys.argv[6])
		
		model(uServers,uCostumers,uArrivalRate,uServiceRate,uPolicy,uSimTime)
	elif (len (sys.argv) >= 8) and (len(sys.argv) <= 9) :
		uServers = int(sys.argv[1])
		uCostumers = int(sys.argv[2])
		uArrivalRate = float(sys.argv[3])
		uServiceRate = float(sys.argv[4])
		uPolicy = str(sys.argv[5]) #BUSYIDLE or BUSYOFF
		uSimTime = str(sys.argv[6])
		
		# optional arguments
		moreArgs = []
		for i in range (7,len(sys.argv)) :
			try :
				moreArgs.append(sys.argv [i])
			except IndexError :
				moreArgs[i] = None
		model(uServers, uCostumers, uArrivalRate , uServiceRate , uPolicy, uSimTime , *moreArgs)
	else:
		sys.exit("ERROR \n\nHow to execute : \npython MBk.py NServers NCostumers ArrRate ServRate Policy SimTime SetupOFFtime ServiceDistribution \nThe last 2 arguments are optional")

# enable import
if __name__ == '__main__':main()
