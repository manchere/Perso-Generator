import maya.cmds as cmds
import json

jpath = cmds.internalVar(usd=True) + 'perso-generator/'

# reading json
with open(jpath + 'data.json') as jsonFile:
    json_object = json.load(jsonFile)


class Skeleton:

    def __init__(self, data):
        self.Data = data
        self.Skel = self.Data['skeleton']

        # self.__baseSkeleton()

    def __base_skeleton(self):
        root_pos = self.Skel['root_hips']['pos']
        cmds.joint(name='root_JNT', p=(root_pos[0], root_pos[1], root_pos[2]), rad=0.5)

    def attach_base(self):
        for key, obj in self.Data['base'].items():
            try:
                if 'joint' in obj.keys():
                    cmds.parent(obj['b_asset_name'], obj['joint'])
            except:
                print('doesnt exist')

    # valider
    def construct_part_by_pos(self, part):
        for j_name, j_info in self.Skel[part]['joints'].items():
            x, y, z = (i for i in j_info['pos_info'])
            cmds.joint(n=str(j_name), p=(x, y, z))
            cmds.select(d=True)

    def construct_part_by_clust(self, part):
        for j_name, j_info in self.Skel[part]['joints'].items():
            x, y, z = [cmds.select() for i in j_info['cluster_info'] for j in j_info['cluster_info']]
            cmds.joint(str(j_name), p=(x, y, z))

    def create_joint_chain(self, part):
        for j_name, j_info in self.Skel[part]['joints'].items():
            try:
                if 'parent' in j_info.keys():
                    cmds.parent(j_name, j_info['parent'])
            except:
                print('a joint is already attached')
                continue

    def attach_joint(self, part):
        for j_name, j_info in self.Skel[part]['joints'].items():
            try:
                if 'b_asset_name' in j_info.keys():
                    cmds.parent(j_info['b_asset_name'], j_name)
            except:
                print('a joint is already attached')
                continue

    def bind_part(self, part):
        for j_name, j_info in self.Skel[part]['joints'].items():
            try:
                if 'binding' in j_info.keys() and j_info['binding'] is True:
                    cmds.skinCluster(j_info['b_asset_name'], str(j_name), dr=4.5)
            except:
                print('a joint is already bound')
                continue

    def attach_ik_system(self):
        pass


class Perso:

    def __init__(self, data):
        self.Data = data
        self.Path = cmds.internalVar(usd=True) + 'perso-generator/Partie/'
        self.Current = self.Data['obj_init']
        self.Selection = self.Data['selection_init']
        self.Skeleton = Skeleton(self.Data)
        self.Tool = Tools()

        self._init_add_part()
        self._check_current()

    def _add_joint_obj(self, joint_name, x_pos, y_pos, rd):
        if not cmds.objExists(joint_name):
            cmds.polySphere(n=joint_name, sx=8, sy=8, r=rd)
            cmds.move(x_pos, y_pos, xy=True)
            # self.__lockTransform(jointName)

    def _lock_transform(self):
        for attr in self.Data['obj_attributes']:
            cmds.setAttr(obj_name + '.' + str(self.Data['obj_attributes'][attr]['attribute_name']),
                         lock=self.Data['obj_attributes'][attr]['locked'])

    def _init_add_part(self):
        self._add_joint_obj('neck', 0, 112.385, 5.3)
        self._add_joint_obj('r_ankle', -13.02, 31.5, 5)
        self._add_joint_obj('l_ankle', 13.02, 31.5, 5)

    def _check_current(self):
        joint_check = [x for x in ('left ankle', 'right ankle', 'neck') if not cmds.objExists(x)]
        for i in joint_check:
            data = self.Data['base'][i]
            self._add_joint_obj(data['b_asset_name'], data['pos'][0], data['pos'][1], data['rad'])

        for cur_key, cur_name in self.Current.items():
            if cur_name not in self.check_obj_in_scene_asset():
                self.Current[cur_key] = None
        for name, key in self.check_obj_in_scene_asset():
            self.Current[key] = name

    def check_obj_in_scene_asset(self):
        info = [s for v in self.Data['elements'].values() for j, s in v.items() if j == 'b_asset_name' or j == 'type']
        grp_info = list(zip(*[iter(info)] * 2))
        init_grp = zip(*[iter(info)] * 2)
        obj_in_scene = cmds.ls(type='transform')
        for single_tuple in init_grp:
            if single_tuple[0] not in obj_in_scene:
                grp_info.remove(single_tuple)
        return grp_info

    def add_part(self, name):
        menu_name = cmds.optionMenu(name, q=True, value=True)
        asset = self.Data['elements'][menu_name]['b_asset_name']
        partType = self.Data['elements'][menu_name]['type']
        self._check_current()
        if not cmds.objExists(asset):
            cmds.delete(self.Current[partType])
            cmds.file(self.Path + asset + '.fbx', i=True, lck=True)

            self.Current[partType] = asset
            self.Selection[partType] = menu_name
        self._check_current()

    # find dropdown name when given asset name
    def get_selection_name_from_asset(self, asset):
        return ''.join([k for k, v in self.Data['elements'].items() if ('b_asset_name', asset) in v.items()])

    # skeleton methods
    def construct_full_perso(self):
        for cur in self.Current.values():
            if cur is not None:
                self.Skeleton.construct_part_by_pos(self.get_selection_name_from_asset(cur))

    def create_joint_chain_full_perso(self):
        for part in self.Current.values():
            if part is not None:
                self.Skeleton.create_joint_chain(self.get_selection_name_from_asset(part))

    def attach_joint_full_perso(self):
        for part in self.Current.values():
            if part is not None:
                self.Skeleton.attach_joint(self.get_selection_name_from_asset(part))
        self.Skeleton.attach_base()

    def bind_full_perso(self):
        for part in self.Current.values():
            if part is not None:
                self.Skeleton.bind_part(self.get_selection_name_from_asset(part))

    def skeletonize(self):
        self._check_current()
        self.construct_full_perso()
        self.create_joint_chain_full_perso()
        self.attach_joint_full_perso()
        self.Tool.arrange_perso()
        self.Tool.group_perso('Perso')

    def randomize(self):
        pass


