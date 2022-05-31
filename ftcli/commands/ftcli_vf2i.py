import os

import click
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode

from ftcli.Lib.utils import add_file_argument, add_common_options
from ftcli.Lib.VFont import VariableFont


@click.command()
@add_file_argument()
@click.option('-s', '--select-instance', 'selectInstance', is_flag=True, default=False,
              help="By default, the script exports all named instances. Use this option to select custom axis values "
                   "for a single instance.")
@click.option('--no-cleanup', 'cleanup', is_flag=True, default=True,
              help="By default, STAT table is dropped and axis nameIDs are deleted from name table. Use --no-cleanup "
                   "to keep STAT table and prevent axis nameIDs from nam table.")
@click.option('--update-name-table', 'updateFontNames', is_flag=True, default=False,
              help="Update the instantiated font's `name` table. Input font must have a STAT table with Axis Value "
                   "Tables")
@add_common_options()
def cli(input_file, selectInstance=False, cleanup=True, updateFontNames=False, outputDir=None, recalcTimestamp=False,
        overWrite=True):
    """
    Exports static instances from a variable font.

    INPUT_FILE must be a valid variable font (at least `fvar` and `STAT` tables must be present).
    """

    if outputDir is not None:
        os.makedirs(outputDir, exist_ok=True)

    try:
        variable_font = VariableFont(input_file, recalcTimestamp=recalcTimestamp)
        name_ids_to_delete = variable_font.getNameIDsToDelete()

        instances = []
        if selectInstance is True:
            selected_coordinates = {}
            print(f"\nSelect coordinates\n")
            for a in variable_font.fvarTable.axes:
                axis_tag = a.axisTag
                min_value = a.minValue
                max_value = a.maxValue

                value = click.prompt(f"{axis_tag} ({min_value} - {max_value})",
                                     type=click.FloatRange(min_value, max_value))
                selected_coordinates[axis_tag] = value

            is_named_instance = selected_coordinates in [i.coordinates for i in variable_font.fvarTable.instances]
            if is_named_instance is False:
                new_instance = NamedInstance()
                new_instance.coordinates = selected_coordinates
                instances.append(new_instance)
            else:
                for i in variable_font.fvarTable.instances:
                    if i.coordinates == selected_coordinates:
                        instances.append(i)
                        break

        else:
            for i in variable_font.fvarTable.instances:
                instances.append(i)

        if len(instances) > 0:
            instance_count = 0

            for i in instances:
                instance_count += 1
                print(f"\nExporting instance {instance_count} of {len(instances)}...")
                static_instance = instantiateVariableFont(varfont=variable_font, axisLimits=i.coordinates,
                                                          updateFontNames=updateFontNames, optimize=True,
                                                          overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS)
                if cleanup is True:
                    static_instance.cleanupInstance(name_ids_to_delete)
                    del static_instance['STAT']
                output_file = variable_font.makeInstanceOutputFileName(i, outputDir, overWrite)
                static_instance.save(output_file)
                click.secho(f'{output_file} saved', fg='green')
        else:
            print("\nNo instances found.")

    except Exception as e:
        click.secho(f'ERROR: {e}', fg='red')
