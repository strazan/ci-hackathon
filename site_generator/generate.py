import os
import urllib.request
from stat import S_ISDIR
from json import loads
import re
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTICIIPANTS_DIR = "participants"


participantsFolder = "%s/site/_participants"%(BASE_DIR,)
solutionsFolder = "%s/site/_solutions"%(BASE_DIR,)

BASE_URL =  sys.argv[1] if len(sys.argv) > 1 else  ''

def htmlPageIn(folder):
    files = os.listdir(folder)

    for f in files:
        if re.compile("[iI][nN][dD][eE][xX]\.[hH][tT][mM][lL]?").match(f):
            return f

    return None

def generateSolution(team, folder):

    print("Getting solutions for...", folder, team)
    solutions = os.listdir(folder)

    result = []

    for solution in solutions:
        if S_ISDIR(os.stat("%s/%s"%(folder, solution)).st_mode):
            solution_page = open("%s/%s_%s.md"%(solutionsFolder, team, solution), 'w')

            solution_page.write("---\n")

            solution_page.write("layout: solution\n")
            solution_page.write("team: %s\n"%(team,))
            solution_page.write("sol: %s\n"%(solution,))

            indexPreview = htmlPageIn("%s/%s"%(folder, solution))

            if indexPreview:
                solution_page.write("demo: %s\n"%(indexPreview))

            solution_page.write("---\n")

            readmeContent = getReadmeContent("%s/%s"%(folder, solution))

            # copy folder
            try:
                shutil.copytree("%s/%s"%(folder, solution), "%s/%s_%s"%(solutionsFolder, team, solution))
            except:
                pass

            if readmeContent:
                solution_page.write(readmeContent)
            else:
                solution_page.write(solution + "\n")
            
            solution_page.close()

            result.append("%s_%s"%(team, solution))

    return result


def getReadmeContent(folder):
    files = os.listdir(folder)

    for f in files:
        if re.compile("[rR][eE][aA][dD][mM][eE]\.(md|markdown)").match(f):
            return open("%s/%s"%(folder, f), 'r').read()

    return None

def setup_site():
    print("Processing site collections...")


    def clean_folder(name):

        print("Recreating", name, "folder")

        try:
            os.rmdir(name)
        except Exception as e:
            pass
        if not os.path.exists(name):
            os.mkdir(name)

    clean_folder(participantsFolder)
    clean_folder(solutionsFolder)

def process_participants():
    i = 0
    for folderName in os.listdir("%s/%s"%(BASE_DIR, PARTICIIPANTS_DIR)):

        if S_ISDIR(os.stat("%s/%s/%s"%(BASE_DIR, PARTICIIPANTS_DIR, folderName)).st_mode):

            names = folderName.split("_")

            print("Discovering team...", names, "Gathering metadata from github API...")

            meta = {}

            for name in names:
                url = "https://api.github.com/users/%s"%(name,)
                print("Requesting to", url)
                try:
                    with urllib.request.urlopen(url) as data:
                        meta[name] = loads(data.read())
                except:
                    meta[name] = {}
                    
            teamPage = open("%s/%s.md"%(participantsFolder, folderName), 'w')

            solutions = generateSolution(folderName, "%s/%s/%s"%(BASE_DIR, PARTICIIPANTS_DIR, folderName))

            # print header
            teamPage.write("---\n")
            teamPage.write("layout: team\n")
            teamPage.write("name: %s\n"%(folderName,))
            teamPage.write("sort: %s\n"%(i,))
            i += 1
            teamPage.write("team: \n")

            for k, v in meta.items():
                teamPage.write("  - id : \"%s\" \n"%(k,))
                for meta, value in v.items():
                    teamPage.write("    %s : \"%s\" \n"%(meta, value))
            teamPage.write("solution_count: %s\n"%(len(solutions,)))

            teamPage.write("---\n")

            # print folder Readme content
            readMeFile = getReadmeContent("%s/%s/%s"%(BASE_DIR, PARTICIIPANTS_DIR, folderName))


            if readMeFile:
                teamPage.write(readMeFile)
            else:
                teamPage.write("## Solutions\n")

                for solution in solutions:
                    teamPage.write("- [%s](%s/solutions/%s.html)\n"%(solution,BASE_URL,solution))
                # print solution list instead



setup_site()
process_participants()