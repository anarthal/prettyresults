from prettyresults import dataloader
import unittest
import pandas as pd
import numpy as np

class DataLoaderTests(unittest.TestCase):
    def test_logical_and(self):
        a =        [0.0, 0.0, 0.0,    1.0, 1.0, 1.0,    np.nan, np.nan, np.nan]
        b =        [0.0, 1.0, np.nan, 0.0, 1.0, np.nan, 0.0,    1.0,    np.nan]
        expected = [0.0, 0.0, 0.0,    0.0, 1.0, np.nan, 0.0,    np.nan, np.nan]
        df = pd.DataFrame({
            'a': a,
            'b': b
        })
        res = dataloader.logical_and('a', 'b')(df, None)
        np.testing.assert_array_equal(res.values, pd.Series(expected).values)

    def test_logical_or(self):
        a =        [0.0, 0.0, 0.0,    1.0, 1.0, 1.0,    np.nan, np.nan, np.nan]
        b =        [0.0, 1.0, np.nan, 0.0, 1.0, np.nan, 0.0,    1.0,    np.nan]
        expected = [0.0, 1.0, np.nan, 1.0, 1.0, 1.0,    np.nan, 1.0,    np.nan]
        df = pd.DataFrame({
            'a': a,
            'b': b
        })
        res = dataloader.logical_or('a', 'b')(df, None)
        np.testing.assert_array_equal(res.values, pd.Series(expected).values)
        
    def test_logical_or_multivar(self):
        a =        [0.0, 0.0, 0.0,    0.0, 0.0, 0.0,    0.0,    0.0,    0.0,  ]
        b =        [0.0, 0.0, 0.0,    1.0, 1.0, 1.0,    np.nan, np.nan, np.nan]
        c =        [0.0, 1.0, np.nan, 0.0, 1.0, np.nan, 0.0,    1.0,    np.nan]
        expected = [0.0, 1.0, np.nan, 1.0, 1.0, 1.0,    np.nan, 1.0,    np.nan]
        
        a +=        [1.0, 1.0, 1.0,    1.0, 1.0, 1.0,    1.0,    1.0,    1.0,  ]
        b +=        [0.0, 0.0, 0.0,    1.0, 1.0, 1.0,    np.nan, np.nan, np.nan]
        c +=        [0.0, 1.0, np.nan, 0.0, 1.0, np.nan, 0.0,    1.0,    np.nan]
        expected += [1.0, 1.0, 1.0,    1.0, 1.0, 1.0,    1.0,    1.0,    1.0   ]
        
        a +=        [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        b +=        [0.0,    0.0,    0.0,    1.0,    1.0,    1.0,    np.nan, np.nan, np.nan]
        c +=        [0.0,    1.0,    np.nan, 0.0,    1.0,    np.nan, 0.0,    1.0,    np.nan]
        expected += [np.nan, 1.0,    np.nan, 1.0,    1.0,    1.0,    np.nan, 1.0,    np.nan]
        
        df = pd.DataFrame({
            'a': a,
            'b': b,
            'c': c
        })
        res = dataloader.logical_or('a', 'b', 'c')(df, None)
        np.testing.assert_array_equal(res.values, pd.Series(expected).values)
        
    def test_logical_and_multivar(self):
        a =        [0.0, 0.0, 0.0,    0.0, 0.0, 0.0,    0.0,    0.0,    0.0,  ]
        b =        [0.0, 0.0, 0.0,    1.0, 1.0, 1.0,    np.nan, np.nan, np.nan]
        c =        [0.0, 1.0, np.nan, 0.0, 1.0, np.nan, 0.0,    1.0,    np.nan]
        expected = [0.0, 0.0, 0.0,    0.0, 0.0, 0.0,    0.0,    0.0,    0.0   ]
        
        a +=        [1.0, 1.0, 1.0,    1.0, 1.0, 1.0,    1.0,    1.0,    1.0,  ]
        b +=        [0.0, 0.0, 0.0,    1.0, 1.0, 1.0,    np.nan, np.nan, np.nan]
        c +=        [0.0, 1.0, np.nan, 0.0, 1.0, np.nan, 0.0,    1.0,    np.nan]
        expected += [0.0, 0.0, 0.0,    0.0, 1.0, np.nan, 0.0,    np.nan, np.nan]
        
        a +=        [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        b +=        [0.0,    0.0,    0.0,    1.0,    1.0,    1.0,    np.nan, np.nan, np.nan]
        c +=        [0.0,    1.0,    np.nan, 0.0,    1.0,    np.nan, 0.0,    1.0,    np.nan]
        expected += [0.0,    0.0,    0.0,    0.0,    np.nan, np.nan, 0.0,    np.nan, np.nan]
        
        df = pd.DataFrame({
            'a': a,
            'b': b,
            'c': c
        })
        res = dataloader.logical_and('a', 'b', 'c')(df, None)
        np.testing.assert_array_equal(res.values, pd.Series(expected).values)
        

if __name__ == '__main__':
    unittest.main()