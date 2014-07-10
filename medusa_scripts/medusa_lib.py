# medusa-lib: 

# general

def run_cmd(cmd, ignore_error=False, verbose=False):
    '''
    Run a command line command
    Returns True or False based on the exit code
    '''
    import sys,subprocess
    sys.stderr.write('Running %s\n'%cmd)
    proc = subprocess.Popen(cmd,shell=(sys.platform!="win32"),
                            stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out = proc.communicate()
    return_code = proc.returncode
    if verbose:
        sys.stderr.write('%s\n'%str(out[0].decode('utf-8')))
        sys.stderr.write('\n')
    if return_code != 0 and not ignore_error:
        sys.stderr.write('Command (%s) failed w/ error %d\n'
                        %(cmd, return_code))
        sys.stderr.write('%s\n'%str(out[1].decode('utf-8')))
        sys.stderr.write('\n')

    return bool(not return_code)


# seqIO parsing

def renameSeqFile(inp,new_name='renamed.fasta',tag='seq',threshold=1000,conv_table=None,loc='./'):
	""" Rename a target fasta file and its sequences. Produces a new file
	 and (optionally) a conversion table. By default sequences shorter
	 than 1000 are removed (see threshold option) """
	# TODO: can use genbank to produce input files, right?
	from Bio.SeqIO import parse,write
	sequences=[f for f in parse(inp,'fasta')]
	i,renamed=0,[]
	if conv_table != None: ctable=open(loc + conv_table,'w')
	for s in sequences:
		if len(s.seq) <= threshold: continue
		i+=1
		old_id,new_id=s.id,'%s_%s' %(tag,i)
		s.id,s.description=new_id,''
		renamed.append(s)
		if conv_table != None: ctable.write('%s\t%s\n' %(old_id,new_id))
	write(renamed,loc+new_name,'fasta')
	return

def convertWithCtable(file_,ctable,out):
	""" Convert the names of a fasta using a conversion table"""
	from Bio.SeqIO import parse,write
	d={k:v for i in open(ctable) for k,v in i.strip().split()}
	sequences,renamed=[f for f in parse(file_,'fasta')],[]
	for s in sequences: s.id=d.get(s.id)
	write(sequences,out,'fasta')
	return

# mummer

def runMummer(file1,file2):
	""" Run nucmer aligner (required mummer to be installed) """
	fname1,fname2=file1.split('/')[-1],file2.split('/')[-1]
	tag1,tag2=fname1.split('.')[1],fname2.split('.')[1]
	prefix="%s_%s" %(tag1,tag2)
	cmd='nucmer --prefix=%s %s %s' %(prefix,file1,file2)
	ecode=run_cmd(cmd)
	if ecode == False: return False,'nucmer failed!'
	cmd2='show-coords -rcl %s.delta > %s.coords' %prefix
	ecode=run_cmd(cmd2)
	if ecode == False: return False,'show-coords failed!'
	return True,'no errors'

# tmp files

def storeTmpFasta(dir_,file_,**rename_args):
	""" If dir_ exists, write a renamed fasta there, otherwise create
		dir and write a fasta there"""
	import os
	if not os.path.exists(dir_): os.makedirs(dir_)
	rename_args['loc']=dir_
	renameSeqFile(file_,**rename_args)
	return

def cleanUp(dir_):
	#TODO
	return