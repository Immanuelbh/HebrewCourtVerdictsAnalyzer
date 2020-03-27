from extraForJson import *


def clean_spaces(text):
    temp_list = list()
    for index in range(len(text)):
        if text[index] == ' ':
            if index != 0:
                if text[index - 1] == ' ':
                    continue
            else:
                continue
        temp_list.append(text[index])
    while temp_list[-1] == ' ':  # clean last spaces in the end
        temp_list.pop(-1)
    return "".join(temp_list)


def makeSureNoNumber(line, minimum=1, maximum=20):
    for number in range(minimum, maximum):
        if str(number) in line:
            line = line.replace(str(number), '')
    return clean_spaces(line)


def drop_extra_info(text, minimum=1, maximum=5):
    product = list()
    bannedWords = ['נגד']
    temp = text.splitlines()
    for index in range(len(temp)):
        if '__' in temp[index]:  # we got all we want lets pack it and go back
            return "\n".join(product)
        elif ':' in temp[index] or 'לפני' in temp[index]:  # In case we have more rows between row 0 to judges names
            maximum = index
        if index not in range(minimum, maximum):  # Include all but unnecessary information
            doBreak = False
            for word in bannedWords:
                if word in temp[index]:
                    doBreak = True
                    break
            if doBreak:
                continue
            product.append(temp[index])
    return '\n'.join(product)


def isThereMore(line, key=';'):
    if key in line:
        values = line.split(key)
        for index in range(len(values)):
            values[index] = clean_spaces(values[index])
        return values
    return line


def get_Key(temp):
    temp_dict = {
        'לפני': ['לפני'],
        'בשם העותר': ['בשם המערערים', 'בשם המערער', 'בשם המערערת', 'בשם המערערות',
                      'בשם העותר', 'בשם העותרת', 'בשם העותרים', 'בשם העותרות',
                      'בשם המבקש', 'בשם המבקשת', 'בשם המבקשים', 'בשם המבקשות'],
        'בשם המשיב': ['בשם המשיבים', 'בשם המשיב', 'בשם המשיבות', 'בשם המשיבה'],
        'העותר': ['המערערים', 'המערער', 'המערערת', 'המערערות',
                  'העותר', 'העותרת', 'העותרים', 'העותרות',
                  'המבקשת', 'המבקשים', 'המבקשות'],
        'המשיב': ['המשיבים', 'המשיב', 'המשיבות', 'המשיבה'],
    }

    for key, item in temp_dict.items():
        if temp in item:
            return key
    return None  # if it get here we missing some keys


def isSpecial(key, values, keyWord='לפני', replaceWord='כבוד'):
    if key == keyWord:
        newValues = list()
        for value in values:
            newValues.append(clean_spaces(value.replace(replaceWord, '')))
            return key, newValues
    return key, values


def gotVerdict(line):
    verdictKeyList = ['החלטה', 'פסק-דין']
    for key in verdictKeyList:
        if key in line:
            return True, key
    return False, None


def gotExtraInformation(line):
    ExtraInformationKeys = ['בקשה']
    for key in ExtraInformationKeys:
        if key in line:
            return True
    return False


def getKeyList(mustHave=True):
    if mustHave:
        return ['לפני', 'העותר', 'המשיב', 'מספר הליך', 'סוג מסמך', 'סיכום']
    return ['מידע נוסף', 'בשם העותר', 'בשם המשיב']


def iGotItAll(tempDict, keyList):
    for key in keyList:
        if key in tempDict.keys():
            if tempDict[key] is None:
                return False
        else:
            return False
    return True


def doc_into_dict(text):
    text = drop_extra_info(text)
    shouldIAdd, someKey, value_list, numOfValues = False, None, None, 1
    doc_dict = dict()
    temp = text.splitlines()
    doc_dict['מספר הליך'] = temp[0]
    for index in range(1, len(temp)):
        if ':' in temp[index]:
            if shouldIAdd:  # finished getting values for previous key
                someKey = makeSureNoNumber(someKey)
                tempKey = get_Key(someKey)
                tempKey, value_list = isSpecial(tempKey, value_list)
                doc_dict[tempKey] = value_list
                numOfValues = 1
            value_list = list()
            temp_list = temp[index].split(':')
            someKey = temp_list[0]
            if len(temp_list[1]) > 0:
                value_list.append(temp_list[1])
            else:
                shouldIAdd = True
                continue
        elif gotVerdict(temp[index])[0]:  # what remain is verdict text
            doc_dict['סוג מסמך'] = gotVerdict(temp[index])[1]
            doc_dict['סיכום'] = "\n".join(temp[index + 1:])
            break
        else:  # get another values for key or get extra text pre verdict
            strValue = str(numOfValues) + '. '  # string splitter
            if strValue in temp[index]:
                numOfValues += 1
                value_list.append(temp[index].split(strValue)[1])
            elif gotExtraInformation(temp[index]):
                doc_dict['מידע נוסף'] = isThereMore(temp[index])
            else:
                value_list.append(temp[index])
    if iGotItAll(doc_dict, getKeyList()):
        for key in getKeyList(mustHave=False):
            if key not in doc_dict.keys():
                doc_dict[key] = None
        return doc_dict, True
    return text, False


def run():
    readFolder = get_path() + os.sep + 'json_products'
    handledFolder = get_path() + os.sep + 'handled_json_products'
    unhandledFolder = get_path() + os.sep + 'unhandled_json_products'
    while True:
        listOfFiles = getFilesFromFolder(folderName=readFolder)
        if len(listOfFiles) > 0:
            for fileName in listOfFiles:
                doc = readJson('', fileName, side='')
                text = drop_extra_info(doc['Doc Details'])
                txtDict, succeed = doc_into_dict(text)
                doc['Doc Details'] = txtDict
                writeFolder = handledFolder if succeed else unhandledFolder
                #os.remove(fileName)
                fileName = change_path(fileName, writeFolder)
                writeJson('', fileName, doc, side='')
        else:
            callSleep(minutes=10)  # after finished with all the files wait a bit - hours * minutes * seconds


if __name__ == '__main__':
    run()