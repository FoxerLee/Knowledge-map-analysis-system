from django.shortcuts import render
from py2neo import Graph,Node,Relationship
import csv
import os


def entity(request):
    graph = Graph("bolt://10.60.42.201:7687", username="neo4j", password="123456")
    if request.method == "POST":
        file_obj = request.FILES.get("up_file")
        print(file_obj.name)

        # f1 = open(file_obj.name, "wb")'
        string = ""
        for i in file_obj.chunks():
            string += str(i, encoding="utf-8")

        datas = string.split(".\n")
        for d in datas:
            d = str(d).split(' ')
            tmp = []
            for item in d:
                item = item.split('/')
                tmp.append(item[-1][:-1])

            node1 = Node(name=tmp[0])
            node2 = Node(name=tmp[2])
            prop = Relationship(node1, tmp[1], node2)
            graph.create(prop)

    return render(request, 'ETL.html')


def relation(request):
    graph = Graph("bolt://10.60.42.201:7687", username="neo4j", password="123456")
    if request.method == "POST":
        file_obj = request.FILES.get("up_file")
        print(file_obj.name)

        # f1 = open(file_obj.name, "wb")'
        string = ""
        for i in file_obj.chunks():
            string += str(i, encoding="utf-8")

        relations = string.split("\r\n")
        for relation in relations:
            rel = relation.split(",")

            node1 = Node(name=rel[0])
            node2 = Node(name=rel[2])
            prop = Relationship(node1, rel[1], node2)
            graph.create(prop)

    return render(request, 'ETL.html')


# Create your views here.
def index(request):

    return render(request, 'ETL.html')
