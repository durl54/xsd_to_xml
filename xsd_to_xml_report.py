# Podawany plik .xsd może zawierać jedynie jedną formę sprawozdania.
# Np. 'Sprawozdanie jednostki małej' bądź 'Sprawozdanie jednostki małej w tyś'.
# Oby dwie struktury nie mogą na raz być podawane do konwersji ponieważ <id> recordów bedą się dublować.
# Pliki należy konwertować oddzielnie i potem łączyć w jeden plik.
# Należy pamiętać aby zmieniać 'record_prefix_id' na właściwy dla każdego sprawozdania aby się nie dublowały.


from bs4 import BeautifulSoup
from tkinter import filedialog
from tkinter import *
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from pprint import pprint
import xml.dom.minidom
from lxml import etree
import re


chose_file =  filedialog.askopenfilename()
file = open(chose_file, 'r')
soup = BeautifulSoup(file, 'lxml')

odoo_tag = Element('odoo')
data_tag = SubElement(odoo_tag, 'data')

record_model = 'account.financial.html.report.line'
record_prefix_id = 'jednostka_mala_rzis_tys_'
code_prefix = 'pol_jm_rzis_tys_'

# def xsd_to_xml(soup,root,record_model):
for section in soup.find_all('element'):
    if not bool(re.search('^PozycjaUszcz', section['name'])):
        ids_set=[]
        for record_set_id in data_tag:
            ids_set.append(record_set_id.attrib['id'])
        if not (record_prefix_id + section['name']) in ids_set:
            record_set = SubElement(data_tag, 'record', {'id':record_prefix_id + section['name'], 'model':record_model})
            field_row_1 = SubElement(record_set, 'field', {'name':'code'}).text=code_prefix + section['name']
        else:
            record_set = SubElement(data_tag, 'record', {'id':record_prefix_id + section['name'] + '2', 'model':record_model})
            field_row_1 = SubElement(record_set, 'field', {'name':'code'}).text=code_prefix + section['name'] + '2'
        # field_row_1 = SubElement(record_set, 'field', {'name':'code'}).text=code_prefix + section['name']
        field_row_2 = SubElement(record_set, 'field', {'name':'name'}).text=section.annotation.documentation.string
        for parent in section.parents:
            if parent.name == 'element' and not bool(re.search('^PozycjaUszcz', parent['name'])):
                field_row_4 = SubElement(record_set, 'field', {'name':'parent_id', 'ref': record_prefix_id + parent['name']})
                parent_name = record_prefix_id + parent['name']
                break
        count_lvl = 0
        for level in section.parents:
            if level.name == 'element':
                count_lvl += 1
        field_row_3 = SubElement(record_set, 'field', {'name':'level', 'eval': str(count_lvl)})

        record_seq = 0
        for record_element in data_tag:
            count_seq = 0
            for field_element in record_element:
                if 'ref' in field_element.attrib:
                    if field_element.attrib['ref'] == parent_name:
                        count_seq += 1
                    else:
                        break
                elif 'name' in field_element.attrib:
                    if field_element.attrib['name'] == 'level':
                        if str(field_element.attrib['eval']) == str(count_lvl):
                            count_seq += 1

            if count_seq == 2:
                record_seq += 1
        field_row_5 = SubElement(record_set, 'field', {'name':'sequence', 'eval': str(record_seq)})

f = open('output.xml', 'x')

xml_str = tostring(odoo_tag)
root = etree.fromstring(xml_str)
f.write('<?xml version="1.0" encoding="utf-8"?>\n')
f.write(etree.tostring(root, pretty_print=True, encoding='UTF-8').decode())
