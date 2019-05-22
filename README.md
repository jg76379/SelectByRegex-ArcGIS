# SelectByRegex

An ArcGIS Python toolbox with a single tool. This tool searches a layer's attribute table for records based on the pattern given in a regular expression string, in a particular field. Matching rows will be selected in the map.



## About Regular Expressions

"A regular expression (or regex) is a sequence of characters that define a search pattern."  - Wikipedia 

Regular expressions are useful tools for searching for strings of text that match a particular pattern. Regular expressions are defined by a series of characters, for example "\d" will match any numerical digit. There are many sources online to learn about regular expressions, and online tools that allow you to test regular expressions. This tool uses Python's re module to evaluate regular expressions, you can view the documentation here: https://docs.python.org/3/library/re.html

This tool allows for records in a layer to be selected based on a regular expression.

## Getting Started

### Prerequisites

This tool requires Python 3 and the Pandas package, and thus can only be used in ArcGIS Pro.

### Usage

Save the source code on your machine and then navigate to the folder using the catalog window in 
ArcGIS Pro. 




