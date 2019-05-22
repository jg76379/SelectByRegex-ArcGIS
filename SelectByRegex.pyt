# -*- coding: utf-8 -*-
import re

import arcpy
import pandas as pd
from pandas import DataFrame

# Suppress warnings about Match groups from pandas.Series.str.contains
# If this warning is not suppressed ArcPro will show that the tool has failed
import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "SelectByRegex Toolbox"
        self.alias = "SelectByRegex"

        # List of tool classes associated with this toolbox
        self.tools = [SelectByRegex]


class SelectByRegex(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "SelectByRegex"
        self.description = "Select features in a layer using a regular expression."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        layer = arcpy.Parameter(
            displayName="Layer",
            name="layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        uniqueIDField = arcpy.Parameter(
            displayName="Unique ID Field",
            name="UniqueIDField",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        uniqueIDField.parameterDependencies = [layer.name]

        selectionField = arcpy.Parameter(
            displayName="Selection Field",
            name="selectionField",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        selectionField.parameterDependencies = [layer.name]

        regex = arcpy.Parameter(
            displayName="Regular Expression String",
            name="regex",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        checkbox = arcpy.Parameter(
            displayName="Select non-matching",
            name="checkbox",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        checkbox.value = "true"

        parameters = [layer, uniqueIDField, selectionField, regex, checkbox]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        self.select_by_regex(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText,
                             parameters[3].valueAsText, parameters[4].valueAsText)
        return

    def feature_class_to_pandas_data_frame(self, feature_class, field_list):
        """
        Load data into a Pandas Data Frame for subsequent analysis.
        :param feature_class: Input ArcGIS Feature Class.
        :param field_list: Fields for input.
        :return: Pandas DataFrame object.
        """
        return DataFrame(
            arcpy.da.FeatureClassToNumPyArray(
                in_table=feature_class,
                field_names=field_list,
                skip_nulls=False,
                null_value=-99999
            )
        )

    def select_by_regex(self, layer, unique_id, selection_field, regex, non_matching):
        """
        Selects fields in layer that DO NOT match the regular expression
        :param layer: layer to apply the selection to
        :param unique_id: ObjectID or other unique ID
        :param selection_field: field that the regex will search in
        :param regex: a regular expression to apply to the search
        :param non_matching: if "true" then records that do not match the regex will be selected, if false then matching
        records will be selected.

        :return:
        """

        field_list = [unique_id, selection_field]
        layer_DF = self.feature_class_to_pandas_data_frame(layer, field_list)
        match = layer_DF[
            layer_DF[selection_field].str.contains(regex, flags=re.IGNORECASE, regex=True, na=False, case=True)]

        merge = pd.merge(layer_DF, match, how='outer', on=unique_id)

        # Query the null records (ones that did not match the regex)
        y_field = selection_field + '_y'
        merge = merge.query(f"{y_field} != {y_field}")

        if non_matching == "true":
            sqlQuery = unique_id + " IN ("
        else:
            sqlQuery = unique_id + " NOT IN ("
        oidList = merge[unique_id].tolist()
        for index, val in enumerate(oidList):
            if index < (len(oidList) - 1):
                sqlQuery = f'{sqlQuery}{val},'
            else:
                sqlQuery = f'{sqlQuery}{val})'

        arcpy.SelectLayerByAttribute_management(layer, 'NEW_SELECTION', sqlQuery)
