import json
import random
import sys
import time
import os
import xml.dom.minidom as minidom
import shutil, json
import zipfile
from django.http import FileResponse
import cv2

from django.shortcuts import render, redirect

# Create your views here.
from register import models
from workspace.models import Image,Project,Box


def firstpage(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        return render(req, 'firstpage.html', {
            'web_title': 'FirstPage',
            'uname': uname[0].username,
        })
    else:
        return redirect('../login/log/')

def logout(req):
    req.session.set_expiry(0)
    return redirect('../../login/log/')

def create(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        if req.method == 'GET':
            return render(req, 'create.html', {
                'web_title': 'create',
                'uname': uname[0].username,
                'upload_success': '',
                'picturenum': 0,
            })
        else:
            pic = Image.objects.filter(username_id=uid,is_usf=0)
            img_load = []
            num = 0
            for item in pic:
                num = num+1
                img_load.append(item.route)
            return render(req, 'create_success.html', {
                'web_title': 'create_successful',
                'picturenum': num,
                'img_load': img_load,
            })
    else:
        return redirect('../../login/log/')

def create_labels(req):
    if req.method == 'GET':
        if 'user' in req.session:
            uid = req.session['user']['user']
            uname = models.User.objects.filter(id=uid)
            # create a new project
            result = Image.objects.filter(username__in=uname)
            project_id = random.randint(100, 999) + int(time.time()) % 100000
            flag = 0
            for item in result:
                if item.is_usf == 0:
                    flag = 1
                    break
            if flag == 1:  # 至少有一张图片没用过
                Project.objects.create(id=project_id, username_id=uid)
            # change the condition of the image
            for item in result:
                if item.is_usf == 0:
                    _t = Image.objects.get(id=item.id)
                    _t.is_usf = 1
                    _t.project_id = project_id
                    _t.save()
            return render(req, 'create_labels.html', {
                'web_title': 'input labels',
                'uname': uname[0].username,
                'project_id': project_id,
            })
        else:
            return redirect('../../login/log/')
    else:
        body = req.body
        json_param = json.loads(body.decode())
        project_id = json_param["project_id"]
        project_id = int(project_id)
        labels = json_param["labels"]
        project = Project.objects.get(id=project_id)
        if project != None:
            project.labels = labels
            project.save()
        return redirect('../create_suc/')

def createsuc(req):
    if req.method == 'GET':
        if 'user' in req.session:
            uid = req.session['user']['user']
            uname = models.User.objects.filter(id=uid)
            # search for the data to be shown
            rest1 = Project.objects.filter(username_id=uid, is_released=0)
            id_list = []
            for item in rest1:
                id_list.append(item.id)
            return  render(req, 'create_success.html', {
                'web_title': 'create successfully',
                'id_list': id_list,
                'uname': uname[0].username,
            })
        else:
            return redirect('../../login/log/')
    else:
        if 'user' in req.session:
            uid = req.session['user']['user']
            uname = models.User.objects.filter(id=uid)
            idlist = req.POST.getlist('select')
            for item in idlist:
                item = int(item)
                proj = Project.objects.get(id=item)
                proj.is_released = 1
                proj.save()
            return  render(req, 'release_success.html', {
                'web_title': 'release successfully',
                'uname': uname[0].username,
            })
        else:
            return redirect('../../login/log/')

def imgupload(req):
    session = req.session
    if req.method == 'GET':
        if 'user' in session:
            uid = session['user']['user']
            uname = models.User.objects.filter(id=uid)
            return render(req, 'imgupload.html', {
                'web_title': '上传图片',
                'uname': uname[0].username,
            })
        else:
            return redirect('../login/log/')
    else:
        if 'user' in session:
            uid = session['user']['user']
            uname = models.User.objects.filter(id=uid)
            now = int(round(time.time() * 1000))
            now02 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now / 1000))
            file = req.FILES.getlist("upload_img")
            if file==None:
                return redirect('.')
            pic = Image.objects.filter(username_id=uid,is_usf=0)
            num = 0
            for item in pic:
                num = num+1
            picnum = num
            print(file)
            for item in file:
                picnum = picnum+1
                filename = item.name
                if filename.find('.jpg')!=-1:
                    filename = filename[0:filename.find('.jpg')]
                    filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.jpg'
                elif filename.find('.jpeg')!=-1:
                    filename = filename[0:filename.find('.jpeg')]
                    filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.jpeg'
                elif filename.find('.png')!=-1:
                    filename = filename[0:filename.find('.png')]
                    filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.png'
                elif filename.find('.webp')!=-1:
                    filename = filename[0:filename.find('.webp')]
                    filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.webp'
                elif filename.find('.bmp')!=-1:
                    filename = filename[0:filename.find('.bmp')]
                    filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.bmp'
                elif filename.find('.gif')!=-1:
                    filename = filename[0:filename.find('.gif')]
                    filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.gif'
                rand = str(random.randint(100,999))
                fileroute = './static/userstatic/'+rand+str(int(time.time())%10000000)+filename.replace(" ","")[-4:]
                with open(fileroute, 'wb') as f:
                    for i in req.FILES['upload_img'].chunks():
                        f.write(i)
                Image.objects.create(username_id=uid,route=fileroute,is_usf=0)
            return render(req, 'create.html', {
                'web_title': 'create',
                'uname': uname[0].username,
                'upload_success': 'ok',
                'picturenum': picnum,
            })

