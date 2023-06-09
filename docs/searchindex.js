Search.setIndex({"docnames": ["CsvTut", "MatTut", "apidocs", "code_autogen/AuxFunctions", "code_autogen/Preprocessing", "code_autogen/StatsTests", "code_autogen/coreLanding", "exercise1", "exercise2", "exercise3", "exercise4", "exercise5", "exercise5S", "guided_exercises", "index", "install", "main_landing", "sceneTut", "theory", "tutorials"], "filenames": ["CsvTut.md", "MatTut.md", "apidocs.rst", "code_autogen/AuxFunctions.rst", "code_autogen/Preprocessing.rst", "code_autogen/StatsTests.rst", "code_autogen/coreLanding.rst", "exercise1.md", "exercise2.md", "exercise3.md", "exercise4.md", "exercise5.md", "exercise5S.md", "guided_exercises.rst", "index.rst", "install.md", "main_landing.md", "sceneTut.md", "theory.md", "tutorials.rst"], "titles": ["Using your own data (.csv)", "Using your own data (.mat)", "API home", "AuxFunctions", "Preprocessing", "StatsTest", "core", "Exercise 1: General MAPIT Familiarity", "Exercise 2: Impacts of measurement error", "Exercise 3: Material Loss", "Exercise 4: Quantifying probability of detection", "Exercise 5: System Optimization", "Exercise 5 Solution", "Guided exercises", "MAPIT documentation home", "Downloading &amp; Installing MAPIT", "MAPIT Reference Manual", "MAPIT Introduction", "Theory", "Tutorials"], "terms": {"core": [2, 3, 4, 5], "auxfunct": [2, 6], "preprocess": [2, 6, 17], "statstest": [2, 6], "mapit_intern": [3, 4, 5], "trapsum": 3, "relevantindex": 3, "time": [3, 4, 5, 7, 8, 10, 17], "data": [3, 4, 5, 7, 10, 16, 19], "IT": 3, "none": [3, 4, 5], "baseline_zero": 3, "1e": 3, "10": [3, 11], "function": [3, 4, 5, 7, 10, 11, 17], "perform": [3, 5, 7, 8, 9, 10, 16, 17], "trapezoid": 3, "integr": [3, 5, 8], "dataset": [3, 7, 8, 9, 10, 11, 16], "segment": 3, "thi": [3, 5, 7, 8, 9, 10, 11, 12, 15, 16, 17], "i": [3, 4, 5, 7, 8, 9, 10, 11, 12, 15, 17], "requir": [3, 7, 8, 9, 10, 15, 17], "bulk": [3, 5, 15], "facil": [3, 5, 7, 9, 15, 17], "flow": [3, 5, 7, 8], "might": [3, 10], "need": [3, 8, 9, 10, 17], "befor": [3, 11, 17], "us": [3, 4, 5, 8, 9, 10, 11, 12, 15, 16, 17, 19], "within": [3, 7, 17], "statist": [3, 5, 7, 8, 9], "test": [3, 5, 7, 8, 9, 10, 11, 16], "In": [3, 7, 8, 9, 10, 15, 16, 17], "some": [3, 5, 7, 9, 10, 12, 16, 17], "case": [3, 7, 10, 16, 17], "repres": 3, "discontinu": 3, "puls": 3, "materi": [3, 5, 7, 8, 10, 13, 16, 17], "which": [3, 5, 7, 8, 9, 10, 11, 12, 16, 17], "special": 3, "care": [3, 16], "identifi": [3, 17], "non": 3, "zero": [3, 7, 8, 17], "region": 3, "enabl": [3, 12, 17], "proper": 3, "first": [3, 4, 7, 8, 17], "list": [3, 4, 5, 8, 17], "each": [3, 4, 5], "np": [3, 5], "trapz": 3, "see": [3, 5, 7, 9, 10, 15, 17], "numpi": [3, 5], "document": [3, 15, 16], "more": [3, 5, 8, 10, 11, 17], "inform": [3, 5, 7, 17], "int": [3, 4], "y": 3, "x": [3, 17], "dx": 3, "paramet": [3, 4, 5, 7, 8, 9, 10, 17], "ndarrai": [3, 4, 5], "an": [3, 5, 7, 8, 9, 10, 11, 12, 17], "arrai": [3, 4, 5, 16], "express": [3, 5], "relev": [3, 17], "slice": 3, "term": [3, 5, 8], "indici": 3, "shape": [3, 4, 5, 17], "m": [3, 4, 5], "j": [3, 4, 5], "where": [3, 4, 5, 10, 17], "total": [3, 5, 9, 10, 11, 12], "number": [3, 4, 5, 7, 8, 10, 17], "sampl": [3, 4, 5, 17], "iter": [3, 4, 5, 7, 8, 9, 10, 11, 12, 16, 17], "contain": [3, 5, 7, 17], "timestep": [3, 5], "valu": [3, 5, 7, 8, 9, 10, 11, 12, 17], "under": [3, 7, 8, 17], "consider": 3, "analysi": [3, 7, 8, 9, 10, 15], "ha": [3, 5, 7, 8, 9, 16, 17], "n": [3, 4, 5], "should": [3, 4, 5, 7, 8, 9, 10, 12, 17], "have": [3, 4, 5, 7, 8, 9, 10, 11, 15, 17], "same": [3, 5, 8, 9, 10, 11, 12, 17], "float": [3, 5], "A": [3, 4, 5, 7, 9, 10, 11, 12], "threshold": [3, 8, 11, 12], "below": [3, 7, 8, 9, 17], "ar": [3, 5, 7, 8, 9, 10, 11, 12, 15, 16, 17], "consid": [3, 4, 8, 9], "import": [3, 5, 8, 9, 10, 17], "often": [3, 5, 10, 17], "do": [3, 8, 9, 17], "exactli": 3, "varieti": 3, "reason": [3, 10], "return": [3, 4, 5, 8, 10, 17], "1": [3, 4, 5, 8, 9, 10, 11, 12, 13, 16], "over": [3, 8, 17], "specifi": [3, 5, 8, 17], "type": [3, 4, 5, 7, 8, 9, 17], "simerror": 4, "rawdata": 4, "errormatrix": [4, 5], "guiobject": [4, 5], "dotqdm": [4, 5], "true": [4, 5, 8, 9, 17], "add": [4, 17], "simul": [4, 7, 8, 10, 17], "measur": [4, 7, 9, 10, 11, 13, 16, 17], "error": [4, 5, 7, 9, 10, 11, 12, 13, 16], "support": [4, 17], "variabl": 4, "rate": [4, 11], "assum": [4, 5, 8, 9, 10, 11], "tradit": [4, 5], "multipl": [4, 7, 16, 17], "model": [4, 7, 8], "m_": 4, "t": [4, 5, 17], "r_": 4, "s_j": 4, "random": [4, 5, 7, 8, 9, 10, 11], "sim": 4, "mathcal": 4, "0": [4, 5, 8, 9, 10, 11, 12, 17], "delta_r": 4, "_j": 4, "2": [4, 5, 7, 9, 10, 11, 12, 13, 16], "systemat": [4, 5, 7, 8, 9, 10, 11], "s_": 4, "delta_": 4, "locat": [4, 5, 7, 8, 9, 10, 11, 12, 15, 17], "raw": [4, 17], "appli": [4, 5, 17], "2d": 4, "entri": [4, 5], "correspond": [4, 5, 8], "differ": [4, 5, 8, 10, 11, 17], "mxn": 4, "dimens": [4, 5], "element": [4, 7, 8, 9, 10, 17], "applic": 4, "If": [4, 7, 8, 9, 10, 15], "onli": [4, 7, 8, 10, 11, 15, 17], "one": [4, 8, 10, 17], "mx1": [4, 5], "mx2": 4, "describ": [4, 16, 17], "rel": [4, 5, 8, 12], "standard": [4, 5, 8], "deviat": [4, 8], "input": [4, 5, 7, 8, 11, 12, 17], "ident": [4, 5], "The": [4, 5, 7, 8, 9, 10, 15, 17], "second": [4, 8, 9, 17], "e": [4, 5, 7, 8, 9, 10, 11, 12, 17], "g": [4, 5, 8], "refer": [4, 5, 8, 9, 11, 17], "respect": [4, 8, 15], "calcul": [4, 5, 7, 8, 9, 10, 12, 16, 17], "obj": 4, "default": [4, 5, 7, 17], "gui": [4, 5, 7], "object": [4, 5], "intern": [4, 16, 17], "mapit": [4, 5, 8, 9, 10, 11, 12, 13, 19], "bool": [4, 5], "control": [4, 5, 7, 8, 17], "tqdm": [4, 5], "progress": [4, 5, 7, 16, 17], "bar": [4, 5, 7, 17], "command": [4, 5, 15], "line": [4, 5], "notebook": [4, 5], "oper": [4, 5, 7, 10, 15, 17], "so": [4, 9, 10, 11, 12, 17], "can": [4, 5, 7, 8, 9, 10, 11, 12, 15, 16, 17], "cumuf": [5, 8, 9], "muf": [5, 8, 9], "cumul": 5, "simpli": [5, 8, 9], "sum": 5, "all": [5, 7, 8, 9, 10, 11, 15, 17], "previou": [5, 8, 9, 10], "particular": [5, 9, 11, 17], "text": [5, 8], "_t": 5, "sum_": 5, "sequenc": [5, 8], "tempor": [5, 7, 8, 9, 10, 17], "expect": [5, 7, 17], "continu": [5, 7, 8, 9, 10], "similar": [5, 8, 9, 10], "format": [5, 17], "what": [5, 17], "guiparam": 5, "option": [5, 7, 8, 9, 10, 17], "carri": 5, "relat": [5, 9, 17], "when": [5, 7, 8, 9, 10, 11, 16, 17], "api": [5, 14], "insid": [5, 15], "inputappliederror": 5, "processedinputtim": 5, "inventoryappliederror": 5, "processedinventorytim": 5, "outputappliederror": 5, "processedoutputtim": 5, "mbp": [5, 7, 8, 9, 10, 17], "unaccount": 5, "For": [5, 7, 8, 10, 11, 17], "sometim": 5, "also": [5, 8, 17], "call": [5, 17], "id": [5, 7], "inventori": [5, 8, 11, 17], "specif": [5, 17], "balanc": [5, 7, 8, 9, 17], "given": 5, "seri": [5, 17], "i_t": 5, "o_t": 5, "c_t": 5, "c_": 5, "output": [5, 7, 8, 9, 11, 12, 17], "note": [5, 7, 8, 9, 10, 17], "c": [5, 11, 12], "denot": [5, 17], "clearer": 5, "notat": 5, "rather": 5, "than": [5, 8], "subscript": 5, "both": [5, 7, 8, 11], "length": [5, 10, 17], "appliederror": 5, "processedtim": 5, "exampl": [5, 7, 8, 9, 10, 11, 16, 17], "assert": 5, "len": 5, "guid": [5, 11, 14], "equal": 5, "reflect": [5, 9, 17], "observ": [5, 7, 8, 9, 17], "quantit": [5, 10], "oppos": 5, "ground": [5, 8, 9, 17], "truth": [5, 8, 9, 17], "unit": [5, 17], "frac": 5, "": [5, 7, 8, 9, 10, 11, 12, 17], "timestamp": 5, "indic": [5, 7, 8, 16], "wa": [5, 8, 9, 11, 17], "taken": 5, "mass": [5, 8], "corresond": 5, "defin": 5, "period": [5, 7, 8, 9, 17], "maximum": 5, "base": [5, 7, 8, 10, 17], "could": [5, 8, 9], "construct": 5, "user": [5, 7, 8, 16, 17], "provid": [5, 7, 10, 12, 17], "find": 5, "minimum": 5, "time1": 5, "400": 5, "time2": 5, "300": [5, 17], "time3": 5, "800": 5, "floor": 5, "min": 5, "pagetrendtest": 5, "inqti": 5, "k": [5, 17], "5": [5, 9, 10, 13, 16], "page": [5, 7, 8, 9, 10, 11, 14, 16, 17], "trend": [5, 8, 9, 10, 11, 17], "commonli": 5, "sitmuf": [5, 7, 8, 9, 10, 17], "formal": 5, "compar": [5, 11], "null": 5, "hypothesi": 5, "versu": 5, "altern": [5, 7], "present": [5, 17], "result": [5, 8, 9, 10, 16], "semuf": 5, "seid": [5, 7, 8, 9], "sigma": [5, 8], "_": [5, 8], "accomplish": 5, "incur": 5, "estim": [5, 8, 10, 11], "emper": 5, "difficult": [5, 17], "practic": [5, 7, 9, 10], "equat": 5, "here": [5, 9, 11, 12, 17], "suitabl": 5, "most": 5, "enrich": [5, 17], "reprocess": [5, 17], "independ": [5, 8], "facilitii": 5, "complex": 5, "depend": [5, 7, 8, 9, 17], "between": 5, "molten": 5, "salt": 5, "reactor": 5, "xx": 5, "across": 5, "stack": 5, "togeth": 5, "order": 5, "3": [5, 8, 10, 11, 12, 13, 16, 17], "would": [5, 7, 17], "tupl": 5, "semufcontribr": 5, "contribut": [5, 16], "overal": 5, "l": 5, "semufcontrib": 5, "observedvalu": 5, "out": 5, "transform": [5, 8, 10], "detail": [5, 8, 17], "found": [5, 8, 11, 12], "goal": 7, "tutori": [7, 8, 9, 10, 14, 17], "gain": [7, 8, 9, 17], "basic": [7, 16, 17], "start": [7, 8, 9, 10, 11], "launch": [7, 8, 9, 10], "new": [7, 8, 9], "python": [7, 15], "window": [7, 8, 15, 17], "run": [7, 8, 9, 10, 15, 17], "bat": 7, "windows_script": [7, 15], "doubl": 7, "click": [7, 8, 15], "unix": [7, 15], "bash": 7, "sh": 7, "consol": 7, "ensur": [7, 16], "current": [7, 8, 17], "work": [7, 8, 11, 16], "directori": [7, 15], "unix_script": 7, "otherwis": 7, "from": [7, 8, 9, 10, 17], "you": [7, 8, 9, 10, 11, 12, 15, 16, 17], "previous": [7, 10, 11], "setup": [7, 11, 12, 17], "environ": [7, 15], "troubl": 7, "view": [7, 8, 17], "your": [7, 8, 9, 10, 11, 15, 17, 19], "screen": 7, "try": [7, 8, 9, 10, 11, 17], "maxim": 7, "now": [7, 15], "shown": [7, 8, 17], "light": 7, "theme": 7, "dark": 7, "avail": [7, 8, 9, 10, 17], "These": [7, 16, 17], "toggl": 7, "ani": [7, 8, 17], "dropdown": [7, 9], "menu": [7, 9, 15, 17], "allow": [7, 17], "font": 7, "size": [7, 8], "fontsiz": 7, "chang": [7, 8, 9, 10, 17], "access": [7, 8, 17], "statu": 7, "bottom": [7, 17], "left": 7, "right": [7, 15], "anim": [7, 17], "tooltip": 7, "help": [7, 10, 16, 17], "understand": [7, 10, 17], "safeguard": [7, 8, 9, 10, 11, 15, 17], "initi": 7, "box": [7, 8, 9, 10, 17], "highlight": [7, 17], "blue": [7, 17], "those": 7, "further": [7, 8, 16, 17], "wait": 7, "uranium": [7, 8, 10, 11, 17], "track": [7, 8], "fuel": [7, 8, 9, 12], "fabric": [7, 9], "column": [7, 8], "broken": 7, "section": [7, 10], "titl": 7, "prompt": [7, 15, 17], "select": [7, 8, 9, 10, 12, 17], "snl": [7, 9, 10, 11, 17], "curat": [7, 9, 10, 11, 17], "load": [7, 8, 9, 10, 11, 12], "own": [7, 10, 11, 16, 19], "fab": [7, 8], "normal": [7, 8, 9, 10, 17], "explor": [7, 10, 12], "bring": 7, "follow": [7, 8, 15, 17], "pop": 7, "up": [7, 8], "block": 7, "tool": [7, 16, 17], "becom": 7, "includ": [7, 8, 11, 16], "develop": [7, 10, 11, 12], "iaea": [7, 17], "str": 7, "150": [7, 12], "kei": [7, 8, 9, 15], "point": [7, 8, 9], "area": [7, 17], "until": [7, 15], "set": [7, 8, 9, 10, 11, 17], "begin": [7, 8, 15], "plot": [7, 8, 9, 10], "press": [7, 8, 9, 10, 12, 17], "plai": 7, "button": [7, 8, 9, 10, 12, 15, 17], "top": [7, 8, 15], "show": [7, 8, 9, 15, 17], "behavior": [7, 8, 17], "sever": [7, 8, 9, 16, 17], "descript": [7, 8], "middl": 7, "paus": 7, "finish": [7, 8, 9, 10, 11, 17], "adjust": [7, 17], "slider": 7, "stop": 7, "repeat": [7, 8, 17], "regardless": 7, "close": [7, 10], "checkbox": [7, 9, 10], "cusum": 7, "next": [7, 8, 9, 10, 17], "configur": [7, 8, 9, 10, 11, 12], "416": [7, 8, 9, 10], "least": [7, 17], "common": [7, 17], "stream": 7, "50": [7, 8, 9, 10, 11, 12], "realiz": [7, 17], "singl": [7, 8, 10, 16], "lower": [7, 8, 10], "devic": [7, 8, 9, 10], "inter": [7, 9], "20": [7, 8, 9, 10], "index": [7, 8, 9, 10, 14, 17], "u": [7, 8, 9, 10, 12, 17], "just": [7, 10], "plutonium": [7, 17], "must": [7, 9], "about": [7, 8, 9, 10, 17], "offset": [7, 8, 9, 10, 17], "empti": [7, 8, 9, 10, 17], "mai": [7, 12, 16, 17], "desir": [7, 17], "ignor": 7, "startup": [7, 8], "rebas": 7, "pane": 7, "percent": [7, 17], "variou": [7, 9, 16, 17], "kmp": [7, 8], "manual": [7, 11, 17], "enter": [7, 8, 10, 11, 17], "drop": [7, 8, 17], "down": [7, 8, 15, 17], "automat": 7, "onc": [7, 15, 17], "tediou": [7, 17], "save": [7, 11, 17], "config": [7, 11, 12, 17], "learn": [7, 8], "how": [7, 8, 10, 15, 16, 17], "metric": [8, 10], "recal": [8, 10], "neg": 8, "abil": 8, "detect": [8, 9, 11, 12, 13, 16, 17], "anomali": 8, "loss": [8, 10, 11, 12, 13, 16], "familiar": [8, 9, 10, 13], "task": [8, 9, 10], "discuss": [8, 9, 10], "scenario": [8, 17], "analys": [8, 11], "etc": 8, "main": [8, 9, 10, 17], "interfac": [8, 9, 10], "imag": [8, 9, 17], "choos": [8, 9, 10, 17], "after": [8, 9, 12, 15, 17], "investig": 8, "abl": [8, 15], "averag": [8, 10], "export": 8, "figur": 8, "later": 8, "floppi": 8, "disc": 8, "icon": [8, 17], "dynam": [8, 17], "sinc": 8, "were": [8, 11, 12, 17], "small": [8, 9, 17], "them": [8, 16, 17], "gener": [8, 9, 13, 16, 17], "look": [8, 9, 17], "like": 8, "vari": [8, 17], "due": [8, 9, 10, 16], "inher": 8, "sigma_": 8, "notic": [8, 9, 16], "tend": 8, "remain": 8, "around": [8, 9], "95": 8, "kg": 8, "smaller": 8, "condit": 8, "decreas": [8, 10], "overtim": 8, "reach": [8, 10, 11], "steadi": 8, "state": [8, 11], "approxim": [8, 10, 12], "mean": 8, "seen": 8, "match": 8, "earlier": 8, "lesson": 8, "That": 8, "howev": [8, 9, 10, 12, 16, 17], "larger": 8, "final": [8, 17], "covari": 8, "matrix": 8, "align": 8, "pmatrix": 8, "11": 8, "12": 8, "ldot": 8, "1n": 8, "21": 8, "22": 8, "2n": 8, "vdot": 8, "ddot": 8, "n1": 8, "n2": 8, "nn": 8, "end": 8, "grow": 8, "made": [8, 17], "better": [8, 11, 12], "fact": 8, "converg": 8, "approach": 8, "infin": 8, "consequ": 8, "varianc": 8, "improv": [8, 17], "subtl": 8, "feel": [8, 12, 17], "free": [8, 12, 17], "exce": [8, 10, 17], "analyz": [8, 17], "system": [8, 9, 13, 15, 16, 17], "even": [8, 17], "still": 8, "examin": [8, 9, 17], "quantiti": [8, 9, 10, 11, 12, 17], "open": [8, 15, 17], "tabl": [8, 17], "uncertainti": [8, 10, 11, 12, 17], "tabular": [8, 17], "displai": 8, "addit": [8, 17], "actual": [8, 17], "instantn": 8, "other": [8, 10, 17], "speci": 8, "potenti": [8, 11, 12], "cylind": [8, 12], "pin": [8, 9, 12], "largest": 8, "again": [8, 9, 10, 11, 17], "doe": [8, 9], "restart": [8, 9, 10], "anoth": [8, 17], "lost": 8, "edit": 8, "reduc": [8, 16, 17], "two": [8, 17], "compon": [8, 17], "check": [8, 9, 10, 17], "newli": 8, "dramat": 8, "560": 8, "210": 8, "similarli": [8, 17], "fallen": 8, "magnitud": 8, "concret": 8, "hypothet": [8, 11], "longer": 8, "lead": 8, "higher": [8, 10], "wherea": 8, "shorter": 8, "limit": [8, 17], "while": [8, 10, 17], "avenhau": 8, "jaech": 8, "capabl": [8, 10, 17], "individu": [8, 17], "introduc": [8, 9, 10, 17], "reli": 8, "notion": [9, 11], "prepar": 9, "evalu": [9, 11], "abrupt": [9, 10], "five": [9, 10], "never": 9, "There": [9, 17], "mani": [9, 10, 16, 17], "take": [9, 15, 16], "hardwar": [9, 17], "1010": 9, "hour": [9, 10, 17], "remov": 9, "100": [9, 11, 16, 17], "did": 9, "Then": [9, 11], "updat": [9, 17], "occur": 9, "distinct": 9, "dure": 9, "exhibit": 9, "presenc": 9, "demonstr": 9, "precis": [9, 10, 16], "too": 9, "reliabl": [9, 17], "level": [9, 10, 12], "third": 9, "concept": 9, "origin": 9, "visibl": 9, "clearli": 9, "phenomena": 9, "4": [9, 11, 12, 13, 16], "far": [10, 11], "focus": [10, 11], "qualit": 10, "induc": 10, "focu": 10, "lectur": 10, "tune": 10, "fals": [10, 11, 12], "alarm": [10, 11, 12], "per": 10, "year": [10, 17], "step": [10, 17], "6480": 10, "long": [10, 17], "translat": 10, "270": 10, "dai": 10, "therefor": 10, "caution": 10, "label": [10, 11], "necessari": [10, 17], "appropri": 10, "fap": [10, 11], "entir": [10, 12], "few": [10, 15, 16], "34": 10, "slightli": 10, "increas": [10, 17], "obtain": [10, 11], "itself": [10, 17], "roughli": 10, "sqrt": 10, "69": 10, "we": [10, 11], "technologi": 10, "deploi": 10, "On": 10, "high": [10, 12], "impact": [10, 13, 17], "leav": 10, "fourth": 10, "along": 10, "challeng": 10, "unconsid": 11, "protract": 11, "determin": 11, "70": 11, "probabl": [11, 12, 13, 16, 17], "assumpt": 11, "consist": [11, 16], "cheapest": 11, "abov": [11, 17], "neglect": 11, "real": 11, "world": 11, "instead": 11, "make": [11, 16, 17], "quickli": [11, 17], "quit": 11, "without": [11, 17], "26": [11, 12], "b": [11, 12], "25": 11, "30": [11, 12], "d": [11, 12], "75": 11, "200": 11, "impli": 11, "31": [11, 17], "775": 11, "8": [11, 12], "6": 11, "against": 11, "our": [11, 16], "It": [12, 17], "imposs": [12, 17], "space": 12, "answer": 12, "let": 12, "know": [12, 17], "place": 12, "src": 12, "folder": [12, 15, 17], "py": [12, 17], "sensor": 12, "260": 12, "490": 12, "fluctuat": 12, "degre": 12, "250": 12, "certainti": 12, "72": 12, "drum": 12, "vapor": 12, "precipit": 12, "offga": 12, "filter": 12, "centrifug": 12, "calcinationreduct": 12, "millingblend": 12, "mix": 12, "tank": 12, "sinter": 12, "grind": 12, "pellet": 12, "storag": 12, "tube": 12, "fill": 12, "adu": 12, "scrap": [12, 17], "green": [12, 15], "dirti": 12, "powder": [12, 17], "grinder": 12, "sludg": 12, "offspec": 12, "oxid": 12, "dissolut": 12, "solvent": 12, "reduct": 12, "uf6": 12, "heel": 12, "quantifi": 13, "optim": [13, 16], "solut": 13, "download": 14, "instal": [14, 16], "exercis": 14, "theori": 14, "modul": [14, 15], "search": 14, "onto": 15, "pc": 15, "toolkit": [15, 16], "written": 15, "aid": 15, "modern": 15, "mac": 15, "linux": 15, "file": [15, 17], "http": 15, "www": 15, "github": 15, "com": 15, "sandialab": 15, "code": [15, 16], "pull": 15, "zip": 15, "complet": [15, 17], "unzip": 15, "comput": 15, "process": [15, 17], "linux_script": 15, "scripts_fold": 15, "three": 15, "remove_mapit": 15, "miniconda3": 15, "minamalist": 15, "version": 15, "anaconda": 15, "packag": 15, "minut": 15, "pleas": [15, 17], "keep": 15, "shell": 15, "welcom": 16, "account": 16, "underli": [16, 17], "well": 16, "csv": [16, 17, 19], "mat": [16, 19], "unusu": 16, "edg": 16, "caus": 16, "fail": 16, "v": 16, "ongo": [16, 17], "respons": 16, "dilig": 16, "sens": 16, "warn": 16, "bug": 16, "project": 16, "report": [16, 17], "through": [16, 17], "issu": 16, "memori": 16, "footprint": 16, "gb": 16, "introduct": [16, 19], "purpos": 17, "str150": 17, "uniqu": 17, "featur": 17, "mt": 17, "uo": 17, "_2": 17, "weight": 17, "235": 17, "product": 17, "lwr": 17, "assembli": 17, "feed": 17, "low": 17, "uf": 17, "_6": 17, "uranyl": 17, "nitrat": 17, "recoveri": 17, "been": 17, "advanc": 17, "pre": 17, "mba2": 17, "envis": 17, "thei": 17, "intuit": 17, "interact": 17, "xenon": 17, "futur": 17, "purex": 17, "tab": 17, "done": 17, "border": 17, "workflow": 17, "go": 17, "ahead": 17, "suggest": 17, "320": 17, "As": 17, "perfect": 17, "interest": 17, "dialog": 17, "group": 17, "One": 17, "itv": 17, "target": 17, "good": 17, "custom": 17, "read": 17, "everi": 17, "disk": 17, "lightweight": 17, "fairli": 17, "monitor": 17, "analyt": 17, "happen": 17, "sure": 17, "alwai": 17, "request": 17, "doesn": 17, "moment": 17, "bake": 17, "attempt": 17, "nuclid": 17, "Not": 17, "usual": 17, "tunabl": 17, "h": 17, "ideal": 17, "shift": 17, "cross": 17, "1000": 17, "max": 17, "past": 17, "yet": 17, "implement": 17, "meantim": 17, "circumv": 17, "want": 17, "yearli": 17, "split": 17, "half": 17, "larg": 17, "sourc": 17, "priorit": 17, "facilit": 17, "wide": 17, "rang": 17, "secondari": 17, "wai": 17, "recommend": 17, "directli": 17, "matplotlib": 17, "backend": 17, "navig": 17, "5000": 17, "creat": 17, "mapit_output": 17, "irregularli": 17, "although": 17, "handl": 17, "valid": 17, "effort": 17, "tbd": 18}, "objects": {"MAPIT_internal.core": [[3, 0, 0, "-", "AuxFunctions"], [4, 0, 0, "-", "Preprocessing"], [5, 0, 0, "-", "StatsTests"]], "MAPIT_internal.core.AuxFunctions": [[3, 1, 1, "", "trapSum"]], "MAPIT_internal.core.Preprocessing": [[4, 1, 1, "", "SimErrors"]], "MAPIT_internal.core.StatsTests": [[5, 1, 1, "", "CUMUF"], [5, 1, 1, "", "MUF"], [5, 1, 1, "", "PageTrendTest"], [5, 1, 1, "", "SEMUF"], [5, 1, 1, "", "SITMUF"]]}, "objtypes": {"0": "py:module", "1": "py:function"}, "objnames": {"0": ["py", "module", "Python module"], "1": ["py", "function", "Python function"]}, "titleterms": {"us": [0, 1, 7], "your": [0, 1], "own": [0, 1], "data": [0, 1, 8, 9, 17], "csv": 0, "mat": 1, "api": 2, "home": [2, 14], "content": [2, 6, 14], "auxfunct": 3, "preprocess": 4, "statstest": 5, "core": 6, "exercis": [7, 8, 9, 10, 11, 12, 13, 16], "1": 7, "gener": 7, "mapit": [7, 14, 15, 16, 17], "familiar": 7, "object": [7, 8, 9, 11, 15], "open": 7, "main": 7, "interfac": 7, "scenario": 7, "selector": 7, "summari": [7, 8, 9, 10], "2": 8, "impact": [8, 9], "measur": 8, "error": [8, 17], "problem": [8, 9, 10], "setup": [8, 9, 10], "explor": [8, 9], "understand": 8, "contribut": [8, 17], "3": 9, "materi": 9, "loss": 9, "baselin": [9, 11], "lower": 9, "uncertainti": 9, "4": 10, "quantifi": 10, "probabl": 10, "detect": 10, "goal": [10, 11], "determin": 10, "statist": [10, 17], "threshold": [10, 17], "evalu": 10, "5": [11, 12], "system": 11, "optim": 11, "sensor": 11, "cost": [11, 12], "solut": [11, 12], "perform": [11, 12], "placement": 12, "guid": [13, 16], "document": 14, "indic": 14, "tabl": 14, "download": 15, "instal": 15, "refer": 16, "manual": 16, "construct": 16, "i": 16, "IN": 16, "beta": 16, "get": [16, 17], "start": [16, 17], "tutori": [16, 19], "benchmark": 16, "function": 16, "theori": [16, 18], "introduct": 17, "fuel": 17, "fabric": 17, "overview": 17, "walkthrough": 17, "load": 17, "includ": 17, "dataset": 17, "test": 17, "configur": 17, "analysi": 17, "plot": 17, "export": 17, "figur": 17}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 6, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx.ext.intersphinx": 1, "sphinx": 56}})