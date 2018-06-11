import requests
from lxml import html
from xml.etree import ElementTree


def main():
    # res = requests.get('http://mappings.dbpedia.org/server/ontology/pages/')
    # print(res)
    f = open("../data/ontology.html", "r")
    res = ""
    l = f.readline()[:-1]

    while l:
        res += l
        l = f.readline()[:-1]

    tree = html.fromstring(res)

    ontologys = tree.xpath('/html/body/div/div/a')
    prefiex = "http://mappings.dbpedia.org/server/ontology/pages/"
    for o in ontologys:
        name = href = o.xpath('./@href')[0]

        name = name.split('%3A')
        varity = name[0]
        if len(name) == 3:
            name = name[1] + ":" + name[2]
        else:
            name = name[1]

        href = prefiex + href
        r = requests.get(href)
        f = open("../data/"+varity+"/"+name+".xml", "w")

        f.write(r.text)
        print("Get: {}".format(name) + " In: {}".format(varity))
        f.close()


if __name__ == '__main__':
    main()
