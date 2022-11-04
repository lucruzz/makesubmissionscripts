import json

class SubmissionFile:
    def __init__(self) -> None:
        self.shabang = '#!/bin/bash'
        self.nodes = '#SBATCH --nodes='
        self.ntaskspernode = '#SBATCH --ntasks-per-node='
        self.ntasks = '#SBATCH --ntasks='
        self.cpupertask = '#SBATCH --cpus-per-task='
        self.partition = '#SBATCH --partition='
        self.jobname = '#SBATCH --jobname='
        self.walltime = '#SBATCH --time='
        self.exclusive = '#SBATCH --exclusive'
        pass

    def getShabang(self):
        return self.shabang
    
    def setNodes(self, nodes):
        self.nodes = self.nodes + nodes

    def getNodes(self):
        return self.nodes

    def setNtaskspernode(self, taskspernode):
        self.ntaskspernode = self.ntaskspernode + taskspernode

    def getNtaskspernode(self):
        return self.ntaskspernode

    def setNtasks(self, tasks):
        self.ntasks = self.ntasks + tasks

    def getNtasks(self):
        return self.ntasks

    def setCpupertask(self, cpupertasks):
        self.cpupertask = self.cpupertask + cpupertasks
    
    def getCpupertask(self):
        return self.cpupertask

    def setPartition(self, partition):
        self.partition = self.partition + partition
    
    def getPartition(self):
        return self.partition
    
    def setJobname(self, jobname):
        self.jobname = self.jobname + jobname
    
    def getJobname(self):
        return self.jobname
    
    def setWalltime(self, walltime):
        self.walltime = self.walltime + walltime

    def getWalltime(self):
        return self.walltime

    def getExclusive(self):
        return self.exclusive

    def getAllDirectives(self):
        lines = list()
        
        lines.append(self.getShabang())
        lines.append(self.getNodes())
        lines.append(self.getNtaskspernode())
        lines.append(self.getNtasks())
        lines.append(self.getCpupertask())
        lines.append(self.getPartition())
        lines.append(self.getJobname())
        lines.append(self.getWalltime())
        lines.append(self.getExclusive())
        
        return lines

    def putOnFileDirectives(self, filename):
        
        scriptFile = open(filename, "a")
        values = self.getAllDirectives()
        
        for line in values:
            scriptFile.writelines(line)
            scriptFile.writelines('\n')
        
        scriptFile.writelines('\n')

        scriptFile.close()
        
        return None

class RunRamxl:
    def __init__(self, bootstrap, inputfile) -> None:
        self.bootstrap = bootstrap
        self.inputfile = inputfile
        pass

    def getBootstrap(self):
        return self.bootstrap
    
    def getInputfile(self):
        return self.inputfile

    def Commands(self):
        
        lines = list()
        lines.append('module load raxml/8.2_openmpi-2.0_gnu')
        lines.append('cd $SLURM_SUBMIT_DIR')
        lines.append('ulimit -s unlimited')
        lines.append('ulimit -c unlimited')
        lines.append('ulimit -v unlimited')
        lines.append('EXEC="raxmlHPC-HYBRID-AVX"')
        lines.append('BOOTSTRAP='+ self.getBootstrap())
        lines.append('INPUT='+ self.getInputfile())
        lines.append('PREFIX=`basename ${input} | cut -d "." -f`')
        lines.append('PARAM="-T $SLURM_CPUS_PER_TASK -m PROTGAMMAWAG -p 112233 -s ${INPUT} -b 223344 -N $BOOTSTRAP -n ${PREFIX}-hybrid-${SLURM_NTASKS}.phylip_tree2.raxml -c 4 -f d"')
        lines.append('echo $INPUT')
        lines.append('time srun -n $SLURM_NTASKS -c $SLURM_CPUS_PER_TASK $EXEC $PARAM')

        return lines
    
    def doubleSpace(self):
        l = []
        l.append('echo $INPUT')
        l.append('ulimit -v unlimited')
        l.append('cd $SLURM_SUBMIT_DIR')
        l.append('module load raxml/8.2_openmpi-2.0_gnu')
        return l

    def putOnFileCommands(self, filename):
        
        scriptFile = open(filename, "a")
        values = self.Commands()
        l = self.doubleSpace()

        for line in values:
            
            if(line in l):
                if(line == 'echo $INPUT'):
                    scriptFile.writelines('\n')
                scriptFile.writelines(line)
                scriptFile.writelines('\n\n')
                l.pop()
                continue

            scriptFile.writelines(line)
            scriptFile.writelines('\n')

        scriptFile.close()

        return None

def readFromJSON():
    try:
        jsonfile = open('data.json', 'r')
        data = json.load(jsonfile)
    except json.decoder.JSONDecodeError as error:
        print('There must be some error on your JSON file! Please, verify!')
    except FileNotFoundError as error:
        print('Your JSON file could not be found! Please, verify!')

    for key, value in data.items():
        print(key)
        fileSubmission = key

        for info in value:
            
            scriptFile = SubmissionFile()
            executeRaxml = RunRamxl(info['bootstrap'], info['input'])
            
            scriptFile.setNodes(info['nodes'])
            scriptFile.setNtaskspernode(info['ntaskspernode'])
            scriptFile.setNtasks(info['ntasks'])
            scriptFile.setCpupertask(info['cpupertask'])
            scriptFile.setPartition(info['partition'])
            scriptFile.setJobname(info['jobname'])
            scriptFile.setWalltime(info['time'])

            fileSubmission += '-' + info['bootstrap'] + 'bs.sh'

            scriptFile.putOnFileDirectives(fileSubmission)
            executeRaxml.putOnFileCommands(fileSubmission)

            fileSubmission = key

def readFromCommandLine():
    import sys
    
    nnodes = sys.argv[1]        # '4'
    taskspernode = sys.argv[2]  # '1'
    tasks = sys.argv[3]         #'4'
    ncpupertask = sys.argv[4]   #'24'
    p = sys.argv[5]             # 'nvidia_long'
    jobname = sys.argv[6]       # '2000bs-24th'
    walltime = sys.argv[7]      # '05:00:00'

    inputfile = sys.argv[8]     # '$SCRATCH/raxml/aminoacido.phylip'
    bootstrap = sys.argv[9]     #'2000'

    fileSubmission = 'sub.sh'

    scriptFile = SubmissionFile()
    executeRaxml = RunRamxl(bootstrap, inputfile)

    scriptFile.setNodes(nnodes)
    scriptFile.setNtaskspernode(taskspernode)
    scriptFile.setNtasks(tasks)
    scriptFile.setCpupertask(ncpupertask)
    scriptFile.setPartition(p)
    scriptFile.setJobname(jobname)
    scriptFile.setWalltime(walltime)

    scriptFile.putOnFileDirectives(fileSubmission)
    executeRaxml.putOnFileCommands(fileSubmission)

if __name__=='__main__':
    readFromCommandLine()
    #readFromJSON()
