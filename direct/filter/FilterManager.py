# File: d (Python 2.4)

from pandac.PandaModules import Point3, Vec3, Vec4
from pandac.PandaModules import NodePath, PandaNode
from pandac.PandaModules import RenderState, Texture, Shader
from pandac.PandaModules import CardMaker
from pandac.PandaModules import TextureStage
from pandac.PandaModules import GraphicsPipe, GraphicsOutput
from pandac.PandaModules import WindowProperties, FrameBufferProperties
from pandac.PandaModules import Camera, DisplayRegion
from pandac.PandaModules import OrthographicLens
from pandac.PandaModules import AuxBitplaneAttrib
from direct.directnotify.DirectNotifyGlobal import *
from direct.showbase.DirectObject import DirectObject
__all__ = [
    'FilterManager']

class FilterManager(DirectObject):
    notify = None
    
    def __init__(self, win, cam, forcex = 0, forcey = 0):
        if FilterManager.notify == None:
            FilterManager.notify = directNotify.newCategory('FilterManager')
        
        region = None
        for i in range(win.getNumDisplayRegions()):
            dr = win.getDisplayRegion(i)
            drcam = dr.getCamera()
            if drcam == cam:
                region = dr
                continue
        
        if region == None:
            self.notify.error('Could not find appropriate DisplayRegion to filter')
            return False
        
        self.win = win
        self.forcex = forcex
        self.forcey = forcey
        self.engine = win.getGsg().getEngine()
        self.region = region
        self.wclears = self.getClears(self.win)
        self.rclears = self.getClears(self.region)
        self.camera = cam
        self.caminit = cam.node().getInitialState()
        self.camstate = self.caminit
        self.buffers = []
        self.sizes = []
        self.nextsort = self.win.getSort() - 1000
        self.basex = 0
        self.basey = 0
        self.accept('window-event', self.resizeBuffers)

    
    def getClears(self, region):
        clears = []
        for i in range(GraphicsOutput.RTPCOUNT):
            clears.append((region.getClearActive(i), region.getClearValue(i)))
        
        return clears

    
    def setClears(self, region, clears):
        for i in range(GraphicsOutput.RTPCOUNT):
            (active, value) = clears[i]
            region.setClearActive(i, active)
            region.setClearValue(i, value)
        

    
    def setStackedClears(self, region, clears0, clears1):
        clears = []
        for i in range(GraphicsOutput.RTPCOUNT):
            (active, value) = clears0[i]
            if active == 0:
                (active, value) = clears1[i]
            
            region.setClearActive(i, active)
            region.setClearValue(i, value)
        
        return clears

    
    def isFullscreen(self):
        if self.region.getLeft() == 0.0 and self.region.getRight() == 1.0 and self.region.getBottom() == 0.0:
            pass
        return self.region.getTop() == 1.0

    
    def getScaledSize(self, mul, div, align):
        winx = self.forcex
        winy = self.forcey
        if winx == 0:
            winx = self.win.getXSize()
        
        if winy == 0:
            winy = self.win.getYSize()
        
        if div != 1:
            winx = ((winx + align - 1) / align) * align
            winy = ((winy + align - 1) / align) * align
            winx = winx / div
            winy = winy / div
        
        if mul != 1:
            winx = winx * mul
            winy = winy * mul
        
        return (winx, winy)

    
    def renderSceneInto(self, depthtex = None, colortex = None, auxtex = None, auxbits = 0, textures = None):
        if textures:
            colortex = textures.get('color', None)
            depthtex = textures.get('depth', None)
            auxtex = textures.get('aux', None)
        
        if colortex == None:
            colortex = Texture('filter-base-color')
            colortex.setWrapU(Texture.WMClamp)
            colortex.setWrapV(Texture.WMClamp)
        
        texgroup = (depthtex, colortex, auxtex, None)
        (winx, winy) = self.getScaledSize(1, 1, 1)
        buffer = self.createBuffer('filter-base', winx, winy, texgroup)
        if buffer == None:
            return None
        
        cm = CardMaker('filter-base-quad')
        cm.setFrameFullscreenQuad()
        quad = NodePath(cm.generate())
        quad.setDepthTest(0)
        quad.setDepthWrite(0)
        quad.setTexture(colortex)
        quad.setColor(Vec4(1, 0.5, 0.5, 1))
        cs = NodePath('dummy')
        cs.setState(self.camstate)
        if auxbits:
            cs.setAttrib(AuxBitplaneAttrib.make(auxbits))
        
        self.camera.node().setInitialState(cs.getState())
        quadcamnode = Camera('filter-quad-cam')
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setFilmOffset(0, 0)
        lens.setNearFar(-1000, 1000)
        quadcamnode.setLens(lens)
        quadcam = quad.attachNewNode(quadcamnode)
        self.region.setCamera(quadcam)
        dr = buffer.getDisplayRegion(0)
        self.setStackedClears(dr, self.rclears, self.wclears)
        if auxtex:
            dr.setClearActive(GraphicsOutput.RTPAuxRgba0, 1)
            dr.setClearValue(GraphicsOutput.RTPAuxRgba0, Vec4(0.5, 0.5, 1.0, 0.0))
        
        self.region.disableClears()
        if self.isFullscreen():
            self.win.disableClears()
        
        dr.setCamera(self.camera)
        dr.setActive(1)
        self.buffers.append(buffer)
        self.sizes.append((1, 1, 1))
        return quad

    
    def renderQuadInto(self, mul = 1, div = 1, align = 1, depthtex = None, colortex = None, auxtex0 = None, auxtex1 = None):
        texgroup = (depthtex, colortex, auxtex0, auxtex1)
        (winx, winy) = self.getScaledSize(mul, div, align)
        depthbits = bool(depthtex != None)
        buffer = self.createBuffer('filter-stage', winx, winy, texgroup, depthbits)
        if buffer == None:
            return None
        
        cm = CardMaker('filter-stage-quad')
        cm.setFrameFullscreenQuad()
        quad = NodePath(cm.generate())
        quad.setDepthTest(0)
        quad.setDepthWrite(0)
        quad.setColor(Vec4(1, 0.5, 0.5, 1))
        quadcamnode = Camera('filter-quad-cam')
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setFilmOffset(0, 0)
        lens.setNearFar(-1000, 1000)
        quadcamnode.setLens(lens)
        quadcam = quad.attachNewNode(quadcamnode)
        buffer.getDisplayRegion(0).setCamera(quadcam)
        buffer.getDisplayRegion(0).setActive(1)
        self.buffers.append(buffer)
        self.sizes.append((mul, div, align))
        return quad

    
    def createBuffer(self, name, xsize, ysize, texgroup, depthbits = 1):
        winprops = WindowProperties()
        winprops.setSize(xsize, ysize)
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setDepthBits(depthbits)
        (depthtex, colortex, auxtex0, auxtex1) = texgroup
        if auxtex0 != None:
            props.setAuxRgba(1)
        
        if auxtex1 != None:
            props.setAuxRgba(2)
        
        buffer = base.graphicsEngine.makeOutput(self.win.getPipe(), name, -1, props, winprops, GraphicsPipe.BFRefuseWindow | GraphicsPipe.BFResizeable, self.win.getGsg(), self.win)
        if buffer == None:
            return buffer
        
        if depthtex:
            buffer.addRenderTexture(depthtex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepthStencil)
        
        if colortex:
            buffer.addRenderTexture(colortex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        
        if auxtex0:
            buffer.addRenderTexture(auxtex0, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)
        
        if auxtex1:
            buffer.addRenderTexture(auxtex1, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba1)
        
        buffer.setSort(self.nextsort)
        buffer.disableClears()
        buffer.getDisplayRegion(0).disableClears()
        self.nextsort += 1
        return buffer

    
    def windowEvent(self, win):
        self.resizeBuffers()

    
    def resizeBuffers(self, win):
        for i in range(len(self.buffers)):
            (mul, div, align) = self.sizes[i]
            (xsize, ysize) = self.getScaledSize(mul, div, align)
            self.buffers[i].setSize(xsize, ysize)
        

    
    def cleanup(self):
        for buffer in self.buffers:
            buffer.clearRenderTextures()
            self.engine.removeWindow(buffer)
        
        self.buffers = []
        self.sizes = []
        self.setClears(self.win, self.wclears)
        self.setClears(self.region, self.rclears)
        self.camstate = self.caminit
        self.camera.node().setInitialState(self.caminit)
        self.region.setCamera(self.camera)
        self.nextsort = self.win.getSort() - 1000
        self.basex = 0
        self.basey = 0


