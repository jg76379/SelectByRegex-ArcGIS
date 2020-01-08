# -*- coding: utf-8 -*-
import os
import re

import arcpy


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

        checkbox.value = "false"

        out_workspace = arcpy.Parameter(
            displayName="Out Workspace",
            name="OutWorkspace",
            datatype="DEWorkspace",
            parameterType="Optional",
            direction="Input")

        parameters = [layer, uniqueIDField, selectionField, regex, checkbox, out_workspace]

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
        # Check if regular expression string can be compiled to a valid regular expression
        if parameters[3].value is not None:
            regex = parameters[3].valueAsText
            try:
                re.compile(regex)
            except Exception as e:
                parameters[3].setErrorMessage("Invalid Regular Expression")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        self.select_by_regex(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText,
                             parameters[3].valueAsText, parameters[4].valueAsText, parameters[5].valueAsText)
        return

    def select_by_regex(self, layer, unique_id, selection_field, regex, non_matching, out_workspace=None):
        """
        Selects fields in layer that match the regular expression
        :param layer: layer to apply the selection to
        :param unique_id: ObjectID or other unique ID
        :param selection_field: field that the regex will search in
        :param regex: a regular expression to apply to the search
        :param non_matching: if "true" then records that do not match the regex will be selected, if false then matching
        :param out_workspace: arcpy.DEWorkspace | None. The workspace to create the output feature class
        records will be selected.
        :return: None
        """

        field_list = [unique_id, selection_field]
        try:
            pattern = re.compile(regex)
        except Exception as e:
            arcpy.AddError("Invalid Regular Expression")
            raise arcpy.ExecuteError
        where_exp = f"{selection_field} IS NOT NULL"
        oid_list = []
        with arcpy.da.SearchCursor(layer, field_list, where_exp) as s_cursor:
            for row in s_cursor:
                if pattern.search(row[1]):
                    oid_list.append(row[0])

        if non_matching == "true":
            sql_query = unique_id + " NOT IN ("
        else:
            sql_query = unique_id + " IN ("
        for index, val in enumerate(oid_list):
            if index < (len(oid_list) - 1):
                sql_query = f'{sql_query}{val},'
            else:
                sql_query = f'{sql_query}{val})'

        arcpy.SelectLayerByAttribute_management(layer, 'NEW_SELECTION', sql_query)

        if out_workspace:
            arcpy.env.workspace = out_workspace
            out_feature_name = layer + '_' + selection_field + '_regexSelection'
            workspace_features = arcpy.ListFeatureClasses()
            print(workspace_features)
            if out_feature_name in workspace_features:
                count = 1
                new_out_feature_name = out_feature_name
                while new_out_feature_name in workspace_features:
                    new_out_feature_name = out_feature_name + str(count)
                    count += 1
                out_feature_name = new_out_feature_name
            out_featureclass = os.path.join(out_workspace, out_feature_name)
            arcpy.CopyFeatures_management(in_features=layer,
                                          out_feature_class=out_featureclass)
