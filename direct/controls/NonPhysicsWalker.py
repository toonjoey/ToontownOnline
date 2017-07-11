# File: d (Python 2.4)

from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.showbase.InputStateGlobal import inputState
from direct.task.Task import Task
from pandac.PandaModules import *

class NonPhysicsWalker(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('NonPhysicsWalker')
    wantDebugIndicator = base.config.GetBool('want-avatar-physics-indicator', 0)
    slideName = 'slide-is-disabled'
    
    def __init__(self):
        DirectObject.DirectObject.__init__(self)
        self.worldVelocity = Vec3.zero()
        self.collisionsActive = 0
        self.speed = 0.0
        self.rotationSpeed = 0.0
        self.slideSpeed = 0.0
        self.vel = Vec3(0.0, 0.0, 0.0)
        self.stopThisFrame = 0

    
    def setWalkSpeed(self, forward, jump, reverse, rotate):
        self.avatarControlForwardSpeed = forward
        self.avatarControlReverseSpeed = reverse
        self.avatarControlRotateSpeed = rotate

    
    def getSpeeds(self):
        return (self.speed, self.rotationSpeed, self.slideSpeed)

    
    def setAvatar(self, avatar):
        self.avatar = avatar
        if avatar is not None:
            pass
        1

    
    def setAirborneHeightFunc(self, getAirborneHeight):
        self.getAirborneHeight = getAirborneHeight

    
    def setWallBitMask(self, bitMask):
        self.cSphereBitMask = bitMask

    
    def setFloorBitMask(self, bitMask):
        self.cRayBitMask = bitMask

    
    def swapFloorBitMask(self, oldMask, newMask):
        self.cRayBitMask = self.cRayBitMask & ~oldMask
        self.cRayBitMask |= newMask
        if self.cRayNodePath and not self.cRayNodePath.isEmpty():
            self.cRayNodePath.node().setFromCollideMask(self.cRayBitMask)
        

    
    def initializeCollisions(self, collisionTraverser, avatarNodePath, avatarRadius = 1.3999999999999999, floorOffset = 1.0, reach = 1.0):
        self.cTrav = collisionTraverser
        self.avatarNodePath = avatarNodePath
        self.cSphere = CollisionSphere(0.0, 0.0, 0.0, avatarRadius)
        cSphereNode = CollisionNode('NPW.cSphereNode')
        cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = avatarNodePath.attachNewNode(cSphereNode)
        cSphereNode.setFromCollideMask(self.cSphereBitMask)
        cSphereNode.setIntoCollideMask(BitMask32.allOff())
        self.cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        cRayNode = CollisionNode('NPW.cRayNode')
        cRayNode.addSolid(self.cRay)
        self.cRayNodePath = avatarNodePath.attachNewNode(cRayNode)
        cRayNode.setFromCollideMask(self.cRayBitMask)
        cRayNode.setIntoCollideMask(BitMask32.allOff())
        self.pusher = CollisionHandlerPusher()
        self.pusher.setInPattern('enter%in')
        self.pusher.setOutPattern('exit%in')
        self.lifter = CollisionHandlerFloor()
        self.lifter.setInPattern('on-floor')
        self.lifter.setOutPattern('off-floor')
        self.lifter.setOffset(floorOffset)
        self.lifter.setReach(reach)
        self.lifter.setMaxVelocity(16.0)
        self.pusher.addCollider(self.cSphereNodePath, avatarNodePath)
        self.lifter.addCollider(self.cRayNodePath, avatarNodePath)
        self.setCollisionsActive(1)

    
    def deleteCollisions(self):
        del self.cTrav
        del self.cSphere
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath
        del self.cRay
        self.cRayNodePath.removeNode()
        del self.cRayNodePath
        del self.pusher
        del self.lifter

    
    def setTag(self, key, value):
        self.cSphereNodePath.setTag(key, value)

    
    def setCollisionsActive(self, active = 1):
        if self.collisionsActive != active:
            self.collisionsActive = active
            if active:
                self.cTrav.addCollider(self.cSphereNodePath, self.pusher)
                self.cTrav.addCollider(self.cRayNodePath, self.lifter)
            else:
                self.cTrav.removeCollider(self.cSphereNodePath)
                self.cTrav.removeCollider(self.cRayNodePath)
                self.oneTimeCollide()
        

    
    def placeOnFloor(self):
        pass

    
    def oneTimeCollide(self):
        tempCTrav = CollisionTraverser('oneTimeCollide')
        tempCTrav.addCollider(self.cSphereNodePath, self.pusher)
        tempCTrav.addCollider(self.cRayNodePath, self.lifter)
        tempCTrav.traverse(render)

    
    def addBlastForce(self, vector):
        pass

    
    def displayDebugInfo(self):
        onScreenDebug.add('controls', 'NonPhysicsWalker')

    
    def _calcSpeeds(self):
        forward = inputState.isSet('forward')
        reverse = inputState.isSet('reverse')
        turnLeft = inputState.isSet('turnLeft')
        turnRight = inputState.isSet('turnRight')
        if not inputState.isSet(self.slideName):
            pass
        slide = 0
        if base.localAvatar.getAutoRun():
            forward = 1
            reverse = 0
        
        if (forward or self.avatarControlForwardSpeed) and reverse:
            pass
        self.speed = -(self.avatarControlReverseSpeed)
        if slide:
            if not reverse and turnLeft or -(self.avatarControlReverseSpeed) * 0.75:
                if not reverse and turnRight or self.avatarControlReverseSpeed * 0.75:
                    if (turnLeft or -(self.avatarControlForwardSpeed) * 0.75) and turnRight:
                        pass
        self.slideSpeed = self.avatarControlForwardSpeed * 0.75
        if not slide:
            if (turnLeft or self.avatarControlRotateSpeed) and turnRight:
                pass
        self.rotationSpeed = -(self.avatarControlRotateSpeed)

    
    def handleAvatarControls(self, task):
        if not self.lifter.hasContact():
            messenger.send('walkerIsOutOfWorld', [
                self.avatarNodePath])
        
        self._calcSpeeds()
        if self.wantDebugIndicator:
            self.displayDebugInfo()
        
        dt = ClockObject.getGlobalClock().getDt()
        if self.speed and self.slideSpeed or self.rotationSpeed:
            if self.stopThisFrame:
                distance = 0.0
                slideDistance = 0.0
                rotation = 0.0
                self.stopThisFrame = 0
            else:
                distance = dt * self.speed
                slideDistance = dt * self.slideSpeed
                rotation = dt * self.rotationSpeed
            self.vel = Vec3(Vec3.forward() * distance + Vec3.right() * slideDistance)
            if self.vel != Vec3.zero():
                rotMat = Mat3.rotateMatNormaxis(self.avatarNodePath.getH(), Vec3.up())
                step = rotMat.xform(self.vel)
                self.avatarNodePath.setFluidPos(Point3(self.avatarNodePath.getPos() + step))
            
            self.avatarNodePath.setH(self.avatarNodePath.getH() + rotation)
            messenger.send('avatarMoving')
        else:
            self.vel.set(0.0, 0.0, 0.0)
        self._NonPhysicsWalker__oldPosDelta = self.avatarNodePath.getPosDelta(render)
        self._NonPhysicsWalker__oldDt = dt
        
        try:
            self.worldVelocity = self._NonPhysicsWalker__oldPosDelta * (1 / self._NonPhysicsWalker__oldDt)
        except:
            self.worldVelocity = 0

        return Task.cont

    
    def doDeltaPos(self):
        pass

    
    def reset(self):
        pass

    
    def getVelocity(self):
        return self.vel

    
    def enableAvatarControls(self):
        taskName = 'AvatarControls-%s' % (id(self),)
        taskMgr.remove(taskName)
        taskMgr.add(self.handleAvatarControls, taskName)

    
    def disableAvatarControls(self):
        taskName = 'AvatarControls-%s' % (id(self),)
        taskMgr.remove(taskName)

    
    def flushEventHandlers(self):
        if hasattr(self, 'cTrav'):
            self.pusher.flush()
        
        self.lifter.flush()


