## ABOUT ------
# o experiment model using the MBk.py
# o usage : python ExModelc.py
#
# Date : 28/4/2013
# Lykourgos Kekempanos
# University of Patras, Computer Engneering & Informatics
## ENDABOUT ---

from MBk import model
import pylab as pyl

## Execute Model
NJobs = 1000
ArrivalRate = 1
ServiceRate = 1
ServerPolicy1 = 'BUSYIDLE'
ServerPolicy2 = 'BUSYOFF'
SimulationTime = 'EndSimulation'

out = model(10, NJobs, ArrivalRate, ServiceRate, ServerPolicy1, SimulationTime , 1, 'constant')

## Figures
pyl.figure(figsize = (7,5.5))

pyl.clf()
n, bins, patches = pyl.hist(out[4], 10, normed= False, label = ServerPolicy1 , color = 'red')
pyl.title('Model : queue length over time')
pyl.xlabel('queue length', fontsize = 9 , fontweight='bold')
pyl.ylabel('frequency' , fontsize = 9 , fontweight='bold')
pyl.legend()
pyl.grid(True)
pyl.xlim(0,max(out[4])+5)
pyl.savefig(r'histogram_'+ServerPolicy1+'.eps')

out = model (10 , NJobs , ArrivalRate , ServiceRate , ServerPolicy2, SimulationTime , 1 , 'constant')

pyl.clf()
n , bins , patches =  pyl.hist(out[4], 10, normed= False, label = ServerPolicy2, color = 'blue')
pyl.title('Model : queue length over time' )
pyl.xlabel('queue length', fontsize=9, fontweight='bold')
pyl.ylabel('frequency ', fontsize=9, fontweight='bold')
pyl.legend()
pyl.grid (True)
pyl.xlim(0,max(out[4])+5)
pyl.savefig(r'histogram_'+ServerPolicy2+'.eps')
