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

def main():
    sample_script = "DSC1Dh1Y0A1I1Bt2tR1NLvhY223I0u2Nomhi0ISJb52owTeG3JX3GP1hRRTO2gGSrG4J5Meb451rQ42vwdps1LljmK2XeBVa0jZytE4Ayl6B2C2cSK1Jz0582BbFd64SvrVO0bZMBJ2ilOVH1mSDfR2emb320CGaKz4PvDv13GnIsr3Jc6tC1FU4Px0nj01y24v1df0ral4M0dWVhV03jINe2T8hQf0aUrNC3nowiy45nVVS4d1Yqc08BeeK4WAW0d3CIfM72tn5Ym2tdv3h0zlPaJ2doZp63qa4uT2XWEmY1OJKEO28It8J2ke2AV03k3VN0gGAJY3pn4tI01gWee4Ojo5B41yXNs3JZ8Ts265QJ00Zwclq4Z0o4549ZUgN4ZcojH2IrjEk0ElTja2l3wZU02PAlW1xzkpV2mcvTu38oepn2SfHCj4crFIV27ilfc0O2Luc4Ixvyr1hIgXC1XvWbf3Jb0RK3GhNFR0NAp6j25gnAj1X1MKZ0YMGAY4XxYkU2IWvBH31izTV4AZK6f42lqXH4Ngf0N3yhzBs2wlvII3nUWcN09IFj62WWNfl4XR8RE3RKGlW0FgrBy3ei6wi0tR5aZ3yRAGE22Ff0h0y2FCQ45RP3B17HkpC2kyLFf4TsO0A4AoL2z3uQTPL4ejGqE34RNkA0ikIG73AchaR0S7zpD3qTrh41p5fLx0LGHBB2PIaxC2VVGRw0KWoJX4I9sLR22ee2R28xIX508zDwL4MPsoI0SrLnF2e38OX1KIcgj2hfrdY0DOJYy42DXVb0Y5Hpj3evNpM3dU8gT3GLJbu3eO8tV4GEDMl3sCiak0TYjVF3hOFJQ13P3qs16aAwv1k2n413Hbcq23681a43XXrU20cG0dp1X9skp2tpEgF1ISEvm1HdmZW2675aL0OH5aP4c0zeH0WpFJP3CVaxC3To1Fv0ZyCK61oR2xM09R8Gc25gh5Q4YT9co06BHrd1W2vXn2rBzuH3UsTZA396oAI23LlWd0cJzqw0J8eBi1nPrQP3LN0932hHkMg3E5F4k0b1MTJ0dM06y4WHezk2VaHOv3yWgUF0cqyIS16UOHK1Xd2mv4fjzKO0MXFSh"

    as_dict =get_dict_from_desynced_str(sample_script)
    print(as_dict)
    as_str = get_desynced_str_from_dict(as_dict)
    print(as_str)




if __name__ == "__main__":
    main()