class Texturing:

    def __init__(self):
        pass

    def set_texture(self, objMesh):
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


class Tools:

    def arrange_perso(self):
        deleteList = []
        for tran in cmds.ls(type='transform'):
            if cmds.nodeType(tran) == 'transform':
                children = cmds.listRelatives(tran, c=True)
                if children == None:
                    deleteList.append(tran)

        if len(deleteList) > 0:
            cmds.delete(deleteList)

    def group_perso(self, name):
        grpname = cmds.group('root_JNT', n=name)
        for cur_name in cmds.listRelatives(grpname, ad=True):
            cmds.rename(cur_name, grpname + '_' + cur_name)

    def symmetrize(self, obj):
        self.Data['elements']


def make_optmenu(optMenName, optMenLbl, menuItems):
    cmds.optionMenu(optMenName, label=optMenLbl)
    for item in menuItems:
        cmds.menuItem(item)


def color_cg_btn(btnName, btnLbl, cmd):
    cmds.button(btnName, label=btnLbl, command=cmd)


if cmds.window('Perso_Maker', exists=True):
    cmds.deleteUI('Perso_Maker')

cmds.window('Perso_Maker', title='Custom Crowd', w=400)
tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

t = cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.checkBox('sym', label='Apply Symmetry')
cmds.checkBox('syme', label='Allow Lost Parts')

pers = Perso(json_object)
tex = Texturing()

