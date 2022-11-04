# makesubmissionscripts

## To run

### Example:

The arguments are:

1. nodes = 4
2. taskspernode = 1
3. tasks = 4
4. cpupertask = 24
5. partition = nvidia_long
6. jobname = 2000bs-24th
7. time = 05:00:00
8. inputfile = $SCRATCH/raxml/aminoacido.phylip
9. bootstrap = 2000

```
python3 create-script.py 4 1 4 24 nvidia_long 2000bs-24th 05:00:00 $SCRATCH/raxml/aminoacido.phylip 2000
```
