from flask import g

from web.controllers.category import CategoryController
from web.views.api.common import (PyAggResourceNew,
                                  PyAggResourceExisting,
                                  PyAggResourceMulti)


CAT_ATTRS = {'name': {'type': str},
             'user_id': {'type': int}}


class CategoryNewAPI(PyAggResourceNew):
    controller_cls = CategoryController
    attrs = CAT_ATTRS


class CategoryAPI(PyAggResourceExisting):
    controller_cls = CategoryController
    attrs = CAT_ATTRS


class CategoriesAPI(PyAggResourceMulti):
    controller_cls = CategoryController
    attrs = CAT_ATTRS


g.api.add_resource(CategoryNewAPI, '/category', endpoint='category_new.json')
g.api.add_resource(CategoryAPI, '/category/<int:obj_id>',
                   endpoint='category.json')
g.api.add_resource(CategoriesAPI, '/categories', endpoint='categories.json')
