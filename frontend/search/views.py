from django.shortcuts import render
from py2neo import Graph, Node, Relationship
from django.http import HttpResponse, JsonResponse
import json
import random
import redis
import re
from pygraph.classes.digraph import digraph

import numpy as np

# 连接 neo4j
graph = Graph("bolt://10.60.42.201:7687", username="neo4j", password="123456")
# 连接 redis
redis_con = redis.Redis(host='10.60.42.201', port=8089, decode_responses=True)


class PRIterator:
    __doc__ = '''计算一张图中的PR值'''

    def __init__(self, dg):
        self.damping_factor = 0.85  # 阻尼系数,即α
        self.max_iterations = 100  # 最大迭代次数
        self.min_delta = 0.00001  # 确定迭代是否结束的参数,即ϵ
        self.graph = dg

    def page_rank(self):
        #  先将图中没有出链的节点改为对所有节点都有出链
        for node in self.graph.nodes():
            if len(self.graph.neighbors(node)) == 0:
                for node2 in self.graph.nodes():
                    digraph.add_edge(self.graph, (node, node2))

        nodes = self.graph.nodes()
        graph_size = len(nodes)

        if graph_size == 0:
            return {}
        page_rank = dict.fromkeys(nodes, 1.0 / graph_size)  # 给每个节点赋予初始的PR值
        damping_value = (1.0 - self.damping_factor) / graph_size  # 公式中的(1−α)/N部分

        flag = False
        for i in range(self.max_iterations):
            change = 0
            for node in nodes:
                rank = 0
                for incident_page in self.graph.incidents(node):  # 遍历所有“入射”的页面
                    rank += self.damping_factor * (page_rank[incident_page] / len(self.graph.neighbors(incident_page)))
                rank += damping_value
                change += abs(page_rank[node] - rank)  # 绝对值
                page_rank[node] = rank

            # print("This is NO.%s iteration" % (i + 1))
            # print(page_rank)

            if change < self.min_delta:
                flag = True
                break
        # if flag:
        #     print("finished in %s iterations!" % node)
        # else:
        #     print("finished out of 100 iterations!")
        return page_rank


def fuzzyfinder(user_input, collection):
    suggestions = []
    pattern = '.*?'.join(user_input)  # Converts 'djm' to 'd.*?j.*?m'
    regex = re.compile(pattern)  # Compiles a regex.
    for item in collection:
        match = regex.search(item)  # Checks if the current item matches the regex.
        if match:
            suggestions.append((len(match.group()), match.start(), item))
    return [x for _, _, x in sorted(suggestions)]

# Create your views here.


def searchbyentity(request):
    return render(request, 'searchbyentity.html')


