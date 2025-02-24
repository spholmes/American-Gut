#!/usr/bin/env python

from StringIO import StringIO
from unittest import TestCase, main
from collections import defaultdict

from americangut.results_utils import (
    filter_mapping_file, clean_and_reformat_mapping,
    count_unique_sequences_per_otu, write_bloom_fasta
)

class ResultsUtilsTests(TestCase):
    def setUp(self):
        reformat_mapping_testdata.seek(0)

    def test_filter_mapping_file(self):
        output = StringIO()
        # filter to just fecal samples, keep the age and title_acronym columns
        criteria = {'SIMPLE_BODY_SITE': lambda x: x == 'FECAL',
                    'AGE': lambda x: float(x) > 20,
                    'TITLE_ACRONYM': None}
        filter_mapping_file(filter_mapping_testdata, output, criteria)
        output.seek(0)

        # parse output
        test_mapping = [l.strip().split('\t') for l in output]

        # fish header, verify sanity of it
        test_header = test_mapping[0]
        self.assertEqual(len(test_header), 4)
        self.assertEqual(test_header[0], '#SampleID')
        self.assertEqual(sorted(test_header), sorted(['#SampleID',
                                                      'SIMPLE_BODY_SITE',
                                                      'AGE', 'TITLE_ACRONYM']))

        # check each record
        test_sbs = test_header.index('SIMPLE_BODY_SITE')
        test_age = test_header.index('AGE')
        for l in test_mapping[1:]:
            self.assertEqual(len(l), 4)
            self.assertEqual(l[test_sbs], 'FECAL')
            self.assertTrue(float(l[test_age]) > 20)

    def test_clean_and_reformat_mapping(self):
        """Exercise the reformat mapping code, verify expected results"""
        out = StringIO()
        is_pgp = ['A', 'C']
        clean_and_reformat_mapping(reformat_mapping_testdata, out, 'body_site',
                                   'test', pgp_ids=is_pgp)
        out.seek(0)

        # verify the resulting header structure
        test_mapping = [l.strip().split('\t') for l in out]
        test_header = test_mapping[0]
        self.assertEqual(test_header[-7:], ['IS_PGP', 'SIMPLE_BODY_SITE', 
                                            'TITLE_ACRONYM', 'TITLE_BODY_SITE', 
                                            'HMP_SITE', 'AGE_CATEGORY', 
                                            'BMI_CATEGORY'])

        self.assertEqual(test_mapping[1][:], ['A', 'w00t', '43.0',
                                              'UBERON_mucosa_of_tongue', '5',
                                              'Yes', 'ORAL', 'test', 'test-ORAL',
                                              'ORAL', '40s', 'Underweight'])
        self.assertEqual(test_mapping[2][:], ['B', 'left', '51.0',
                                              'UBERON:FECES', '10',
                                              'No', 'FECAL', 'test', 'test-FECAL',
                                              'FECAL', '50s', 'Underweight'])
        self.assertEqual(test_mapping[3][:], ['C', 'right', '12.0',
                                              'UBERON_FECES', '15',
                                              'Yes', 'FECAL', 'test', 'test-FECAL',
                                              'FECAL', 'Child', 'Underweight'])
        self.assertEqual(test_mapping[4][:], ['E', 'stuff', '56.0',
                                              'UBERON:SKIN', '37',
                                              'No', 'SKIN', 'test', 'test-SKIN',
                                              'SKIN', '50s', 'Severely obese'])

    def test_clean_and_reformat_mapping_nopgp(self):
        """Exercise the reformat mapping code, verify expected results"""
        out = StringIO()
        clean_and_reformat_mapping(reformat_mapping_testdata, out, 'body_site',
                                   'test')
        out.seek(0)

        # verify the resulting header structure
        test_mapping = [l.strip().split('\t') for l in out]
        test_header = test_mapping[0]
        self.assertEqual(test_header[-7:], ['IS_PGP', 'SIMPLE_BODY_SITE', 
                                            'TITLE_ACRONYM', 'TITLE_BODY_SITE', 
                                            'HMP_SITE', 'AGE_CATEGORY', 
                                            'BMI_CATEGORY'])

        self.assertEqual(test_mapping[1][:], ['A', 'w00t', '43.0',
                                              'UBERON_mucosa_of_tongue', '5',
                                              'No', 'ORAL', 'test', 'test-ORAL',
                                              'ORAL', '40s', 'Underweight'])
        self.assertEqual(test_mapping[2][:], ['B', 'left', '51.0',
                                              'UBERON:FECES', '10',
                                              'No', 'FECAL', 'test', 'test-FECAL',
                                              'FECAL', '50s', 'Underweight'])
        self.assertEqual(test_mapping[3][:], ['C', 'right', '12.0',
                                              'UBERON_FECES', '15',
                                              'No', 'FECAL', 'test', 'test-FECAL',
                                              'FECAL', 'Child', 'Underweight'])
        self.assertEqual(test_mapping[4][:], ['E', 'stuff', '56.0',
                                              'UBERON:SKIN', '37',
                                              'No', 'SKIN', 'test', 'test-SKIN',
                                              'SKIN', '50s', 'Severely obese'])

    def test_clean_and_reformat_mapping_allpgp(self):
        """Exercise the reformat mapping code, verify expected results"""
        out = StringIO()
        clean_and_reformat_mapping(reformat_mapping_testdata, out, 'body_site',
                                   'test', pgp_ids=True)
        out.seek(0)

        # verify the resulting header structure
        test_mapping = [l.strip().split('\t') for l in out]
        test_header = test_mapping[0]
        self.assertEqual(test_header[-7:], ['IS_PGP', 'SIMPLE_BODY_SITE', 
                                            'TITLE_ACRONYM', 'TITLE_BODY_SITE', 
                                            'HMP_SITE', 'AGE_CATEGORY', 
                                            'BMI_CATEGORY'])

        self.assertEqual(test_mapping[1][:], ['A', 'w00t', '43.0',
                                              'UBERON_mucosa_of_tongue', '5',
                                              'Yes', 'ORAL', 'test', 'test-ORAL',
                                              'ORAL', '40s', 'Underweight'])
        self.assertEqual(test_mapping[2][:], ['B', 'left', '51.0',
                                              'UBERON:FECES', '10',
                                              'Yes', 'FECAL', 'test', 'test-FECAL',
                                              'FECAL', '50s', 'Underweight'])
        self.assertEqual(test_mapping[3][:], ['C', 'right', '12.0',
                                              'UBERON_FECES', '15',
                                              'Yes', 'FECAL', 'test', 'test-FECAL',
                                              'FECAL', 'Child', 'Underweight'])
        self.assertEqual(test_mapping[4][:], ['E', 'stuff', '56.0',
                                              'UBERON:SKIN', '37',
                                              'Yes', 'SKIN', 'test', 'test-SKIN',
                                              'SKIN', '50s', 'Severely obese'])

    def test_count_unique_sequences_per_otu(self):
        input_fasta = StringIO(test_fasta)
        otu_map = StringIO(test_otu_map)

        otu_ids = set(['otu1', 'otu2'])

        result = count_unique_sequences_per_otu(otu_ids, otu_map, input_fasta)

        expected = {x:defaultdict(int) for x in otu_ids}
        expected['otu1']['ATCG'] = 3
        expected['otu2']['AT'] = 2
        expected['otu2']['A'] = 1

        self.assertEqual(expected, result)


    def test_write_bloom_fasta(self):
        otu_ids = set(['otu1', 'otu2'])
        unique_counts = {x:defaultdict(int) for x in otu_ids}
        unique_counts['otu1']['ATCG'] = 3
        unique_counts['otu2']['AT'] = 2
        unique_counts['otu2']['A'] = 1

        result = StringIO()
        write_bloom_fasta(unique_counts, result, 0.67)

        result.seek(0)
        self.assertEqual(result.read(), '>otu1_1\nATCG\n')


