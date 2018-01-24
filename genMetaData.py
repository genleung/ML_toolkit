#!/usr/bin/env python3
# Python3 required.

import sys
import os
import time
import random


# --------------------------------------------
# 常量
# --------------------------------------------
# label文件扩展名，在使用时会自动匹配大小写情况，所以
# 此处只需要小写即可。
LABEL_FILE_EXT=['.txt']

# trainning文件扩展名，在使用时会自动匹配大小写情况，所以
# 此处只需要小写即可。
TRAINNING_FILE_EXT=['.jpg', '.png', '.jpeg']

# --------------------------------------------
# 全局变量
# --------------------------------------------
# 训练用的图像目录
# 里面是大量的图片，尽量用jpg和png格式
trainningImagesDir=''

# 图像的标签(labels)目录
# darknet的label文件的格式：
# 每一行表示一个object及其bounding box：
#    <object-class> <x> <y> <width> <height>
# 其中 x, y, width, and height 都是归一化的值
trainningLabelsDir=''

# 所有object的名字文件
# 所有训练图像中包含的object名字，每一行一个名字，例如：
# person
# car
# motorbike
# bus
# ...
allNamesFile=''
# 所有object的名字的列表
allNames=[]

# 目标object的名字文件
# 想detect的object的名字文件列表，每一行一个名字，例如：
# person
# dog
# ...
targetNamesFile=''
# 目标object的名字的列表
targetNames=[]

# 唯一后缀名
uniquePostfix=''

def setParams(argv, currentDir):
    global trainningImagesDir
    global trainningLabelsDir
    global allNamesFile,allNames
    global targetNamesFile,targetNames
    trainningImagesDir=argv[1].strip()
    trainningLabelsDir=argv[2].strip()
    allNamesFile=argv[3].strip()
    targetNamesFile=argv[4].strip()
    # 转为绝对路径
    if trainningImagesDir[0]!='/':
        trainningImagesDir=currentDir+'/'+trainningImagesDir
    if trainningLabelsDir[0]!='/':
        trainningLabelsDir=currentDir+'/'+trainningLabelsDir
    if allNamesFile[0]!='/':
        allNamesFile=currentDir+'/'+allNamesFile
    if targetNamesFile[0]!='/':
        targetNamesFile=currentDir+'/'+targetNamesFile
    # 检查目录是否存在
    if (not os.path.exists(trainningImagesDir)) or (not os.path.isdir(trainningImagesDir)):
        print("Invalid trainningImagesDir!")
        return False
    else: print(">> trainningImagesDir: " + trainningImagesDir)
    # 检查目录是否存在
    if (not os.path.exists(trainningLabelsDir)) or (not os.path.isdir(trainningLabelsDir)):
        print("Invalid trainningLabelsDir!")
        return False
    else: print(">> trainningLabelsDir: " + trainningLabelsDir)
    # 检查文件是否存在
    if (not os.path.exists(allNamesFile)) or (not os.path.isfile(allNamesFile)):
        print("Invalid allNamesFile!")
        return False
    else: print(">> allNamesFile: " + allNamesFile)
    # 检查文件是否存在
    if (not os.path.exists(targetNamesFile)) or (not os.path.isfile(targetNamesFile)):
        print("Invalid targetNamesFile!")
        return False
    else: print(">> targetNamesFile: " + targetNamesFile)
    # 设置names列表
    allNames=[]
    targetNames=[]
    for line in open(allNamesFile):
        line = line.strip()
        if not len(line) or line.startswith('#'): continue
        allNames.append(line.strip())
    for line in open(targetNamesFile):
        line = line.strip()
        if not len(line) or line.startswith('#'): continue
        targetNames.append(line.strip())
    print('>> allnames:\n', allNames)
    print('>> targetnames:\n', targetNames)
    return True