def searchbytwoentities(request):
    return render(request, 'searchbytwoentities.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def chart(r, t):
    data = {}
    r_unique = []
    flag = 0
    position = 0
    result = []
    count = 0
    for i in range(0, len(r)):
        if len(r_unique) != 0:
            for j in range(0, len(r_unique)):
                if r[i]['re'] == r_unique[j]:
                    flag = 1
                    position = j
                    break
        if flag == 0:
            re = {}
            print(r[i]['re'])
            r_unique.append(r[i]['re'])
            re['id'] = str(count)
            count += 1
            re['name'] = r[i]['re']
            #re['id'] = 1
            re['children'] = []
            re['data'] = {}
            c = {}
            c['id'] = str(count)
            count += 1
            if t == 2 or t == 4:
                c['name'] = r[i]['e2']
            if t == 3 or t == 5:
                c['name'] = r[i]['e1']
            c['data'] = {}
            c['children'] = []
            #c['value'] = 1
            re['children'].append(c)
            result.append(re)
        else:
            c = {}
            c['id'] = str(count)
            count += 1
            if t == 2 or t == 4:
                c['name'] = r[i]['e2']
            if t == 3 or t == 5:
                c['name'] = r[i]['e1']
            c['data'] = {}
            c['children'] = []
            #c['value'] = 1
            result[position]['children'].append(c)
            #result[position]['value'] += 1
            flag = 0
            position = 0
    data['id'] = str(count)
    count += 1
    if t == 2 or t == 4:
        data['name'] = r[0]['e1']
    if t == 3 or t == 5:
        data['name'] = r[0]['e2']
    data['children'] = result
    data['data'] = []
    print(data)
    return data


def chart2(r,t):
    #print(r)
    data = {}
    r_unique = []
    flag = 0
    position = 0
    result = []
    for i in range(0,len(r)):
        if len(r_unique) != 0:
            for j in range(0,len(r_unique)):
                if r[i]['re'] == r_unique[j]:
                    flag =1
                    position = j
                    break
        if flag == 0:
            re = {}
            print(r[i]['re'])
            r_unique.append(r[i]['re'])
            re['name'] = r[i]['re']
            re['value'] = 1
            re['children'] = []
            c = {}
            if t == 2 or t == 4:
                c['name'] = r[i]['e2']
            if t == 3 or t == 5:
                c['name'] = r[i]['e1']
            c['value'] = 1
            re['children'].append(c)
            result.append(re)
        else:
            c = {}
            if t == 2 or t == 4:
                c['name'] = r[i]['e2']
            if t == 3 or t == 5:
                c['name'] = r[i]['e1']
            c['value'] = 1
            result[position]['children'].append(c)
            result[position]['value'] += 1
            flag = 0
            position = 0
    data['result'] = result
    print(data)
    return data


def chart3(r,e1,e2):
    result = {}
    nodes1 = []
    nodes2 = []
    nodes = []
    links = []
    count = 0
    match = {}
    for i in range(0,len(r)):
        if r[i]['e1'] != r[i]['e2']:
            match[r[i]['e2']] = r[i]['category']
            style = {}
            style['normal'] = {}
            label = {}
            label['show'] = True
            label['formatter'] = r[i]['re']
            label1 = {}
            label1['normal'] = label
            l = {}
            l['id'] = count
            l['name'] = r[i]['re']
            
            l['source'] = r[i]['e1']
            l['target'] = r[i]['e2']
            l['lineStyle'] = style
            l['label'] = label1
            links.append(l)
            count = count+1
            nodes.append(r[i]['e1'])
            nodes.append(r[i]['e2'])
    print(match)
    nodes = list(set(nodes))
    node = []
    #print("lllll:",ll)
    #print("len:", len(nodes))
    for i in range(0,len(nodes)):
        start = i*20
        last = start + 20
        
        n = {}
        n['id'] = nodes[i]
        n['name'] = nodes[i]
        if nodes[i] == e1:
            n['category'] = 0
            n['symbolSize'] = 30
        elif nodes[i] == e2:
            n['category'] = 0
            n['symbolSize'] = 30
        else:
            n['category'] = match[nodes[i]]
            n['symbolSize'] = 15
        n['x'] = random.randint((-1)*last,(-1)*start)
        n['y'] = random.randint(start,last)
        n['value'] = random.randint(5, 20)
        node.append(n)

    result['nodes'] = node
    result['links'] = links
    print(result)
    return result



def add(request):
    type = 2
    name = request.GET.get('name')
    print(name)
    data = graph.run(cypher="match({name:\"" + name + "\"})-[r]->(n) return r.property,n")
    d = []
    result = data.data()
    length = len(result)
    for i in range(0, length):
        r = {}
        r['e1'] = name
        r['re'] = result[i]['r.property']
        r['e2'] = result[i]['n']['name']
        d.append(r)
    print(d)
    result2 = chart2(d, type)
    return JsonResponse(result2)


def showEntity(request):
    name = request.GET.get('name')
    print(name)
    f = open("../frontend/search/json/"+name+".json",'r')
    setting = json.load(f)
    print(setting)
    return JsonResponse(setting)


def searchTwoEntities(request):

    entity1 = request.GET.get('entity1')
    entity2 = request.GET.get('entity2')
    if entity1 != '' and entity2 != '':

        data = graph.run(cypher="MATCH p = (a{name:\""+entity1+"\"})-[*1..3]->(b{name:\""+entity2+"\"}) return p")
        d = []
        result = data.data()
        length = len(result)
        node = set()
        edge = []
        for i in range(0, length):
            for j in range(0,len(result[i]['p'])):
                r = {}
                r['e1'] = re.findall("\((.*)\)-.*", str(result[i]['p'][j]))[0]
                r['re'] = re.findall(".*'(.*)'}.*", str(result[i]['p'][j]))[0]
                r['e2'] = re.findall("->\((.*)\).*", str(result[i]['p'][j]))[0]
                r['category'] = j+1
                d.append(r)

                edge.append((re.findall("\((.*)\)-.*", str(result[i]['p'][j]))[0],
                             re.findall("->\((.*)\).*", str(result[i]['p'][j]))[0]))
                node.add(re.findall("\((.*)\)-.*", str(result[i]['p'][j]))[0])
                node.add(re.findall("->\((.*)\).*", str(result[i]['p'][j]))[0])

        node = list(node)
        edge = list(set(edge))
        dg = digraph()

        dg.add_nodes(node)
        for e in edge:
            dg.add_edge(e)

        pr = PRIterator(dg)
        page_ranks = pr.page_rank()
        page_ranks = sorted(page_ranks.items(), key=lambda item:item[1], reverse=True)

        pagerank = []
        print(page_ranks)
        for i in page_ranks:
            r = {}
            r["name"] = i[0]
            r["pagerank"] = i[1]

            pagerank.append(r)

        result = chart3(d, entity1, entity2)
        # print("hhh", result)
        # print(pagerank)

        return render(request, 'searchbytwoentities.html', {'data': d, 'num': len(d), 'graph': json.dumps(result),
                                                            'data2': pagerank})


def fsearch(request):
    q = request.GET['entity1']
    relist = []
    with open("static/entity1.json", 'r') as load_f:
        load_dict = json.load(load_f)
    try:
        load = load_dict["entity1"]
        relist = fuzzyfinder(q, load)
    except:
        print(q)
        print(q[0])

    rejson = dict()
    if len(relist) > 10:
        rejson["res"] = relist[:10]
    else:
        rejson["res"] = relist

    return JsonResponse(rejson)


def search(request):
    entity1 = request.GET.get('entity1')
    print("************",entity1)
    entity2 = request.GET.get('entity2')


    # 待获取的参数
    result = dict()
    result2 = dict()
    d = []
    length = 0

    # if entity1 != '' and entity2 != '' and relationship == '':
    #     # 针对 redis 中的 key 的存储格式：#_#_#
    #     # 分别代表 En1 - Rel - En2
    #     # 如果空则为 # 填充
    #     key = entity1 + '_' + '#' + '_' + entity2
    #
    #     # 如果在 redis 里面存在缓存
    #     if redis_con.hkeys(key):
    #         print("From redis!")
    #         result = eval(redis_con.hmget(key, 'result')[0])
    #         d = eval(redis_con.hmget(key, 'd')[0])
    #         length = eval(redis_con.hmget(key, 'length')[0])
    #
    #     else:
    #         data = graph.run(cypher="match({name:\""+entity1+"\"})-[r]->({name:\""+entity2+"\"}) return r.property")
    #
    #         result = data.data()
    #         length = len(result)
    #
    #         for i in range(0, length):
    #             r = dict()
    #             r['e1'] = entity1
    #             r['re'] = result[i]['r.property']
    #             r['e2'] = entity2
    #             d.append(r)
    #             result = chart(d)
    #
    #             # 不存在则写入 redis 缓存
    #             print("Write to redis!")
    #             redis_con.hmset(key, {'length': length, 'd': d, 'result': result})

        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})

    if entity1 != '' and entity2 == '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = entity1 + '_' + '#' + '_' + '#'
        type = 2
        print("hhhhhhhhhhhhh")

        # 如果在 redis 里面存在缓存
        if redis_con.hkeys(key):
            print(redis_con.hkeys(key))
            print("From redis!")
            # result = eval(redis_con.hmget(key, 'result')[0])
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

            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d})

        result = chart(d, type)
        result2 = chart2(d, type)

        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    if entity1 == '' and entity2 != '':
        # 针对 redis 中的 key 的存储格式：#_#_#
        # 分别代表 En1 - Rel - En2
        # 如果空则为 # 填充
        key = '#' + '_' + '#' + '_' + entity2
        type = 3

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

            # 不存在则写入 redis 缓存
            print("Write to redis!")
            redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
            
        result = chart(d, type)
        result2 = chart2(d, type)

        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    # if entity1 != '' and entity2 == '' and relationship != '':
    #     # 针对 redis 中的 key 的存储格式：#_#_#
    #     # 分别代表 En1 - Rel - En2
    #     # 如果空则为 # 填充
    #     key = entity1 + '_' + relationship + '_' + '#'
    #
    #     # 如果在 redis 里面存在缓存
    #     if redis_con.hkeys(key):
    #         print("From redis!")
    #         result = eval(redis_con.hmget(key, 'result')[0])
    #         d = eval(redis_con.hmget(key, 'd')[0])
    #         length = eval(redis_con.hmget(key, 'length')[0])
    #
    #     else:
    #         data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[{type:\""+relationship+"\"}]->(n) return n")
    #
    #         result = data.data()
    #         length = len(result)
    #         for i in range(0, length):
    #             r = dict()
    #             r['e1'] = entity1
    #             r['re'] = relationship
    #             r['e2'] = result[i]['n']['name']
    #             d.append(r)
    #
    #         result = chart(d)
    #
    #         # 不存在则写入 redis 缓存
    #         print("Write to redis!")
    #         redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
            
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    # if entity1 == '' and entity2 != '' and relationship != '':
    #     # 针对 redis 中的 key 的存储格式：#_#_#
    #     # 分别代表 En1 - Rel - En2
    #     # 如果空则为 # 填充
    #     key = '#' + '_' + relationship + '_' + entity2
    #
    #     # 如果在 redis 里面存在缓存
    #     if redis_con.hkeys(key):
    #         print("From redis!")
    #         result = eval(redis_con.hmget(key, 'result')[0])
    #         d = eval(redis_con.hmget(key, 'd')[0])
    #         length = eval(redis_con.hmget(key, 'length')[0])
    #
    #     else:
    #
    #         data = graph.run(cypher="match(n)-[{type:\""+relationship+"\"}]->({name:\"" + entity2 + "\"}) return n")
    #         # d = []
    #         result = data.data()
    #         length = len(result)
    #         for i in range(0, length):
    #             r = dict()
    #             r['e1'] = result[i]['n']['name']
    #             r['re'] = relationship
    #             r['e2'] = entity2
    #             d.append(r)
    #
    #         result = chart(d)
    #
    #         # 不存在则写入 redis 缓存
    #         print("Write to redis!")
    #         redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
            
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    # if entity1 != '' and entity2 != '' and relationship != '':
    #     # 针对 redis 中的 key 的存储格式：#_#_#
    #     # 分别代表 En1 - Rel - En2
    #     # 如果空则为 # 填充
    #     key = entity1 + '_' + relationship + '_' + entity2
    #
    #     # 如果在 redis 里面存在缓存
    #     if redis_con.hkeys(key):
    #         print("From redis!")
    #         result = eval(redis_con.hmget(key, 'result')[0])
    #         d = eval(redis_con.hmget(key, 'd')[0])
    #         length = eval(redis_con.hmget(key, 'length')[0])
    #
    #     else:
    #
    #         data = graph.run(cypher="match({name:\"" + entity1 + "\"})-[{type:\""+relationship+"\"}]->(n{name:\"" + entity2 + "\"}) return n")
    #         # d = []
    #         result = data.data()
    #         length = len(result)
    #         for i in range(0, length):
    #             r = dict()
    #             r['e1'] = entity1
    #             r['re'] = relationship
    #             r['e2'] = entity2
    #             d.append(r)
    #
    #         result = chart(d)
    #
    #         # 不存在则写入 redis 缓存
    #         print("Write to redis!")
    #         redis_con.hmset(key, {'length': length, 'd': d, 'result': result})
        # return render(request, 'searchbyentity.html', {'data': d, 'num': length, 'graph': json.dumps(result)})
    
    # if entity1 == '' and entity2 == ''and relationship != '':
    #     # 针对 redis 中的 key 的存储格式：#_#_#
    #     # 分别代表 En1 - Rel - En2
    #     # 如果空则为 # 填充
    #     key = '#' + '_' + relationship + '_' + '#'
    #
    #     # 如果在 redis 里面存在缓存
    #     if redis_con.hkeys(key):
    #         print("From redis!")
    #         result = eval(redis_con.hmget(key, 'result')[0])
    #         d = eval(redis_con.hmget(key, 'd')[0])
    #         length = eval(redis_con.hmget(key, 'length')[0])
    #
    #     else:
    #
    #         data = graph.run(cypher="match(m)-[{type:\""+relationship+"\"}]->(n) return m,n")
    #         # d = []
    #         result = data.data()
    #         length = len(result)
    #         for i in range(0, length):
    #             r = dict()
    #             r['e1'] = result[i]['m']['name']
    #             r['re'] = relationship
    #             r['e2'] = result[i]['n']['name']
    #             d.append(r)
    #
    #         result = chart(d)
    #
    #         # 不存在则写入 redis 缓存
    #         print("Write to redis!")
    #         redis_con.hmset(key, {'length': length, 'd': d, 'result': result})

    return render(request, 'searchbyentity.html', {'data': d, 'num': length,
                                                   'graph': json.dumps(result), 'graph2': json.dumps(result2)})





