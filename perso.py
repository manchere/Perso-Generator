import maya.cmds as cmds
import json

class Skeleton:

    def __init__(self, data):
        self.Data = data
        self.Skel = self.Data['skeleton']

        #self.__baseSkeleton()

    def __baseSkeleton(self):
        root_pos = self.Skel['root_hips']['pos']
        cmds.joint(name='root_JNT', p=(root_pos[0], root_pos[1], root_pos[2]), rad=0.5)

    def constructPartByPos(self, part):
        for joint_name, joint_info in self.Skel[part]['joints']:
            x, y, z = (i for i in joint_info['pos_info'])
            cmds.joint(str(jointname), p=(x, y, z))

    def constructPartByClust(self):
        for joint_name, joint_info in self.Skel[part]['joints']:
            x, y, z = [cmds.select() for i in joint_info['cluster_info'] for j in joint_info['cluster_info']]
            cmds.joint(str(jointname), p=(x, y, z))

    def constructBody(self):
        pass

    def constructArm(self):
        pass


    def skeletonize(self):
        pass

jpath = cmds.internalVar(usd=True) + 'TP_Perso/'

# reading json
with open(jpath + 'data.json') as jsonFile:
    jsonObject = json.load(jsonFile)

class Perso:

    def __init__(self, data):
        self.Data = data
        self.Path = cmds.internalVar(usd=True) + 'TP_Perso/Partie/'
        self.Current = self.Data['initialization']
        self.__checkCurrent()

        self.__addJointObj('neck', 0, 3.211, 0.161)
        self.__addJointObj('r_ankle', -0.372, 0.9, 0.121)
        self.__addJointObj('l_ankle', 0.372, 0.9, 0.121)
        self.__initAddPart('deca_body')

    def __addJointObj(self, jointName, xPos, yPos, rd):
        if not cmds.objExists(jointName):
            cmds.polySphere(n=jointName, sx=15, sy=15, r=rd)
            cmds.move(xPos, yPos, xy=True)
            #self.__lockTransform(jointName)

    def __initAddPart(self, partName):
        pass

    def addPart(self, name):
        self.__checkCurrent()
        menuName = cmds.optionMenu(name, q=True, value=True)
        asset = self.Data['elements'][menuName]['b_asset_name']
        partType = self.Data['elements'][menuName]['type']

        if not cmds.objExists(asset):
            cmds.delete(self.Current[partType])
            isGrouped = self.Data['elements'][menuName]['grouped']
            cmds.file(self.Path + asset + '.obj', i=True, lck=True, gr=isGrouped, gn=asset)

            self.Current[partType] = asset
            #self.__lockTransform(asset)

    def __checkCurrent(self):
        for k, v in self.Current.items():
            if not cmds.objExists(str(v)):
                print(k, v)
                self.Current[k] = None

    def __lockTransform(self, objName):
        for attr in self.Data['obj_attributes']:
            cmds.setAttr(objName + '.' + str(self.Data['obj_attributes'][attr]['attribute_name']),
                         lock=self.Data['obj_attributes'][attr]['locked'])

    def applySymmetry(self, ):
        if cmds.checkBox('sym', q=True, v=True):
            pass


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



def make_optmenu(optMenName, optMenLbl, menuItems):
    cmds.optionMenu(optMenName, label=optMenLbl)
    for item in menuItems:
        cmds.menuItem(item)


def colorCgBtn(btnName, btnLbl, cmd):
    cmds.button(btnName, label=btnLbl, command=cmd)


if cmds.window('Perso_Maker', exists=True):
    cmds.deleteUI('Perso_Maker')

cmds.window('Perso_Maker', title='Perso Maker')
cmds.frameLayout(label='Body Part Modification', cll=False, cl=False, bgc=[0.2, .35, 0.2], w=200)

cmds.checkBox('sym', label='Apply Symmetry')
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)

pers = Perso(jsonObject)
tex = Texturing()

