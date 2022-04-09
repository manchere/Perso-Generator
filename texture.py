class Texturing:

    def __init__(self):
        pass

    def setTexture(self, objMesh):
        myShader1 = cmds.shadingNode('aiStandardSurface', asShader=True)
        mySG1 = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=myShader1 + 'SG')

        # Connection entres les nodes du materiaux
        cmds.connectAttr(myShader1 + '.outColor', mySG1 + '.surfaceShader')
        if cmds.colorEditor(query=False, result=True):
            values = cmds.colorEditor(query=True, rgb=True)

            # Personalisation du shader
            cmds.setAttr(myShader1 + '.baseColor', values[0], values[1], values[2], type='double3')

        # Selection d'un objet et set le shader
        cmds.select(objMesh)
        cmds.sets(edit=True, forceElement=myShader1 + 'SG')
