import time

from fontTools.misc.cliTools import makeOutputFileName
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathvalidate import sanitize_filename

from ftCLI.Lib.VFont import VariableFont
from ftCLI.Lib.utils.click_tools import (
    generic_warning_message,
    generic_info_message,
    file_saved_message,
    generic_error_message,
)


class Options(object):
    def __init__(self):
        self.cleanup = True
        self.update_name_table = True
        self.output_dir = None
        self.overwrite = True


class VariableToStatic(object):
    def __init__(self):
        self.options = Options()

    def run(self, variable_font: VariableFont, instances: list = None):
        start_time = time.time()

        if not instances:
            instances = variable_font.get_instances()

        if len(instances) == 0:
            generic_error_message("No instances found")
            return

        if self.options.update_name_table:
            if "STAT" not in variable_font:
                self.options.update_name_table = False
                generic_warning_message("Cannot update name table if there is no STAT table.")
            if not hasattr(variable_font["STAT"], "AxisValueArray"):
                self.options.update_name_table = False
                generic_warning_message("Cannot update name table if there are no STAT Axis Values.")

        instance_count = 0
        for instance in instances:
            t = time.time()
            instance_count += 1

            print()
            generic_info_message(f"Exporting instance {instance_count} of {len(instances)}")

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
                name_ids_to_delete = variable_font.get_var_name_ids_to_delete() if self.options.cleanup else []
                static_instance.name_table.del_names(name_ids=name_ids_to_delete)

                if "STAT" in static_instance:
                    del static_instance["STAT"]

                static_instance.reorder_ui_name_ids()

            static_instance_name = sanitize_filename(variable_font.get_instance_file_name(instance))
            static_instance_extension = static_instance.get_real_extension()
            output_file = makeOutputFileName(
                static_instance_name,
                extension=static_instance_extension,
                outputDir=self.options.output_dir,
                overWrite=self.options.overwrite,
            )
            static_instance.save(output_file)

            generic_info_message(f"Done in {round(time.time() - t, 3)} seconds")
            file_saved_message(output_file)

        print()
        generic_info_message(f"Total instances : {len(instances)}")
        generic_info_message(f"Elapsed time    : {round(time.time() - start_time)} seconds")
