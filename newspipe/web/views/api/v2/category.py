from flask import current_app
from flask_restful import Api

from newspipe.bootstrap import application
from newspipe.bootstrap import csrf
from newspipe.controllers.category import CategoryController
from newspipe.web.views.api.v2.common import PyAggResourceExisting
from newspipe.web.views.api.v2.common import PyAggResourceMulti
from newspipe.web.views.api.v2.common import PyAggResourceNew


class CategoryNewAPI(PyAggResourceNew):
    controller_cls = CategoryController


class CategoryAPI(PyAggResourceExisting):
    controller_cls = CategoryController


class CategoriesAPI(PyAggResourceMulti):
    controller_cls = CategoryController


api = Api(current_app, prefix=application.config["API_ROOT"], decorators=[csrf.exempt])
api.add_resource(CategoryNewAPI, "/category", endpoint="category_new.json")
api.add_resource(CategoryAPI, "/category/<int:obj_id>", endpoint="category.json")
api.add_resource(CategoriesAPI, "/categories", endpoint="categories.json")
