import logging
import os

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.ttLib.ttFont import TTFont
from pathvalidate import sanitize_filename

log = logging.getLogger(__name__)


class VariableFont(TTFont):

    def __init__(self, file, recalcTimestamp=False):
        super().__init__(file=file, recalcTimestamp=recalcTimestamp)

        self.file = file

        try:
            self.fvarTable = self['fvar']
            self.statTable = self['STAT'].table
            self.nameTable = self['name']
        except Exception:
            raise Exception(f"{file}\nNot a valid variable font. Required table(s) missing: "
                            f"{', '.join([t for t in ['fvar', 'STAT', 'name'] if t not in self])}\n")

        self.gsubTable = self['GSUB'].table if 'GSUB' in self else None

    def getFamilyName(self):
        """
        Tries to retrieve the Family Name string from nameIDs 16, 1 or 25.
        """
        family_name = None

        try:
            family_name = self.nameTable.getName(16, 3, 1, 0x409).toUnicode()
        except AttributeError:
            try:
                family_name = self.nameTable.getName(16, 1, 0, 0x0).toUnicode()
            except AttributeError:
                try:
                    family_name = self.nameTable.getName(1, 3, 1, 0x409).toUnicode()
                except AttributeError:
                    try:
                        family_name = self.nameTable.getName(1, 1, 0, 0x0).toUnicode()
                    except AttributeError:
                        try:
                            family_name = self.nameTable.getName(25, 3, 1, 0x409).toUnicode()
                        except AttributeError:
                            try:
                                family_name = self.nameTable.getName(25, 1, 0, 0x0).toUnicode()
                            except AttributeError:
                                pass
        finally:
            return family_name

    def getInstancePostscriptName(self, instance: NamedInstance):
        """
        Tries to retrieve the postscriptName string of a fvar instance.
        """
        try:
            return self.nameTable.getName(instance.postscriptNameID, 3, 1, 0x409).toUnicode()
        except:
            return None

    def getInstanceSubfamilyName(self, instance: NamedInstance):
        """
        Tries to retrieve the subfamilyName string of a fvar instance.
        """
        try:
            return self.nameTable.getName(instance.subfamilyNameID, 3, 1, 0x409).toUnicode()
        except:
            return None

    def makeInstanceOutputFileName(self, instance: NamedInstance, outputDir, overWrite) -> str:
        psname = self.getInstancePostscriptName(instance) if instance.postscriptNameID < 65535 else None
        family_name = self.getFamilyName()
        subfamily_name = self.getInstanceSubfamilyName(instance) if instance.subfamilyNameID > 0 else None

        file_name = (os.path.splitext(os.path.basename(self.file))[0])
        ext = (os.path.splitext(self.file)[1])

        if psname is not None:
            s = psname
        elif subfamily_name is not None:
            if family_name is not None:
                s = f"{family_name}-{subfamily_name}".replace(" ", "")
            else:
                s = f"{file_name}-{subfamily_name}".replace(" ", "")
        else:
            if family_name is not None:
                s = f"{family_name}-"
            else:
                s = f"{file_name}-"
            for k, v in instance.coordinates.items():
                s += f"{k}_{v}-"
            s = s[0:-1]

        s = sanitize_filename(s)
        s = os.path.join(os.path.dirname(self.file), f"{s}{ext}")
        output_file = makeOutputFileName(input=s, outputDir=outputDir, overWrite=overWrite)
        return output_file

    def getNameIDsToDelete(self) -> list:
        name_ids_to_keep = sorted(list(set(n.nameID for n in self.nameTable.names if n.nameID < 25)))
        name_ids_to_delete = [25]

        try:
            for a in self.fvarTable.axes:
                if a.axisNameID not in name_ids_to_keep:
                    name_ids_to_delete.append(a.axisNameID)
        except:
            pass

        try:
            for instance in self.fvarTable.instances:
                if instance.subfamilyNameID not in name_ids_to_keep:
                    name_ids_to_delete.append(instance.subfamilyNameID)
                if instance.postscriptNameID not in name_ids_to_keep:
                    name_ids_to_delete.append(instance.postscriptNameID)
        except:
            pass

        try:
            for a in self.statTable.DesignAxisRecord.Axis:
                if a.AxisNameID not in name_ids_to_keep:
                    name_ids_to_delete.append(a.AxisNameID)
        except:
            pass

        try:
            for v in self.statTable.AxisValueArray.AxisValue:
                if v.ValueNameID not in name_ids_to_keep:
                    name_ids_to_delete.append(v.ValueNameID)
        except:
            pass

        return sorted(list(set(name_ids_to_delete)))

    def cleanupInstance(self, nameIDsToDelete: list):
        del self.statTable
        for n in self.nameTable.names:
            if n.nameID in nameIDsToDelete:
                self.nameTable.removeNames(n.nameID, n.platformID, n.platEncID, n.langID)

        if self.gsubTable is not None:
            named_features = []
            for r in self.gsubTable.FeatureList.FeatureRecord:
                try:
                    named_features.append(r.Feature.FeatureParams.UINameID)
                    named_features = list(set(named_features))
                except:
                    pass

            feature_name_ids = [n.nameID for n in self.nameTable.names if n.nameID in named_features]
            feature_name_ids = list(set(feature_name_ids))

            for count, value in enumerate(feature_name_ids, start=256):
                for n in self.nameTable.names:
                    if n.nameID == value:
                        n.nameID = count
                try:
                    for r in self.gsubTable.FeatureList.FeatureRecord:
                        if r.Feature.FeatureParams.UINameID == value:
                            r.Feature.FeatureParams.UINameID = count
                except:
                    pass