def videoupload(req):
    session = req.session
    if req.method == 'GET':
        if 'user' in session:
            uid = session['user']['user']
            uname = models.User.objects.filter(id=uid)
            return render(req, 'videoupload.html', {
                'web_title': '上传视频',
                'uname': uname[0].username,
                'upload_success': '',
            })
        else:
            return redirect('../login/log/')
    else:#POST
        if 'user' in session:
            uid = session['user']['user']
            uname = models.User.objects.filter(id=uid)
            now = int(round(time.time() * 1000))
            now02 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now / 1000))
            file = req.FILES.get("upload_video")
            if file!=None:
                filename = file.name
            else:
                return redirect('.')
            if filename.find('.mp4')!=-1:
                filename = filename[0:filename.find('.mp4')]
                filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.mp4'
            elif filename.find('.mkv')!=-1:
                filename = filename[0:filename.find('.mkv')]
                filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.mkv'
            elif filename.find('.wmv') != -1:
                filename = filename[0:filename.find('.wmv')]
                filename = filename + '_' + str(uid) + '_' + uname[0].username + now02 + '.wmv'
            rand = str(random.randint(100,999))
            fileroute = './static/userstatic/'+rand+str(int(time.time())%10000000)+filename.replace(" ","")[-4:]
            with open(fileroute, 'wb') as f:
                for i in req.FILES['upload_video'].chunks():
                    f.write(i)
            extract = req.POST.get('extract')
            extractnum = int(extract)
            extractVideo(uid,extractnum,fileroute)
            images = Image.objects.filter(username_id=uid, is_usf=0)
            picnum = 0
            for item in images:
                picnum += 1
            return render(req, 'create.html', {
                'web_title': 'create',
                'uname': uname[0].username,
                'upload_success': 'ok',
                'picturenum': picnum,
            })
        else:
            return redirect('../login/log/')

def my_create_return(req):
    session = req.session
    if req.method == 'GET':
        if 'user' in session:
            uid = session['user']['user']
            img = Image.objects.filter(username_id=uid, is_usf=0)
            for item in img:
                os.remove(item.route)
            img.delete()
            return redirect('../')
    else:
        return redirect('../login/log/')
