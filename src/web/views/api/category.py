from conf import API_ROOT
from flask import current_app
from flask.ext.restful import Api

from web.controllers.category import CategoryController
from web.views.api.common import (PyAggResourceNew,
                                  PyAggResourceExisting,
                                  PyAggResourceMulti)


class CategoryNewAPI(PyAggResourceNew):
    controller_cls = CategoryController


class CategoryAPI(PyAggResourceExisting):
    controller_cls = CategoryController


class CategoriesAPI(PyAggResourceMulti):
    controller_cls = CategoryController


api = Api(current_app, prefix=API_ROOT)
api.add_resource(CategoryNewAPI, '/category', endpoint='category_new.json')
api.add_resource(CategoryAPI, '/category/<int:obj_id>',
                 endpoint='category.json')
api.add_resource(CategoriesAPI, '/categories', endpoint='categories.json')
