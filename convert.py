import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By


def get_dict_from_desynced_str(str_to_decode):
    with open("DesyncedJavaScriptUtils/dsconvert.js", "r") as file:
        javascript_code = file.read()

    doc = """
    <!DOCTYPE html>
    <html>
    <head></head>
    <body>
    <script type="text/javascript">
    """ + javascript_code + """
    </script>

    <div id="resultDiv"></div>

    <script type="text/javascript">
    function run(){
    var result= DesyncedStringToObject(\"""" + str_to_decode + """\");
    document.getElementById("resultDiv").innerHTML = JSON.stringify(result, null, 4);
    }
    run();
    </script>    
    </body>
    </html>
    """

    wd = os.getcwd()
    temp_file = os.path.join(wd, "TEMP.html")
    assert not os.path.isfile(temp_file)
    with open(temp_file, "w") as outfile:
        outfile.write(doc)

    # TODO allow to configure other browsers?
    os.environ['MOZ_HEADLESS'] = '1'
    driver = webdriver.Firefox()

    driver.get("file://"+temp_file)
    elem = driver.find_element(By.ID, "resultDiv")
    json_str = elem.text
    driver.close()
    os.remove(temp_file)

    return json.loads(json_str)


def get_desynced_str_from_dict(dict_to_convert):
    as_str = json.dumps(dict_to_convert)
    with open("DesyncedJavaScriptUtils/dsconvert.js", "r") as file:
        javascript_code = file.read()

    assert "'" not in as_str
    # otherwise quotation will not work correctly

    doc = """
    <!DOCTYPE html>
    <html>
    <head></head>
    <body>
    <script type="text/javascript">
    """ + javascript_code + """
    </script>

    <div id="resultDiv"></div>

    <script type="text/javascript">
    function run(){
    var jsonobj;
    try { jsonobj = JSON.parse('""" + as_str + """'); } catch { }
    var result= ObjectToDesyncedString();
    var type = (jsonobj[0] ? 'C' : 'B');
    result = ObjectToDesyncedString(jsonobj, type);
    document.getElementById("resultDiv").innerHTML = result;
    }
    run();
    </script>    
    </body>
    </html>
    """

    wd = os.getcwd()
    temp_file = os.path.join(wd, "TEMP.html")
    assert not os.path.isfile(temp_file)
    with open(temp_file, "w") as outfile:
        outfile.write(doc)

    # TODO allow to configure other browsers?
    os.environ['MOZ_HEADLESS'] = '1'
    driver = webdriver.Firefox()

    driver.get("file://"+temp_file)
    elem = driver.find_element(By.ID, "resultDiv")
    result_str = elem.text
    driver.close()
    os.remove(temp_file)

    return result_str
