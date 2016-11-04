#SP2M v1.01b author 戴巍
#http://weibo.com/david376

import maya.cmds as mc
if mc.window('SP2Maya',ex = 1):
	mc.deleteUI('SP2Maya')
mc.window('SP2Maya',t = 'SP2Maya' )
mc.showWindow()

mainRCL = mc.rowColumnLayout(w = 100,numberOfColumns = 1)

mc.separator(style = 'none',h = 20)


#define which renderer is using 
vrayUsing =False
arnoldUsing = False
rendererBools = [vrayUsing,arnoldUsing]
def choosingRenderer(rendererNumber):
	
	global rendererBools
	i = 0
	while i < len(rendererBools):
		rendererBools[i] = False
		i+= 1
	rendererBools[rendererNumber] = True
	

		
#the UI used to choose renderer
mc.radioButtonGrp( label='Renderer', labelArray2=['vray', 'arnold'], numberOfRadioButtons=2,on1 = "choosingRenderer(0)",on2 = "choosingRenderer(1)",ann = 'choose a renderer',vr = 1)


def connectUVNodeToTextureNode(UVnode,textureNode):
	mc.connectAttr(UVnode +'.outUV',textureNode + '.uvCoord',force = 1)
	mc.connectAttr(UVnode +'.outUvFilterSize',textureNode + '.uvFilterSize',force = 1)
	mc.connectAttr(UVnode +'.coverage',textureNode + '.coverage',force = 1)
	mc.connectAttr(UVnode +'.translateFrame',textureNode + '.translateFrame',force = 1)
	mc.connectAttr(UVnode +'.rotateFrame',textureNode + '.rotateFrame',force = 1)
	mc.connectAttr(UVnode +'.mirrorU',textureNode + '.mirrorU',force = 1)
	mc.connectAttr(UVnode +'.mirrorV',textureNode + '.mirrorV',force = 1)
	mc.connectAttr(UVnode +'.wrapU',textureNode + '.wrapU',force = 1)
	mc.connectAttr(UVnode +'.wrapV',textureNode + '.wrapV',force = 1)
	mc.connectAttr(UVnode +'.repeatUV',textureNode + '.repeatUV',force = 1)
	mc.connectAttr(UVnode +'.vertexUvOne',textureNode + '.vertexUvOne',force = 1)
	mc.connectAttr(UVnode +'.vertexUvTwo',textureNode + '.vertexUvTwo',force = 1)
	mc.connectAttr(UVnode +'.vertexUvThree',textureNode + '.vertexUvThree',force = 1)
	mc.connectAttr(UVnode +'.vertexCameraOne',textureNode + '.vertexCameraOne',force = 1)
	mc.connectAttr(UVnode +'.noiseUV',textureNode + '.noiseUV',force = 1)
	mc.connectAttr(UVnode +'.offset',textureNode + '.offset',force = 1)
	mc.connectAttr(UVnode +'.rotateUV',textureNode + '.rotateUV',force = 1)

#get all file names will be used in the sourceimages folder
def getFileNames(materialName):
	scenes = mc.workspace(dir =1 ,q =1)
	projectPath =''
	if 'scenes' in scenes:
		projectPath = scenes[0:-7]
	else:
		mc.error('工程路径出错')
	sourceimagesPath = projectPath + 'sourceimages'
	allFileNames = mc.getFileList(folder = sourceimagesPath)
	fileNamesUsing = []
	for fileName in allFileNames:
		if materialName in fileName:
			fileNamesUsing.append(fileName)
	return fileNamesUsing

#udim bool used to judge weather to use udim
udim = False
def UDIM_on(*argus):
	global udim
	udim = True
def UDIM_off(*argus):
	global udim
	udim = False
def UDIM_judge(fileNode):
	global udim
	if udim:
		mc.setAttr(fileNode + '.uvTilingMode',3)
		mc.setAttr(fileNode + '.uvTileProxyQuality',4)
		
	
#create a dict which containts all the textures that having the materialName
#the keys of the dict are the texture's name
#the values of the dict are the file nodes which ref to the texture 
def createTexturesUsing(fileNamesUsing):
	texturesUsing = {}
	targetFileExist = False
	for fileName in fileNamesUsing:
		try:
			tempFile = mc.shadingNode('file',at = 1,icm = 1)
		except:
			tempFile = mc.shadingNode('file',at = 1)
		texturesUsing[fileName] = tempFile
		mc.setAttr(tempFile + '.fileTextureName','sourceimages' + '\\' + fileName,type = 'string')
		targetFileExist = True
	if not targetFileExist:
		mc.error('写错名字了吧小伙子，检查一下')
	return texturesUsing

