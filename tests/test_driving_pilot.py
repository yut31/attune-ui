import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.io import savemat

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driving_prep',ROOT/'base/scripts/dataproc/prepare_driving_pilot.py')
prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)


class DrivingPreparationTests(unittest.TestCase):
    def test_mat_byte_offsets_recover_exact_channel_and_time_samples(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'raw').mkdir()
            matrix=np.arange(33*400,dtype=np.float32).reshape((33,400),order='F')
            path=root/'raw/example.set.part'
            savemat(path,{'EEG':{'nbchan':np.uint8(33),'srate':np.uint16(500),'data':matrix}},appendmat=False)
            entry={'name':'example.set','size':path.stat().st_size,'download_url':'unused'}
            with patch.object(prep,'ROOT',root):
                source=prep.RemoteMAT(entry);fields=source.fields()
                self.assertEqual(source.scalar(fields['nbchan']),33)
                self.assertEqual(source.scalar(fields['srate']),500)
                offset=fields['data']['data']+100*33*4
                values=np.frombuffer(source.fetch(offset,20*33*4),dtype='<f4').reshape((-1,33)).T
                np.testing.assert_array_equal(values,matrix[:,100:120])
                self.assertEqual(len(prep.CHANNELS),30)
                self.assertNotIn('A1',prep.CHANNELS)
                self.assertNotIn('A2',prep.CHANNELS)

    def test_response_pairing_and_slowest_decile(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'events.tsv'
            with path.open('w') as handle:
                writer=csv.DictWriter(handle,fieldnames=['onset','value'],delimiter='\t');writer.writeheader()
                for i in range(20):
                    onset=10+10*i
                    writer.writerow({'onset':onset,'value':251})
                    writer.writerow({'onset':onset+.2+i*.1,'value':253})
                    writer.writerow({'onset':onset+4,'value':254})
            trials,labels=prep.labeled_events(path)
            self.assertEqual(len(trials),20)
            np.testing.assert_array_equal(np.where(labels)[0],[18,19])
            np.testing.assert_allclose(trials[:,1],.2+np.arange(20)*.1)


if __name__=='__main__':unittest.main()