filter_mapping_testdata = StringIO(
"""#SampleID	COUNTRY	TITLE_ACRONYM	AGE	SIMPLE_BODY_SITE
A	United States of America	AGP	43.0	ORAL
B	United States of America	foo	51.0	FECAL
C	United States of America	bar	12.0	FECAL
D	United States of America	AGP	32.0	SKIN
E	United States of America	AGP	56.0	FECAL
""")
reformat_mapping_testdata = StringIO(
"""#SampleID	COUNTRY	AGE	BODY_SITE	BMI
A	GAZ:w00t	43.0	UBERON_mucosa_of_tongue	5
B	GAZ:left	51.0	UBERON:FECES	10
C	GAZ:right	12.0	UBERON_FECES	15
D	GAZ:stuff	32.0	unknown	26
E	GAZ:stuff	56.0	UBERON:SKIN	37
""")

# Inputs for count_unique_seqs_per_otu
test_fasta = """>sample1_1 yea
ATCG
>sample1_2 awyea
ATCG
>sample2_1 dumb
ATCG
>sample2_2 dummy
AT
>sample2_3 wow
AT
>sample2_4 wowagain
A
>sample9_1
ATGC
>sample9_2
A
"""

test_otu_map = """otu1	sample1_1	sample1_2	sample2_1
otu2	sample2_2	sample2_3	sample2_4
otu3	sample9_1	smaple9_2
"""

if __name__ == '__main__':
    main()