#cut the video into pictures and save them into a folder
#named after the name of the user under 'userstatic' folder
def extractVideo(uid, extractnum, videoroute):
    print(videoroute)
    user = models.User.objects.get(id=uid)
    times = 0
    outPutDirName = './static/userstatic/'
    if not os.path.exists(outPutDirName):  # 如果文件目录不存在则创建目录
        os.makedirs(outPutDirName)
    camera = cv2.VideoCapture(videoroute)
    while True:
        times += 1
        res, image = camera.read()
        if not res:
            break
        if times % extractnum == 0:
            file_route = outPutDirName + videoroute[20:-4] + str(times) + '.jpg'
            cv2.imwrite(file_route, image)
            Image.objects.create(username_id=user.id, route=file_route, is_usf=0)
    camera.release()
    os.remove(videoroute)


def chakan(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        return render(req, 'chakan.html', {
            'web_title': '查看',
            'uname': uname[0].username,
        })
    else:
        return redirect('../login/log/')

def chakan_create(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        if req.method == 'GET':
            projects = Project.objects.filter(username_id=uid)
            project = []
            for item in projects:
                if item.adapter!=0:
                    username = models.User.objects.get(id=item.adapter).username
                else:
                    username = ''
                project.append({'project_id': item.id, 'project_adapter': username, 'project_isreleased': item.is_released});
            return render(req, 'chakan_create.html', {
                'web_title': '我创建的项目',
                'uname': uname[0].username,
                'project': project,
            })
        else:
            body = req.body
            json_param = json.loads(body.decode())
            id = json_param["id"]
            number = int(json_param["number"])
            if number==1:#查看
                print(1)
            elif number==2:#撤销
                project = Project.objects.get(id=id)
                if project!=None:
                    project.is_released = 0
                    project.adapter = 0
                    project.save()
            elif number==3:#发布
                project = Project.objects.get(id=id)
                if project != None:
                    project.is_released = 1
                    project.adapter = 0
                    project.save()
            elif number==4:#销毁
                project = Project.objects.get(id=id)
                if project != None:
                    images = Image.objects.filter(project_id=id)
                    for i in images:
                        os.remove(i.route)
                    Image.objects.filter(project_id=id).delete()
                    Project.objects.filter(id=id).delete()
            return  render(req, 'chakan_create.html', {
                'web_title': '我创建的项目',
                'uname': uname[0].username,
            })
    else:
        return redirect('../login/log/')

def zipDir(dirpath,outFullName):
    zip = zipfile.ZipFile(outFullName,"w",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        fpath = path.replace(dirpath,'')
        for filename in filenames:
            zip.write(os.path.join(path,filename),os.path.join(fpath,filename))
    zip.close()

def chakan_project(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        if req.method == 'GET':
            id = int(req.GET.get('id'))
            images = Image.objects.filter(project_id=id)
            total_number = 0
            count = 0
            for item in images:
                total_number += 1
                if item.is_tagged == 1:
                    count += 1
            return render(req, 'show_project.html', {
                'web_title': '我创建的项目',
                'uname': uname[0].username,
                'project_id': int(id),
                'total_number': total_number,
                'is_tagged_number': count,
            })
        else:
            body = req.body
            json_param = json.loads(body.decode())
            id = json_param["id"]
            id = int(id)
            #下载
            images = Image.objects.filter(project_id=id)
            # pascal voc2012
            for item in images:
                boxes = Box.objects.filter(image_id=item.id)
                box_number = 0
                img_width = 0
                img_height = 0
                box_width = []
                box_height = []
                vertex_left = []
                vertex_top = []
                tag = []
                cou = 0
                for it in boxes:
                    cou += 1
                if cou != 0:
                    img_width = boxes[0].img_width
                    img_height = boxes[0].img_height
                for it in boxes:
                    box_number += 1
                    box_width.append(it.box_width)
                    box_height.append(it.box_height)
                    vertex_left.append(it.vertex_left)
                    vertex_top.append(it.vertex_top)
                    tag.append(it.tag)
                name = item.route[20:]
                dom = minidom.getDOMImplementation().createDocument(None, 'annotation', None)
                root = dom.documentElement
                folder = dom.createElement('folder')
                folder.appendChild(dom.createTextNode('VOC2012'))
                root.appendChild(folder)
                filename = dom.createElement('filename')
                filename.appendChild(dom.createTextNode(name))
                source = dom.createElement('source')
                database = dom.createElement('database')
                database.appendChild(dom.createTextNode('BS'))
                annotation_two = dom.createElement('annotation')
                annotation_two.appendChild(dom.createTextNode('PASCAL VOC2012'))
                source.appendChild(database)
                source.appendChild(annotation_two)
                root.appendChild(source)
                size = dom.createElement('size')
                width = dom.createElement('width')
                height = dom.createElement('height')
                depth = dom.createElement('depth')
                width.appendChild(dom.createTextNode(str(img_width)))
                height.appendChild(dom.createTextNode(str(img_height)))
                depth.appendChild(dom.createTextNode('3'))
                size.appendChild(width)
                size.appendChild(height)
                size.appendChild(depth)
                root.appendChild(size)
                segmented = dom.createElement('segmented')
                segmented.appendChild(dom.createTextNode(str(item.is_tagged)))
                root.appendChild(segmented)

                for i in range(box_number):
                    object = dom.createElement('object')
                    tag_name = dom.createElement('name')
                    tag_name.appendChild(dom.createTextNode(tag[i]))
                    object.appendChild(tag_name)
                    pose = dom.createElement('pose')
                    pose.appendChild(dom.createTextNode('Frontal'))
                    object.appendChild(pose)
                    truncated = dom.createElement('truncated')
                    truncated.appendChild(dom.createTextNode('0'))
                    object.appendChild(truncated)
                    difficult = dom.createElement('difficult')
                    difficult.appendChild(dom.createTextNode('0'))
                    object.appendChild(difficult)
                    bndbox = dom.createElement('bndbox')
                    xmin = dom.createElement('xmin')
                    xmin.appendChild(dom.createTextNode(str(vertex_left[i])))
                    ymin = dom.createElement('ymin')
                    ymin.appendChild(dom.createTextNode(str(vertex_top[i])))
                    xmax = dom.createElement('xmax')
                    xmax.appendChild(dom.createTextNode(str(vertex_left[i]+box_width[i])))
                    ymax = dom.createElement('ymax')
                    ymax.appendChild(dom.createTextNode(str(vertex_top[i]+box_height[i])))
                    bndbox.appendChild(xmin)
                    bndbox.appendChild(ymin)
                    bndbox.appendChild(xmax)
                    bndbox.appendChild(ymax)
                    object.appendChild(bndbox)
                    root.appendChild(object)

                with open('./static/download/VOC2012/Annotations/xml/'+name[:-4]+'.xml', 'w', encoding='utf-8') as f:
                    dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')
            shutil.copyfile(item.route, './static/download/VOC2012/Images/'+name)
            # coco
            shutil.copyfile(item.route, './static/download/COCO/Images/' + name)
            data = {}
            data['info'] = {}
            data['licenses'] = []
            data['images'] = []
            data['annotations'] = []
            data['categories'] = []
            # info
            data['info']['description'] = 'COCO 2017 Dataset'
            data['info']['url'] = ''
            data['info']['version'] = '1.0'
            data['info']['year'] = 2017
            data['info']['contributor'] = 'zynm'
            data['info']['date_create'] = '2021/12/18'
            # license 为空
            # categories
            project = Project.objects.get(id=id)
            labels = project.labels.split(',')
            data['categories'] = []
            for i in range(len(labels)):
                category_dict = {}
                category_dict['supercategory'] = labels[i]
                category_dict['id'] = i
                category_dict['name'] = labels[i]
                data['categories'].append(category_dict)
            # images
            for item in images:
                img_dict = {}
                img_dict['license'] = ''
                img_dict['file_name'] = item.route[20:]
                img_dict['coco_url'] = ''
                img_width = 0
                img_height = 0
                cou = 0
                for it in boxes:
                    cou += 1
                if cou != 0:
                    img_width = boxes[0].img_width
                    img_height = boxes[0].img_height
                img_dict['height'] = img_height
                img_dict['width'] = img_width
                img_dict['data_captured'] = ''
                img_dict['flickr_url'] = ''
                img_dict['id'] = item.id
                data['images'].append(img_dict)
            #annotations
            for item in images:
                boxes = Box.objects.filter(image_id=item.id)
                for it in boxes:
                    annotations_dict = {}
                    annotations_dict['id'] = it.id
                    annotations_dict['image_id'] = item.id
                    annotations_dict['segmentation'] = []
                    annotations_dict['is_crowd'] = 1
                    boxes_position = []
                    box_number += 1
                    boxes_position.append(it.vertex_left)
                    boxes_position.append(it.vertex_top)
                    boxes_position.append(it.vertex_left)
                    boxes_position.append(it.vertex_top+it.box_height)
                    boxes_position.append(it.vertex_left+it.box_width)
                    boxes_position.append(it.vertex_top+it.box_height)
                    boxes_position.append(it.vertex_left+it.box_width)
                    boxes_position.append(it.vertex_top)
                    tag = it.tag
                    tag_num = -1
                    for j in range(len(labels)):
                        if labels[j] == tag:
                            tag_num = j
                            break
                    annotations_dict['category_id'] = tag_num
                    bbox = []
                    bbox.append(it.vertex_left)
                    bbox.append(it.vertex_top)
                    bbox.append(it.box_width)
                    bbox.append(it.box_height)
                    annotations_dict['bbox'] = bbox
                    area = it.box_width*it.box_height
                    annotations_dict['area'] = area
                    data['annotations'].append(annotations_dict)
            with open('./static/download/COCO/json/instance.json', 'w') as f:
                json.dump(data, f)
            zipDir('./static/download', './static/download.zip')
            return redirect('../download/')
    else:
        return redirect('../login/log/')

def download(req):
    del_path_one = './static/download/VOC2012/Annotations/xml'
    del_path_two = './static/download/VOC2012/Images'
    del_path_three = './static/download/COCO/Images'
    del_path_four = './static/download/COCO/json'
    if os.path.exists(del_path_one):
        shutil.rmtree(del_path_one)
    if os.path.exists(del_path_two):
        shutil.rmtree(del_path_two)
    if os.path.exists(del_path_three):
        shutil.rmtree(del_path_three)
    if os.path.exists(del_path_four):
        shutil.rmtree(del_path_four)
    os.mkdir('./static/download/VOC2012/Annotations/xml')
    os.mkdir('./static/download/VOC2012/Images')
    os.mkdir('./static/download/COCO/Images')
    os.mkdir('./static/download/COCO/json')

    file_name = './static/download.zip'
    file = open(file_name, 'rb')  # 使用FileResponse 来进行文件读取传输
    f_name = 'download.zip'
    response = FileResponse(file, filename=f_name, as_attachment=True)
    response['Content-Type'] = 'application/octet-stream'
    return response

def chakan_allow(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        if req.method == 'GET':
            projects = Project.objects.filter(adapter=uid)
            project = []
            for item in projects:
                username = models.User.objects.get(id=item.username_id)
                project.append({'project_id': item.id, 'username': username.username})
            return render(req, 'chakan_allow.html', {
                'web_title': '我接受的项目',
                'uname': uname[0].username,
                'project': project
            })
        else:
            body = req.body
            json_param = json.loads(body.decode())
            id = json_param["id"]
            return render(req, 'chakan_allow.html', {
                'web_title': '我接受的项目',
                'uname': uname[0].username,
            })
    else:
        return redirect('../login/log/')

def work(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        if req.method == 'GET':
            id = int(req.GET.get('id'))
            require_seq = int(req.GET.get('require_seq'))
            project = Project.objects.get(id=id)
            images = Image.objects.filter(project_id=id)
            images_route = []
            for item in images:
                images_route.append(item.route)
            return_route = 'empty'
            if images_route!=[]:
                return_route = images_route[require_seq-1]
                return_route = '../..'+return_route[1:]
            labels = project.labels
            mylabels = labels.split(",")
            send_labels = {}
            for i in range(len(mylabels)):
                send_labels[str(i)] = mylabels[i]
            return render(req, 'workspace.html', {
                'web_title': '工作区',
                'uname': uname[0].username,
                'img_route': return_route,
                'sequence_number': require_seq,
                'id': id,
                'total_img_number': len(images_route),
                'labels': send_labels,
                'label_num': len(mylabels),
            })
        else:#post
            body = req.body
            json_param = json.loads(body.decode())
            id = json_param["id"]
            id = int(id)
            img_width = json_param["img_width"]
            print('img_width:', img_width)
            img_height = json_param["img_height"]
            print('img_height:', img_height)
            box_width = json_param["box_width"]
            tmp_box_width = []
            for i in box_width:
                tmp_box_width.append(round(float(i), 2))
            box_width = tmp_box_width
            box_height = json_param["box_height"]
            tmp_box_height = []
            for i in box_height:
                tmp_box_height.append(round(float(i), 2))
            box_height = tmp_box_height
            vertex_left = json_param["vertex_left"]
            tmp_vertex_left = []
            for i in vertex_left:
                tmp_vertex_left.append(round(float(i), 2))
            vertex_left = tmp_vertex_left
            vertex_top = json_param["vertex_top"]
            tmp_vertex_top = []
            for i in vertex_top:
                tmp_vertex_top.append(round(float(i), 2))
            vertex_top = tmp_vertex_top
            tag_text = json_param["tag_text"]
            sequence_number = json_param["sequence_number"]
            sequence_number = int(sequence_number)
            print('box_width:', box_width)
            print('box_height:', box_height)
            print('vertex_top:', vertex_top)
            print('vertex_left:', vertex_left)
            print('tag_text:', tag_text)
            print('sequence_number:', sequence_number)

            images = Image.objects.filter(project_id=id)
            img_id = images[sequence_number-1].id
            del_box = Box.objects.filter(image_id=img_id).delete()
            this_image = Image.objects.get(id=img_id)
            this_image.is_tagged = 1
            this_image.save()
            for i in range(len(box_width)):
                Box.objects.create(image_id=img_id, img_width=img_width, img_height=img_height, box_width=box_width[i],
                                   box_height=box_height[i], vertex_left=vertex_left[i], vertex_top=vertex_top[i], tag=tag_text[i])
            return render(req, 'workspace.html', {
                'web_title': '工作区',
                'uname': uname[0].username,
            })
    else:
        return redirect('../login/log/')

def receive(req):
    session = req.session
    if 'user' in session:
        uid = session['user']['user']
        uname = models.User.objects.filter(id=uid)
        if req.method == 'GET':
            projects = Project.objects.filter(adapter=0)
            project = []
            for item in projects:
                username = models.User.objects.get(id=item.username_id)
                mydict = {'id': item.id, "name": username.username}
                project.append(mydict)
            print(project)
            return render(req, 'receive.html', {
                'web_title': '接受项目',
                'uname': uname[0].username,
                'project': project,
            })
        else:
            body = req.body
            json_param = json.loads(body.decode())
            project_id = json_param["project_id"]
            project_id = int(project_id)
            myproject = Project.objects.get(id=project_id)
            if myproject!=None:
                myproject.is_released = 1
                myproject.adapter = uid
                myproject.save()
            return render(req, 'receive.html', {
                'web_title': '接受项目',
                'uname': uname[0].username,
            })
    else:
        return redirect('../login/log/')
