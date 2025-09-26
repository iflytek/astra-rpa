import os
import sys

import clr

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exes", "ie"))

clr.AddReference("IEAutomationProvider2")
from IEAutomationProvider2 import IEAutomationClass

IEAutomationClass = IEAutomationClass


tag_path = os.path.join(os.path.dirname(__file__), "exes", "ie", "tag.ts")
ie_similarElementjs_path = os.path.join(os.path.dirname(__file__), "exes", "ie", "SimilarElement.js")
