import ast, sys
sys.path.insert(0, "C:/Users/roman/rota_review43")
from rota.onboarding import indexer
from rota.onboarding.languages import Language, lang_of

target = "C:/Users/roman/rota_review43/rota/onboarding/indexer.py"
src = open(target, "rb").read()
lang = lang_of(target) if hasattr(indexer, "lang_of") else None
print("lang_of:", [n for n in dir(indexer) if "lang" in n.lower()][:8])