# Bouton head
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Head', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Head', 'Head Type', ['box', 'sauce pan', 'bowl', 'lamp'])
cmds.optionMenu('Head', cc=lambda x: pers.add_part('Head'), e=True)
color_cg_btn('head_color', 'Change head color', lambda x: tex.set_texture(pers.Current['head']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Body
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Body', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Body', 'Body Type', ['decagon body', 'wavy body', 'sphere body'])
cmds.optionMenu('Body', cc=lambda x: pers.add_part('Body'), e=True)
color_cg_btn('body_color', 'Change body color', lambda x: tex.set_texture(pers.Current['body']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Hand
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Left Hand', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_hand', 'Left Hand Type', ['left boxing glove', 'left mecha hand'])
color_cg_btn('l_hand_color', 'Change hand color', lambda x: tex.set_texture(pers.Current['left_hand']))
cmds.optionMenu('Left_hand', cc=lambda x: pers.add_part('Left_hand'), e=True)

cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Hand
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Right Hand', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_hand', 'Right Hand Type', ['right boxing glove', 'right mecha hand'])
color_cg_btn('r_hand_color', 'Change hand color', lambda x: tex.set_texture(pers.Current['right_hand']))
cmds.optionMenu('Right_hand', cc=lambda x: pers.add_part('Right_hand'), e=True)

cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Arm
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Left Arm', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_arm', 'Left Arm Type', ['left mecha arm', 'smooth surface'])
cmds.optionMenu('Left_arm', cc=lambda x: pers.add_part('Left_arm'), e=True)
color_cg_btn('l_arm_color', 'Change arm color', lambda x: tex.set_texture(pers.Current['left_arm']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Arm
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Right Arm', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_arm', 'Right Arm Type', ['right mecha arm', 'smooth surface'])
cmds.optionMenu('Right_arm', cc=lambda x: pers.add_part('Right_arm'), e=True)
color_cg_btn('r_arm_color', 'Change arm color', lambda x: tex.set_texture(pers.Current['right_arm']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Leg
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Left Leg', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_leg', 'Left Leg Type', ['left mecha leg', 'smooth surface'])
cmds.optionMenu('Left_leg', cc=lambda x: pers.add_part('Left_leg'), e=True)
color_cg_btn('l_leg_color', 'Change head color', lambda x: tex.set_texture(pers.Current['left_leg']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Leg
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Right leg', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_leg', 'Right Leg Type', ['right mecha leg', 'smooth surface'])
cmds.optionMenu('Right_leg', cc=lambda x: pers.add_part('Right_leg'), e=True)
color_cg_btn('r_leg_color', 'Change leg color', lambda x: tex.set_texture(pers.Current['right_leg']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Left-Foot
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Left foot', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_foot', 'Left Foot Type', ['left boot', 'left shoe'])
cmds.optionMenu('Left_foot', cc=lambda x: pers.add_part('Left_foot'), e=True)
color_cg_btn('l_foot_color', 'Change foot color', lambda x: tex.set_texture(pers.Current['left_foot']))

cmds.setParent('..')
cmds.setParent('..')

# Bouton Right-Foot
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Right Foot', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_foot', 'Right Foot Type', ['right boot', 'right shoe'])
cmds.optionMenu('Right_foot', cc=lambda x: pers.add_part('Right_foot'), e=True)
color_cg_btn('r_foot_color', 'Change foot color', lambda x: tex.set_texture(pers.Current['right_foot']))

cmds.setParent('..')
cmds.setParent('..')

# Left Back
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Left Back', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Left_back', 'Left Back Type', ['left wing', 'left stick'])
cmds.optionMenu('Left_back', cc=lambda x: pers.add_part('Left_back'), e=True)
color_cg_btn('l_back_color', 'Change back object color', lambda x: tex.set_texture(pers.Current['left_back']))

cmds.setParent('..')
cmds.setParent('..')

# Right Back
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Right Back', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Right_back', 'Right Back Type', ['right wing', 'right stick'])
cmds.optionMenu('Right_back', cc=lambda x: pers.add_part('Right_back'), e=True)
color_cg_btn('r_back_color', 'Change back object color', lambda x: tex.set_texture(pers.Current['right_back']))

cmds.setParent('..')
cmds.setParent('..')

# Eyes custom
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Eyes', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Eyes', 'Eyes Type', ['boot', 'shoe'])
cmds.optionMenu('Eyes', cc=lambda x: pers.add_part('Eyes'), e=True)
color_cg_btn('eyes_color', 'Change eyes color', lambda x: tex.set_texture(pers.Current['eyes']))

cmds.setParent('..')
cmds.setParent('..')

# Tail custom
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Tail', cll=True, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
make_optmenu('Tail', 'Tail Type', ['mecha tail', 'bionic'])
cmds.optionMenu('Tail', cc=lambda x: pers.add_part('Tail'), e=True)
color_cg_btn('tail_color', 'Change tail color', lambda x: tex.set_texture(pers.Current['tail']))
cmds.setParent('..')
cmds.setParent('..')

cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='Create', cll=False, cl=True, bgc=[0.2, 0.2, 0.2], w=200)
cmds.button(label="Finalize Character", bgc=[0, 0.2, 0.3], command=lambda x: pers.skeletonize(), w=200)
cmds.button(label='Randomize Character', bgc=[0, 0.2, 0], command='', w=200)

cmds.setParent('..')
cmds.setParent('..')

cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=2)
cmds.frameLayout(label='List:', cll=False, cl=True, bgc=[0.2, 0.2, 0.2], w=200)

cmds.setParent('..')
cmds.setParent('..')
cmds.setParent('..')

# ----------------------------------------------------------------------

# Skeleton Definition
u = cmds.frameLayout(label='Crowd Definition', cll=False, cl=False, bgc=[0.1, .35, 0.], w=200)
cmds.rowColumnLayout(rowSpacing=(20, 20), numberOfColumns=1)
cmds.button()
cmds.setParent('..')
cmds.setParent('..')
# ----------------------------------------------------------------------------------------------

cmds.tabLayout(tabs, edit=True, tabLabel=((t, "Character"), (u, "Crowd")))
# On affiche la fenetre
cmds.showWindow()
jsonFile.close()
