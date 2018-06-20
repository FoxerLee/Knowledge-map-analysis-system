from django.shortcuts import render
from py2neo import Graph,Node,Relationship
from django.http import HttpResponse
import json
import random
import redis
import numpy as np

# 连接 neo4j
graph = Graph("bolt://10.60.42.201:7687", username="neo4j", password="123456")
# 连接 redis
redis_con = redis.Redis(host='10.60.42.201', port=8089, decode_responses=True)

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

def searchbyentity(request):
    return render(request, 'searchbyentity.html')


def chart(r):
    result = {}
    nodes = []
    links = []
    count = 0
    for i in range(0, len(r)):

        style = dict()
        style['normal'] = {}
        
        l = dict()
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
    # print(result)
    return result


def add(request):
    name = request.GET.get('name')
    data = graph.run(cypher="match({name:\"" + name + "\"})-[r]->(n) return r.property,n")
    d = []
    result = data.data()
    length = len(result)
    for i in range(0, length):
        
        r = dict()
        r['e1'] = name
        r['re'] = result[i]['r.property']
        r['e2'] = result[i]['n']['name']
        d.append(r)
    print(d)
    result = chart(d)
    return HttpResponse(result)


def search(request):
    entity1 = request.GET.get('entity1')
    entity2 = request.GET.get('entity2')
    relationship = request.GET.get('relationship')

    # 待获取的参数
    result = dict()
    d = []
    length = 0

    if entity1 != '' and entity2 != '' and relationship == '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = entity1 + '_' + '#' + '_' + entity2

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
            data = graph.run(cypher="match({name:\""+entity1+"\"})-[r]->({name:\""+entity2+"\"}) return r.property")
    
            result = data.data()
            length = len(result)
    
            for i in range(0, length):
                r = dict()
                r['e1'] = entity1
                r['re'] = result[i]['r.property']
                r['e2'] = entity2
                d.append(r)
                result = chart(d)

                # 不存在则写入 redis 缓存
                print("Write to redis!")
                redis_con.hmset(key, {'length': length, 'd': d, 'result': result})

        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})

    if entity1 != '' and entity2 == '' and relationship == '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = entity1 + '_' + '#' + '_' + '#'

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print(redis_con.hkeys(key))
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
            data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[r]->(n) return r.property,n")

            result = data.data()
            length = len(result)
            for i in range(0, length):
                r = dict()
                r['e1'] = entity1
                r['re'] = result[i]['r.property']
                r['e2'] = result[i]['n']['name']
                d.append(r)

            result = chart(d)

            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    if entity1 == '' and entity2 != '' and relationship == '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = '#' + '_' + '#' + '_' + entity2

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
            data = graph.run(cypher="match(n)-[r]->({name:\"" + entity2 + "\"}) return r.property,n")
            # d = []
            result = data.data()
            length = len(result)
            for i in range(0, length):
                r = dict()
                r['e1'] = result[i]['n']['name']
                r['re'] = result[i]['r.property']
                r['e2'] = entity2
                d.append(r)
            
            result = chart(d)

            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
            
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    if entity1 != '' and entity2 == '' and relationship != '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = entity1 + '_' + relationship + '_' + '#'

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
            data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[{type:\""+relationship+"\"}]->(n) return n")
            
            result = data.data()
            length = len(result)
            for i in range(0, length):
                r = dict()
                r['e1'] = entity1
                r['re'] = relationship
                r['e2'] = result[i]['n']['name']
                d.append(r)
            
            result = chart(d)
    
            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
            
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    if entity1 == '' and entity2 != '' and relationship != '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = '#' + '_' + relationship + '_' + entity2

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
            
            data = graph.run(cypher="match(n)-[{type:\""+relationship+"\"}]->({name:\"" + entity2 + "\"}) return n")
            # d = []
            result = data.data()
            length = len(result)
            for i in range(0, length):
                r = dict()
                r['e1'] = result[i]['n']['name']
                r['re'] = relationship
                r['e2'] = entity2
                d.append(r)
            
            result = chart(d)
            
            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
            
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    if entity1 != '' and entity2 != '' and relationship != '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = entity1 + '_' + relationship + '_' + entity2

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
        
            data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[{type:\""+relationship+"\"}]->(n{name:\"" + entity2 + "\"}) return n")
            # d = []
            result = data.data()
            length = len(result)
            for i in range(0, length):
                r = dict()
                r['e1'] = entity1
                r['re'] = relationship
                r['e2'] = entity2
                d.append(r)
            
            result = chart(d)

            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    if entity1 == '' and entity2 == ''and relationship != '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = '#' + '_' + relationship + '_' + '#'

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print("From redis!")
            result = eval(redis_con.hmget(key, 'result')[0])
            d = eval(redis_con.hmget(key, 'd')[0])
            length = eval(redis_con.hmget(key, 'length')[0])

        else:
            
            data = graph.run(cypher="match(m)-[{type:\""+relationship+"\"}]->(n) return m,n")
            # d = []
            result = data.data()
            length = len(result)
            for i in range(0, length):
                r = dict()
                r['e1'] = result[i]['m']['name']
                r['re'] = relationship
                r['e2'] = result[i]['n']['name']
                d.append(r)
           
            result = chart(d)
    
            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})

    return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})