# Bouton head
cmds.frameLayout(label='Head', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Head', 'Head Type', ['box', 'sauce pan', 'bowl', 'lamp'])
cmds.optionMenu('Head', cc=lambda x: pers.addPart('Head'), e=True)
colorCgBtn('head_color', 'Change head color', lambda x: tex.setTexture(pers.Current['head']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Body
cmds.frameLayout(label='Body', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Body', 'Body Type', ['decagon body', 'wavy body'])
cmds.optionMenu('Body', cc=lambda x: pers.addPart('Body'), e=True)
colorCgBtn('body_color', 'Change body color', lambda x: tex.setTexture(pers.Current['body']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Hand

cmds.frameLayout(label='Left Hand', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_hand', 'Left Hand Type', ['left boxing glove', 'left mecha hand'])
colorCgBtn('l_hand_color', 'Change hand color', lambda x: tex.setTexture(pers.Current['left_hand']))
cmds.optionMenu('Left_hand', cc=lambda x: pers.addPart('Left_hand'), e=True)
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Hand

cmds.frameLayout(label='Right Hand', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_hand', 'Right Hand Type', ['right boxing glove', 'right mecha hand'])
colorCgBtn('r_hand_color', 'Change hand color', lambda x: tex.setTexture(pers.Current['right_hand']))
cmds.optionMenu('Right_hand', cc=lambda x: pers.addPart('Right_hand'), e=True)
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Arm

cmds.frameLayout(label='Left Arm', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_arm', 'Left Arm Type', ['left mecha arm', 'smooth surface'])
cmds.optionMenu('Left_arm', cc=lambda x: pers.addPart('Left_arm'), e=True)
colorCgBtn('l_arm_color', 'Change arm color', lambda x: tex.setTexture(pers.Current['left_arm']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Arm

cmds.frameLayout(label='Right Arm', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_arm', 'Right Arm Type', ['right mecha arm', 'smooth surface'])
cmds.optionMenu('Right_arm', cc=lambda x: pers.addPart('Right_arm'), e=True)
colorCgBtn('r_arm_color', 'Change arm color', lambda x: tex.setTexture(pers.Current['right_arm']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Leg

cmds.frameLayout(label='Left Leg', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_leg', 'Left Leg Type', ['left mecha leg', 'smooth surface'])
cmds.optionMenu('Left_leg', cc=lambda x: pers.addPart('Left_leg'), e=True)
colorCgBtn('l_leg_color', 'Change head color', lambda x: tex.setTexture(pers.Current['left_leg']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Leg

cmds.frameLayout(label='Right leg', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_leg', 'Right Leg Type', ['right mecha leg', 'smooth surface'])
cmds.optionMenu('Right_leg', cc=lambda x: pers.addPart('Right_leg'), e=True)
colorCgBtn('r_leg_color', 'Change leg color', lambda x: tex.setTexture(pers.Current['right_leg']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Foot

cmds.frameLayout(label='Left foot', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_foot', 'Left Foot Type', ['left boot', 'left shoe'])
cmds.optionMenu('Left_foot', cc=lambda x: pers.addPart('Left_foot'), e=True)
colorCgBtn('l_foot_color', 'Change foot color', lambda x: tex.setTexture(pers.Current['left_foot']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Foot

cmds.frameLayout(label='Right Foot', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_foot', 'Right Foot Type', ['right boot', 'right shoe'])
cmds.optionMenu('Right_foot', cc=lambda x: pers.addPart('Right_foot'), e=True)
colorCgBtn('r_foot_color', 'Change foot color', lambda x: tex.setTexture(pers.Current['right_foot']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Left Back
cmds.frameLayout(label='Left Back', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_back', 'Left Back Type', ['left wing', 'left stick'])
cmds.optionMenu('Left_back', cc=lambda x: pers.addPart('Left_back'), e=True)
colorCgBtn('l_back_color', 'Change back object color', lambda x: tex.setTexture(pers.Current['left_back']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Right Back
cmds.frameLayout(label='Right Back', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_back', 'Right Back Type', ['right wing', 'right stick'])
cmds.optionMenu('Right_back', cc=lambda x: pers.addPart('Right_back'), e=True)
colorCgBtn('r_back_color', 'Change back object color', lambda x: tex.setTexture(pers.Current['right_back']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Eyes custom

cmds.frameLayout(label='Eyes', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Eyes', 'Eyes Type', ['boot', 'shoe'])
cmds.optionMenu('Eyes', cc=lambda x: pers.addPart('Eyes'), e=True)
colorCgBtn('eyes_color', 'Change eyes color', lambda x: tex.setTexture(pers.Current['eyes']))
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

# Tail custom

cmds.frameLayout(label='Tail', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Tail', 'Tail Type', ['mecha tail', 'bionic'])
cmds.optionMenu('Tail', cc=lambda x: pers.addPart('Tail'), e=True)
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.setParent('..')
cmds.setParent('..')

cmds.setParent('..')
cmds.setParent('..')
cmds.setParent('..')

# ----------------------------------------------------------------------

# Skeleton Definitioon

cmds.frameLayout(label='Skeleton Definition', cll=False, cl=False, bgc=[0.2, .35, 0.2], w=200)
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=1)

cmds.button(label='Create FK', bgc=[0.4, 0.4, 0.4], command='', w=400)
cmds.button(label='Create IK', bgc=[0, 0, .4], command='')
# ----------------------------------------------------------------------------------------------
# On affiche la fenetre
cmds.showWindow()
jsonFile.close()
