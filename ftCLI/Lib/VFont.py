import os

from fontTools.ttLib.tables._f_v_a_r import NamedInstance

from ftCLI.Lib.Font import Font


class VariableFont(Font):
    def __init__(self, file, recalcTimestamp=False):
        super().__init__(file=file, recalcTimestamp=recalcTimestamp)
        self.fvar_table = self["fvar"]

    def get_axes(self) -> list:
        return [axis for axis in self["fvar"].axes if axis.flags == 0]

    def get_instances(self) -> list:
        return [instance for instance in self["fvar"].instances]

    def get_var_name_ids_to_delete(self) -> list:
        name_ids_to_delete = [25]

        if "fvar" in self.keys():
            for axis in self.get_axes():
                name_ids_to_delete.append(axis.axisNameID)
            for instance in self.get_instances():
                if hasattr(instance, "subfamilyNameID"):
                    name_ids_to_delete.append(instance.subfamilyNameID)
                if hasattr(instance, "postscriptNameID"):
                    name_ids_to_delete.append(instance.postscriptNameID)

        if "STAT" in self.keys():
            if hasattr(self["STAT"].table, "DesignAxisRecord"):
                for axis in self["STAT"].table.DesignAxisRecord.Axis:
                    name_ids_to_delete.append(axis.AxisNameID)
            if hasattr(self["STAT"].table, "AxisValueArray") and self["STAT"].table.AxisValueArray is not None:
                for axis in self["STAT"].table.AxisValueArray.AxisValue:
                    name_ids_to_delete.append(axis.ValueNameID)

        name_ids_to_delete = [n for n in name_ids_to_delete if n > 24]
        name_ids_to_delete = sorted(list(set(name_ids_to_delete)))

        return name_ids_to_delete

    def get_instance_file_name(self, instance: NamedInstance) -> str:
        if hasattr(instance, "postscriptNameID") and instance.postscriptNameID < 65535:
            instance_file_name = self.name_table.getDebugName(instance.postscriptNameID)

        else:
            if hasattr(instance, "subfamilyNameID") and instance.subfamilyNameID > 0:
                subfamily_name = self.name_table.getDebugName(instance.subfamilyNameID)
            else:
                subfamily_name = "_".join([f"{k}_{v}" for k, v in instance.coordinates.items()])

            if self.name_table.getBestFamilyName() is not None:
                family_name = self.name_table.getBestFamilyName()
            else:
                family_name = os.path.splitext(os.path.basename(self.file))[0]

            instance_file_name = f"{family_name}-{subfamily_name}".replace(" ", "")

        return instance_file_name
