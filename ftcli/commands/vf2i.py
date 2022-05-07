import os

import click
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode

from ftcli.Lib.VFont import VariableFont


@click.command()
@click.argument('input_file', type=click.Path(exists=True, resolve_path=True, dir_okay=False))
@click.option('-s', '--select-instance', 'selectInstance', is_flag=True, default=False,
              help="Use this option to select a single instance instead of exporting all named instances.")
@click.option('--no-cleanup', 'cleanup', is_flag=True, default=True,
              help="By default, STAT table is dropped and axis nameIDs are deleted from name table. Use --no-cleanup "
                   "to keep STAT table and prevent axis nameIDs ftom nam table.")
@click.option('-o', '--output-dir', 'outputDir', type=click.Path(file_okay=False, resolve_path=True), default=None,
              help="Specify the output directory where the output files are to be saved. If output_directory doesn't "
                   "exist, will be created. If not specified, files are saved to the same folder.")
@click.option('--recalc-timestamp', 'recalcTimestamp', is_flag=True, default=False,
              help="Keep the original font 'modified' timestamp (head.modified) or set it to current time. By "
                   "default, original timestamp is kept.")
@click.option('--no-overwrite', 'overWrite', is_flag=True, default=True,
              help="Overwrite existing output files or save them to a new file (numbers are appended at the end of "
                   "file name). By default, files are overwritten.")
def cli(input_file, selectInstance=False, cleanup=True,  outputDir=None, recalcTimestamp=False, overWrite=True):
    """
Exports static instances from a variable font.

INPUT_FILE must be a valid variable font (at least fvar and STAT tables must be present).

By default, the script exports all named instances. Use the -s/--select-instance option to export a single instance.
When the -s/--select-instance is passed, user will be asked to insert the desired axis values.
    """

    if outputDir is not None:
        os.makedirs(outputDir, exist_ok=True)

    try:
        var_font = VariableFont(input_file, recalcTimestamp=recalcTimestamp)
        name_ids_to_delete = var_font.getNameIDsToDelete()

        instances = []
        if selectInstance is True:
            selected_coordinates = {}
            print(f"\nSelect coordinates\n")
            for a in var_font.fvarTable.axes:
                axis_tag = a.axisTag
                min_value = a.minValue
                max_value = a.maxValue

                value = click.prompt(f"{axis_tag} ({min_value} - {max_value})",
                                     type=click.FloatRange(min_value, max_value))
                selected_coordinates[axis_tag] = value

            is_named_instance = selected_coordinates in [i.coordinates for i in var_font.fvarTable.instances]
            if is_named_instance is False:
                new_instance = NamedInstance()
                new_instance.coordinates = selected_coordinates
                instances.append(new_instance)
            else:
                for i in var_font.fvarTable.instances:
                    if i.coordinates == selected_coordinates:
                        instances.append(i)
                        break

        else:
            for i in var_font.fvarTable.instances:
                instances.append(i)

        if len(instances) > 0:
            instance_count = 0

            for i in instances:
                instance_count += 1
                print(f"\nExporting instance {instance_count} of {len(instances)}...")
                staticfont = instantiateVariableFont(varfont=var_font, axisLimits=i.coordinates,
                                                     overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS, optimize=True)
                if cleanup is True:
                    staticfont.cleanupInstance(name_ids_to_delete)
                output_file = var_font.makeInstanceOutputFileName(i, outputDir, overWrite)
                staticfont.save(output_file)
                click.secho(f'{output_file} saved', fg='green')
        else:
            print("\nNo instances found.")

    except Exception as e:
        click.secho(f'ERROR: {e}', fg='red')
