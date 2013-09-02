import urllib2
from lxml import etree
import re

output_file = open('messages_en.txt', 'w')

output_file.write("# *** messages_default.txt ***\n")
output_file.write("\n")

messages_default = urllib2.urlopen("https://bitbucket.org/commcare/javarosa/raw/0eff137d315de3410addd80a0c7bffad3a64e315/j2me/shared-resources/resources/messages_default.txt")

for line in messages_default:
    output_file.write(line.strip() + '\n')

output_file.write("\n")
output_file.write("# *** messages_cc_default.txt ***\n")
output_file.write("\n")

messages_cc_default = urllib2.urlopen("https://bitbucket.org/commcare/commcare/raw/a6f8ba32e97d24ec1705735036fc4a494b5330d7/application/resources/messages_cc_default.txt")

for line in messages_cc_default:
    output_file.write(line.strip() + '\n')

output_file.write("\n")
output_file.write("# *** messages_ccodk_default.txt ***\n")
output_file.write("\n")

messages_ccodk_default = urllib2.urlopen("https://bitbucket.org/commcare/commcare-odk/raw/dc5e832e8f48123bba1751a635aecf4158ed5405/app/assets/locales/messages_ccodk_default.txt")

for line in messages_ccodk_default:
    output_file.write(line.strip() + '\n')

output_file.write("\n")
output_file.write("# *** strings.xml ***\n")
output_file.write("\n")

strings_xml = urllib2.urlopen("https://bitbucket.org/commcare/opendatakit.collect/raw/b257c927f68d2567fc44b4ea910fa34f66ab32bc/res/values/strings.xml")

e = etree.parse(strings_xml)
string_elements = e.xpath('//resources/string')

for element in string_elements:
    element_text = element.text

    # replace strings with multiple interpolations that have
    # the format "%$1s received %$2s hugs from Danny"
    vals = re.findall(r'\%(\d*)\$s', element_text)
    for val in vals:
        reg = '\%' + val + '\$s'
        replacement = '${%s}' % str(int(val) - 1)
        element_text = re.sub(reg, replacement, element_text)

    # replace all %s occurences
    element_text = re.sub(r'\%s', '\${0}', element_text)

    line = 'odk_' + element.attrib['name'] + '=' + element_text
    output_file.write(line + '\n')
