import modeling

m = modeling.Modeling('USA')

testList = [{'high': 1.1237, 'low': 1.12345, 'open': 1.1235, 'minute': 40, 'relative_minute': 0, 'close': 1.1234},
 {'high': 1.12366, 'low': 1.1234, 'open': 1.1234, 'minute': 41, 'relative_minute': 1, 'close': 1.12365},
 {'high': 1.12373, 'low': 1.1235, 'open': 1.12365, 'minute': 42, 'relative_minute': 2, 'close': 1.12368},
 {'high': 1.12371, 'low': 1.1234, 'open': 1.12368, 'minute': 43, 'relative_minute': 3, 'close': 1.1236},
 {'high': 1.12361, 'low': 1.1234, 'open': 1.1236, 'minute': 44, 'relative_minute': 4, 'close': 1.12356},
 {'high': 1.1236, 'low': 1.1233, 'open': 1.12356, 'minute': 45, 'relative_minute': 5, 'close': 1.12346},
 {'high': 1.12352, 'low': 1.1233, 'open': 1.12346, 'minute': 46, 'relative_minute': 6, 'close': 1.12348},
 {'high': 1.1235, 'low': 1.1232, 'open': 1.12348, 'minute': 47, 'relative_minute': 7, 'close': 1.12337},
 {'high': 1.12356, 'low': 1.1232, 'open': 1.12337, 'minute': 48, 'relative_minute': 8, 'close': 1.12336},
 {'high': 1.1234, 'low': 1.1232, 'open': 1.12336, 'minute': 49, 'relative_minute': 9, 'close': 1.12327},
 {'high': 1.12341, 'low': 1.12319, 'open': 1.12327, 'minute': 50, 'relative_minute': 10, 'close': 1.12337},
 {'high': 1.12339, 'low': 1.1231, 'open': 1.12337, 'minute': 51, 'relative_minute': 11, 'close': 1.1233},
 {'high': 1.1233, 'low': 1.1231, 'open': 1.1233, 'minute': 52, 'relative_minute': 12, 'close': 1.12321},
 {'high': 1.12325, 'low': 1.123, 'open': 1.12321, 'minute': 53, 'relative_minute': 13, 'close': 1.12314},
 {'high': 1.12332, 'low': 1.1229, 'open': 1.12314, 'minute': 54, 'relative_minute': 14, 'close': 1.1233},
 {'high': 1.1233, 'low': 1.1233, 'open': 1.1233, 'minute': 55, 'relative_minute': 15}]

m.loadModel('USA')
print(m.getPredictions(testList[:-1]))