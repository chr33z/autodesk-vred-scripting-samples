from vrVariantSets import getVariantSet

viewpoints_group = None
variantSets = []

def createVariantSetWithViewpoint(viewpoint):
    variantSetGroupName = "VR_Tool_Viewpoints"
    variantSetName = viewpoint.getName()
    createVariantSetGroup(variantSetGroupName)
    createVariantSet(variantSetName)
    moveVariantSetToGroup(variantSetName, variantSetGroupName)
    
    variantSet = getVariantSet(variantSetName)
    variantSet.addView(variantSetName)
    variantSets.append(variantSetName)

def deleteVariantSets():
    for vs in variantSets:
        deleteVariantSet(vs)

def createTouchSensor(viewpoint, geometryNode):
    touchSensor = vrTouchSensor(geometryNode)
    touchSensorAtt = geometryNode.getAttachment("TouchSensorAttachment")
    touchSensorAttAccess = vrFieldAccess(touchSensorAtt)
    touchSensorAttAccess.setMString("variantSets", [viewpoint.getName()])

def createViewpointGeometry():
    global viewpoints_group
    
    viewpoints = vrCameraService.getAllViewpoints()
    viewpoints_group = vrdNode(createNode("Group", "VR_Tool_Viewpoints"))
    
    for vp in viewpoints:
        # Create geometry for each viewpoint and add it to the scenegraph
        position = vp.getFromAtUpWorld().getFrom() + QVector3D(0, 0, 500)
        sphere = createSphere(1,100,1,1,1)
        sphereNode = vrdTransformNode(vrdNode(sphere))
        sphereNode.setWorldTranslation(position)
        viewpoints_group.children.append(sphereNode)

        # Create a variant set for each viewpoint and attach the view to it
        createVariantSetWithViewpoint(vp)

        # Create touch sensor for each viewpoint and link it with the variant set
        createTouchSensor(vp, sphere)        
        
def enableViewpoints():
    createViewpointGeometry()
    
def disableViewpoints():
    deleteVariantSets()
    if viewpoints_group != None and viewpoints_group.isValid():
        vrScenegraphService.deleteNodes([viewpoints_group])


viewpointTool = vrImmersiveUiService.createTool("ViewpointTool")
viewpointTool.setText("Viewpoint Tool")
viewpointTool.setCheckable(True)
viewpointTool.signal().checked.connect(enableViewpoints)
viewpointTool.signal().unchecked.connect(disableViewpoints)