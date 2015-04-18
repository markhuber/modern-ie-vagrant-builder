import json
import wget
import hashlib
import urllib2
import os.path
import zipfile
import virtualbox
import time

DEBUG = False
vbox = virtualbox.VirtualBox()


def log(msg):
    if DEBUG: print msg


def md5sum(filename, blocksize=65536):
    if filename is None or not os.path.exists(filename):
        log('md5sum: zip file does not exist to calculate MD5, skipping...')
        return

    hash = hashlib.md5()
    with open(filename, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hash.update(block)
    return hash.hexdigest()


def compareMd5Hashes(name, build=0):
    fileIndex = 1
    file = destinationDir(build) + name + '.md5'
    log('Comparing MD5 Hash from: ' + file)
    if not os.path.exists(file):
        return False

    storedMd5 = open(file).readline().strip()
    print 'Stored MD5: ' + storedMd5
    return storedMd5.lower() == urllib2.urlopen(files[fileIndex]['md5']).read().lower()


def unzip(source_filename, dest_dir):
    if source_filename is None or not os.path.exists(source_filename):
        log('Unzip: zip file does not exist, skipping...')
        return getOvaName(dest_dir + source_filename + '.md5')

    log('Unzipping ' + source_filename + ' to ' + dest_dir)
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)
        return zf.namelist()[0]


def writeMd5File(filename, md5, build, ovaFile):
    if filename is None or not os.path.exists(filename):
        log('writeMd5File: zip file does not exist, skipping...')
        return

    if len(ovaFile) == 0:
        log('writeMd5File: No updated OVA File found...')
        return

    log('Writing MD5: ' + destinationDir(build) + filename + '.md5')
    target = open(destinationDir(build) + filename + '.md5', 'w')
    target.truncate()
    target.write(md5 + '\n')
    target.write(ovaFile + '\n')
    target.close()


def destinationDir(build):
    return './downloads/' + str(build) + '/'


def vboxVmExists(name):
    matching = [vm.name for vm in vbox.machines if name in vm.name]
    return len(matching) > 0


def vboxGetName(filename, build=0):
    manifest = destinationDir(build) + filename + '.md5'
    if not os.path.exists(manifest):
        return ''

    ovaFile = getOvaName(manifest)

    if (len(ovaFile) > 0):
        return build + '-' + ovaFile.replace(' ', '').replace('.ova', '').strip()
    else:
        return ''


def getOvaName(manifest):
    target = open(manifest)
    md5 = target.readline()
    ovaFile = target.readline()

    return ovaFile


def importVbox(filename, build, vmName):
    file = (destinationDir(build) + filename).strip()

    log('importVbox filename: ' + file)
    if filename is not None: log('importVbox exists:' + str(os.path.exists(file)))
    if filename is None or not os.path.exists(file):
        log('importVbox: No OVA file to import, skipping...')
        return

    if vboxVmExists(vmName):
        log('VM already imported to VirtualBox: ' + vmName)
        return

    log('Importing file: ' + file + ' with name: ' + vmName)

    appliance = vbox.create_appliance()

    appliance.read(os.path.abspath(file.strip()).strip())

    desc = appliance.find_description(filename.strip().replace('.ova', ''))
    desc.set_name(vmName)

    p = appliance.import_machines()
    p.wait_for_completion()


def downloadFile(url, name, build):
    if not compareMd5Hashes(name, build):
        wget.download(url)
    return name


json_data = open('result.json').read()
data = json.loads(json_data)

linuxOsList = data['osList'][0]
browsers = linuxOsList['softwareList'][0]['browsers']


def activateWinRM(vmname):
    sleeptime = 60
    if 'Win7' in vmname:
        sleeptime = 30
    print 'activateWinRM: ' + vmname
    session = virtualbox.Session()
    vm = vbox.find_machine(vmname)
    print 'vm: ' + str(vm)
    progress = vm.launch_vm_process(session, 'gui', '')
    progress.wait_for_completion(-1)
    print 'Starting VM...'
    time.sleep(sleeptime)
    gs = session.console.guest.create_session('IEUser', 'Passw0rd!')
    print 'Creating bin directory...'
    gs.execute('C:\\Windows\\System32\\cmd.exe', ['/C', 'mkdir C:\\Users\\IEUser\\bin'])
    gs.copy_to('./bin/elevate.exe', 'C:\\Users\\IEUser\\bin\\elevate.exe')
    gs.copy_to('./bin/install-winrm.cmd', 'C:\\Users\\IEUser\\bin\\install-winrm.cmd')
    gs.copy_to('./bin/fixnetwork.ps1', 'C:\\Users\\IEUser\\bin\\fixnetwork.ps1')
    print 'Installing WinRM...Please click ok on the UAC prompt...'
    process, stdout, stderr = gs.execute('C:\\Users\\IEUser\\bin\\elevate.exe', ['/k', 'C:\\Users\\IEUser\\bin\\install-winrm.cmd'])
    print 'Sleeping 60 seconds...'
    time.sleep(sleeptime)
    print 'Removing bin directory...'
    process, stdout, stderr = gs.execute('C:\\Windows\\system32\\cmd.exe', ['/C', 'rmdir /s /q C:\\Users\\IEUser\\bin'])
    print 'Shutting down vm...'
    session.console.power_button()
    time.sleep(5)
    session.unlock_machine()

for x in range(0, len(browsers)):
    fileIndex = 1

    build = browsers[x]['build']
    files = browsers[x]['files']

    md5 = files[fileIndex]['md5']
    name = files[fileIndex]['name']
    url = files[fileIndex]['url']

    fileMatchesMd5 = compareMd5Hashes(name, build)

    if fileMatchesMd5:
        action = 'File exists and matches MD5. No Action Taken'
    else:
        action = 'File does not exist or match MD5. File will be downloaded'
    print '---------------------------------------------------'
    print 'Build: ' + build
    print 'MD5: ' + md5
    print 'Name: ' + name
    print 'URL: ' + url
    print 'Match: ' + str(fileMatchesMd5)
    print 'Action: ' + action
    print 'vboxName: ' + vboxGetName(name, build)
    print 'vboxExists: ' + str(vboxVmExists(vboxGetName(name, build)))
    print '---------------------------------------------------'

    file = downloadFile(url, name, build)
    print ''
    print 'Unpacking...'
    ovaFile = unzip(file, destinationDir(build))
    print 'Storing MD5...'
    writeMd5File(file, md5sum(file), build, ovaFile)
    print 'Removing zip file...'
    if os.path.exists(file): os.remove(file)
    print 'Importing OVA...'
    importVbox(ovaFile, build, vboxGetName(name, build))

    if ('XP' not in name) and ('Win8' not in name): activateWinRM(vboxGetName(name, build))

    if DEBUG: break