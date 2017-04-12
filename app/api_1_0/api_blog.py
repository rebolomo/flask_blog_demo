from flask import jsonify, request, g, abort, url_for, current_app, g
from .. import db
from ..models import User, Blog, Permission
from . import api
from .decorators import permission_required
from .errors import bad_request
from app import logger
import json

@api.route('/blog/all', methods=['GET'])
# all blogs, no pager
#@authentication.login_exempt
def get_blogs_all():
    items = Blog.query.filter_by(user_id= g.current_user.id).all()

    ret = {}
    ret['errorcode'] = 0
    results = [item.to_json() for item in items]
    
    ret['blogs'] = results
    #ret['revision'] = current_revision
    return jsonify(ret)

# REBOL note, with pager, the client app handle the pager logic
@api.route('/blog', methods=['GET'])
# 所有shops
def get_blogs():
    item_id = request.args.get('item_id', 0, type=int)

    # REBOL note, if param is 0, return id of the latest created blog.
    if item_id == 0:
        item = Blog.query.filter(Blog.user_id == g.current_user.id).order_by(Blog.id.desc()).first()
        if item is not None:
            # REBOL note, 最大值加1，这样后面找的时候，可以统一用Shop.id < item_id
            item_id = item.id + 1

    # REBOL note，return the latest several blogs which has id less than item_id
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    #logger.info(item_id)
    items = Blog.query.filter(Blog.user_id == g.current_user.id, Blog.id < item_id).order_by(Blog.id.desc()).limit(per_page).all()
    logger.info(items)
    
    ret = {}
    ret['errorcode'] = 0

    if items is not None:
        items_count = len(items)
        last_item_id = item_id
        if items_count > 0:
            last_item_index = items_count - 1
            logger.info("last_item_index" + str(last_item_index))
            last_item = items[last_item_index]
            last_item_id = last_item.id

        ret['item_id'] = last_item_id
        ret['blogs'] = [item.to_json() for item in items]
        ret['view_more'] = True
        if items_count < per_page:
            ret['view_more'] = False        
    else:
        ret['item_id'] = item_id
        ret['blogs'] = None
        ret['view_more'] = False

    return jsonify(ret)

@api.route('/blog', methods=['POST'])
@permission_required(Permission.CREATE_BLOG)
def create_blog():
    ret = {}
    ret['errorcode'] = 0

    params = request.json
    logger.info(params)
    item = Blog.from_dict(params)

    db.session.add(item)
    db.session.commit()

    ret['blog'] = item.to_json()
    return jsonify(ret)

@api.route('/blog/<int:id>', methods=['PUT'])
@permission_required(Permission.CREATE_BLOG)
def edit_blog(id):
    ret = {}
    ret['errorcode'] = 0
 
    item = Blog.query.filter_by(id=id, user_id=g.current_user.id).first()

    if item is None:
        return bad_request(WebReturnCode.SHOP_NOT_FOUND)

    #item_id = request.args.get('item_id', 0, type=int)
    #param = {'name' : 'shop1111', 'address' : '222222', 'tel' : '13988277281', 'user_id' : 3 }

    params = request.json
    #logger.info(params)
    item.title = params['title']
    item.content = params['content']

    db.session.add(item)
    db.session.commit()
    ret['blog'] = item.to_json()
    return json.dumps(ret)

@api.route('/blog/<int:id>', methods=['DELETE'])
@permission_required(Permission.CREATE_BLOG)
def delete_blog(id):
    ret = {}
    ret['errorcode'] = 0

    item = Blog.query.filter_by(id=id, user_id=g.current_user.id).first()

    if item is None:
        return bad_request(WebReturnCode.SHOP_NOT_FOUND)

    if item.user_id != g.current_user.id:
        return bad_request(WebReturnCode.SHOP_NOT_FROM_THIS_USER)

    db.session.delete(item)
    db.session.commit()
    return json.dumps(item.to_json())