#遍历targetDir及其子目录，寻找所有文件，并返回文件名(fullpath)列表
# extFilters是扩展名过滤列表，用来指示相应的文件名的类型
# extFilters形如['.txt'],或['.jpg', '.png', '.jpeg']
def getAllFiles(targetDir, extFilters=[]):
    allFiles=[]
    wd=os.getcwd()
    # 如果有扩展名过滤列表，全部转化为小写
    if len(extFilters):
        for i in range(len(extFilters)):
            extFilters[i]=extFilters[i].lower()
    # 遍历targetDir及其子目录，得到所有子目录(包括targetDir)下的文件
    for parent,dirnames,filenames in os.walk(targetDir):
        for filename in filenames:
            # 检查扩展名是否是extFilters允许范围内的
            ext=os.path.splitext(filename)[1].lower()
            if ext in extFilters:
                filepath=os.path.join(parent,filename)
                if filepath[0] != '/' : filepath=wd+'/'+filepath
                allFiles.append(filepath)
    print("Found %d files in directory %s" %(len(allFiles), targetDir))
    return allFiles

def genTargetLabels(labelDir, targetLabelDir):
    # 找出labelDir下的所有label文件
    allLabelFiles=getAllFiles(labelDir, LABEL_FILE_EXT)
    # 遍历原来的label files
    for filepath in allLabelFiles:
        targetLines=[]
        entry=os.path.split(filepath)[1]
        targetFilepath=targetLabelDir+'/'+entry;
        for line in open(filepath):
            # 跳过空行或'#'开头的行
            line = line.strip()
            if not len(line) or line.startswith('#'): continue
            # 或取原来的class label (以index的形式)
            index=int(line.split(' ')[0])
            if allNames[index] in targetNames:
                # 获取name在targetNames列表中的位置作为新的class label
                newIndex=targetNames.index(allNames[index])
                splitted=line.split(' ')
                # 用新的class label替换掉旧的label
                splitted[0]=repr(newIndex)
                # 组合成一个新行
                newLine=' '.join(splitted)
                # 写入到目标list
                targetLines.append(newLine)
        if len(targetLines):
            with open(targetFilepath,'w') as F:
                for l in targetLines: F.write(l+'\n')

def getNames(pathsList):
    names=[]
    for name in pathsList:
        names.append(os.path.split(name)[1].split('.')[0])
    return names

def genTrainningDataList(trainningDir, labelsDir, newTrainningDataFile):
    labelsList=getAllFiles(labelsDir, LABEL_FILE_EXT)
    labelBodyNames=getNames(labelsList)
    trainningList=getAllFiles(trainningDir, TRAINNING_FILE_EXT)
    traningBodyNames=getNames(trainningList)
    newTrainningList = []
    for i in range(len(traningBodyNames)):
        if traningBodyNames[i] in labelBodyNames:
            newTrainningList.append(trainningList[i])
    with open(newTrainningDataFile,'w') as F:
        for line in newTrainningList: F.write(line+'\n')

def uniqueString():
    random.seed()
    str1=time.strftime("%H%M%S")
    str2= ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789',4))
    return str1+str2

def main():
    global uniquePostfix
    if len(sys.argv)!=5:
        print("Usage:\n\t%s <trainningImagesDir> <trainningLabelsDir> <allNamesFile> <targetNamesFile>\n" % sys.argv[0])
        sys.exit(0)
    # 获取当前工作目录
    wd=os.getcwd()
    # 设置必要的参数
    setParams(sys.argv, wd)
    # 设置唯一后缀
    uniquePostfix=uniqueString()
    # 创建新的labels目录及文件
    prefix=os.path.split(trainningLabelsDir)[1]
    targetLabelsDir=wd+'/'+prefix+'_'+uniquePostfix
    # 创建目标目录
    if not os.path.exists(targetLabelsDir):
        os.makedirs(targetLabelsDir)
    if not os.path.isdir(targetLabelsDir):
        print('Create directory(%s) failed: there is a file with the same name!' % targetLabelsDir)
        return -1
    # 创建新的labels
    genTargetLabels(trainningLabelsDir, targetLabelsDir)
    # 新的trainning list file全路径
    newTrainningDataFile=wd+'/train_'+uniquePostfix+'.txt'
    # 生成新的trainning list
    # genTrainningDataList()必须在genTargetLabels()之后调用
    genTrainningDataList(trainningImagesDir, targetLabelsDir, newTrainningDataFile)

if __name__ =="__main__":
    main()
