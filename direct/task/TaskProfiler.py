# File: d (Python 2.4)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.StatePush import FunctionCall
from direct.showbase.PythonUtil import Averager

class TaskTracker:
    notify = directNotify.newCategory('TaskProfiler')
    MinSamples = None
    SpikeThreshold = None
    
    def __init__(self, namePrefix):
        self._namePrefix = namePrefix
        self._durationAverager = Averager('%s-durationAverager' % namePrefix)
        self._avgSession = None
        if TaskTracker.MinSamples is None:
            TaskTracker.MinSamples = config.GetInt('profile-task-spike-min-samples', 30)
            TaskTracker.SpikeThreshold = TaskProfiler.GetDefaultSpikeThreshold()
        

    
    def destroy(self):
        self.flush()
        del self._namePrefix
        del self._durationAverager

    
    def flush(self):
        self._durationAverager.reset()
        if self._avgSession:
            self._avgSession.release()
        
        self._avgSession = None

    
    def getNamePrefix(self, namePrefix):
        return self._namePrefix

    
    def _checkSpike(self, session):
        duration = session.getDuration()
        isSpike = False
        if self.getNumDurationSamples() > self.MinSamples:
            if duration > self.getAvgDuration() * self.SpikeThreshold:
                isSpike = True
                avgSession = self.getAvgSession()
                s = '\n%s task CPU spike profile (%s) %s\n' % ('=' * 30, self._namePrefix, '=' * 30)
                s += '|' * 80 + '\n'
                for sorts in ([
                    'cumulative'], [
                    'time'], [
                    'calls']):
                    s += '-- AVERAGE --\n%s-- SPIKE --\n%s' % (avgSession.getResults(sorts = sorts, totalTime = duration), session.getResults(sorts = sorts))
                
                self.notify.info(s)
            
        
        return isSpike

    
    def addProfileSession(self, session):
        duration = session.getDuration()
        if duration == 0.0:
            return None
        
        isSpike = self._checkSpike(session)
        self._durationAverager.addValue(duration)
        storeAvg = True
        if self._avgSession is not None:
            avgDur = self.getAvgDuration()
            if abs(self._avgSession.getDuration() - avgDur) < abs(duration - avgDur):
                storeAvg = False
            
        
        if storeAvg:
            if self._avgSession:
                self._avgSession.release()
            
            self._avgSession = session.getReference()
        

    
    def getAvgDuration(self):
        return self._durationAverager.getAverage()

    
    def getNumDurationSamples(self):
        return self._durationAverager.getCount()

    
    def getAvgSession(self):
        return self._avgSession

    
    def log(self):
        if self._avgSession:
            s = 'task CPU profile (%s):\n' % self._namePrefix
            s += '|' * 80 + '\n'
            for sorts in ([
                'cumulative'], [
                'time'], [
                'calls']):
                s += self._avgSession.getResults(sorts = sorts)
            
            self.notify.info(s)
        else:
            self.notify.info('task CPU profile (%s): no data collected' % self._namePrefix)



class TaskProfiler:
    notify = directNotify.newCategory('TaskProfiler')
    
    def __init__(self):
        self._enableFC = FunctionCall(self._setEnabled, taskMgr.getProfileTasksSV())
        self._enableFC.pushCurrentState()
        self._namePrefix2tracker = { }
        self._task = None

    
    def destroy(self):
        if taskMgr.getProfileTasks():
            self._setEnabled(False)
        
        self._enableFC.destroy()
        for tracker in self._namePrefix2tracker.itervalues():
            tracker.destroy()
        
        del self._namePrefix2tracker
        del self._task

    
    def GetDefaultSpikeThreshold():
        return config.GetFloat('profile-task-spike-threshold', 5.0)

    GetDefaultSpikeThreshold = staticmethod(GetDefaultSpikeThreshold)
    
    def SetSpikeThreshold(spikeThreshold):
        TaskTracker.SpikeThreshold = spikeThreshold

    SetSpikeThreshold = staticmethod(SetSpikeThreshold)
    
    def GetSpikeThreshold():
        return TaskTracker.SpikeThreshold

    GetSpikeThreshold = staticmethod(GetSpikeThreshold)
    
    def logProfiles(self, name = None):
        if name:
            name = name.lower()
        
        for (namePrefix, tracker) in self._namePrefix2tracker.iteritems():
            if name and name not in namePrefix.lower():
                continue
            
            tracker.log()
        

    
    def flush(self, name):
        if name:
            name = name.lower()
        
        for (namePrefix, tracker) in self._namePrefix2tracker.iteritems():
            if name and name not in namePrefix.lower():
                continue
            
            tracker.flush()
        

    
    def _setEnabled(self, enabled):
        if enabled:
            self.notify.info('task profiler started')
            self._taskName = 'profile-tasks-%s' % id(self)
            taskMgr.add(self._doProfileTasks, self._taskName, priority = -200)
        else:
            taskMgr.remove(self._taskName)
            del self._taskName
            self.notify.info('task profiler stopped')

    
    def _doProfileTasks(self, task = None):
        if self._task is not None and taskMgr._hasProfiledDesignatedTask():
            session = taskMgr._getLastTaskProfileSession()
            if session.profileSucceeded():
                namePrefix = self._task.getNamePrefix()
                if namePrefix not in self._namePrefix2tracker:
                    self._namePrefix2tracker[namePrefix] = TaskTracker(namePrefix)
                
                tracker = self._namePrefix2tracker[namePrefix]
                tracker.addProfileSession(session)
            
        
        self._task = taskMgr._getRandomTask()
        taskMgr._setProfileTask(self._task)
        return task.cont


