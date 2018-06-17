from django.shortcuts import render
from py2neo import Graph,Node,Relationship
from django.http import HttpResponse
import json
import random
import numpy as np

# Create your views here.
graph = Graph("bolt://localhost:7687", username="neo4j", password="123456")
# graph.delete_all()
# test_node_1 = Node(label = "Person",name = "cc")
# test_node_2 = Node(label = "Person",name = "bb")
# test_node_3 = Node(label = "Person",name = "aa")
# graph.create(test_node_1)
# graph.create(test_node_2)
# graph.create(test_node_3)
# node_1_call_node_2 = Relationship(test_node_1,'like',test_node_2)
# node_1_call_node_2['name'] = 'rel'
# node_1_call_node_2['type'] = 'like'
# node_1_call_node_2_new = Relationship(test_node_1,'know',test_node_2)
# node_1_call_node_2_new['name'] = 'rel'
# node_1_call_node_2_new['type'] = 'know'
# node_1_call_node_3 = Relationship(test_node_1,'know',test_node_3)
# node_1_call_node_3['name'] = 'rel'
# node_1_call_node_3['type'] = 'know'
# node_2_call_node_3 = Relationship(test_node_2,'know',test_node_3)
# node_2_call_node_3['name'] = 'rel'
# node_2_call_node_3['type'] = 'know'
# node_2_call_node_1 = Relationship(test_node_2,'like',test_node_1)
# node_2_call_node_1['name'] = 'rel'
# node_2_call_node_1['type'] = 'like'
# graph.create(node_1_call_node_2)
# graph.create(node_1_call_node_2_new)
# graph.create(node_1_call_node_3)
# graph.create(node_2_call_node_1)

# def search():


# Create your views here.
def index(request):
    return render(request, 'ETL.html')


def searchbyentity(request):
    return render(request, 'searchbyentity.html')


def chart(r):
    result = {}
    nodes = []
    links = []
    count = 0
    for i in range(0,len(r)):

        style = {}
        style['normal'] = {}
        l = {}
        l['id'] = count
        l['name'] = r[i]['re']
        l['source'] = r[i]['e1']
        l['target'] = r[i]['e2']
        l['lineStyle'] = style
        links.append(l)
        count = count+1
        nodes.append(r[i]['e1'])
        nodes.append(r[i]['e2'])
    nodes = list(set(nodes))
    node = []
    for i in range(0,len(nodes)):

        n = {}
        n['id'] = nodes[i]
        n['name'] = nodes[i]
        n['symbolSize'] = random.randint(5, 20)
        n['category'] = 0
        n['value'] = random.randint(5, 20)

        node.append(n)
    result['nodes'] = node
    result['links'] = links
    print(result)
    return result


def add(request):
    name = request.GET.get('name')
    data = graph.run(cypher="match({name:\"" + name + "\"})-[r]->(n) return r.type,n")
    d = []
    result = data.data()
    length = len(result)
    for i in range(0, length):
        r = {}
        r['e1'] = name
        r['re'] = result[i]['r.type']
        r['e2'] = result[i]['n']['name']
        d.append(r)
    print(d)
    result = chart(d)
    return HttpResponse(result)


def search(request):
    entity1 = request.GET.get('entity1')
    # print(entity1)

    relationship = request.GET.get('relationship')

    entity2 = request.GET.get('entity2')
    # print("e2", entity2)

    if entity1 != '' and entity2 != '' and relationship == '':
        data = graph.run(cypher="match({name:\""+entity1+"\"})-[r]->({name:\""+entity2+"\"}) return r.type")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = entity1
            r['re'] = result[i]['r.type']
            r['e2'] = entity2
            d.append(r)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    if entity1 != '' and entity2 == '' and relationship == '':
        data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[r]->(n) return r.type,n")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = entity1
            r['re'] = result[i]['r.type']
            r['e2'] = result[i]['n']['name']
            d.append(r)
        print(d)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    if entity1 == '' and entity2 != '' and relationship == '':
        data = graph.run(cypher="match(n)-[r]->({name:\"" + entity2 + "\"}) return r.type,n")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = result[i]['n']['name']
            r['re'] = result[i]['r.type']
            r['e2'] = entity2
            d.append(r)
        print(d)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    if entity1 != '' and entity2 == '' and relationship != '':
        data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[{type:\""+relationship+"\"}]->(n) return n")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = entity1
            r['re'] = relationship
            r['e2'] = result[i]['n']['name']
            d.append(r)
        print(d)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    if entity1 == '' and entity2 != '' and relationship != '':
        data = graph.run(cypher="match(n)-[{type:\""+relationship+"\"}]->({name:\"" + entity2 + "\"}) return n")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = result[i]['n']['name']
            r['re'] = relationship
            r['e2'] = entity2
            d.append(r)
        print(d)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    if entity1 != '' and entity2 != '' and relationship != '':
        data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[{type:\""+relationship+"\"}]->(n{name:\"" + entity2 + "\"}) return n")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = entity1
            r['re'] = relationship
            r['e2'] = entity2
            d.append(r)
        print(d)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    if entity1 == '' and entity2 == ''and relationship != '':
        data = graph.run(cypher="match(m)-[{type:\""+relationship+"\"}]->(n) return m,n")
        d = []
        result = data.data()
        length = len(result)
        for i in range(0, length):
            r = {}
            r['e1'] = result[i]['m']['name']
            r['re'] = relationship
            r['e2'] = result[i]['n']['name']
            d.append(r)
        print(d)
        result = chart(d)
        return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})