def createVrayShadingNetwork(materialName,texturesUsing):
	#get current version of maya
	version = mc.about(version = 1)
	version = int(version)
	#if the version is newer than 2016 ,we can use the colormanagement directly
	if version >= 2016:
		#create vray mtl
		vrayMtl = mc.shadingNode('VRayMtl',asShader = 1,n = materialName)
		mc.setAttr(vrayMtl + '.bumpMapType',1)
		try:
			mc.setAttr(vrayMtl + '.brdfType' , 3)
		except:
			mc.warning('当前版本vray没有ggx_brdf，效果可能不好，请注意')

		#create place2dtexture
		UVnode = mc.shadingNode('place2dTexture',au =1)
		#connect textures to material
		for textureUsing in texturesUsing.keys():
			
			if 'Diffuse' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.diffuseColor')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Reflection' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.reflectionColor')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Glossiness' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.reflectionGlossiness')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'ior' in textureUsing:
				mc.setAttr(vrayMtl + '.lockFresnelIORToRefractionIOR',0)
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.fresnelIOR')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Normal' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.bumpMap')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			
	else:
		#create vray mtl
		vrayMtl = mc.shadingNode('VRayMtl',asShader = 1,n = materialName)
		mc.setAttr(vrayMtl + '.bumpMapType',1)
		try:
			mc.setAttr(vrayMtl + '.brdfType' , 3)
		except:
			mc.warning('当前版本vray没有ggx_brdf，效果可能不好，请注意')
		#create place2dtexture
		UVnode = mc.shadingNode('place2dTexture',au =1)
		#connect textures to material
		for textureUsing in texturesUsing.keys():
			if 'Diffuse' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.diffuseColor')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Reflection' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.reflectionColor')
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Glossiness' in textureUsing:
				gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
				mc.setAttr(gammaCorret + '.gammaX',2.2)
				mc.setAttr(gammaCorret + '.gammaY',2.2)
				mc.setAttr(gammaCorret + '.gammaZ',2.2)
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
				mc.connectAttr(gammaCorret + '.outValueX',vrayMtl + '.reflectionGlossiness')
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'ior' in textureUsing:
				mc.setAttr(vrayMtl + '.lockFresnelIORToRefractionIOR',0)
				gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
				mc.setAttr(gammaCorret + '.gammaX',2.2)
				mc.setAttr(gammaCorret + '.gammaY',2.2)
				mc.setAttr(gammaCorret + '.gammaZ',2.2)
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
				mc.connectAttr(gammaCorret + '.outValueX',vrayMtl + '.fresnelIOR')
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Normal' in textureUsing:
				gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
				mc.setAttr(gammaCorret + '.gammaX',2.2)
				mc.setAttr(gammaCorret + '.gammaY',2.2)
				mc.setAttr(gammaCorret + '.gammaZ',2.2)
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
				mc.connectAttr(gammaCorret + '.outValue',vrayMtl + '.bumpMap')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])

def createArnoldShadingNetwork(materialName,texturesUsing):
	
	#create aistandard mtl
	aiStandard = mc.shadingNode('aiStandard',asShader = 1,n = materialName)
	mc.setAttr(aiStandard + '.Kd',1)
	mc.setAttr(aiStandard + '.Ks',1)
	try:
		mc.setAttr(aiStandard + '.specularDistribution' ,1 )
	except:
		mc.warning('你使用的arnold版本没有ggx_brdf，效果可能不好')
	
	#create place2dtexture
	UVnode = mc.shadingNode('place2dTexture',au =1)
	
	#connect textures to material
	for textureUsing in texturesUsing.keys():
		if 'Diffuse' in textureUsing:
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',aiStandard + '.color')
			mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Specular' in textureUsing:
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',aiStandard + '.KsColor')
			mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Roughness' in textureUsing:
			gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
			mc.setAttr(gammaCorret + '.gammaX',2.2)
			mc.setAttr(gammaCorret + '.gammaY',2.2)
			mc.setAttr(gammaCorret + '.gammaZ',2.2)
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
			mc.connectAttr(gammaCorret + '.outValueX',aiStandard + '.specularRoughness')
			mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'f0' in textureUsing:
			mc.setAttr(aiStandard + '.specularFresnel',1)
			gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
			mc.setAttr(gammaCorret + '.gammaX',2.2)
			mc.setAttr(gammaCorret + '.gammaY',2.2)
			mc.setAttr(gammaCorret + '.gammaZ',2.2)
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
			mc.connectAttr(gammaCorret + '.outValueX',aiStandard + '.Ksn')
			mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Normal' in textureUsing:
			bumpNode = mc.shadingNode('bump2d',au = 1)
			mc.setAttr(bumpNode + '.bumpInterp', 1)
			mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',bumpNode + '.bumpValue')
			mc.connectAttr(bumpNode + '.outNormal',aiStandard + '.normalCamera')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
	
		
def main(materialName):
	#get all file names in the sourceimages folder
	targetFileNames = getFileNames(materialName)
	textureNamesUsing =[]
	if udim:
		for targetFileName01 in targetFileNames:
			textureRepeated = False
			for textureUsing in textureNamesUsing:
				if targetFileName01[:-9] == textureUsing[:-9]:
					textureRepeated = True
					break
			if textureRepeated:
				continue
			for targetFileName02 in targetFileNames:
				if (not targetFileName01 == targetFileName02) and (targetFileName01[:-9] == targetFileName02[:-9]):
					
					textureNamesUsing.append(targetFileName01)
					break
					
		print textureNamesUsing
	else:
		textureNamesUsing = targetFileNames			

	#get a dict contains all the textures will be used
	texturesUsing = createTexturesUsing(textureNamesUsing)
		
	#judge every texture using, whether is a udim texture,if yes,change the settings
	for textureUsing in texturesUsing.values():
		UDIM_judge(textureUsing)
		
	if rendererBools[0]:
		createVrayShadingNetwork(materialName,texturesUsing)
	elif rendererBools[1]:
		createArnoldShadingNetwork(materialName,texturesUsing)
	else:
		mc.error('请选择一个你要使用的渲染器,please choose a renderer')


mc.rowColumnLayout(co = (1,'left',141))
mc.separator(h = 50) 
mc.separator(style = 'out') 
mc.checkBox(l = 'udim textures',onc = UDIM_on,ofc = UDIM_off,align = 'right')  

mc.rowColumnLayout(p = mainRCL)
materialNameInput = mc.textFieldButtonGrp(l = 'materialName',bl = 'excute',bc = 'main(mc.textFieldButtonGrp(materialNameInput,q = 1,text =1 ))')
mc.separator(style = 'none',h = 20)
mc.separator()
mc.text(l = 'sp2m v1.01b',w =230,al = 'right',hyperlink = 1,ww = 1,ann = 'the version of the script')