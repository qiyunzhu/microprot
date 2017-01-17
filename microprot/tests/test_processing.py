from unittest import TestCase, main
from shutil import rmtree
from os import remove
from os.path import join
from tempfile import mkstemp, mkdtemp
from skbio.util import get_data_path
from skbio import Sequence

from microprot.scripts.processing import (extract_sequences,
                                          write_sequences,
                                          read_representatives,
                                          _processing)


class ProcessingTests(TestCase):
    def setUp(self):
        # temporary working directory
        self.working_dir = mkdtemp()

        # test data files
        dir = 'test_processing'
        self.input_faa = get_data_path(join(dir, 'input.faa'))
        self.represent = get_data_path(join(dir, 'represent.xml'))
        self.pdb_seqres = get_data_path(join(dir, 'pdb_seqres.txt'))

        # test protein sequences
        self.seqs = []
        x = Sequence('PIVQNLQGQMVHQAISPRTLNAWVKVVEEKAFSPEVIPMFSALSEGATPQDLNTML'
                     'NTVGGHQAAMQMLKETINEEAAEWDRLHPVHAGPIEPGQMREPRGSDIAGTTSTLQ'
                     'EQIGWMTHNPPIPVGEIYKRWIILGLNKIVRMYSPTSILDIRQGPKEPFRDYVDRF'
                     'YKTLRAEQASQEVKNWMTETLLVQNANPDCKTILKALGPAATLEEMMTACQGVGGP'
                     'GHKARVL')
        x.metadata['id'] = '3J4F_A'
        x.metadata['description'] = ('Chain A, Structure Of Hiv-1 Capsid Prote'
                                     'in By Cryo-em')
        self.seqs.append(x)
        x = Sequence('MIQRTPKIQVYSRHPAENGKSNFLNCYVSGFHPSDIEVDLLKNGERIEKVEHSDLS'
                     'FSKDWSFYLLYYTEFTPTEKDEYACRVNHVTLSQPKIVKWDRDM')
        x.metadata['id'] = '1K5N_B'
        x.metadata['description'] = ('Chain B, Hla-B2709 Bound To Nona-Peptide'
                                     ' M9')
        self.seqs.append(x)
        x = Sequence('KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGIL'
                     'QINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWR'
                     'NRCKGTDVQAWIRGCRL')
        x.metadata['id'] = '2VB1_A'
        x.metadata['description'] = ('Chain A, Hewl At 0.65 Angstrom Resolutio'
                                     'n')
        self.seqs.append(x)

    def tearDown(self):
        rmtree(self.working_dir)

    def test_extract_sequences(self):
        # extract all sequences
        obs = extract_sequences(self.input_faa)
        exp = self.seqs
        self.assertListEqual(obs, exp)

        # specify protein index
        obs = extract_sequences(self.input_faa, identifiers='2')
        exp = [self.seqs[1]]
        self.assertListEqual(obs, exp)

        # specify protein ID
        obs = extract_sequences(self.input_faa, identifiers='1K5N_B')
        exp = [self.seqs[1]]
        self.assertListEqual(obs, exp)

        # specify protein indexes using a comma-separated list
        obs = extract_sequences(self.input_faa, identifiers='1,3')
        exp = [self.seqs[0], self.seqs[2]]
        self.assertListEqual(obs, exp)

        # specify protein entries using an external file
        listfile = join(self.working_dir, 'list.txt')
        with open(listfile, 'w') as f:
            f.write('%s\n%s\n' % ('1K5N_B', '2VB1_A'))
        obs = extract_sequences(self.input_faa, identifiers=listfile)
        remove(listfile)
        exp = [self.seqs[1], self.seqs[2]]
        self.assertListEqual(obs, exp)

    def test_write_sequences(self):
        seqs = extract_sequences(self.input_faa, identifiers='1')
        outfile = join(self.working_dir, 'output.faa')
        write_sequences(seqs, outfile)
        with open(outfile, 'r') as f:
            obs = f.read().splitlines()
        remove(outfile)
        exp = ['>%s %s' % (self.seqs[0].metadata['id'],
                           self.seqs[0].metadata['description']),
               str(self.seqs[0])]
        self.assertListEqual(obs, exp)

    def test_read_representatives(self):
        obs = read_representatives(self.represent)
        exp = ['1k5n_B', '2vb1_A', '3j4f_A']
        self.assertListEqual(obs, exp)


if __name__ == '__main__':
    main()