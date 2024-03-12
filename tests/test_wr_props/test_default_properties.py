def test_Hs(waves):
    assert waves.Hs

def test_Tp(waves):
    assert waves.Tp

def test_Tz(waves):
    assert waves.Tz

def test_dirs(waves):
    assert len(waves.dirs)>0

def test_freq(waves):
    assert len(waves.freq) > 0



