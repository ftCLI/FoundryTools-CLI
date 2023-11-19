from pathlib import Path
from typing import Optional, List

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathvalidate import sanitize_filename

from foundryToolsCLI.Lib.VFont import VariableFont
from foundryToolsCLI.Lib.converters.options import Var2StaticOptions
from foundryToolsCLI.Lib.tables.name import TableName
from foundryToolsCLI.Lib.utils.logger import logger, Logs


class VariableToStatic(object):
    def __init__(self):
        self.options = Var2StaticOptions()

    def run(self, variable_font: VariableFont, instances: Optional[List] = None):
        if not instances:
            instances = variable_font.get_instances()

        if len(instances) == 0:
            logger.error("No instances found")
            return

        if self.options.update_name_table:
            if "STAT" not in variable_font:
                self.options.update_name_table = False
                logger.warning("Cannot update name table since there is no STAT table.")
            stat_table = variable_font["STAT"].table
            if not stat_table.AxisValueArray:
                self.options.update_name_table = False
                logger.warning("Cannot update name table since there are no STAT Axis Values")

        for count, instance in enumerate(instances, start=1):
            logger.info(f"Exporting instance {count} of {len(instances)}")

            static_instance = instantiateVariableFont(
                varfont=variable_font,
                axisLimits=instance.coordinates,
                inplace=False,
                overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS,
                optimize=True,
                updateFontNames=self.options.update_name_table,
            )

            if "cvar" in static_instance:
                del static_instance["cvar"]

            if self.options.cleanup:
                name_table: TableName = static_instance["name"]
                if "STAT" in static_instance:
                    del static_instance["STAT"]
                name_table.removeUnusedNames(static_instance)
                name_table.del_names(name_ids=[25])
                static_instance.reorder_ui_name_ids()

            static_instance_name = sanitize_filename(variable_font.get_instance_file_name(instance))
            # Replace dots with underscores to prevent makeOutputFileName truncating names
            static_instance_name = static_instance_name.replace(".", "_")
            static_instance_extension = static_instance.get_real_extension()
            output_file = Path(
                makeOutputFileName(
                    static_instance_name,
                    extension=static_instance_extension,
                    outputDir=self.options.output_dir,
                    overWrite=self.options.overwrite,
                )
            )
            static_instance.save(output_file)
            static_instance.close()
            logger.success(Logs.file_saved, file=output_file)

        variable_font.close()
