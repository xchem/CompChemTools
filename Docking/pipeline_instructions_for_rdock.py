class WritePrm(luigi.Task):
    job_directory = luigi.Parameter()
    job_name = luigi.Parameter()

    def requires(self):
        pass

    def output(self):
        return luigi.LocalTarget(os.path.join(self.job_directory, self.job_prm))

    def run(self):
        os.chdir(self.job_directory)
        job_input = '''RBT_PARAMETER_FILE_V1.00
TITLE %s

RECEPTOR_FILE %s_apo_desolv.mol2
RECEPTOR_FLEX 3.0

##################################################################
### CAVITY DEFINITION: REFERENCE LIGAND METHOD
##################################################################
SECTION MAPPER
    SITE_MAPPER RbtLigandSiteMapper
    REF_MOL %s_mol.sdf
    RADIUS 6.0
    SMALL_SPHERE 1.0
    MIN_VOLUME 100
    MAX_CAVITIES 1
    VOL_INCR 0.0
   GRIDSTEP 0.5
END_SECTION

#################################
#CAVITY RESTRAINT PENALTY
#################################
SECTION CAVITY
    SCORING_FUNCTION RbtCavityGridSF
    WEIGHT 1.0
END_SECTION

#################################
## PHARMACOPHORIC RESTRAINTS
#################################
#SECTION PHARMA
#    SCORING_FUNCTION RbtPharmaSF
#    WEIGHT 1.0
#    CONSTRAINTS_FILE pharma_cdk2.const
#   OPTIONAL_FILE optional.const
#   NOPT 3
#   WRITE_ERRORS TRUE
#END_SECTION

''' %(self.job_name, self.job_name, self.job_name)

        with self.output().open('wb') as f:
            f.write(job_input)

class WriteRDJob(luigi.Task):
    job_directory = luigi.Parameter()
    job_name = luigi.Parameter()

    def requires(self):
        return WritePrm(job_directory=self.job_directory, job_name=self.job_name)


    def output(self):
        return luigi.LocalTarget(os.path.join(self.job_directory, self.job_filename))

    def run(self):
        os.chdir(self.job_directory)

        job_script = '''#!/bin/bash
cd %s
touch %s_rdock.running
grep -v HOH %s_apo.pdb | grep -v \ ACT\  | grep -v DMS  > %s_apo_desolv.pdb
obabel -ipdb %s_apo_desolv.pdb -osy2 -O %s_apo_desolv.mol2
rbcavity -was -d -r %s > %s_rbcavity.log
rbdock -i %s_mol.sdf -o %s_rdock_out -r %s -p dock.prm -n 50 > %s_rbcavity.log
rm %s_rdock.running
touch %s_rdock.done
''' % (self.job_directory, self.job_name, self.job_name, self.job_name, self.job_name,
       self.job_name, self.input().path, self.job_name, self.job_name, self.job_name,
       self.input().path, self.job_name, self.job_name, self.job_name) 

        with self.output().open('wb') as f:
            f.write(job_script)
